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
        return {"error": "API 키 설정 오류", "prediction": "Error", "score": 0}
        
    try:
        truncated_text = text[:3000]
        
        system_prompt = """
        당신은 뉴스 기사의 신뢰도를 평가하는 '팩트체크 AI'입니다.
        제공된 기사를 분석하여 JSON 형식으로 답하세요.
        
        [응답 형식]
        {
            "prediction": "True" 또는 "Fake",
            "score": 0~100 (높을수록 진실, 정확한 숫자로),
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
        
        # score가 없거나 잘못된 경우 기본값 설정
        if "score" not in result or not isinstance(result["score"], (int, float)):
            result["score"] = 50
            
        return result
        
    except Exception as e:
        print(f"GPT Error: {e}")
        return {"error": str(e), "prediction": "Error", "score": 0}


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
    """Playwright를 사용하여 구글 뉴스 탭 검색 결과를 가져옵니다."""
    if not keyword:
        return []

    articles = []
    browser = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()
            
            url = f"https://www.google.com/search?q={keyword}&tbm=nws&hl=ko&gl=KR"
            page.goto(url, wait_until='domcontentloaded', timeout=10000)
            page.wait_for_timeout(3000) 

            news_elements = page.query_selector_all('div.SoaBEf, div.MjjYud')

            count = 0
            for item in news_elements:
                if count >= 5: break
                
                try:
                    link_tag = item.query_selector('a')
                    if not link_tag: continue
                    
                    link = link_tag.get_attribute('href')
                    if not link.startswith('http'): continue

                    title_div = item.query_selector('div[role="heading"]')
                    title = title_div.inner_text() if title_div else link_tag.inner_text()
                    
                    if not title: continue

                    press_div = item.query_selector('.MgUUmf span')
                    press = press_div.inner_text() if press_div else "Google News"

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


# --- 2. 언론사 신뢰도 DB (확장 버전) ---
MEDIA_TRUST_DB = {
    "KBS": {"rank": 1, "score": 95, "category": "공영방송"},
    "MBC": {"rank": 2, "score": 92, "category": "공영방송"},
    "SBS": {"rank": 3, "score": 88, "category": "지상파"},
    "YTN": {"rank": 4, "score": 85, "category": "뉴스전문"},
    "JTBC": {"rank": 5, "score": 82, "category": "종편"},
    "연합뉴스": {"rank": 6, "score": 90, "category": "통신사"},
    "뉴스1": {"rank": 7, "score": 80, "category": "통신사"},
    "조선일보": {"rank": 8, "score": 75, "category": "종합일간지"},
    "중앙일보": {"rank": 9, "score": 75, "category": "종합일간지"},
    "동아일보": {"rank": 10, "score": 75, "category": "종합일간지"},
    "한겨레": {"rank": 11, "score": 75, "category": "종합일간지"},
    "경향신문": {"rank": 12, "score": 75, "category": "종합일간지"},
    "한국경제": {"rank": 13, "score": 70, "category": "경제지"},
    "매일경제": {"rank": 14, "score": 70, "category": "경제지"},
}

def get_media_trust_score(publisher_name):
    """언론사 신뢰도 점수 (0~100)"""
    for key, value in MEDIA_TRUST_DB.items():
        if key in publisher_name:
            return {
                "rank": value["rank"],
                "score": value["score"],
                "category": value["category"]
            }
    # 순위권 외 언론사는 중간 점수
    return {"rank": None, "score": 60, "category": "순위권 외"}


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
    """로컬 AI 모델 예측 (0~100 점수로 변환)"""
    if not tokenizer or not model: 
        return {
            "error": "AI 모델 로딩 실패",
            "score": 50,  # 기본값
            "prediction": "Unknown"
        }
    
    input_text = f"{title} [SEP] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    
    with torch.no_grad(): 
        outputs = model(**inputs)
    
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    prob_true = probs[0][0].item()
    prob_fake = probs[0][1].item()
    
    # True 확률을 점수로 변환 (높을수록 진실)
    score = round(prob_true * 100, 2)
    
    return {
        "prediction": "Fake" if prob_fake > prob_true else "True",
        "score": score,  # 진실 점수
        "fake_percentage": round(prob_fake * 100, 2),
        "true_percentage": round(prob_true * 100, 2)
    }


# --- 5. 자극적인 단어 체크 (신규 구현) ---
def check_sensational_words(title, text):
    """
    클릭베이트/자극적 표현 탐지
    Returns: {"score": 0~100, "detected_words": [...], "count": N}
    """
    clickbait_keywords = [
        '충격', '경악', '발칵', '긴급', '속보', '대박', '실화',
        '폭로', '논란', '역대급', '초유', '사상최대', '최악',
        '반전', '결국', '드디어', '불법', '파문', '진실',
        '헐', '미쳤', '실제상황', '끝판왕', '레전드'
    ]
    
    detected = []
    full_text = title + " " + text[:500]  # 제목+본문 앞부분만
    
    for word in clickbait_keywords:
        if word in full_text:
            detected.append(word)
    
    count = len(detected)
    
    # 패널티: 1개당 -10점 (최대 -50점)
    penalty = min(count * 10, 50)
    score = max(100 - penalty, 50)
    
    return {
        "score": score,
        "detected_words": detected,
        "count": count,
        "description": f"자극적 표현 {count}개 감지" if count > 0 else "정상"
    }


# --- 6. 광고성/상업성 체크 (신규 구현) ---
def check_commercial_content(text, url):
    """
    광고/홍보성 콘텐츠 탐지
    Returns: {"score": 0~100, "detected_patterns": [...], "is_commercial": bool}
    """
    commercial_patterns = [
        r'구매하[기는]', r'할인', r'이벤트', r'쿠폰', r'\bAD\b',
        r'협찬', r'제공:', r'바로가기', r'클릭', r'지금\s?바로',
        r'무료\s?체험', r'가입', r'회원', r'포인트', r'혜택',
        r'http[s]?://bit\.ly', r'http[s]?://smartstore', r'coupang\.com'
    ]
    
    detected = []
    for pattern in commercial_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(pattern)
    
    # URL에 쇼핑몰/광고 도메인 포함 여부
    ad_domains = ['smartstore', 'coupang', 'gmarket', '11st', 'auction']
    url_commercial = any(domain in url.lower() for domain in ad_domains)
    
    is_commercial = len(detected) >= 3 or url_commercial
    
    # 광고성이면 -40점, 약간 의심되면 -20점
    if is_commercial:
        score = 60
    elif len(detected) > 0:
        score = 80
    else:
        score = 100
    
    return {
        "score": score,
        "detected_patterns": detected,
        "is_commercial": is_commercial,
        "description": "광고성 콘텐츠" if is_commercial else "정상"
    }


# --- 7. 크로스체크 (관련 기사와 사실 대조) ---
def cross_check_with_related_articles(title, text, related_articles):
    """
    관련 기사와 내용 일치도를 GPT로 검증
    Returns: {"score": 0~100, "consistency": "높음/보통/낮음", "reason": "..."}
    """
    if not client or not related_articles:
        return {
            "score": 70,  # 기본값 (검증 불가)
            "consistency": "검증불가",
            "reason": "관련 기사가 없거나 API 오류"
        }
    
    try:
        # 관련 기사 제목들 요약
        related_titles = "\n".join([f"- {art['title']}" for art in related_articles[:5]])
        
        prompt = f"""
당신은 팩트체크 전문가입니다. 
원본 기사와 관련 기사들의 내용 일치도를 평가하세요.

[원본 기사]
제목: {title}
본문: {text[:1000]}

[관련 기사 제목들]
{related_titles}

위 정보를 바탕으로 JSON 형식으로 답변:
{{
    "consistency_score": 0~100 (관련 기사들과 내용이 일치할수록 높음),
    "consistency_level": "높음" 또는 "보통" 또는 "낮음",
    "reason": "판단 근거 1문장"
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return {
            "score": result.get("consistency_score", 70),
            "consistency": result.get("consistency_level", "보통"),
            "reason": result.get("reason", "검증 완료")
        }
        
    except Exception as e:
        print(f"크로스체크 오류: {e}")
        return {
            "score": 70,
            "consistency": "검증실패",
            "reason": f"오류 발생: {str(e)}"
        }


# --- 8. 발행일 신선도 점수 (신규) ---
def calculate_date_freshness(publish_date):
    """
    발행일 신선도 점수 (최신일수록 높음)
    Returns: {"score": 0~100, "days_ago": N, "freshness": "신선/보통/오래됨"}
    """
    try:
        if not publish_date or publish_date == "날짜 찾기 실패":
            return {"score": 70, "days_ago": None, "freshness": "불명"}
        
        from datetime import datetime, timezone
        
        # 발행일 파싱
        if isinstance(publish_date, str):
            pub_dt = date_parser.parse(publish_date)
        else:
            pub_dt = publish_date
        
        # 현재 시각
        now = datetime.now(timezone.utc)
        
        # 날짜 차이 계산
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        
        days_ago = (now - pub_dt).days
        
        # 점수 계산
        if days_ago < 0:  # 미래 날짜 (의심)
            score = 50
            freshness = "의심"
        elif days_ago <= 7:
            score = 100
            freshness = "신선"
        elif days_ago <= 30:
            score = 90
            freshness = "최근"
        elif days_ago <= 90:
            score = 80
            freshness = "보통"
        elif days_ago <= 365:
            score = 70
            freshness = "오래됨"
        else:
            score = 60
            freshness = "매우 오래됨"
        
        return {
            "score": score,
            "days_ago": days_ago,
            "freshness": freshness
        }
        
    except Exception as e:
        print(f"날짜 분석 오류: {e}")
        return {"score": 70, "days_ago": None, "freshness": "오류"}


# --- 9. 도메인/출처 처리 ---
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
        tag = soup.find('meta', attrs={'property': attr}) or \
              soup.find('meta', attrs={'name': attr})
            
        if tag and tag.get('content'):
            try: return date_parser.parse(tag['content']).isoformat()
            except: continue
            
    url_date = extract_date_from_url(url)
    if url_date: return url_date
    return "날짜 찾기 실패"


# --- 10. 최종 점수 계산 함수 ---
def calculate_final_score(scores_dict):
    """
    각 지표별 점수를 가중 평균하여 최종 점수 산출
    
    가중치:
    - GPT 분석: 25%
    - AI 모델: 20%
    - 언론사 신뢰도: 15%
    - 크로스체크: 15%
    - 자극적 표현: 10%
    - 광고성: 10%
    - 발행일 신선도: 5%
    """
    weights = {
        "gpt_score": 0.25,
        "ai_model_score": 0.20,
        "media_trust_score": 0.15,
        "cross_check_score": 0.15,
        "sensational_score": 0.10,
        "commercial_score": 0.10,
        "date_freshness_score": 0.05
    }
    
    # 가중 합계
    final = 0
    for key, weight in weights.items():
        final += scores_dict.get(key, 50) * weight
    
    # 최종 등급
    if final >= 80:
        grade = "A"
        reliability = "신뢰도 높음"
    elif final >= 60:
        grade = "B"
        reliability = "보통"
    elif final >= 40:
        grade = "C"
        reliability = "주의 필요"
    else:
        grade = "D"
        reliability = "신뢰도 낮음"
    
    return {
        "final_score": round(final, 2),
        "grade": grade,
        "reliability": reliability,
        "weights": weights
    }


# --- 11. Django View ---
@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeView(APIView):
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        # 1. URL 및 데이터 준비
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
        except: 
            return JsonResponse({"success": False, "error": {"message": "잘못된 요청"}}, status=400)

        domain = get_domain_from_url(url_to_check)
        
        # 2. 크롤링 (Playwright)
        html = None
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                page.goto(url_to_check, wait_until='domcontentloaded', timeout=90000)  
                html = page.content()
        except Exception as e:
            return JsonResponse({"success": False, "error": {"message": f"크롤링 오류: {e}"}}, status=500)
        finally:
            if browser: 
                try: browser.close() 
                except: pass
        
        if not html: 
            return JsonResponse({"success": False, "error": {"message": "HTML 추출 실패"}}, status=500)

        # 3. 데이터 추출
        soup = BeautifulSoup(html, "html.parser")
        publisher_name = find_publisher_name(soup, domain)
        publish_date = find_publish_date(soup, url_to_check)
        title, text_content = find_article_content(soup)

        if not title or len(text_content) < 50:
            return JsonResponse({"success": False, "error": {"message": "본문 추출 실패"}}, status=400)

        # 4. 모든 지표 분석 실행
        print("📊 분석 시작...")
        
        # 4-1. GPT 분석
        gpt_result = get_gpt_prediction(title, text_content)
        gpt_score = gpt_result.get("score", 50)
        
        # 4-2. AI 모델 분석
        ai_result = get_fake_news_prediction(title, text_content)
        ai_score = ai_result.get("score", 50)
        
        # 4-3. 언론사 신뢰도
        media_trust = get_media_trust_score(publisher_name)
        media_score = media_trust.get("score", 60)
        
        # 4-4. 자극적 표현
        sensational = check_sensational_words(title, text_content)
        sensational_score = sensational.get("score", 100)
        
        # 4-5. 광고성
        commercial = check_commercial_content(text_content, url_to_check)
        commercial_score = commercial.get("score", 100)
        
        # 4-6. 발행일 신선도
        date_freshness = calculate_date_freshness(publish_date)
        date_score = date_freshness.get("score", 70)
        
        # 4-7. 관련 기사 검색 및 크로스체크
        related_articles = []
        cross_check_result = {"score": 70, "consistency": "검증불가"}
        
        keywords = gpt_result.get("keywords", "")
        if keywords:
            print(f"🔎 검색 키워드: {keywords}")
            naver_raw = get_related_articles(keywords)
            google_raw = get_google_news(keywords)
            all_articles = naver_raw + google_raw
            
            # 중복 제거
            current_title_norm = normalize_text(title)
            filtered_list = []
            
            for item in all_articles:
                item_title_norm = normalize_text(item['title'])
                if len(item_title_norm) < 2: continue
                if current_title_norm in item_title_norm or item_title_norm in current_title_norm:
                    continue
                filtered_list.append(item)
            
            related_articles = filtered_list[:5]
            
            # 크로스체크 실행
            if related_articles:
                cross_check_result = cross_check_with_related_articles(title, text_content, related_articles)
        
        cross_check_score = cross_check_result.get("score", 70)
        
        # 5. 최종 점수 계산
        scores_dict = {
            "gpt_score": gpt_score,
            "ai_model_score": ai_score,
            "media_trust_score": media_score,
            "cross_check_score": cross_check_score,
            "sensational_score": sensational_score,
            "commercial_score": commercial_score,
            "date_freshness_score": date_score
        }
        
        final_result = calculate_final_score(scores_dict)
        
        print(f"✅ 분석 완료 - 최종 점수: {final_result['final_score']}")
        
        # 6. 응답 반환
        return JsonResponse({
            "success": True,
            "data": {
                "requested_url": url_to_check,
                "publisher_name": publisher_name,
                "published_date": publish_date,
                "scraped_title": title,
                
                # 개별 지표 점수들
                "detailed_scores": {
                    "gpt_analysis": {
                        "score": gpt_score,
                        "prediction": gpt_result.get("prediction", "Unknown"),
                        "reason": gpt_result.get("reason", ""),
                        "model_type": gpt_result.get("model_type", "GPT-4o-mini")
                    },
                    "ai_model": {
                        "score": ai_score,
                        "prediction": ai_result.get("prediction", "Unknown"),
                        "fake_percentage": ai_result.get("fake_percentage", 0),
                        "true_percentage": ai_result.get("true_percentage", 0)
                    },
                    "media_trust": {
                        "score": media_score,
                        "rank": media_trust.get("rank"),
                        "category": media_trust.get("category", "순위권 외")
                    },
                    "sensational_check": {
                        "score": sensational_score,
                        "detected_words": sensational.get("detected_words", []),
                        "count": sensational.get("count", 0),
                        "description": sensational.get("description", "정상")
                    },
                    "commercial_check": {
                        "score": commercial_score,
                        "is_commercial": commercial.get("is_commercial", False),
                        "detected_patterns": commercial.get("detected_patterns", []),
                        "description": commercial.get("description", "정상")
                    },
                    "date_freshness": {
                        "score": date_score,
                        "days_ago": date_freshness.get("days_ago"),
                        "freshness": date_freshness.get("freshness", "불명")
                    },
                    "cross_check": {
                        "score": cross_check_score,
                        "consistency": cross_check_result.get("consistency", "검증불가"),
                        "reason": cross_check_result.get("reason", "")
                    }
                },
                
                # 최종 종합 점수
                "final_analysis": {
                    "final_score": final_result["final_score"],
                    "grade": final_result["grade"],
                    "reliability": final_result["reliability"],
                    "weights_used": final_result["weights"]
                },
                
                # 관련 기사
                "related_articles": related_articles,
                "search_keywords": keywords,
                
                "cached": False
            }
        }, status=200)