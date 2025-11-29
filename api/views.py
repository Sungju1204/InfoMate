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

# API 키 설정
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- 헬퍼 함수: 텍스트 정규화 (제목 비교용) ---
def normalize_text(text):
    """공백과 특수문자를 제거하여 비교하기 쉽게 만듦"""
    if not text: return ""
    return re.sub(r'\s+|[^\w]', '', text)


def get_gpt_prediction(title, text):
    """GPT 모델 분석 + 키워드 추출"""
    if not client:
        return {"error": "API 키 설정 오류", "prediction": "Error"}
        
    try:
        truncated_text = text[:3000]
        
        system_prompt = """
        당신은 뉴스 기사의 신뢰도를 평가하는 '팩트체크 AI'입니다.
        제공된 기사를 분석하여 JSON 형식으로 답하세요.
        
        [응답 형식]
        {
            "prediction": "True" 또는 "Fake",
            "score": 0~100 (높을수록 진실),
            "reason": "판단 이유를 한국어로 2문장 요약",
            "keywords": "검색용 핵심 키워드 2~3개를 띄어쓰기로 구분하여 한 줄로 작성 (예: 비트코인 폭락 전망)" 
        }
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"제목: {title}\n본문: {truncated_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        result["model_type"] = "GPT-4o-mini"
        return result
        
    except Exception as e:
        print(f"GPT Error: {e}")
        return {"error": str(e), "prediction": "Error"}

# 관련 기사 추출 (네이버)
def get_related_articles(keyword):
    if not keyword: return []

    try:
        search_url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        
        articles = []
        news_items = soup.select("div.news_wrap.api_ani_send")
        
        # [수정] 3개 -> 5개로 늘림 (중복 제거 대비)
        for item in news_items[:5]:
            try:
                title_tag = item.select_one("a.news_tit")
                if not title_tag: continue
                
                link = title_tag['href']
                title = title_tag.get_text().strip()
                
                img_tag = item.select_one("img.thumb")
                img_url = img_tag['data-lazysrc'] if img_tag and 'data-lazysrc' in img_tag.attrs else None
                if not img_url and img_tag: img_url = img_tag.get('src')

                press_tag = item.select_one("a.info.press")
                press = press_tag.get_text().strip() if press_tag else "알수없음"

                articles.append({
                    "title": title,
                    "link": link,
                    "press": press,
                    "thumbnail": img_url,
                    "source": "Naver"
                })
            except: continue     
        return articles

    except Exception as e:
        print(f"관련 기사 검색 실패: {e}")
        return []

# 관련 기사 추출 (구글)
def get_google_news(keyword):
    """
    Playwright를 사용하여 구글 뉴스 탭 검색 결과를 가져옵니다. (에러 방지 강화판)
    """
    if not keyword:
        return []

    articles = []
    browser = None
    try:
        with sync_playwright() as p:
            # 헤드리스 모드지만 봇 탐지를 피하기 위한 설정들
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
            
            # 구글 뉴스 검색 URL
            url = f"https://www.google.com/search?q={keyword}&tbm=nws&hl=ko&gl=KR"
            
            # 타임아웃을 30초 -> 10초로 줄여서 실패하면 빨리 포기하게 함 (전체 응답 속도 위해)
            page.goto(url, wait_until='domcontentloaded', timeout=10000)
            
            # [수정] 특정 ID(#search)를 기다리다가 에러나지 말고, 그냥 2~3초 멍때리며 로딩 기다리기
            page.wait_for_timeout(3000) 

            # 구글 뉴스 카드 요소들 선택 (여러 클래스명 시도)
            # div.SoaBEf: 전통적인 뉴스 카드 / div.MjjYud: 최신 레이아웃
            news_elements = page.query_selector_all('div.SoaBEf, div.MjjYud')

            count = 0
            for item in news_elements:
                if count >= 5: break # 5개만 채우면 중단
                
                try:
                    # 링크 태그 찾기
                    link_tag = item.query_selector('a')
                    if not link_tag: continue
                    
                    link = link_tag.get_attribute('href')
                    if not link.startswith('http'): continue # 이상한 링크 제외

                    # 제목 찾기 (role="heading"이 가장 정확함)
                    title_div = item.query_selector('div[role="heading"]')
                    title = title_div.inner_text() if title_div else link_tag.inner_text()
                    
                    if not title: continue

                    # 언론사 찾기
                    press_div = item.query_selector('.MgUUmf span')
                    press = press_div.inner_text() if press_div else "Google News"

                    # 썸네일 찾기
                    img_tag = item.query_selector('img')
                    img = img_tag.get_attribute('src') if img_tag else None

                    articles.append({
                        "title": title,
                        "link": link,
                        "press": press,
                        "thumbnail": img,
                        "source": "Google"
                    })
                    count += 1
                except:
                    continue
                    
    except Exception as e:
        # 구글 검색이 실패해도 로그만 찍고 빈 리스트 반환 (서버 안 죽음)
        print(f"⚠️ 구글 검색 건너뜀 (사유: {e})")
        return []
        
    finally:
        if browser:
            try: browser.close()
            except: pass
            
    return articles


# --- 1. AI 모델 로딩 (로컬) ---
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
        if key in publisher_name: return MEDIA_TRUST_DB[key]
    return {"rank": None, "score": None, "category": "순위권 외"}

def extract_date_from_url(url):
    match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', url)
    if match: return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    match_compact = re.search(r'/(\d{4})(\d{2})(\d{2})/', url)
    if match_compact: return f"{match_compact.group(1)}-{match_compact.group(2)}-{match_compact.group(3)}"
    return None


# --- 3. 기사 제목/본문 크롤링 ---
def find_article_content(soup):
    title = ""
    text = ""
    
    title_tag = soup.select_one('h2.media_end_head_headline') or soup.select_one('h3.tit_view')
    if title_tag: title = title_tag.get_text().strip()
    if not title and soup.find('h1'): title = soup.find('h1').get_text().strip()
    if not title:
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'): title = og_title['content'].strip()

    article_body = soup.select_one('div#dic_area') or soup.select_one('div.article_view') or soup.find('article')
    if article_body:
        text = article_body.get_text(separator=" ").strip()
    else:
        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text().strip() for p in paragraphs if p.get_text())

    return title, text


# --- 4. AI 예측 (로컬) ---
def get_fake_news_prediction(title, text):
    if not tokenizer or not model: return {"error": "AI 모델 로딩 실패"}
    input_text = f"{title} [SEP] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad(): outputs = model(**inputs)
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
    except: return None

def find_publisher_name(soup, domain):
    try:
        og = soup.find('meta', {'property': 'og:site_name'})
        if og and og.get('content'): return og['content'].strip()
    except: pass
    return domain

def find_publish_date(soup, url):
    meta_targets = ['article:published_time', 'og:published_time', 'pubdate']
    for attr in meta_targets:
        # [수정] property=... 와 name=... 을 attrs 딕셔너리로 감싸서 충돌 방지
        tag = soup.find('meta', attrs={'property': attr}) or \
            soup.find('meta', attrs={'name': attr})
            
        if tag and tag.get('content'):
            try: return date_parser.parse(tag['content']).isoformat()
            except: continue
            
    url_date = extract_date_from_url(url)
    if url_date: return url_date
    return "날짜 찾기 실패"


# --- 6. Django View ---
@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        # 1. URL 및 데이터 준비
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
        except: return JsonResponse({"success": False, "error": {"message": "잘못된 요청"}}, status=400)

        domain = get_domain_from_url(url_to_check)
        
        # 2. 크롤링 (Playwright)
        html = None
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                page.goto(url_to_check, wait_until='domcontentloaded', timeout=90000)  
                html = page.content()
        except Exception as e:
            return JsonResponse({"success": False, "error": {"message": f"크롤링 오류: {e}"}}, status=500)
        finally:
            if browser: 
                try: browser.close() 
                except: pass
        
        if not html: return JsonResponse({"success": False, "error": {"message": "HTML 추출 실패"}}, status=500)

        # 3. 데이터 추출
        soup = BeautifulSoup(html, "html.parser")
        publisher_name = find_publisher_name(soup, domain)
        publish_date = find_publish_date(soup, url_to_check)
        title, text_content = find_article_content(soup)

        if not title or len(text_content) < 50:
            return JsonResponse({"success": False, "error": {"message": "본문 추출 실패"}}, status=400)

        # 4. AI 분석 실행
        ai_result = get_fake_news_prediction(title, text_content)
        gpt_result = get_gpt_prediction(title, text_content)
        
        # 5. 관련 기사 검색 및 필터링 (★★★ 수정된 부분 ★★★)
        related_articles = []
        keywords = gpt_result.get("keywords", "")
        
        if keywords:
            print(f"🔎 검색 키워드: {keywords}")
            # 각각 5개씩 넉넉히 가져옴
            naver_raw = get_related_articles(keywords)
            google_raw = get_google_news(keywords)

            # 검색 결과 합치기
            all_articles = naver_raw + google_raw
            
            # [중복 제거 로직] 현재 기사 제목과 유사하면 제거
            # 정규화된 현재 제목
            current_title_norm = normalize_text(title)
            
            filtered_list = []
            for item in all_articles:
                item_title_norm = normalize_text(item['title'])
                
                # 1. 제목이 너무 짧으면 패스
                if len(item_title_norm) < 2: continue
                
                # 2. 현재 기사 제목이 검색된 기사 제목에 포함되거나, 그 반대인 경우 (유사도 높음)
                # 예: "비트코인 폭락" vs "오늘 비트코인 폭락 충격"
                if current_title_norm in item_title_norm or item_title_norm in current_title_norm:
                    print(f"🚫 중복 제외됨: {item['title']}")
                    continue
                    
                filtered_list.append(item)

            # 필터링 후 최대 5개만 자르기 (네이버 우선순위 유지를 위해 섞지 않고 순서대로)
            related_articles = filtered_list[:5]

        return JsonResponse({
            "success": True,
            "data": {
                "requested_url": url_to_check,
                "publisher_name": publisher_name,
                "published_date": publish_date,
                "scraped_title": title,
                "ai_prediction": ai_result,
                "media_trust": get_media_trust_score(publisher_name),
                "gpt_model": {
                    "score": gpt_result.get('score', 0),
                    "reason": gpt_result.get('reason', ""),
                    "prediction": gpt_result.get('prediction', ""),
                    "keywords": keywords
                },
                "related_articles": related_articles, # 필터링된 리스트
                "cached": False
            }
        }, status=200)