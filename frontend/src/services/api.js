// src/services/api.js

// 백엔드 API 주소
// 환경 변수에서 가져오거나 기본값 사용
// ngrok 주소: https://noncrucial-filomena-undeliberately.ngrok-free.dev/api/analyze/
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://134.185.99.4'

/**
 * 신뢰도 점수 계산
 * 백엔드 응답 데이터를 기반으로 신뢰도 점수 계산
 * 
 * @param {Object} backendData - 백엔드 응답 데이터
 * @returns {number} 신뢰도 점수 (0-100)
 */
function calculateReliabilityScore(backendData) {
  // AI 예측 결과가 있으면 사용
  if (backendData.ai_prediction) {
    // ai_prediction이 객체인 경우
    let fakeProbability = 0
    
    if (typeof backendData.ai_prediction === 'object') {
      fakeProbability = backendData.ai_prediction.fake_probability || 
                       backendData.ai_prediction.prediction || 
                       0
    } else if (typeof backendData.ai_prediction === 'number') {
      // 숫자로 직접 전달된 경우 (0: 진짜, 1: 가짜)
      fakeProbability = backendData.ai_prediction
    }
    
    // 가짜 확률을 신뢰도 점수로 변환 (0-100)
    // fake_probability가 0.2면 신뢰도 80점
    return Math.round((1 - fakeProbability) * 100)
  }
  
  // 기본값: 50점
  return 50
}

/**
 * 가짜뉴스 여부 판단
 * 
 * @param {Object} backendData - 백엔드 응답 데이터
 * @returns {boolean} 가짜뉴스면 true
 */
function determineIsFake(backendData) {
  if (backendData.ai_prediction) {
    let fakeProbability = 0
    
    if (typeof backendData.ai_prediction === 'object') {
      fakeProbability = backendData.ai_prediction.fake_probability || 
                         backendData.ai_prediction.prediction || 
                         0
    } else if (typeof backendData.ai_prediction === 'number') {
      fakeProbability = backendData.ai_prediction
    }
    
    // 0.5 이상이면 가짜뉴스로 판단
    return fakeProbability >= 0.5
  }
  
  return false
}

/**
 * 뉴스 URL을 분석하는 함수
 * 캐싱 기능 포함: 같은 URL 재요청 시 캐시된 결과 반환 (해시 테이블 사용)
 * 
 * @param {string} url - 분석할 뉴스 URL
 * @param {boolean} useCache - 캐시 사용 여부 (기본값: true)
 * @returns {Promise<Object>} 분석 결과
 */
export const analyzeNews = async (url, useCache = true) => {
  try {
    // 캐싱: 해시 테이블을 사용하여 같은 URL 재요청 방지
    // 시간 복잡도: O(1) - 해시 테이블 조회
    if (useCache) {
      const { historyService } = await import('./historyService.js')
      const cachedRecord = historyService.getRecordByURL(url)
      
      if (cachedRecord && cachedRecord.data) {
        console.log('캐시된 결과 사용 (API 호출 생략):', url)
        // 캐시된 결과를 프론트엔드 형식으로 반환
        return {
          success: true,
          data: cachedRecord.data
        }
      }
    }
    
    console.log('API 호출 시작:', url)
    
    // 백엔드에 POST 요청 보내기
    const endpoint = '/api/analyze'
    const fullUrl = `${API_BASE_URL}${endpoint}`
    
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'ngrok-skip-browser-warning': 'true',
      },
      body: JSON.stringify({ url }),
    })

    // HTTP 상태 코드 확인
    if (!response.ok) {
      // 400 오류 등 에러 응답의 상세 정보 확인
      let errorData = {}
      try {
        const responseText = await response.text()
        console.error('백엔드 에러 응답 (원본):', responseText)
        errorData = JSON.parse(responseText)
        console.error('백엔드 에러 응답 (파싱됨):', errorData)
      } catch (parseError) {
        console.error('에러 응답 파싱 실패:', parseError)
      }
      
      // 에러 메시지 추출 (다양한 형식 지원)
      const errorMessage = 
        errorData.error?.message || 
        errorData.message || 
        errorData.detail || 
        errorData.error || 
        `HTTP 오류: ${response.status}`
      
      throw new Error(errorMessage)
    }

    // JSON 응답을 JavaScript 객체로 파싱
    const data = await response.json()
    
    // 응답 데이터 로그 출력 (디버깅용)
    console.log('백엔드 응답:', data)
    
    // 백엔드 응답 형식 확인
    // 형식 1: { success: true, data: {...} } 형태
    if (data.success !== undefined) {
      if (!data.success) {
        // 에러 메시지가 있으면 상세 정보 출력
        console.error('백엔드 에러 상세:', data.error)
        throw new Error(data.error?.message || '분석에 실패했습니다.')
      }
      // success가 true면 data 필드 반환
      console.log('API 응답 성공:', data)
      return data
    }
    
    // 형식 2: 직접 데이터 반환 (success 필드 없음)
    // 백엔드가 직접 데이터를 반환하는 경우
    if (data.requested_url || data.publisher_name || data.ai_prediction) {
      // 백엔드 응답을 프론트엔드 형식으로 변환
      const formattedData = {
        success: true,
        data: {
          reliability_score: calculateReliabilityScore(data),
          is_fake: determineIsFake(data),
          metadata: {
            publisher: data.publisher_name || '정보 없음',
            publish_date: data.published_date || null,
            article_title: data.scraped_title || '정보 없음',
            article_content: data.scraped_content || ''
          },
          analysis_details: {
            ai_prediction: data.ai_prediction || null
          }
        }
      }
      console.log('API 응답 성공 (변환됨):', formattedData)
      return formattedData
    }
    
    // 알 수 없는 응답 형식
    console.error('알 수 없는 응답 형식:', data)
    throw new Error('알 수 없는 응답 형식입니다.')
  } catch (error) {
    console.error('API 호출 오류:', error)
    throw error
  }
}

