/**
 * URL 파싱 및 검증 유틸리티 모듈
 * 문자열 알고리즘을 사용한 URL 처리
 */

/**
 * URL 파싱 (URL Parsing)
 * URL 문자열을 구성 요소로 분해
 * 
 * @param {string} urlString - 파싱할 URL 문자열
 * @returns {Object} 파싱된 URL 객체
 *   - protocol: 프로토콜 (http, https 등)
 *   - hostname: 호스트명 (도메인)
 *   - port: 포트 번호
 *   - pathname: 경로
 *   - search: 쿼리 문자열
 *   - hash: 해시
 */
export function parseURL(urlString) {
  // URL 객체 초기화
  const url = {
    protocol: '',
    hostname: '',
    port: '',
    pathname: '',
    search: '',
    hash: ''
  }

  // 프로토콜 추출 (예: "http://", "https://")
  const protocolEnd = urlString.indexOf('://')
  if (protocolEnd !== -1) {
    url.protocol = urlString.substring(0, protocolEnd)
    urlString = urlString.substring(protocolEnd + 3) // "://" 제거
  }

  // 해시 추출 (예: "#section")
  const hashIndex = urlString.indexOf('#')
  if (hashIndex !== -1) {
    url.hash = urlString.substring(hashIndex + 1)
    urlString = urlString.substring(0, hashIndex)
  }

  // 쿼리 문자열 추출 (예: "?key=value")
  const searchIndex = urlString.indexOf('?')
  if (searchIndex !== -1) {
    url.search = urlString.substring(searchIndex + 1)
    urlString = urlString.substring(0, searchIndex)
  }

  // 경로 추출
  const pathIndex = urlString.indexOf('/')
  if (pathIndex !== -1) {
    url.pathname = urlString.substring(pathIndex)
    urlString = urlString.substring(0, pathIndex)
  }

  // 호스트명과 포트 추출
  const portIndex = urlString.indexOf(':')
  if (portIndex !== -1) {
    url.hostname = urlString.substring(0, portIndex)
    url.port = urlString.substring(portIndex + 1)
  } else {
    url.hostname = urlString
  }

  return url
}

/**
 * 도메인 추출 (Domain Extraction)
 * URL에서 도메인만 추출
 * 
 * @param {string} urlString - URL 문자열
 * @returns {string} 도메인
 */
export function extractDomain(urlString) {
  const parsed = parseURL(urlString)
  return parsed.hostname
}

/**
 * URL 검증 (URL Validation)
 * URL 형식이 올바른지 검증
 * 
 * @param {string} urlString - 검증할 URL 문자열
 * @returns {boolean} 유효한 URL이면 true
 */
export function validateURL(urlString) {
  // 빈 문자열 체크
  if (!urlString || urlString.trim() === '') {
    return false
  }

  // 기본 URL 패턴 체크
  // 프로토콜이 있어야 함 (http:// 또는 https://)
  const protocolPattern = /^https?:\/\//
  if (!protocolPattern.test(urlString)) {
    return false
  }

  // 도메인 패턴 체크
  // 도메인은 영문자, 숫자, 하이픈, 점으로 구성
  const domainPattern = /^https?:\/\/([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}/
  if (!domainPattern.test(urlString)) {
    return false
  }

  return true
}

/**
 * 뉴스 사이트 도메인 확인
 * 주요 뉴스 사이트의 도메인인지 확인
 * 
 * @param {string} urlString - URL 문자열
 * @returns {boolean} 뉴스 사이트면 true
 */
export function isNewsSite(urlString) {
  const domain = extractDomain(urlString)
  
  // 주요 뉴스 사이트 도메인 목록
  const newsDomains = [
    'news.naver.com',
    'news.daum.net',
    'chosun.com',
    'joongang.co.kr',
    'donga.com',
    'hani.co.kr',
    'khan.co.kr',
    'mk.co.kr',
    'ytn.co.kr',
    'sbs.co.kr',
    'kbs.co.kr',
    'mbc.co.kr'
  ]

  // 도메인이 뉴스 사이트 목록에 있는지 확인
  return newsDomains.some(newsDomain => 
    domain === newsDomain || domain.endsWith('.' + newsDomain)
  )
}

/**
 * URL 정규화 (URL Normalization)
 * URL을 표준 형식으로 변환
 * 
 * @param {string} urlString - 정규화할 URL 문자열
 * @returns {string} 정규화된 URL
 */
export function normalizeURL(urlString) {
  // 앞뒤 공백 제거
  let normalized = urlString.trim()

  // 소문자로 변환 (프로토콜과 도메인 부분)
  const protocolEnd = normalized.indexOf('://')
  if (protocolEnd !== -1) {
    const protocol = normalized.substring(0, protocolEnd).toLowerCase()
    const rest = normalized.substring(protocolEnd + 3)
    const hostEnd = rest.indexOf('/')
    
    if (hostEnd !== -1) {
      const host = rest.substring(0, hostEnd).toLowerCase()
      const path = rest.substring(hostEnd)
      normalized = protocol + '://' + host + path
    } else {
      const host = rest.toLowerCase()
      normalized = protocol + '://' + host
    }
  }

  return normalized
}

