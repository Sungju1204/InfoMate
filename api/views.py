# api/views.py (출처 이름 + 발행일 추출)

import json
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import re

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# --- 1. 도메인 추출 함수 (기존과 동일) ---
def get_domain_from_url(url):
    try:
        netloc = urlparse(url).netloc
        if netloc.startswith('www.'):
            netloc = netloc.replace('www.', '', 1)
        return netloc
    except Exception:
        return None

# --- 2. (NEW) 출처(언론사 이름) 추출 함수 ---
def find_publisher_name(soup, domain):
    """
    (범용) URL이 포털이든 아니든, 실제 '언론사 이름'을 찾습니다.
    """
    try:
        # 1순위: 네이버 뉴스 (n.news.naver.com)
        # 네이버는 'media_end_head_top_logo' 클래스 안의 <img> alt 속성에 이름이 있음
        if domain == "n.news.naver.com":
            logo_tag = soup.select_one('a.media_end_head_top_logo img')
            if logo_tag and logo_tag.get('alt'):
                return logo_tag['alt'].strip()

        # 2순위: 다음 뉴스 (v.daum.net / news.daum.net)
        # 다음은 'info_cp' 클래스 안의 <img> alt
        if domain.endswith("daum.net"):
            logo_tag = soup.select_one('div.info_cp a.link_cp img')
            if logo_tag and logo_tag.get('alt'):
                return logo_tag['alt'].strip()

        # 3순위: (범용) Open Graph (og:site_name) - 조선일보 등 자체 사이트
        # 예: <meta property="og:site_name" content="조선일보">
        og_name = soup.find('meta', {'property': 'og:site_name'})
        if og_name and og_name.get('content'):
            return og_name['content'].strip()

        # 4순위: (범용) JSON-LD (publisher.name)
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if not script.string:
                continue
            data = json.loads(script.string)
            if data.get('publisher') and data['publisher'].get('name'):
                return data['publisher']['name'].strip()
                
    except Exception as e:
        print(f"출처 이름 파싱 중 오류: {e}")
    
    # 정 못찾겠으면, 최소한 도메인이라도 반환
    return domain

# --- 3. (IMPROVED) 범용 날짜 추출 함수 (기존과 동일) ---
def find_publish_date(soup, url):
    """
    (범용) 표준 메타 태그, JSON-LD, URL 등에서 날짜를 찾습니다.
    """
    
    # 1순위: JSON-LD
    try:
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        for script in json_ld_scripts:
            if not script.string:
                continue
            data = json.loads(script.string)
            if data.get('@type') == 'NewsArticle' and data.get('datePublished'):
                return date_parser.parse(data['datePublished']).isoformat()
            if data.get('datePublished'):
                return date_parser.parse(data['datePublished']).isoformat()
    except Exception:
        pass

    # 2순위: Meta 태그 (OpenGraph 등)
    meta_selectors = [
        {'property': 'article:published_time'},
        {'name': 'date'},
        {'name': 'Creation-Date'},
        {'name': 'publish-date'},
    ]
    for selector in meta_selectors:
        meta_tag = soup.find('meta', selector)
        if meta_tag and meta_tag.get('content'):
            try:
                return date_parser.parse(meta_tag['content']).isoformat()
            except Exception:
                continue

    # 3순위: <time> 태그
    time_tag = soup.find('time', datetime=True)
    if time_tag and time_tag['datetime']:
        try:
            return date_parser.parse(time_tag['datetime']).isoformat()
        except Exception:
            pass
            
    # 4순위: 본문 텍스트에서 정규식 (YYYY.MM.DD)
    try:
        date_regex = re.compile(r'\d{4}[.-]\d{1,2}[.-]\d{1,2}')
        body_text = soup.get_text()
        match = date_regex.search(body_text)
        if match:
            return date_parser.parse(match.group(0)).isoformat()
    except Exception:
        pass

    # 5순위: URL 자체에서 정규식 (조선일보 .../2025/11/01/...)
    try:
        url_regex = re.compile(r'/(\d{4})[/-](\d{1,2})[/-](\d{1,2})/')
        url_match = url_regex.search(url)
        if url_match:
            date_str = f"{url_match.group(1)}-{url_match.group(2)}-{url_match.group(3)}"
            return date_parser.parse(date_str).isoformat()
    except Exception:
        pass

    return "날짜 찾기 실패"


# --- 4. (CLEANED) Django 뷰 클래스 ---

@method_decorator(csrf_exempt, name='dispatch')
class AnalyzeView(View):
    
    def post(self, request, *args, **kwargs):
        # 1. URL 추출
        try:
            data = json.loads(request.body)
            url_to_check = data.get('url')
            if not url_to_check:
                return JsonResponse({"error": "URL이 누락되었습니다."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "잘못된 JSON 형식입니다."}, status=400)

        # 2. 도메인 추출
        domain = get_domain_from_url(url_to_check)
        if not domain:
            return JsonResponse({"error": "유효하지 않은 URL입니다."}, status=400)

        # 3. 웹 크롤링 및 파싱
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url_to_check, headers=headers, timeout=10)
            response.raise_for_status() 

            soup = BeautifulSoup(response.text, 'html.parser')

            # --- 4. (개선됨) 출처 이름 + 날짜 추출 ---
            # ⭐️ 기사 제목 로직 완전 삭제 ⭐️
            
            # (NEW) 출처(언론사 이름) 찾기
            publisher_name = find_publisher_name(soup, domain)
            
            # (EXISTING) 날짜 찾기
            publish_date = find_publish_date(soup, url_to_check)
            
            # 5. 프론트엔드로 보낼 결과 조합
            result = {
                "requested_url": url_to_check,
                "domain": domain, # (참고용)
                "publisher_name": publisher_name, # (핵심)
                "published_date": publish_date     # (핵심)
            }
            return JsonResponse(result, status=200)

        except requests.exceptions.HTTPError as e:
            return JsonResponse({"error": f"HTTP 에러: {e.response.status_code}"}, status=500)
        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"URL에 연결할 수 없습니다: {e}"}, status=500)
        except Exception as e:
            print(f"알 수 없는 오류: {e}") 
            return JsonResponse({"error": f"알 수 없는 오류 발생"}, status=500)