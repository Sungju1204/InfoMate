import os 
import json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import re
import torch 
from dotenv import load_dotenv

# dotenv 로드
load_dotenv() 

# Playwright
from playwright.sync_api import sync_playwright

from django.http import JsonResponse
from rest_framework.views import APIView 
from rest_framework.throttling import AnonRateThrottle
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from openai import OpenAI

# API 키 설정 (settings.py나 .env에서 가져옴)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_gpt_prediction(title, text):
    """GPT 모델 분석"""
    if not client:
        return {"error": "API 키 설정 오류", "prediction": "Error"}
        
    try:
        truncated_text = text[:3000] # 토큰 절약
        
        # ★★★ [수정됨] 점수 기준을 '신뢰도'로 변경 ★★★
        system_prompt = """
        당신은 뉴스 기사의 신뢰도를 평가하는 '팩트체크 AI'입니다.
        제공된 기사를 분석하여 JSON 형식으로 답하세요.
        
        [점수 기준]
        - 점수(score)는 0~100점 사이의 '신뢰도 점수'입니다.
        - 100점에 가까울수록: 사실에 기반함, 출처 명확, 객관적 (진짜 뉴스)
        - 0점에 가까울수록: 거짓 정보, 선동, 근거 없음 (가짜 뉴스)
        
        [응답 형식]
        {
            "prediction": "True" (신뢰할 수 있음) 또는 "Fake" (신뢰할 수 없음),
            "score": 0~100 (높을수록 진실),
            "reason": "판단 이유를 한국어로 명확하게 2문장 요약"
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"제목: {title}\n본문: {truncated_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # 분석은 냉정하게
        )
        
        result = json.loads(response.choices[0].message.content)
        result["model_type"] = "GPT-4o-mini"
        return result
        
    except Exception as e:
        print(f"GPT Error: {e}")
        return {"error": str(e), "prediction": "Error"}

        
# --- 1. AI 모델 로딩 ---
from transformers import AutoTokenizer, AutoModelForSequenceClassification
MODEL_PATH = os.environ.get("MODEL_DIRECTORY", "./my_fake_news_model") 

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print(f"✅ AI 모델 로딩 성공 ({MODEL_PATH})")
except Exception as e:
    print(f"❌ AI 모델 로딩 실패: {e}")
    tokenizer = None
    model = None


# --- 2. 언론사 신뢰도 DB ---
MEDIA_TRUST_DB = {
    "KBS": {"rank": 1, "score": 42.2, "category": "신뢰도 1위"},
    "MBC": {"rank": 2, "score": 30.5, "category": "신뢰도 2위"},
    "YTN": {"rank": 3, "score": 22.8, "category": "신뢰도 3위"},
}

def get_media_trust_score(publisher_name):
    for key in MEDIA_TRUST_DB.keys():
        if key in publisher_name:
            return MEDIA_TRUST_DB[key]
    return {"rank": None, "score": None, "category": "신뢰도 순위권 외"}

import re

def extract_date_from_url(url):
    # 예: /2025/11/23/ 또는 /20251123/ 형태 찾기
    match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', url)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    
    match_compact = re.search(r'/(\d{4})(\d{2})(\d{2})/', url)
    if match_compact:
        return f"{match_compact.group(1)}-{match_compact.group(2)}-{match_compact.group(3)}"
        
    return None


# --- 3. 기사 제목/본문 크롤링 ---
def find_article_content(soup):
    title = ""
    text = ""
    
    # 네이버/다음
    title_tag = soup.select_one('h2.media_end_head_headline')
    if not title_tag:
        title_tag = soup.select_one('h3.tit_view')

    if title_tag:
        title = title_tag.get_text().strip()

    # 범용 h1
    if not title and soup.find('h1'):
        title = soup.find('h1').get_text().strip()

    # og:title
    if not title:
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()

    # 본문
    article_body = soup.select_one('div#dic_area')
    if not article_body:
        article_body = soup.select_one('div.article_view')
    if not article_body:
        article_body = soup.find('article')

    if article_body:
        for junk in article_body.select('div.vod_player, div.promotion, span.end_photo_org'):
            junk.decompose()

        paragraphs = article_body.find_all('p', recursive=False)
        if paragraphs:
            text = " ".join(p.get_text().strip() for p in paragraphs if p.get_text())
        else:
            text = article_body.get_text().strip()

    # 최후 수단
    if not text:
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text().strip() for p in paragraphs if p.get_text())

    # "뉴스" 같은 기본 텍스트 방지
    if title == "뉴스":
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()

    return title, text


# --- 4. AI 예측 ---
def get_fake_news_prediction(title, text):
    if not tokenizer or not model:
        return {"error": "AI 모델 로딩 실패"}

    input_text = f"{title} [SEP] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True,
                       max_length=512, padding="max_length")
    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    prob_true = probs[0][0].item()
    prob_fake = probs[0][1].item()

    return {
        "prediction": "Fake" if prob_fake > prob_true else "True",
        "fake_percentage": round(prob_fake * 100, 2),
        "true_percentage": round(prob_true * 100, 2)
    }


# --- 5. 도메인/출처 처리 ---
def get_domain_from_url(url):
    try:
        netloc = urlparse(url).netloc
        return netloc.replace('www.', '') if netloc.startswith('www.') else netloc
    except:
        return None


def find_publisher_name(soup, domain):
    try:
        if domain == "n.news.naver.com":
            logo = soup.select_one('a.media_end_head_top_logo img')
            if logo and logo.get('alt'):
                return logo['alt'].strip()

        if domain.endswith("daum.net"):
            logo = soup.select_one('div.info_cp a.link_cp img')
            if logo and logo.get('alt'):
                return logo['alt'].strip()

        og = soup.find('meta', {'property': 'og:site_name'})
        if og and og.get('content'):
            return og['content'].strip()

        json_ld = soup.find_all('script', {'type': 'application/ld+json'})
        for s in json_ld:
            if not s.string:
                continue
            data = json.loads(s.string)
            if data.get('publisher') and data['publisher'].get('name'):
                return data['publisher']['name']

    except:
        pass

    return domain


def find_publish_date(soup, url):
    date_found = None

    # 1. Meta 태그 확인 (가장 신뢰도 높음)
    # article:published_time, og:updated_time, pubdate, lastmod 등 다양한 키워드 시도
    meta_targets = [
        {'property': 'article:published_time'},
        {'property': 'og:published_time'},
        {'property': 'og:updated_time'},
        {'name': 'pubdate'},
        {'name': 'date'},
        {'itemprop': 'datePublished'},
        {'itemprop': 'dateModified'}
    ]

    for attr in meta_targets:
        tag = soup.find('meta', attr)
        if tag and tag.get('content'):
            try:
                date_found = date_parser.parse(tag['content']).isoformat()
                return date_found # 찾으면 즉시 반환
            except:
                continue

    # 2. JSON-LD (구조화된 데이터) 확인
    try:
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                # JSON이 리스트일 수도, 딕셔너리일 수도 있음
                if isinstance(data, list):
                    for item in data:
                        if 'datePublished' in item:
                            return date_parser.parse(item['datePublished']).isoformat()
                elif isinstance(data, dict):
                    if 'datePublished' in data:
                        return date_parser.parse(data['datePublished']).isoformat()
                    # @graph 구조로 되어있는 경우 (Wordpress 등)
                    if '@graph' in data:
                         for item in data['@graph']:
                            if 'datePublished' in item:
                                return date_parser.parse(item['datePublished']).isoformat()
            except:
                continue
    except:
        pass

    # 3. HTML 태그 선택자 (사이트별 특화)
    selectors = [
        'span.media_end_head_info_datestamp_time', # 네이버 뉴스
        'span.num_date',                             # 다음 뉴스
        'div.news_date',                             # 일반적인 언론사
        'p.date',
        'span.date',
        '.input-date',
        '#date-text',                                # 일부 언론사 ID
        '.wdate',                                    # 위키트리 등
        '.t-11',                                     # 조선일보 일부 레이아웃
    ]
    
    for selector in selectors:
        tags = soup.select(selector)
        for tag in tags:
            text = tag.get_text().strip()
            # 텍스트에 숫자가 포함되어 있어야 날짜로 간주
            if text and any(c.isdigit() for c in text):
                try:
                    # "입력 2025.11.23" 같은 한글 제거 후 파싱 시도
                    clean_text = re.sub(r'[^\d\-\.\: ]', '', text).strip()
                    return date_parser.parse(clean_text).isoformat()
                except:
                    continue

    # 4. [최후의 수단] URL에서 날짜 추출
    # 조선일보 URL에는 날짜가 들어있습니다 (court_law/2025/11/23/...)
    url_date = extract_date_from_url(url)
    if url_date:
        return url_date

    return "날짜 찾기 실패"

# --- 6. Django View ---
@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):

        # URL 파싱
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
            if not url_to_check:
                return JsonResponse({"success": False, "error": {"message": "URL 누락"}}, status=400)
        except:
            return JsonResponse({"success": False, "error": {"message": "잘못된 JSON"}}, status=400)

        parsed_url = urlparse(url_to_check)
        if not parsed_url.scheme or not parsed_url.netloc:
            return JsonResponse({"success": False, "error": {"message": "유효하지 않은 URL"}}, status=400)

        domain = get_domain_from_url(url_to_check)
        
        # ★★★ 도메인 제한 로직 제거 완료 ★★★
        # 이제 모든 도메인에 대한 접근을 허용합니다.

        # 미리 모든 변수 초기화 → UnboundLocalError 방지
        publisher_name = ""
        publish_date = ""
        title = ""
        text_content = ""
        ai_result = None
        html = None # Playwright가 실패했을 때 html 변수가 정의되지 않는 것을 방지

        # Playwright 실행
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    # 최신 크롬 사용자 에이전트 사용 (크롤링 차단 회피)
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )

                # 안정적인 크롤링 설정: 네트워크 활동이 잠잠해질 때까지 대기
                # 2. timeout=60000 -> 90000 (90초로 늘림)
                page.goto(url_to_check, wait_until='domcontentloaded', timeout=90000)  
                html = page.content()

        except Exception as e:
            print(f"Playwright/크롤링 오류: {e}")
            return JsonResponse({
                "success": False,
                "error": {"message": f"크롤링 중 오류: {e}"}
            }, status=500)

        finally:
            if browser:
                try:
                    browser.close()
                except:
                    pass
        
        # 크롤링 결과가 없는 경우 처리
        if not html:
            return JsonResponse({
                "success": False,
                "error": {"message": "크롤링 후 HTML 내용을 가져오지 못했습니다."},
            }, status=500)


        # BeautifulSoup 파싱 및 정보 추출
        soup = BeautifulSoup(html, "html.parser")

        publisher_name = find_publisher_name(soup, domain)
        publish_date = find_publish_date(soup, url_to_check)
        title, text_content = find_article_content(soup)

        # 크롤링 실패 체크 (제목/본문이 짧거나 없는 경우)
        if not title or not text_content or len(text_content.strip()) < 50:
            return JsonResponse({
                "success": False,
                "error": {"message": "기사 제목/본문 크롤링 실패 또는 내용이 너무 짧음"},
                "data": {
                    "requested_url": url_to_check,
                    "publisher_name": publisher_name,
                    "published_date": publish_date,
                    "scraped_title": title,
                    "ai_prediction": None,
                    "media_trust": get_media_trust_score(publisher_name),
                    "cached": False
                }
            }, status=400)

        # AI 분석 실행
        ai_result = get_fake_news_prediction(title, text_content)
        gpt_result = get_gpt_prediction(title, text_content)
        # 정상 응답
        return JsonResponse({
            "success": True,
            "data": {
                "requested_url": url_to_check,
                "publisher_name": publisher_name,
                "published_date": publish_date,
                "scraped_title": title,
                "ai_prediction": ai_result,
                "media_trust": get_media_trust_score(publisher_name),

                # GPT 결과가 여기에 들어갑니다
                "gpt_model": {
                        "score": gpt_result.get('score', 0), 
                        "reason": gpt_result.get('reason', "분석 결과를 가져오지 못했습니다."),
                        "prediction": gpt_result.get('prediction', "Unknown")         # 판단 이유
                },

                "cached": False
            }
        }, status=200)


