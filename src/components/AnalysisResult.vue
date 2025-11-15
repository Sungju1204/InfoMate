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

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>분석 중입니다...</p>
    </div>

    <!-- 에러 상태 -->
    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2>오류가 발생했습니다</h2>
      <p>{{ error }}</p>
      <button @click="$router.push('/')" class="back-btn">
        다시 시도하기
      </button>
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
          <button class="eval-btn primary">평가하고 피드백</button>
          <button class="eval-btn secondary">제보하기</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import { analyzeNews } from '../services/api.js'
import { Graph } from '../utils/dataStructures.js'
import { extractKeywords, stringMatch } from '../utils/algorithms.js'
import { historyService } from '../services/historyService.js'

export default {
  name: 'AnalysisResult',
  data() {
    return {
      analysisResult: null,
      isLoading: true,
      error: null,
      url: '',
      relatedArticles: [],
      recommendedArticles: []
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
        const result = await analyzeNews(this.url)
        this.analysisResult = result.data
        // 그래프 기반 관련 기사 추천 (DFS/BFS 사용)
        this.findRelatedArticles()
      } catch (error) {
        this.error = error.message || '분석 결과를 가져올 수 없습니다.'
        console.error('분석 오류:', error)
      } finally {
        this.isLoading = false
      }
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
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  text-align: center;
  padding: 2rem;
}

.error-icon {
  font-size: 4rem;
}

.error-container h2 {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.error-container p {
  color: #6b7280;
  margin-bottom: 1rem;
}

.back-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.back-btn:hover {
  background: #2563eb;
}

.evaluation-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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


