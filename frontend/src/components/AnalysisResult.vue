<template>
  <div class="analysis-result">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <div class="logo-icon">✓</div>
          <span class="logo-text">InfoMate</span>
        </div>
        <nav class="nav">
          <a href="#" class="nav-link">서비스 소개</a>
          <router-link to="/history" class="nav-link">평가 기록</router-link>
          <a href="#" class="nav-link">문의/Q&A</a>
        </nav>
      </div>
    </header>

    <!-- 로딩 상태 (스피너 + 프로그레스 바 + 예상 소요 시간) -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <div class="progress-container">
        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
      </div>
      <p>분석 중입니다...</p>
      <p class="estimated-time">예상 소요 시간: 약 {{ estimatedTime }}초</p>
    </div>

    <!-- 에러 상태 (개선됨) -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <div class="error-content">
        <h2>{{ getErrorTitle(error) }}</h2>
        <p class="error-message">{{ getErrorMessage(error) }}</p>
        <p class="error-solution" v-if="getErrorSolution(error)">
          💡 {{ getErrorSolution(error) }}
        </p>
      </div>
      <div class="error-actions">
        <button @click="retryAnalysis" class="retry-btn" :disabled="isLoading">
          🔄 다시 시도
        </button>
        <button @click="$router.push('/')" class="back-btn">
          홈으로 돌아가기
        </button>
      </div>
    </div>

    <!-- 결과 표시 -->
    <div v-else-if="analysisResult" class="content">
      <div class="main-content">
        <!-- 종합 신뢰도 -->
        <section class="reliability-section">
          <h2>종합 신뢰도</h2>
          <div class="reliability-score">
            <div 
              class="score-circle" 
              :style="{ 
                background: `linear-gradient(135deg, ${getScoreColor(analysisResult.reliability_score)}, ${getScoreColor(analysisResult.reliability_score)}dd)` 
              }"
            >
              <span class="score-number">{{ analysisResult.reliability_score }}</span>
              <span class="score-total">/100</span>
            </div>
            <div class="score-description">
              <div 
                class="score-icon" 
                :style="{ background: getScoreColor(analysisResult.reliability_score) }"
              >
                {{ getScoreIcon(analysisResult.is_fake) }}
              </div>
              <p>
                {{ analysisResult.is_fake 
                  ? '이 뉴스는 가짜뉴스일 가능성이 있습니다. 주의가 필요합니다.' 
                  : '이 뉴스는 신뢰될 수 있는 정보입니다. 검증된 플랫폼입니다.' 
                }}
              </p>
            </div>
          </div>
        </section>

        <!-- 상세 분석 내역 -->
        <section class="analysis-details">
          <h2>상세 분석 내역</h2>
          <div class="analysis-cards">
            <div class="analysis-card">
              <div class="card-icon">🏢</div>
              <div class="card-content">
                <h3>출처 신뢰도</h3>
                <p>{{ analysisResult.metadata?.publisher || '정보 없음' }}</p>
              </div>
            </div>
            
            <div class="analysis-card">
              <div class="card-icon">📅</div>
              <div class="card-content">
                <h3>작성일/발행일</h3>
                <p>{{ formatDate(analysisResult.metadata?.publish_date) }}</p>
              </div>
            </div>
            
            <div class="analysis-card" v-if="analysisResult.analysis_details?.bias">
              <div class="card-icon">⚖️</div>
              <div class="card-content">
                <h3>정보의 편향성</h3>
                <p>{{ 
                  analysisResult.analysis_details.bias === 'neutral' ? '중립적인 관점에서 작성된 기사입니다' :
                  analysisResult.analysis_details.bias === 'left' ? '진보적 관점이 포함되어 있습니다' :
                  analysisResult.analysis_details.bias === 'right' ? '보수적 관점이 포함되어 있습니다' :
                  '편향성 정보 없음'
                }}</p>
              </div>
            </div>
            
            <div class="analysis-card warning" v-if="analysisResult.analysis_details?.advertisement">
              <div class="card-icon">⚠️</div>
              <div class="card-content">
                <h3>광고/상업성</h3>
                <p>일부 상업적 내용이 포함되어 있습니다</p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 사이드바 -->
      <aside class="sidebar">
        <!-- 관련 기사 -->
        <div class="sidebar-section">
          <h3>관련 기사</h3>
          <div class="article-list">
            <div class="article-item" v-for="(article, index) in relatedArticles" :key="index">
              <div class="article-thumbnail">📰</div>
              <div class="article-content">
                <h4>{{ article.title || '관련 뉴스 제목' }}</h4>
                <p>{{ article.description || '관련 기사 설명...' }}</p>
              </div>
            </div>
            <div v-if="relatedArticles.length === 0" class="no-articles">
              관련 기사가 없습니다.
            </div>
          </div>
        </div>

        <!-- 함께 보면 좋은 글 -->
        <div class="sidebar-section">
          <h3>함께 보면 좋은 글</h3>
          <div class="article-list">
            <div class="article-item" v-for="(article, index) in recommendedArticles" :key="index">
              <div class="article-thumbnail">📖</div>
              <div class="article-content">
                <h4>{{ article.title || '추천 기사 제목' }}</h4>
                <p>{{ article.description || '추천 기사 설명...' }}</p>
              </div>
            </div>
            <div v-if="recommendedArticles.length === 0" class="no-articles">
              추천 기사가 없습니다.
            </div>
          </div>
        </div>

        <!-- 정보 평가 기능 -->
        <div class="evaluation-section">
          <button @click="showEvaluationModal = true" class="eval-btn primary">
            평가하고 피드백
          </button>
          <button @click="showReportModal = true" class="eval-btn secondary">
            신고하기
          </button>
        </div>
      </aside>
    </div>

    <!-- 평가 모달 -->
    <div v-if="showEvaluationModal" class="modal-overlay" @click="showEvaluationModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>분석 결과 평가</h3>
          <button @click="showEvaluationModal = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="rating-section">
            <label>평가 점수</label>
            <div class="rating-stars">
              <button
                v-for="star in 5"
                :key="star"
                @click="evaluationRating = star"
                class="star-btn"
                :class="{ active: star <= evaluationRating }"
              >
                {{ star <= evaluationRating ? '★' : '☆' }}
              </button>
            </div>
            <p class="rating-text">{{ getRatingText(evaluationRating) }}</p>
          </div>
          <div class="feedback-section">
            <label>피드백 (선택사항)</label>
            <textarea
              v-model="evaluationFeedback"
              placeholder="분석 결과에 대한 의견을 남겨주세요..."
              class="feedback-input"
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showEvaluationModal = false" class="btn-cancel">취소</button>
          <button @click="submitEvaluation" class="btn-submit" :disabled="evaluationRating === 0">
            제출하기
          </button>
        </div>
      </div>
    </div>

    <!-- 신고 모달 -->
    <div v-if="showReportModal" class="modal-overlay" @click="showReportModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>부적절한 내용 신고</h3>
          <button @click="showReportModal = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div class="report-reason-section">
            <label>신고 사유</label>
            <div class="reason-options">
              <label
                v-for="reason in reportReasons"
                :key="reason.value"
                class="reason-option"
              >
                <input
                  type="radio"
                  :value="reason.value"
                  v-model="reportReason"
                  name="reportReason"
                />
                <span>{{ reason.label }}</span>
              </label>
            </div>
          </div>
          <div class="report-description-section">
            <label>상세 설명 (선택사항)</label>
            <textarea
              v-model="reportDescription"
              placeholder="신고 사유에 대한 상세한 설명을 입력해주세요..."
              class="report-input"
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showReportModal = false" class="btn-cancel">취소</button>
          <button @click="submitReport" class="btn-submit" :disabled="!reportReason">
            신고하기
          </button>
        </div>
      </div>
    </div>

    <!-- 성공 메시지 토스트 -->
    <div v-if="showSuccessToast" class="toast success">
      {{ successMessage }}
    </div>
  </div>
</template>

<script>
import { analyzeNews } from '../services/api.js'
import { Graph } from '../utils/dataStructures.js'
import { extractKeywords, stringMatch } from '../utils/algorithms.js'
import { historyService } from '../services/historyService.js'
import { evaluationService } from '../services/evaluationService.js'

export default {
  name: 'AnalysisResult',
  data() {
    return {
      analysisResult: null,
      isLoading: true,
      error: null,
      url: '',
      relatedArticles: [],
      recommendedArticles: [],
      progress: 0, // 프로그레스 바 진행률 (0-100)
      estimatedTime: 10, // 예상 소요 시간 (초)
      progressInterval: null, // 프로그레스 업데이트 인터벌
      startTime: null, // 분석 시작 시간
      // 평가 관련
      showEvaluationModal: false,
      evaluationRating: 0,
      evaluationFeedback: '',
      // 신고 관련
      showReportModal: false,
      reportReason: '',
      reportDescription: '',
      reportReasons: [
        { value: 'fake_news', label: '가짜뉴스' },
        { value: 'misleading', label: '오보/왜곡' },
        { value: 'inappropriate', label: '부적절한 내용' },
        { value: 'spam', label: '스팸/광고' },
        { value: 'other', label: '기타' }
      ],
      // 토스트 메시지
      showSuccessToast: false,
      successMessage: ''
    }
  },
  async mounted() {
    // 1. URL 가져오기 (query parameter에서)
    this.url = this.$route.query.url || ''
    
    // 2. 라우터 상태에서 결과 가져오기
    if (history.state && history.state.analysisResult) {
      this.analysisResult = history.state.analysisResult
      this.isLoading = false
      // 그래프 기반 관련 기사 추천 (DFS/BFS 사용)
      this.findRelatedArticles()
    } 
    // 3. 새로고침 등으로 상태가 없으면 API 재호출
    else if (this.url) {
      await this.fetchAnalysis()
    } 
    // 4. URL도 없으면 에러
    else {
      this.error = '분석할 URL이 없습니다.'
      this.isLoading = false
    }
  },
  methods: {
    async fetchAnalysis() {
      try {
        this.isLoading = true
        this.progress = 0
        this.startTime = Date.now()
        this.estimatedTime = 10 // 기본 예상 시간 10초

        // 프로그레스 바 애니메이션 시작
        this.startProgressAnimation()

        const result = await analyzeNews(this.url)
        this.analysisResult = result.data
        // 그래프 기반 관련 기사 추천 (DFS/BFS 사용)
        this.findRelatedArticles()
      } catch (error) {
        // 에러 처리 개선
        this.error = error
        console.error('분석 오류:', error)
      } finally {
        this.stopProgressAnimation()
        this.isLoading = false
        this.progress = 0
      }
    },

    /**
     * 재시도 함수
     * 같은 URL로 다시 분석 시도
     */
    async retryAnalysis() {
      if (this.url) {
        await this.fetchAnalysis()
      }
    },

    /**
     * 프로그레스 바 애니메이션 시작
     * 실제 진행률을 시뮬레이션하여 사용자에게 피드백 제공
     */
    startProgressAnimation() {
      // 기존 인터벌이 있으면 정리
      if (this.progressInterval) {
        clearInterval(this.progressInterval)
      }

      // 초기 진행률 설정
      this.progress = 0

      // 프로그레스 바 업데이트 (0% → 90%까지 점진적으로 증가)
      // 실제 완료는 API 응답이 올 때 100%로 설정
      this.progressInterval = setInterval(() => {
        if (this.progress < 90) {
          // 시간이 지날수록 증가 속도가 느려짐 (실제 분석과 유사하게)
          const increment = Math.max(0.5, (90 - this.progress) * 0.1)
          this.progress = Math.min(90, this.progress + increment)
          
          // 경과 시간에 따라 예상 소요 시간 업데이트
          if (this.startTime) {
            const elapsed = (Date.now() - this.startTime) / 1000
            // 경과 시간의 1.2배를 예상 시간으로 설정 (여유있게)
            this.estimatedTime = Math.ceil(elapsed * 1.2)
          }
        }
      }, 200) // 200ms마다 업데이트
    },

    /**
     * 프로그레스 바 애니메이션 중지
     */
    stopProgressAnimation() {
      if (this.progressInterval) {
        clearInterval(this.progressInterval)
        this.progressInterval = null
      }
      // 완료 시 100%로 설정
      this.progress = 100
      // 잠시 후 0으로 리셋 (다음 분석을 위해)
      setTimeout(() => {
        this.progress = 0
      }, 500)
    },

    /**
     * 에러 타입에 따른 제목 반환
     * @param {Error} error - 에러 객체
     * @returns {string} 에러 제목
     */
    getErrorTitle(error) {
      const message = error?.message || error || ''
      const errorStr = message.toLowerCase()

      if (errorStr.includes('network') || errorStr.includes('fetch') || errorStr.includes('connection')) {
        return '연결 오류'
      } else if (errorStr.includes('timeout') || errorStr.includes('timed out')) {
        return '시간 초과'
      } else if (errorStr.includes('400') || errorStr.includes('bad request')) {
        return '잘못된 요청'
      } else if (errorStr.includes('500') || errorStr.includes('internal server')) {
        return '서버 오류'
      } else if (errorStr.includes('cors')) {
        return 'CORS 오류'
      } else if (errorStr.includes('404') || errorStr.includes('not found')) {
        return '페이지를 찾을 수 없음'
      } else {
        return '분석 실패'
      }
    },

    /**
     * 에러 타입에 따른 메시지 반환
     * @param {Error} error - 에러 객체
     * @returns {string} 사용자 친화적인 에러 메시지
     */
    getErrorMessage(error) {
      const message = error?.message || error || '알 수 없는 오류가 발생했습니다.'
      const errorStr = message.toLowerCase()

      // 백엔드에서 온 상세 에러 메시지가 있으면 그대로 사용
      if (error?.message && !errorStr.includes('http') && !errorStr.includes('network')) {
        return error.message
      }

      // 일반적인 에러 메시지 변환
      if (errorStr.includes('network') || errorStr.includes('fetch') || errorStr.includes('connection')) {
        return '백엔드 서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.'
      } else if (errorStr.includes('timeout') || errorStr.includes('timed out')) {
        return '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.'
      } else if (errorStr.includes('400') || errorStr.includes('bad request')) {
        return '요청 형식이 올바르지 않습니다. URL을 확인해주세요.'
      } else if (errorStr.includes('500') || errorStr.includes('internal server')) {
        return '서버에서 오류가 발생했습니다. 백엔드 개발자에게 문의해주세요.'
      } else if (errorStr.includes('cors')) {
        return 'CORS 정책으로 인해 요청이 차단되었습니다. 백엔드 CORS 설정을 확인해주세요.'
      } else if (errorStr.includes('404') || errorStr.includes('not found')) {
        return '요청한 페이지를 찾을 수 없습니다. URL을 확인해주세요.'
      } else {
        return message
      }
    },

    /**
     * 에러 타입에 따른 해결 방법 반환
     * @param {Error} error - 에러 객체
     * @returns {string|null} 해결 방법 (없으면 null)
     */
    getErrorSolution(error) {
      const message = error?.message || error || ''
      const errorStr = message.toLowerCase()

      if (errorStr.includes('network') || errorStr.includes('fetch') || errorStr.includes('connection')) {
        return '인터넷 연결을 확인하고, 백엔드 서버가 실행 중인지 확인해주세요.'
      } else if (errorStr.includes('timeout') || errorStr.includes('timed out')) {
        return '잠시 후 다시 시도하거나, 백엔드 서버의 응답 속도를 확인해주세요.'
      } else if (errorStr.includes('500') || errorStr.includes('internal server')) {
        return '백엔드 개발자에게 오류 내용을 전달해주세요: ' + message
      } else if (errorStr.includes('cors')) {
        return '백엔드 개발자에게 CORS 설정을 요청해주세요.'
      } else if (errorStr.includes('400') || errorStr.includes('bad request')) {
        return '올바른 뉴스 URL 형식인지 확인해주세요.'
      }

      return null
    },

    /**
     * 그래프 기반 관련 기사 찾기
     * 그래프 자료구조와 DFS/BFS 알고리즘 사용
     * 시간 복잡도: O(V + E) - V: 정점 수, E: 간선 수
     */
    findRelatedArticles() {
      if (!this.analysisResult) {
        return
      }

      // 1. 현재 기사의 키워드 추출 (문자열 알고리즘 사용)
      const currentTitle = this.analysisResult.metadata?.article_title || ''
      const currentPublisher = this.analysisResult.metadata?.publisher || ''
      const currentKeywords = extractKeywords(currentTitle + ' ' + currentPublisher)

      // 2. 그래프 생성
      const articleGraph = new Graph()

      // 3. 모든 분석 기록 가져오기
      const allRecords = historyService.getAllRecords()

      // 4. 현재 기사를 그래프에 추가
      const currentArticleId = this.url
      articleGraph.addVertex(currentArticleId)

      // 5. 다른 기사들과의 관계 구축
      for (const record of allRecords) {
        // 현재 기사는 제외
        if (record.url === this.url) {
          continue
        }

        const recordTitle = record.data?.metadata?.article_title || ''
        const recordPublisher = record.data?.metadata?.publisher || ''
        const recordKeywords = extractKeywords(recordTitle + ' ' + recordPublisher)

        // 6. 키워드 유사도 계산 (문자열 매칭 알고리즘 사용)
        const similarity = this.calculateKeywordSimilarity(currentKeywords, recordKeywords)

        // 7. 유사도가 일정 수준 이상이면 그래프에 간선 추가
        if (similarity > 0.3) {
          articleGraph.addVertex(record.url)
          // 가중치는 유사도 (높을수록 더 관련있음)
          articleGraph.addEdge(currentArticleId, record.url, similarity)
        }
      }

      // 8. DFS 알고리즘을 사용하여 관련 기사 탐색
      // 최대 깊이 2로 제한하여 직접적으로 관련된 기사만 찾기
      const relatedUrls = articleGraph.getConnectedVertices(currentArticleId, 2)

      // 9. 관련 기사 정보 구성
      this.relatedArticles = relatedUrls
        .map(url => {
          const record = historyService.getRecordByURL(url)
          if (!record) return null

          return {
            title: record.data?.metadata?.article_title || '관련 뉴스',
            description: `${record.data?.metadata?.publisher || '언론사'} - ${this.formatDate(record.analyzedAt)}`,
            url: record.url,
            score: record.data?.reliability_score || 0
          }
        })
        .filter(article => article !== null)
        .slice(0, 5) // 최대 5개만 표시

      // 10. 추천 기사: 신뢰도가 높은 기사들
      const allArticles = allRecords
        .filter(record => record.url !== this.url)
        .map(record => ({
          title: record.data?.metadata?.article_title || '추천 기사',
          description: `${record.data?.metadata?.publisher || '언론사'} - 신뢰도 ${record.data?.reliability_score || 0}점`,
          url: record.url,
          score: record.data?.reliability_score || 0
        }))
        .filter(article => article.score >= 70) // 신뢰도 70점 이상
        .sort((a, b) => b.score - a.score) // 점수 높은 순으로 정렬
        .slice(0, 3) // 최대 3개만 표시

      this.recommendedArticles = allArticles
    },

    /**
     * 키워드 유사도 계산
     * 두 키워드 배열의 유사도를 계산 (간단한 Jaccard 유사도)
     * 시간 복잡도: O(n * m) - n, m: 각 키워드 배열의 길이
     * 
     * @param {Array} keywords1 - 첫 번째 키워드 배열
     * @param {Array} keywords2 - 두 번째 키워드 배열
     * @returns {number} 유사도 (0 ~ 1)
     */
    calculateKeywordSimilarity(keywords1, keywords2) {
      if (keywords1.length === 0 && keywords2.length === 0) {
        return 0
      }

      // 교집합 계산 (문자열 매칭 알고리즘 사용)
      const intersection = keywords1.filter(keyword1 =>
        keywords2.some(keyword2 => stringMatch(keyword1, keyword2) || keyword1 === keyword2)
      )

      // 합집합 계산
      const union = [...new Set([...keywords1, ...keywords2])]

      // Jaccard 유사도: 교집합 / 합집합
      return union.length > 0 ? intersection.length / union.length : 0
    },
    getScoreColor(score) {
      if (score >= 70) return '#10b981' // 초록
      if (score >= 40) return '#f59e0b' // 노랑
      return '#ef4444' // 빨강
    },
    getScoreIcon(isFake) {
      return isFake ? '✗' : '✓'
    },
    formatDate(dateString) {
      if (!dateString) return '정보 없음'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('ko-KR', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      } catch {
        return dateString
      }
    },

    /**
     * 평가 제출
     */
    submitEvaluation() {
      if (this.evaluationRating === 0) {
        alert('평가 점수를 선택해주세요.')
        return
      }

      if (!this.url) {
        alert('URL 정보가 없습니다.')
        return
      }

      // 평가 저장
      evaluationService.addEvaluation({
        url: this.url,
        rating: this.evaluationRating,
        feedback: this.evaluationFeedback
      })

      // 성공 메시지 표시
      this.showSuccessToast = true
      this.successMessage = '평가가 저장되었습니다. 감사합니다!'
      
      // 모달 닫기
      this.showEvaluationModal = false
      
      // 입력 초기화
      this.evaluationRating = 0
      this.evaluationFeedback = ''

      // 토스트 메시지 자동 닫기
      setTimeout(() => {
        this.showSuccessToast = false
      }, 3000)
    },

    /**
     * 신고 제출
     */
    submitReport() {
      if (!this.reportReason) {
        alert('신고 사유를 선택해주세요.')
        return
      }

      if (!this.url) {
        alert('URL 정보가 없습니다.')
        return
      }

      // 신고 저장
      evaluationService.addReport({
        url: this.url,
        reason: this.reportReason,
        description: this.reportDescription
      })

      // 성공 메시지 표시
      this.showSuccessToast = true
      this.successMessage = '신고가 접수되었습니다. 검토 후 조치하겠습니다.'
      
      // 모달 닫기
      this.showReportModal = false
      
      // 입력 초기화
      this.reportReason = ''
      this.reportDescription = ''

      // 토스트 메시지 자동 닫기
      setTimeout(() => {
        this.showSuccessToast = false
      }, 3000)
    },

    /**
     * 평가 점수에 따른 텍스트 반환
     */
    getRatingText(rating) {
      const texts = {
        0: '점수를 선택해주세요',
        1: '매우 불만족',
        2: '불만족',
        3: '보통',
        4: '만족',
        5: '매우 만족'
      }
      return texts[rating] || ''
    }
  },
  beforeUnmount() {
    // 컴포넌트 언마운트 시 인터벌 정리
    if (this.progressInterval) {
      clearInterval(this.progressInterval)
    }
  }
}
</script>

<style scoped>
.analysis-result {
  min-height: 100vh;
  background: #f8fafc;
}

.header {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.logo-icon {
  background: #3b82f6;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #6b7280;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #3b82f6;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.reliability-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.reliability-section h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.reliability-score {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.score-circle {
  color: white;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.score-number {
  font-size: 2.5rem;
  line-height: 1;
}

.score-total {
  font-size: 1rem;
  opacity: 0.8;
}

.score-description {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.score-icon {
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.score-description p {
  color: #374151;
  font-size: 1.1rem;
  line-height: 1.5;
}

.analysis-details h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.analysis-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.analysis-card:hover {
  transform: translateY(-2px);
}

.analysis-card.warning {
  border-left: 4px solid #f59e0b;
}

.card-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 12px;
}

.card-content h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.card-content p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sidebar-section {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.sidebar-section h3 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.article-item:hover {
  background: #f9fafb;
}

.article-thumbnail {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 8px;
}

.article-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.article-content p {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.3;
}

.no-articles {
  color: #9ca3af;
  font-size: 0.9rem;
  text-align: center;
  padding: 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #6b7280;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

/* 프로그레스 바 컨테이너 */
.progress-container {
  width: 300px;
  height: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem auto;
}

/* 프로그레스 바 */
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
  transition: width 0.3s ease-out;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.estimated-time {
  font-size: 0.9rem;
  color: #6b7280;
  font-style: italic;
  margin-top: 0.5rem;
}

/* 에러 컨테이너 (개선됨) */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1.5rem;
  text-align: center;
  padding: 3rem 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 700px;
  margin: 2rem auto;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 4rem;
}

.error-content {
  width: 100%;
}

.error-container h2 {
  color: #dc2626;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.error-message {
  color: #991b1b;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.error-solution {
  color: #7c2d12;
  font-size: 0.9rem;
  line-height: 1.5;
  background: rgba(220, 38, 38, 0.1);
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  text-align: left;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.retry-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #4b5563;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(107, 114, 128, 0.3);
}

.evaluation-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.eval-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.eval-btn.primary {
  background: #3b82f6;
  color: white;
}

.eval-btn.primary:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.eval-btn.secondary {
  background: #ef4444;
  color: white;
}

.eval-btn.secondary:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body label {
  display: block;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
}

/* 평가 섹션 */
.rating-section {
  margin-bottom: 1.5rem;
}

.rating-stars {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.star-btn {
  background: none;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  width: 48px;
  height: 48px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #d1d5db;
}

.star-btn:hover {
  border-color: #f59e0b;
  transform: scale(1.1);
}

.star-btn.active {
  border-color: #f59e0b;
  background: #fef3c7;
  color: #f59e0b;
}

.rating-text {
  color: #6b7280;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.feedback-section {
  margin-bottom: 1rem;
}

.feedback-input,
.report-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.feedback-input:focus,
.report-input:focus {
  outline: none;
  border-color: #3b82f6;
}

/* 신고 섹션 */
.report-reason-section {
  margin-bottom: 1.5rem;
}

.reason-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reason-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.reason-option:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.reason-option input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.reason-option input[type="radio"]:checked + span {
  font-weight: 600;
  color: #3b82f6;
}

.reason-option span {
  flex: 1;
  color: #1f2937;
}

.report-description-section {
  margin-bottom: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  background: #3b82f6;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 토스트 메시지 */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 2000;
  animation: slideInRight 0.3s ease-out;
  max-width: 400px;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast.success {
  background: #10b981;
  color: white;
  font-weight: 500;
}

.eval-btn {
  padding: 1rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.eval-btn.primary {
  background: #3b82f6;
  color: white;
}

.eval-btn.primary:hover {
  background: #2563eb;
}

.eval-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.eval-btn.secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .reliability-score {
    flex-direction: column;
    text-align: center;
  }
  
  .analysis-cards {
    grid-template-columns: 1fr;
  }
}
</style>


