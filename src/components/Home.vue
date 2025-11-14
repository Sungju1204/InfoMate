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
        
        <!-- 에러 메시지 표시 -->
        <div v-if="error" class="error-message">
          {{ error }}
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
      error: null
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
        // 8. 에러 처리
        this.error = error.message || '분석 중 오류가 발생했습니다.'
        alert(this.error)
        console.error('분석 오류:', error)
      } finally {
        // 9. 로딩 종료
        this.isLoading = false
      }
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

.error-message {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border-radius: 8px;
  font-size: 0.9rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
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
