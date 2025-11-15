# api/views.py (Playwright 적용 최종본)

import json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import re
import torch 

# (!!! NEW !!!) Playwright 라이브러리 임포트
from playwright.sync_api import sync_playwright

from django.http import JsonResponse
from rest_framework.views import APIView # <-- 이 줄을 추가
from rest_framework.throttling import AnonRateThrottle
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .trusted_domains import TRUSTED_DOMAINS #신뢰 URL

# --- 1. AI 모델 로딩 (기존과 동일) ---
from transformers import AutoTokenizer, AutoModelForSequenceClassification
MODEL_PATH = os.environ.get("MODEL_DIRECTORY", "./my_fake_news_model") # 모델 불러오기
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print(f"✅ AI 모델 로딩 성공 ({MODEL_PATH})")
except Exception as e:
    print(f"❌ AI 모델 로딩 실패: {e}")
    tokenizer = None
    model = None

# --- 2. 언론사 신뢰도 DB (기존과 동일) ---
MEDIA_TRUST_DB = {
    "KBS": {"rank": 1, "score": 42.2, "category": "신뢰도 1위"},
    "MBC": {"rank": 2, "score": 30.5, "category": "신뢰도 2위"},
    "YTN": {"rank": 3, "score": 22.8, "category": "신뢰도 3위"},
    # ... (이하 생략) ...
}
def get_media_trust_score(publisher_name):
    # ... (기존 코드와 동일) ...
    for key in MEDIA_TRUST_DB.keys():
        if key in publisher_name:
            return MEDIA_TRUST_DB[key]
    return {"rank": None, "score": None, "category": "신뢰도 순위권(Top 10) 외"}


# --- 3. (!!! UPGRADED !!!) 기사 제목/본문 크롤링 함수 ---
# (네이버/다음의 동적 태그를 지원하도록 수정)
def find_article_content(soup):
    title = ""
    text = ""
    
    # --- 네이버/다음 제목 (우선순위 1) ---
    title_tag = soup.select_one('h2.media_end_head_headline') # 네이버
    if not title_tag:
        title_tag = soup.select_one('h3.tit_view') # 다음
    if title_tag:
        title = title_tag.get_text().strip()

    # --- 범용 제목 (우선순위 2) ---
    if not title:
        if soup.find('h1'):
            title = soup.find('h1').get_text().strip()
    if not title:
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()

    # --- 네이버/다음 본문 (우선순위 1) ---
    # (네이버: dic_area, 다음: article_view)
    article_body = soup.select_one('div#dic_area') 
    if not article_body:
        article_body = soup.select_one('div.article_view')
    
    # --- 범용 본문 (우선순위 2) ---
    if not article_body:
        article_body = soup.find('article')
    
    if article_body:
        # 본문 내의 불필요한 광고/댓글 섹션 제거 (선택적)
        for junk in article_body.select('div.vod_player, div.promotion, span.end_photo_org'):
            junk.decompose()
            
        paragraphs = article_body.find_all('p', recursive=False) # 직계 p 태그
        if not paragraphs:
             # p 태그가 없는 경우 (div로 쪼개진 경우) 통째로 텍스트 추출
             text = article_body.get_text().strip()
        else:
             text = " ".join([p.get_text().strip() for p in paragraphs if p.get_text()])
    
    # --- 최후의 수단 (우선순위 3) ---
    if not text:
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs if p.get_text()])

    # 네이버에서 제목이 "뉴스"로만 나오는 경우 재시도
    if title == "뉴스":
        og_title = soup.find('meta', {'property': 'og:title'})
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()

    return title, text

# --- 4. AI 예측 함수 (기존과 동일) ---
def get_fake_news_prediction(title, text):
    # ... (기존 코드와 동일) ...
    input_text = f"{title} [SEP] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    prob_true = probabilities[0][0].item()
    prob_fake = probabilities[0][1].item()
    return {
        "prediction": "Fake" if prob_fake > prob_true else "True",
        "fake_percentage": round(prob_fake * 100, 2),
        "true_percentage": round(prob_true * 100, 2)
    }

# --- 5. 크롤링 헬퍼 함수 (기존과 동일) ---
# (get_domain_from_url, find_publisher_name, find_publish_date)
# ... (생략 - 님의 기존 코드 그대로 사용) ...
def get_domain_from_url(url):
    try:
        netloc = urlparse(url).netloc
        if netloc.startswith('www.'):
            netloc = netloc.replace('www.', '', 1)
        return netloc
    except Exception:
        return None

def find_publisher_name(soup, domain):
    try:
        if domain == "n.news.naver.com":
            logo_tag = soup.select_one('a.media_end_head_top_logo img')
            if logo_tag and logo_tag.get('alt'):
                return logo_tag['alt'].strip()
        if domain.endswith("daum.net"):
            logo_tag = soup.select_one('div.info_cp a.link_cp img')
            if logo_tag and logo_tag.get('alt'):
                return logo_tag['alt'].strip()
        og_name = soup.find('meta', {'property': 'og:site_name'})
        if og_name and og_name.get('content'):
            return og_name['content'].strip()
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if not script.string: continue
            data = json.loads(script.string)
            if data.get('publisher') and data['publisher'].get('name'):
                return data['publisher']['name'].strip()
    except Exception as e:
        print(f"출처 이름 파싱 중 오류: {e}")
    return domain

def find_publish_date(soup, url):
    # (네이버/다음용 날짜 선택자 추가)
    try:
        # 네이버
        date_tag = soup.select_one('span.media_end_head_info_datestamp_time')
        if date_tag:
            return date_parser.parse(date_tag['data-date-time']).isoformat()
        # 다음
        date_tag = soup.select_one('span.num_date')
        if date_tag:
            return date_parser.parse(date_tag.get_text()).isoformat()
    except Exception:
        pass
    
    # (이하 님의 기존 범용 날짜 찾기 로직)
    try:
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        # ... (이하 생략) ...
    except Exception: pass
    return "날짜 찾기 실패"


# --- 6. (FINAL) Django 뷰 클래스 ---
@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        # 1. URL 추출 (기존과 동일)
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
            if not url_to_check:
                return JsonResponse({"error": "URL이 누락되었습니다."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

        parsed_url = urlparse(url_to_check)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return JsonResponse({"error": "유효하지 않은 URL 형식입니다. (Scheme/Domain 누락)"}, status=400)
        
        # 2-2. 도메인 추출 및 허용 도메인 검증
        domain = get_domain_from_url(url_to_check)
        
        # --- (!!! TRUSTED_DOMAINS로 변경된 부분 !!!) ---
        if domain not in TRUSTED_DOMAINS: 
            return JsonResponse({
                "error": f"허용되지 않은 도메인입니다: {domain}",
                "allowed_domains": TRUSTED_DOMAINS # (선택 사항: 디버깅용으로 제거 가능)
            }, status=400)
        # 3. (!!! NEW !!!) Playwright로 웹 크롤링 및 파싱
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # 님의 User-Agent를 유지합니다
                page = browser.new_page(user_agent='Mozilla/5.0 ... (기존 User-Agent)')
                
                # --- (!!!) 여기가 수정되었습니다 (!!!) ---
                page.goto(
                    url_to_check, 
                    # 1. 기준 변경: 'load' -> 'domcontentloaded' (HTML 본문만 로드되면 OK)
                    wait_until='domcontentloaded', 
                    # 2. 시간 연장: 15000ms -> 30000ms (30초)
                    timeout=30000 
                )
                # ----------------------------------------
                
                html_content = page.content()
                browser.close()

            # (3) Playwright가 가져온 HTML을 BeautifulSoup에게 전달
            soup = BeautifulSoup(html_content, 'html.parser')

            # --- 4. (최종) 모든 정보 추출 (이하 동일) ---
            publisher_name = find_publisher_name(soup, domain)
            publish_date = find_publish_date(soup, url_to_check)
            title, text_content = find_article_content(soup)
            
            if not title or not text_content:
                ai_result = {"error": "기사 제목 또는 본문을 크롤링하지 못했습니다."}
            else:
                ai_result = get_fake_news_prediction(title, text_content)

            trust_result = get_media_trust_score(publisher_name)

            # 5. 프론트엔드로 보낼 최종 결과
            result = {
                "requested_url": url_to_check,
                "publisher_name": publisher_name,
                "published_date": publish_date,
                "scraped_title": title,
                "ai_prediction": ai_result,
                "media_trust": trust_result
            }
            return JsonResponse(result, status=200)

        except Exception as e:
            # Playwright가 타임아웃되거나, 크롤링이 차단될 수 있음
            print(f"Playwright/크롤링 오류: {e}") 
            return JsonResponse({"error": f"크롤링 중 오류 발생: {e}"}, status=500)