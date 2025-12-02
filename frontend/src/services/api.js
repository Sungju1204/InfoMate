// src/services/api.js

// 백엔드 API 주소
// 환경 변수에서 가져오거나 기본값 사용
// 로컬 개발: http://localhost:8000/api/analyze
// ngrok 주소: https://noncrucial-filomena-undeliberately.ngrok-free.dev/api/analyze/
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/analyze'

// 모킹 모드 활성화 (백엔드 연결 없이 프론트엔드 개발용)
// true로 설정하면 실제 API 호출 대신 모킹 데이터를 반환합니다
// 환경 변수 VITE_USE_MOCK_DATA가 'true'일 때만 모킹 모드 활성화
// ⚠️ 실제 백엔드 연결을 위해 false로 설정됨
const USE_MOCK_DATA = false // 실제 백엔드 데이터 사용

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
      // 백엔드 형식: { "prediction": "Fake", "fake_percentage": 75.5, "true_percentage": 24.5 }
      if (backendData.ai_prediction.fake_percentage !== undefined) {
        // fake_percentage를 0-1 범위로 변환 (예: 75.5 -> 0.755)
        fakeProbability = backendData.ai_prediction.fake_percentage / 100
      } else {
        // 다른 형식 지원
        fakeProbability = backendData.ai_prediction.fake_probability || 
                         backendData.ai_prediction.prediction || 
                         0
      }
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
      // 백엔드 형식: { "prediction": "Fake", "fake_percentage": 75.5, "true_percentage": 24.5 }
      if (backendData.ai_prediction.fake_percentage !== undefined) {
        // fake_percentage를 0-1 범위로 변환
        fakeProbability = backendData.ai_prediction.fake_percentage / 100
      } else if (backendData.ai_prediction.prediction === 'Fake') {
        // prediction이 "Fake" 문자열인 경우
        return true
      } else {
        // 다른 형식 지원
        fakeProbability = backendData.ai_prediction.fake_probability || 0
      }
    } else if (typeof backendData.ai_prediction === 'number') {
      fakeProbability = backendData.ai_prediction
    }
    
    // 0.5 이상이면 가짜뉴스로 판단
    return fakeProbability >= 0.5
  }
  
  return false
}

/**
 * 모킹 데이터 생성 함수
 * 백엔드 연결 없이 개발할 때 사용하는 샘플 데이터
 */
function generateMockData(url) {
  // URL에 따라 다른 결과 반환 (테스트용)
  const isFakeNews = url.includes('fake') || url.includes('test')
  const fakePercentage = isFakeNews ? Math.random() * 30 + 60 : Math.random() * 30 + 10 // 60-90 또는 10-40
  const truePercentage = 100 - fakePercentage
  
  return {
    success: true,
    data: {
      reliability_score: Math.round(truePercentage),
      is_fake: isFakeNews,
      metadata: {
        publisher: extractDomainFromUrl(url) || '조선일보',
        publish_date: new Date().toISOString().split('T')[0],
        article_title: '샘플 뉴스 기사 제목입니다',
        article_content: '이것은 모킹 데이터입니다. 백엔드 연결 없이 프론트엔드 개발을 위해 사용됩니다.'
      },
      analysis_details: {
        ai_prediction: {
          prediction: isFakeNews ? 'Fake' : 'True',
          fake_percentage: Math.round(fakePercentage * 10) / 10,
          true_percentage: Math.round(truePercentage * 10) / 10
        },
        media_trust: {
          trust_score: Math.round(truePercentage),
          reliability: isFakeNews ? 'Low' : 'High'
        },
        // GPT 의견 및 점수
        gpt_opinion: isFakeNews 
          ? '이 뉴스는 가짜뉴스일 가능성이 높습니다. 주의가 필요합니다.' 
          : '이 뉴스는 신뢰할 수 있는 정보입니다.',
        gpt_score: Math.round(truePercentage),
        // 지도학습AI 모델 점수
        ai_model_score: Math.round(truePercentage),
        // 발행일 점수 (최근일수록 높음)
        publish_date_score: 85,
        // 자극적인 단어
        sensational_words: isFakeNews ? ['충격', '폭로', '발각'] : [],
        sensational_words_score: isFakeNews ? 30 : 85,
        // 광고성/상업성
        advertisement: !isFakeNews ? false : { level: 'medium' },
        advertisement_score: isFakeNews ? 45 : 85,
        // 크로스 체크 정보
        cross_check: {
          verified_sources: isFakeNews ? 1 : 4,
          status: isFakeNews ? 'unverified' : 'verified'
        },
        cross_check_score: isFakeNews ? 35 : 85
      }
    }
  }
}

/**
 * URL에서 도메인 추출
 */
function extractDomainFromUrl(url) {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace('www.', '')
  } catch {
    return null
  }
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
    // 모킹 모드: 실제 API 호출 없이 모킹 데이터 반환
    if (USE_MOCK_DATA) {
      console.log('🔧 모킹 모드: 실제 API 호출 없이 모킹 데이터 반환')
      console.log('📝 요청 URL:', url)
      
      // 약간의 지연 시뮬레이션 (실제 API 호출 느낌)
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockData = generateMockData(url)
      console.log('✅ 모킹 데이터 반환:', mockData)
      return mockData
    }
    
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
    console.log('API_BASE_URL:', API_BASE_URL)
    
    // 백엔드에 POST 요청 보내기
    // API_BASE_URL이 이미 /api/analyze로 끝나므로, 끝에 슬래시 추가
    const apiUrl = API_BASE_URL.endsWith('/') ? API_BASE_URL : `${API_BASE_URL}/`
    console.log('API 요청 URL:', apiUrl)
    console.log('요청 본문:', JSON.stringify({ url }))
    
    let response
    try {
      response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // ngrok-skip-browser-warning 헤더는 백엔드 CORS 설정 후 사용 가능
          // 'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({ url }),
      })
      console.log('응답 상태:', response.status, response.statusText)
    } catch (fetchError) {
      console.error('Fetch 오류 상세:', fetchError)
      console.error('오류 타입:', fetchError.name)
      console.error('오류 메시지:', fetchError.message)
      throw new Error(`네트워크 오류: ${fetchError.message}. 백엔드 서버가 http://localhost:8000에서 실행 중인지 확인해주세요.`)
    }

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
      
      // 백엔드가 detailed_scores 형식으로 응답하는 경우 프론트엔드 형식으로 변환
      if (data.data && data.data.detailed_scores) {
        const backendData = data.data
        const detailedScores = backendData.detailed_scores
        
        // 프론트엔드 형식으로 변환
        const formattedData = {
          success: true,
          data: {
            reliability_score: backendData.final_analysis?.final_score || 50,
            is_fake: (backendData.final_analysis?.final_score || 50) < 50,
            metadata: {
              publisher: backendData.publisher_name || '정보 없음',
              publish_date: backendData.published_date || null,
              article_title: backendData.scraped_title || '정보 없음',
              article_content: backendData.scraped_content || ''
            },
            analysis_details: {
              // GPT 의견 및 점수
              gpt_opinion: detailedScores.gpt_analysis?.reason || '',
              gpt_score: detailedScores.gpt_analysis?.score || 50,
              
              // AI 모델 예측
              ai_prediction: {
                prediction: detailedScores.ai_model?.prediction === 'Fake' ? 'Fake' : 'True',
                fake_percentage: detailedScores.ai_model?.fake_percentage || 0,
                true_percentage: detailedScores.ai_model?.true_percentage || 0
              },
              ai_model_score: detailedScores.ai_model?.score || 50,
              
              // 미디어 신뢰도
              media_trust: {
                trust_score: detailedScores.media_trust?.score || 60,
                reliability: detailedScores.media_trust?.rank ? 'High' : 'Medium',
                rank: detailedScores.media_trust?.rank,
                category: detailedScores.media_trust?.category
              },
              
              // 발행일 점수
              publish_date_score: detailedScores.date_freshness?.score || 70,
              
              // 자극적인 단어
              sensational_words: detailedScores.sensational_check?.detected_words || [],
              sensational_words_score: detailedScores.sensational_check?.score || 100,
              
              // 광고성/상업성
              advertisement: detailedScores.commercial_check?.is_commercial || false,
              advertisement_score: detailedScores.commercial_check?.score || 100,
              
              // 크로스 체크
              cross_check: {
                verified_sources: detailedScores.cross_check?.consistency === '높음' ? 5 : 
                                 detailedScores.cross_check?.consistency === '보통' ? 3 : 1,
                status: detailedScores.cross_check?.consistency === '높음' ? 'verified' : 'unverified'
              },
              cross_check_score: detailedScores.cross_check?.score || 70
            }
          }
        }
        console.log('API 응답 성공 (변환됨 - detailed_scores):', formattedData)
        return formattedData
      }
      
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
          // 백엔드가 analysis_details를 제공하면 그대로 사용
          // 없으면 백엔드 응답의 루트 레벨 필드들을 analysis_details로 병합
          analysis_details: data.analysis_details ? {
            ...data.analysis_details,
            // analysis_details에 없는 필드가 루트 레벨에 있으면 병합
            ai_prediction: data.analysis_details.ai_prediction || data.ai_prediction || null,
            media_trust: data.analysis_details.media_trust || data.media_trust || null,
            gpt_opinion: data.analysis_details.gpt_opinion || data.gpt_opinion || null,
            gpt_score: data.analysis_details.gpt_score !== undefined ? data.analysis_details.gpt_score : (data.gpt_score || null),
            ai_model_score: data.analysis_details.ai_model_score !== undefined ? data.analysis_details.ai_model_score : (data.ai_model_score || null),
            publish_date_score: data.analysis_details.publish_date_score !== undefined ? data.analysis_details.publish_date_score : (data.publish_date_score || null),
            sensational_words: data.analysis_details.sensational_words || data.sensational_words || null,
            sensational_words_score: data.analysis_details.sensational_words_score !== undefined ? data.analysis_details.sensational_words_score : (data.sensational_words_score || null),
            advertisement: data.analysis_details.advertisement || data.advertisement || null,
            advertisement_score: data.analysis_details.advertisement_score !== undefined ? data.analysis_details.advertisement_score : (data.advertisement_score || null),
            cross_check: data.analysis_details.cross_check || data.cross_check || null,
            cross_check_score: data.analysis_details.cross_check_score !== undefined ? data.analysis_details.cross_check_score : (data.cross_check_score || null)
          } : {
            // analysis_details가 없으면 루트 레벨 필드들을 사용
            ai_prediction: data.ai_prediction || null,
            media_trust: data.media_trust || null,
            gpt_opinion: data.gpt_opinion || null,
            gpt_score: data.gpt_score || null,
            ai_model_score: data.ai_model_score || null,
            publish_date_score: data.publish_date_score || null,
            sensational_words: data.sensational_words || null,
            sensational_words_score: data.sensational_words_score || null,
            advertisement: data.advertisement || null,
            advertisement_score: data.advertisement_score || null,
            cross_check: data.cross_check || null,
            cross_check_score: data.cross_check_score || null
          }
        }
      }
      console.log('API 응답 성공 (변환됨):', formattedData)
      return formattedData
    }
    
    // 형식 3: 백엔드가 { success: true, data: {...} } 형식으로 응답하는 경우
    // 백엔드의 data 필드 안에 실제 데이터가 있음
    if (data.data && (data.data.requested_url || data.data.publisher_name || data.data.ai_prediction)) {
      const backendData = data.data
      const formattedData = {
        success: true,
        data: {
          reliability_score: calculateReliabilityScore(backendData),
          is_fake: determineIsFake(backendData),
          metadata: {
            publisher: backendData.publisher_name || '정보 없음',
            publish_date: backendData.published_date || null,
            article_title: backendData.scraped_title || '정보 없음',
            article_content: backendData.scraped_content || ''
          },
          // 백엔드가 analysis_details를 제공하면 그대로 사용
          // 없으면 백엔드 응답의 루트 레벨 필드들을 analysis_details로 병합
          analysis_details: backendData.analysis_details ? {
            ...backendData.analysis_details,
            // analysis_details에 없는 필드가 루트 레벨에 있으면 병합
            ai_prediction: backendData.analysis_details.ai_prediction || backendData.ai_prediction || null,
            media_trust: backendData.analysis_details.media_trust || backendData.media_trust || null,
            gpt_opinion: backendData.analysis_details.gpt_opinion || backendData.gpt_opinion || null,
            gpt_score: backendData.analysis_details.gpt_score !== undefined ? backendData.analysis_details.gpt_score : (backendData.gpt_score || null),
            ai_model_score: backendData.analysis_details.ai_model_score !== undefined ? backendData.analysis_details.ai_model_score : (backendData.ai_model_score || null),
            publish_date_score: backendData.analysis_details.publish_date_score !== undefined ? backendData.analysis_details.publish_date_score : (backendData.publish_date_score || null),
            sensational_words: backendData.analysis_details.sensational_words || backendData.sensational_words || null,
            sensational_words_score: backendData.analysis_details.sensational_words_score !== undefined ? backendData.analysis_details.sensational_words_score : (backendData.sensational_words_score || null),
            advertisement: backendData.analysis_details.advertisement || backendData.advertisement || null,
            advertisement_score: backendData.analysis_details.advertisement_score !== undefined ? backendData.analysis_details.advertisement_score : (backendData.advertisement_score || null),
            cross_check: backendData.analysis_details.cross_check || backendData.cross_check || null,
            cross_check_score: backendData.analysis_details.cross_check_score !== undefined ? backendData.analysis_details.cross_check_score : (backendData.cross_check_score || null)
          } : {
            // analysis_details가 없으면 루트 레벨 필드들을 사용
            ai_prediction: backendData.ai_prediction || null,
            media_trust: backendData.media_trust || null,
            gpt_opinion: backendData.gpt_opinion || null,
            gpt_score: backendData.gpt_score || null,
            ai_model_score: backendData.ai_model_score || null,
            publish_date_score: backendData.publish_date_score || null,
            sensational_words: backendData.sensational_words || null,
            sensational_words_score: backendData.sensational_words_score || null,
            advertisement: backendData.advertisement || null,
            advertisement_score: backendData.advertisement_score || null,
            cross_check: backendData.cross_check || null,
            cross_check_score: backendData.cross_check_score || null
          }
        }
      }
      console.log('API 응답 성공 (data 필드에서 변환됨):', formattedData)
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

