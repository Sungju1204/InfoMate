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
    try:
        tag = soup.select_one('span.media_end_head_info_datestamp_time')
        if tag:
            return date_parser.parse(tag['data-date-time']).isoformat()

        tag = soup.select_one('span.num_date')
        if tag:
            return date_parser.parse(tag.get_text()).isoformat()

        json_ld = soup.find_all('script', {'type': 'application/ld+json'})
        for s in json_ld:
            if not s.string:
                continue
            data = json.loads(s.string)
            if data.get('datePublished'):
                return date_parser.parse(data['datePublished']).isoformat()
    except:
        pass

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
                page.goto(url_to_check, wait_until='networkidle', timeout=60000)  
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
                "cached": False
            }
        }, status=200)