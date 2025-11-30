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
            <!-- GPT 의견+점수 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getGPTScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getGPTScore(analysisResult)) + '15' }">
                  <div class="card-icon">🤖</div>
                </div>
                <div class="card-title-section">
                  <h3>GPT 의견</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getGPTScore(analysisResult)) }">
                    <span class="score-number-small">{{ getGPTScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ getGPTOpinion(analysisResult) }}</p>
              </div>
            </div>

            <!-- 지도학습AI 모델 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getAIModelScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getAIModelScore(analysisResult)) + '15' }">
                  <div class="card-icon">🧠</div>
                </div>
                <div class="card-title-section">
                  <h3>지도학습AI 모델</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getAIModelScore(analysisResult)) }">
                    <span class="score-number-small">{{ getAIModelScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ getAIModelPrediction(analysisResult) }}</p>
              </div>
            </div>

            <!-- 발행일 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getPublishDateScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getPublishDateScore(analysisResult)) + '15' }">
                  <div class="card-icon">📅</div>
                </div>
                <div class="card-title-section">
                  <h3>발행일</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getPublishDateScore(analysisResult)) }">
                    <span class="score-number-small">{{ getPublishDateScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ formatDate(analysisResult.metadata?.publish_date) }}</p>
              </div>
            </div>

            <!-- 자극적인 단어 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getSensationalWordsScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getSensationalWordsScore(analysisResult)) + '15' }">
                  <div class="card-icon">⚠️</div>
                </div>
                <div class="card-title-section">
                  <h3>자극적인 단어</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getSensationalWordsScore(analysisResult)) }">
                    <span class="score-number-small">{{ getSensationalWordsScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ getSensationalWords(analysisResult) }}</p>
              </div>
            </div>

            <!-- 미디어/도메인 신뢰도 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getMediaTrustScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getMediaTrustScore(analysisResult)) + '15' }">
                  <div class="card-icon">🏢</div>
                </div>
                <div class="card-title-section">
                  <h3>미디어/도메인 신뢰도</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getMediaTrustScore(analysisResult)) }">
                    <span class="score-number-small">{{ getMediaTrustScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ analysisResult.metadata?.publisher || '정보 없음' }}</p>
              </div>
            </div>

            <!-- 광고성/상업성 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getAdvertisementScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getAdvertisementScore(analysisResult)) + '15' }">
                  <div class="card-icon">💰</div>
                </div>
                <div class="card-title-section">
                  <h3>광고성/상업성</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getAdvertisementScore(analysisResult)) }">
                    <span class="score-number-small">{{ getAdvertisementScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ getAdvertisementText(analysisResult) }}</p>
              </div>
            </div>

            <!-- 크로스 체크 정보/신뢰성 -->
            <div class="analysis-card" :style="{ borderTopColor: getScoreColor(getCrossCheckScore(analysisResult)) }">
              <div class="card-header">
                <div class="card-icon-wrapper" :style="{ background: getScoreColor(getCrossCheckScore(analysisResult)) + '15' }">
                  <div class="card-icon">🔍</div>
                </div>
                <div class="card-title-section">
                  <h3>크로스 체크 정보</h3>
                  <div class="score-circle-small" :style="{ borderColor: getScoreColor(getCrossCheckScore(analysisResult)) }">
                    <span class="score-number-small">{{ getCrossCheckScore(analysisResult) }}</span>
                  </div>
                </div>
              </div>
              <div class="card-content">
                <p>{{ getCrossCheckInfo(analysisResult) }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 평가 기록 섹션 -->
        <section class="history-section">
          <router-link to="/history" class="history-link-btn">
            평가 기록 보기 →
          </router-link>
        </section>

        <!-- 관련 기사 섹션 -->
        <section class="related-articles-section">
          <h2>관련 기사</h2>
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
        </section>

        <!-- 정보 평가 기능 -->
        <section class="evaluation-section-wrapper">
          <div class="evaluation-section">
            <button @click="showEvaluationModal = true" class="eval-btn primary">
              평가하고 피드백
            </button>
            <button @click="showReportModal = true" class="eval-btn secondary">
              신고하기
            </button>
          </div>
        </section>
      </div>
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
     * GPT 의견 텍스트 반환
     */
    getGPTOpinion(result) {
      if (result.analysis_details?.gpt_opinion) {
        return result.analysis_details.gpt_opinion
      }
      // 기본값: AI 예측 결과 기반
      if (result.analysis_details?.ai_prediction) {
        const pred = result.analysis_details.ai_prediction
        if (pred.prediction === 'Fake') {
          return '가짜뉴스일 가능성이 높습니다. 주의가 필요합니다.'
        }
        return '신뢰할 수 있는 뉴스로 판단됩니다.'
      }
      return 'GPT 분석 결과를 확인할 수 없습니다.'
    },

    /**
     * GPT 점수 계산 (0-100)
     */
    getGPTScore(result) {
      if (result.analysis_details?.gpt_score !== undefined) {
        return Math.round(result.analysis_details.gpt_score)
      }
      // AI 예측 결과 기반으로 점수 계산
      if (result.analysis_details?.ai_prediction) {
        const pred = result.analysis_details.ai_prediction
        if (pred.true_percentage !== undefined) {
          return Math.round(pred.true_percentage)
        }
      }
      return result.reliability_score || 50
    },

    /**
     * 지도학습AI 모델 예측 텍스트 반환
     */
    getAIModelPrediction(result) {
      if (result.analysis_details?.ai_prediction) {
        const pred = result.analysis_details.ai_prediction
        if (pred.prediction === 'Fake') {
          return `가짜뉴스로 판단됨 (가짜 확률: ${pred.fake_percentage || 0}%)`
        }
        return `진짜뉴스로 판단됨 (진짜 확률: ${pred.true_percentage || 0}%)`
      }
      return 'AI 모델 분석 결과 없음'
    },

    /**
     * 지도학습AI 모델 점수 계산 (0-100)
     */
    getAIModelScore(result) {
      if (result.analysis_details?.ai_model_score !== undefined) {
        return Math.round(result.analysis_details.ai_model_score)
      }
      // AI 예측 결과 기반으로 점수 계산
      if (result.analysis_details?.ai_prediction) {
        const pred = result.analysis_details.ai_prediction
        if (pred.true_percentage !== undefined) {
          return Math.round(pred.true_percentage)
        }
      }
      return result.reliability_score || 50
    },

    /**
     * 발행일 점수 계산 (0-100)
     * 최근일수록 높은 점수
     */
    getPublishDateScore(result) {
      if (result.analysis_details?.publish_date_score !== undefined) {
        return Math.round(result.analysis_details.publish_date_score)
      }
      const publishDate = result.metadata?.publish_date
      if (!publishDate) return 30 // 날짜 정보 없으면 낮은 점수
      
      try {
        const date = new Date(publishDate)
        const now = new Date()
        const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
        
        // 최근 7일 이내: 90점, 30일 이내: 70점, 90일 이내: 50점, 그 이상: 30점
        if (diffDays <= 7) return 90
        if (diffDays <= 30) return 70
        if (diffDays <= 90) return 50
        return 30
      } catch {
        return 50
      }
    },

    /**
     * 자극적인 단어 텍스트 반환
     */
    getSensationalWords(result) {
      if (result.analysis_details?.sensational_words) {
        const words = result.analysis_details.sensational_words
        if (Array.isArray(words) && words.length > 0) {
          return `자극적인 단어 ${words.length}개 발견: ${words.slice(0, 3).join(', ')}${words.length > 3 ? '...' : ''}`
        }
      }
      return '자극적인 단어가 거의 없습니다.'
    },

    /**
     * 자극적인 단어 점수 계산 (0-100)
     * 자극적인 단어가 적을수록 높은 점수
     */
    getSensationalWordsScore(result) {
      if (result.analysis_details?.sensational_words_score !== undefined) {
        return Math.round(result.analysis_details.sensational_words_score)
      }
      if (result.analysis_details?.sensational_words) {
        const words = result.analysis_details.sensational_words
        if (Array.isArray(words)) {
          // 자극적인 단어가 없으면 100점, 1-2개면 80점, 3-5개면 50점, 6개 이상이면 20점
          if (words.length === 0) return 100
          if (words.length <= 2) return 80
          if (words.length <= 5) return 50
          return 20
        }
      }
      return 80 // 기본값: 자극적인 단어 정보 없으면 중간 점수
    },

    /**
     * 미디어/도메인 신뢰도 점수 계산 (0-100)
     */
    getMediaTrustScore(result) {
      if (result.analysis_details?.media_trust?.trust_score !== undefined) {
        return Math.round(result.analysis_details.media_trust.trust_score)
      }
      if (result.analysis_details?.media_trust) {
        // media_trust 객체가 있으면 신뢰도 기반으로 점수 계산
        const trust = result.analysis_details.media_trust
        if (trust.reliability === 'High') return 90
        if (trust.reliability === 'Medium') return 60
        if (trust.reliability === 'Low') return 30
      }
      // 출처 정보가 있으면 기본 점수, 없으면 낮은 점수
      return result.metadata?.publisher ? 60 : 40
    },

    /**
     * 광고성/상업성 텍스트 반환
     */
    getAdvertisementText(result) {
      if (result.analysis_details?.advertisement) {
        const ad = result.analysis_details.advertisement
        if (typeof ad === 'boolean') {
          return ad ? '상업적 내용이 포함되어 있습니다' : '상업적 내용이 거의 없습니다'
        }
        if (typeof ad === 'object' && ad.level) {
          if (ad.level === 'high') return '상업적 내용이 많이 포함되어 있습니다'
          if (ad.level === 'medium') return '일부 상업적 내용이 포함되어 있습니다'
          return '상업적 내용이 거의 없습니다'
        }
      }
      return '광고성/상업성 정보 없음'
    },

    /**
     * 광고성/상업성 점수 계산 (0-100)
     * 광고가 적을수록 높은 점수
     */
    getAdvertisementScore(result) {
      if (result.analysis_details?.advertisement_score !== undefined) {
        return Math.round(result.analysis_details.advertisement_score)
      }
      if (result.analysis_details?.advertisement) {
        const ad = result.analysis_details.advertisement
        if (typeof ad === 'boolean') {
          return ad ? 30 : 90 // 광고 있으면 낮은 점수, 없으면 높은 점수
        }
        if (typeof ad === 'object' && ad.level) {
          if (ad.level === 'high') return 20
          if (ad.level === 'medium') return 50
          return 90
        }
      }
      return 70 // 기본값: 광고 정보 없으면 중간 점수
    },

    /**
     * 크로스 체크 정보 텍스트 반환
     */
    getCrossCheckInfo(result) {
      if (result.analysis_details?.cross_check) {
        const check = result.analysis_details.cross_check
        if (check.verified_sources) {
          return `다른 ${check.verified_sources}개 출처에서도 확인됨`
        }
        if (check.status === 'verified') return '다른 출처에서 확인됨'
        if (check.status === 'unverified') return '다른 출처에서 확인되지 않음'
      }
      return '크로스 체크 정보 없음'
    },

    /**
     * 크로스 체크 점수 계산 (0-100)
     */
    getCrossCheckScore(result) {
      if (result.analysis_details?.cross_check_score !== undefined) {
        return Math.round(result.analysis_details.cross_check_score)
      }
      if (result.analysis_details?.cross_check) {
        const check = result.analysis_details.cross_check
        if (check.verified_sources) {
          // 확인된 출처가 많을수록 높은 점수
          if (check.verified_sources >= 5) return 95
          if (check.verified_sources >= 3) return 80
          if (check.verified_sources >= 1) return 60
          return 40
        }
        if (check.status === 'verified') return 80
        if (check.status === 'unverified') return 30
      }
      return 50 // 기본값: 크로스 체크 정보 없으면 중간 점수
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
  background: var(--bg-primary);
  position: relative;
}

.header {
  background: var(--bg-secondary);
  padding: 1.5rem 0;
  box-shadow: var(--shadow-sm);
  border-bottom: 1px solid var(--gray-lightest);
  position: sticky;
  top: 0;
  z-index: 100;
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
  transition: transform var(--transition-fast);
}

.logo:hover {
  transform: translateX(5px);
}

.logo-icon {
  background: var(--black);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast);
}

.logo:hover .logo-icon {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--black);
  letter-spacing: -0.5px;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-normal);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) scaleX(0);
  width: 80%;
  height: 2px;
  background: var(--black);
  transition: transform var(--transition-normal);
}

.nav-link:hover {
  color: var(--black);
  background: var(--gray-lightest);
}

.nav-link:hover::after {
  transform: translateX(-50%) scaleX(1);
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem 2rem;
  display: block;
  position: relative;
  z-index: 1;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 0;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.reliability-section {
  background: linear-gradient(135deg, var(--bg-card) 0%, rgba(255, 255, 255, 0.8) 100%);
  padding: 3rem 2rem;
  border-radius: 24px;
  border: 2px solid var(--gray-lighter);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  margin-bottom: 3rem;
  position: relative;
  overflow: hidden;
}

.reliability-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
  border-radius: 24px 24px 0 0;
}

.reliability-section h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 1.5rem;
  letter-spacing: -0.5px;
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
  box-shadow: var(--shadow-lg);
  position: relative;
  animation: scoreReveal 1s ease-out;
}

@keyframes scoreReveal {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.score-number {
  font-size: 2.5rem;
  line-height: 1;
  font-weight: 800;
}

.score-total {
  font-size: 1rem;
  opacity: 0.9;
  margin-top: 0.25rem;
}

.score-description {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.score-icon {
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.5rem;
  box-shadow: var(--shadow-md);
}

.score-description p {
  color: var(--text-secondary);
  font-size: 1.15rem;
  line-height: 1.6;
  font-weight: 500;
}

.analysis-details {
  margin-bottom: 3rem;
}

.analysis-details h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 2rem;
  letter-spacing: -0.5px;
  padding-bottom: 1rem;
  border-bottom: 3px solid var(--gray-lighter);
  position: relative;
}

.analysis-details h2::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 80px;
  height: 3px;
  background: var(--black);
  border-radius: 2px;
}

.related-articles-section {
  background: var(--bg-card);
  padding: 2.5rem;
  border-radius: 20px;
  border-left: 4px solid var(--gray-light);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-bottom: 3rem;
  transition: all 0.3s ease;
}

.related-articles-section:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-left-color: var(--black);
}

.related-articles-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 2rem;
  letter-spacing: -0.5px;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--gray-lightest);
}

.history-section {
  display: flex;
  justify-content: center;
  margin-bottom: 3rem;
}

.history-link-btn {
  display: inline-block;
  padding: 0.875rem 2rem;
  background: var(--black);
  color: white;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.history-link-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background: var(--black-soft);
}

.evaluation-section-wrapper {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.02) 0%, var(--bg-card) 100%);
  padding: 2.5rem;
  border-radius: 20px;
  border: 2px solid var(--gray-lighter);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  margin-top: 2rem;
}

.evaluation-section {
  display: flex;
  flex-direction: row;
  gap: 1.25rem;
  justify-content: center;
  flex-wrap: wrap;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.analysis-card {
  background: var(--bg-card);
  padding: 0;
  border-radius: 16px;
  border: 2px solid var(--gray-lighter);
  border-top: 4px solid var(--gray-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.analysis-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: inherit;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.analysis-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: var(--gray-light);
  border-top-width: 5px;
}

.analysis-card:hover::before {
  opacity: 1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.25rem 1rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.1));
  border-bottom: 1px solid var(--gray-lightest);
}

.card-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.analysis-card:hover .card-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.card-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.card-title-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.card-title-section h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--black);
  margin: 0;
  letter-spacing: -0.3px;
}

.score-circle-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2.5px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.analysis-card:hover .score-circle-small {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.score-number-small {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--black);
  letter-spacing: -0.5px;
}

.card-content {
  padding: 1rem 1.25rem 1.25rem;
  flex: 1;
}

.card-content p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
  font-weight: 400;
}

.score-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  animation: fadeInUp 0.6s ease-out 0.2s backwards;
}

.sidebar-section {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--gray-lighter);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.sidebar-section:hover {
  box-shadow: var(--shadow-hover);
  border-color: var(--gray-light);
}

.sidebar-section h3 {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 1.5rem;
  letter-spacing: -0.3px;
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
  border-radius: 12px;
  transition: all var(--transition-normal);
  cursor: pointer;
  border: 1px solid transparent;
}

.article-item:hover {
  background: var(--gray-lightest);
  border-color: var(--gray-lighter);
  transform: translateX(5px);
}

.article-thumbnail {
  font-size: 1.75rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-lightest);
  border-radius: 12px;
}

.article-content h4 {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.article-content p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.no-articles {
  color: var(--text-muted);
  font-size: 0.95rem;
  text-align: center;
  padding: 2rem 1rem;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1.5rem;
  background: var(--bg-card);
  margin: 3rem 2rem;
  padding: 4rem 2rem;
  border-radius: 20px;
  border: 1px solid var(--gray-lighter);
  box-shadow: var(--shadow-lg);
}

.loading-spinner {
  width: 70px;
  height: 70px;
  border: 6px solid var(--gray-lightest);
  border-top: 6px solid var(--black);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

/* 프로그레스 바 컨테이너 */
.progress-container {
  width: 400px;
  max-width: 90%;
  height: 10px;
  background: var(--gray-lightest);
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem auto;
}

/* 프로그레스 바 */
.progress-bar {
  height: 100%;
  background: var(--black);
  border-radius: 10px;
  transition: width 0.3s ease-out;
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.estimated-time {
  font-size: 1rem;
  color: var(--text-secondary);
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
  gap: 2rem;
  text-align: center;
  padding: 4rem 3rem;
  background: var(--bg-card);
  border-radius: 20px;
  border: 2px solid rgba(239, 68, 68, 0.2);
  box-shadow: var(--shadow-lg);
  max-width: 800px;
  margin: 3rem auto;
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  font-size: 5rem;
}

.error-content {
  width: 100%;
}

.error-container h2 {
  color: var(--error);
  margin-bottom: 1.25rem;
  font-size: 1.75rem;
  font-weight: 700;
}

.error-message {
  color: var(--text-secondary);
  font-size: 1.1rem;
  line-height: 1.7;
  margin-bottom: 1.25rem;
}

.error-solution {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  background: rgba(239, 68, 68, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  margin-top: 1.25rem;
  text-align: left;
  border-left: 4px solid var(--error);
}

.error-actions {
  display: flex;
  gap: 1.25rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 1.5rem;
}

.retry-btn {
  background: var(--black);
  color: white;
  border: none;
  padding: 1rem 2.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.retry-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background: var(--black-soft);
}

.retry-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--gray-light);
}

.back-btn {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--gray-lighter);
  padding: 1rem 2.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.back-btn:hover {
  background: var(--gray-lighter);
  border-color: var(--gray-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}


.eval-btn {
  padding: 1.25rem 1.75rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.eval-btn.primary {
  background: var(--black);
  color: white;
  box-shadow: var(--shadow-sm);
}

.eval-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background: var(--black-soft);
}

.eval-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--gray-lighter);
}

.eval-btn.secondary:hover {
  background: var(--gray-lighter);
  border-color: var(--gray-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.4s ease-out;
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
  background: var(--bg-card);
  border: 1px solid var(--gray-lighter);
  border-radius: 20px;
  width: 90%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid var(--gray-lightest);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--black);
  letter-spacing: -0.3px;
}

.modal-close {
  background: var(--gray-lightest);
  border: none;
  font-size: 2rem;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--gray-lighter);
  color: var(--black);
  transform: rotate(90deg);
}

.modal-body {
  padding: 2rem;
}

.modal-body label {
  display: block;
  font-weight: 600;
  color: var(--black);
  margin-bottom: 1rem;
  font-size: 1.05rem;
}

/* 평가 섹션 */
.rating-section {
  margin-bottom: 2rem;
}

.rating-stars {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.star-btn {
  background: var(--bg-tertiary);
  border: 2px solid var(--gray-lighter);
  border-radius: 12px;
  width: 54px;
  height: 54px;
  font-size: 1.75rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--text-muted);
}

.star-btn:hover {
  border-color: var(--warning);
  background: rgba(245, 158, 11, 0.1);
  transform: scale(1.15);
}

.star-btn.active {
  border-color: var(--warning);
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning);
}

.rating-text {
  color: var(--text-secondary);
  font-size: 1rem;
  margin-top: 0.75rem;
  font-weight: 500;
}

.feedback-section {
  margin-bottom: 1.5rem;
}

.feedback-input,
.report-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid var(--gray-lighter);
  border-radius: 12px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all var(--transition-normal);
  box-sizing: border-box;
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.feedback-input::placeholder,
.report-input::placeholder {
  color: var(--text-muted);
}

.feedback-input:focus,
.report-input:focus {
  outline: none;
  border-color: var(--black);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
  background: var(--bg-secondary);
}

/* 신고 섹션 */
.report-reason-section {
  margin-bottom: 2rem;
}

.reason-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reason-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 2px solid var(--gray-lighter);
  border-radius: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
  background: var(--bg-tertiary);
}

.reason-option:hover {
  border-color: var(--black);
  background: var(--bg-secondary);
  transform: translateX(5px);
}

.reason-option input[type="radio"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: var(--black);
}

.reason-option input[type="radio"]:checked + span {
  font-weight: 700;
  color: var(--black);
}

.reason-option span {
  flex: 1;
  color: var(--text-primary);
  font-weight: 500;
}

.report-description-section {
  margin-bottom: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1.25rem;
  padding: 2rem;
  border-top: 1px solid var(--gray-lightest);
}

.btn-cancel,
.btn-submit {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-cancel {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--gray-lighter);
}

.btn-cancel:hover {
  background: var(--gray-lighter);
  border-color: var(--gray-light);
  transform: translateY(-2px);
}

.btn-submit {
  background: var(--black);
  color: white;
  box-shadow: var(--shadow-sm);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  background: var(--black-soft);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--gray-light);
}

/* 토스트 메시지 */
.toast {
  position: fixed;
  bottom: 2.5rem;
  right: 2.5rem;
  padding: 1.25rem 2rem;
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  z-index: 2000;
  animation: slideInRight 0.4s ease-out;
  max-width: 450px;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(150px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.toast.success {
  background: var(--success);
  color: white;
  font-weight: 600;
  font-size: 1.05rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

@media (max-width: 1024px) {
  .content {
    padding: 2rem 1.5rem;
  }
  
  .reliability-score {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }

  .score-description {
    flex-direction: column;
    text-align: center;
  }
  
  .analysis-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
  }

  .reliability-section {
    padding: 2rem 1.5rem;
    margin-bottom: 2rem;
  }

  .analysis-details {
    margin-bottom: 2rem;
  }

  .related-articles-section {
    padding: 2rem 1.5rem;
    margin-bottom: 2rem;
  }

  .history-section {
    margin-bottom: 2rem;
  }

  .evaluation-section-wrapper {
    padding: 2rem 1.5rem;
    margin-top: 1.5rem;
  }

  .loading-container,
  .error-container {
    padding: 3rem 2rem;
    margin: 2rem 1rem;
  }

  .modal-content {
    width: 95%;
  }

  .toast {
    bottom: 1.5rem;
    right: 1.5rem;
    left: 1.5rem;
    max-width: none;
  }
}

@media (max-width: 640px) {
  .header-content {
    padding: 0 1.5rem;
  }

  .nav {
    gap: 1rem;
  }

  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }

  .reliability-section h2,
  .analysis-details h2 {
    font-size: 1.5rem;
  }

  .score-circle {
    width: 120px;
    height: 120px;
  }

  .score-number {
    font-size: 2.5rem;
  }

  .analysis-cards {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .analysis-card {
    padding: 0;
  }

  .card-header {
    padding: 1rem 1rem 0.75rem;
    flex-wrap: wrap;
  }

  .card-title-section {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }

  .card-title-section h3 {
    font-size: 0.9rem;
  }

  .card-content {
    padding: 0.75rem 1rem 1rem;
  }

  .card-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .card-icon {
    font-size: 1.25rem;
  }

  .score-circle-small {
    width: 36px;
    height: 36px;
  }

  .score-number-small {
    font-size: 0.8rem;
  }

  .reliability-section {
    padding: 1.5rem 1.25rem;
    margin-bottom: 1.5rem;
  }

  .analysis-details {
    margin-bottom: 1.5rem;
  }

  .analysis-details h2 {
    font-size: 1.5rem;
    margin-bottom: 1.25rem;
  }

  .related-articles-section {
    padding: 1.5rem 1.25rem;
    margin-bottom: 1.5rem;
  }

  .related-articles-section h2 {
    font-size: 1.5rem;
    margin-bottom: 1.25rem;
  }

  .history-section {
    margin-bottom: 1.5rem;
  }

  .evaluation-section-wrapper {
    padding: 1.5rem 1.25rem;
    margin-top: 1rem;
  }

  .history-link-btn {
    padding: 0.875rem 1.5rem;
    font-size: 0.95rem;
  }

  .evaluation-section {
    flex-direction: column;
  }

  .evaluation-section {
    gap: 1rem;
  }

  .eval-btn {
    padding: 1rem 1.5rem;
  }

  .modal-body,
  .modal-header,
  .modal-footer {
    padding: 1.5rem;
  }

  .rating-stars {
    gap: 0.5rem;
  }

  .star-btn {
    width: 48px;
    height: 48px;
    font-size: 1.5rem;
  }

  .error-actions {
    flex-direction: column;
    width: 100%;
  }

  .retry-btn,
  .back-btn {
    width: 100%;
  }
}
</style>


