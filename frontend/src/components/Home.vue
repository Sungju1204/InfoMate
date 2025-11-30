<template>
  <div class="home">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
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

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 헤드라인 -->
      <div class="headline">
        <h1>가짜뉴스, AI로 10초 만에 판별해요</h1>
      </div>

      <!-- 링크 입력창 -->
      <div class="input-section">
        <div class="input-container">
          <input 
            type="text" 
            v-model="newsUrl"
            placeholder="분석하고 싶은 뉴스 링크를 여기에 붙여넣으세요"
            class="url-input"
            :disabled="isLoading"
            @keyup.enter="analyzeNews"
          />
          <button 
            @click="analyzeNews" 
            class="analyze-btn"
            :disabled="isLoading"
          >
            {{ isLoading ? '분석 중...' : '신뢰도 분석' }}
          </button>
        </div>
        
        <!-- 로딩 상태 (스피너 + 프로그레스 바 + 예상 소요 시간) -->
        <div v-if="isLoading" class="loading-section">
          <div class="loading-spinner"></div>
          <div class="progress-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
          </div>
          <p class="loading-text">분석 중입니다...</p>
          <p class="estimated-time">예상 소요 시간: 약 {{ estimatedTime }}초</p>
        </div>

        <!-- 에러 메시지 표시 (개선됨) -->
        <div v-if="error && !isLoading" class="error-container">
          <div class="error-icon">⚠️</div>
          <div class="error-content">
            <h3 class="error-title">{{ getErrorTitle(error) }}</h3>
            <p class="error-message">{{ getErrorMessage(error) }}</p>
            <p class="error-solution" v-if="getErrorSolution(error)">
              💡 {{ getErrorSolution(error) }}
            </p>
          </div>
          <button @click="retryAnalysis" class="retry-btn" :disabled="isLoading">
            🔄 다시 시도
          </button>
        </div>
      </div>

      <!-- 서비스 핵심 소개 -->
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">📄</div>
          <h3>AI 기반 신뢰성 검증</h3>
          <p>최신 AI 기술로 뉴스의 신뢰성을 종합적으로 분석합니다</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔄</div>
          <h3>실시간 이슈 모니터링</h3>
          <p>핫한 이슈들을 실시간으로 모니터링하고 분석합니다</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🏢</div>
          <h3>강력한 콘텐츠 팀</h3>
          <p>전문가들이 검증한 신뢰할 수 있는 정보를 제공합니다</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { analyzeNews } from '../services/api.js'
import { validateURL, normalizeURL, extractDomain, isNewsSite } from '../utils/urlParser.js'
import { historyService } from '../services/historyService.js'

export default {
  name: 'Home',
  data() {
    return {
      newsUrl: '',
      isLoading: false,
      error: null,
      lastErrorUrl: null, // 재시도를 위한 마지막 URL 저장
      progress: 0, // 프로그레스 바 진행률 (0-100)
      estimatedTime: 10, // 예상 소요 시간 (초)
      progressInterval: null, // 프로그레스 업데이트 인터벌
      startTime: null // 분석 시작 시간
    }
  },
  methods: {
    async analyzeNews() {
      // 1. 입력 검증
      if (!this.newsUrl.trim()) {
        alert('뉴스 링크를 입력해주세요.')
        return
      }

      // 2. URL 정규화 (문자열 알고리즘 사용)
      this.newsUrl = normalizeURL(this.newsUrl)

      // 3. URL 검증 (문자열 알고리즘 사용)
      if (!validateURL(this.newsUrl)) {
        alert('유효한 URL을 입력해주세요.\n예: https://example.com/news/article')
        return
      }

      // 4. 뉴스 사이트 확인 (선택적)
      const domain = extractDomain(this.newsUrl)
      if (!isNewsSite(this.newsUrl)) {
        // 경고만 표시하고 계속 진행
        console.warn('뉴스 사이트가 아닐 수 있습니다:', domain)
      }

      // 3. 로딩 시작
      this.isLoading = true
      this.error = null
      this.progress = 0
      this.startTime = Date.now()
      this.estimatedTime = 10 // 기본 예상 시간 10초

      // 프로그레스 바 애니메이션 시작 (시뮬레이션)
      this.startProgressAnimation()

      try {
        // 5. API 호출
        const result = await analyzeNews(this.newsUrl)
        
        // 6. 분석 기록 저장 (해시 테이블 사용 - O(1) 중복 검사)
        historyService.addRecord({
          url: this.newsUrl,
          data: result.data
        })
        
        // 7. 결과를 라우터 상태로 전달하며 페이지 이동
        this.$router.push({
          path: '/analysis',
          query: { url: this.newsUrl }, // URL은 query에 (새로고침 대응)
          state: { 
            analysisResult: result.data // 결과는 state에
          }
        })
      } catch (error) {
        // 8. 에러 처리 (개선됨)
        this.error = error
        this.lastErrorUrl = this.newsUrl // 재시도를 위해 URL 저장
        console.error('분석 오류:', error)
        // alert 제거 - UI에 표시된 에러 메시지로 충분
      } finally {
        // 9. 로딩 종료
        this.stopProgressAnimation()
        this.isLoading = false
        this.progress = 0
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
     * 재시도 함수
     * 마지막에 실패한 URL로 다시 분석 시도
     */
    async retryAnalysis() {
      if (this.lastErrorUrl) {
        this.newsUrl = this.lastErrorUrl
        await this.analyzeNews()
      } else if (this.newsUrl) {
        // URL이 있으면 그대로 재시도
        await this.analyzeNews()
      }
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
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
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

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
  text-align: center;
}

.headline h1 {
  font-size: 3rem;
  font-weight: bold;
  color: white;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.input-section {
  margin-bottom: 4rem;
}

.input-container {
  display: flex;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.url-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  outline: none;
}

.url-input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.analyze-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  white-space: nowrap;
}

.analyze-btn:hover:not(:disabled) {
  background: #2563eb;
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.url-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 로딩 섹션 (스피너 + 프로그레스 바 + 예상 소요 시간) */
.loading-section {
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  text-align: center;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 스피너 애니메이션 */
.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  margin: 0 auto 1.5rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 프로그레스 바 컨테이너 */
.progress-container {
  width: 100%;
  height: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

/* 프로그레스 바 */
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
  transition: width 0.3s ease-out;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.estimated-time {
  font-size: 0.9rem;
  color: #6b7280;
  font-style: italic;
}

/* 에러 메시지 컨테이너 (개선됨) */
.error-container {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(220, 38, 38, 0.1);
  border: 2px solid rgba(220, 38, 38, 0.3);
  border-radius: 12px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  font-size: 2rem;
  text-align: center;
}

.error-content {
  flex: 1;
}

.error-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-message {
  color: #991b1b;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.error-solution {
  color: #7c2d12;
  font-size: 0.9rem;
  line-height: 1.5;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  align-self: center;
  margin-top: 0.5rem;
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

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #6b7280;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .headline h1 {
    font-size: 2rem;
  }
  
  .input-container {
    flex-direction: column;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
