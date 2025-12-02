<template>
  <div class="history">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <div class="logo-icon">✓</div>
          <span class="logo-text">InfoMate</span>
        </div>
        <nav class="nav">
          <router-link to="/" class="nav-link">홈</router-link>
          <router-link to="/history" class="nav-link active">평가 기록</router-link>
        </nav>
      </div>
    </header>

    <div class="content">
      <!-- 통계 섹션 -->
      <section class="statistics-section">
        <h2>분석 통계</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <h3>총 분석 수</h3>
              <p class="stat-value">{{ statistics.total }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⭐</div>
            <div class="stat-content">
              <h3>평균 신뢰도</h3>
              <p class="stat-value">{{ statistics.avgScore }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✓</div>
            <div class="stat-content">
              <h3>신뢰 가능</h3>
              <p class="stat-value">{{ statistics.realCount }}</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✗</div>
            <div class="stat-content">
              <h3>의심 기사</h3>
              <p class="stat-value">{{ statistics.fakeCount }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 검색 및 정렬 섹션 -->
      <section class="controls-section">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="URL 또는 언론사로 검색..."
            class="search-input"
            @input="handleSearch"
          />
        </div>
        <div class="sort-controls">
          <select v-model="sortBy" @change="handleSort" class="sort-select">
            <option value="date">날짜순</option>
            <option value="score">신뢰도순</option>
            <option value="count">분석 횟수순</option>
          </select>
          <select v-model="sortOrder" @change="handleSort" class="sort-select">
            <option value="desc">내림차순</option>
            <option value="asc">오름차순</option>
          </select>
          <button @click="clearAll" class="clear-btn">전체 삭제</button>
        </div>
      </section>

      <!-- 기록 목록 -->
      <section class="history-section">
        <h2>분석 기록 ({{ filteredRecords.length }}개)</h2>
        <div v-if="filteredRecords.length === 0" class="empty-state">
          <p>분석 기록이 없습니다.</p>
        </div>
        <div v-else class="history-list">
          <div
            v-for="record in filteredRecords"
            :key="record.id"
            class="history-item"
          >
            <div class="item-header">
              <div class="item-score" :style="{ color: getScoreColor(record.data?.reliability_score || 0) }">
                {{ record.data?.reliability_score || 0 }}점
              </div>
              <div class="item-meta">
                <span class="item-date">{{ formatDate(record.analyzedAt) }}</span>
                <span class="item-count">분석 {{ record.analyzeCount || 1 }}회</span>
              </div>
            </div>
            <div class="item-content">
              <p class="item-url">{{ record.url }}</p>
              <div class="item-details">
                <span v-if="record.data?.metadata?.publisher" class="item-publisher">
                  📰 {{ record.data.metadata.publisher }}
                </span>
                <span :class="['item-status', record.data?.is_fake ? 'fake' : 'real']">
                  {{ record.data?.is_fake ? '⚠️ 의심' : '✓ 신뢰' }}
                </span>
              </div>
            </div>
            <button @click="deleteRecord(record.id)" class="delete-btn">삭제</button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { historyService } from '../services/historyService.js'

export default {
  name: 'History',
  data() {
    return {
      records: [],
      filteredRecords: [],
      searchQuery: '',
      sortBy: 'date',
      sortOrder: 'desc',
      statistics: {
        total: 0,
        avgScore: 0,
        fakeCount: 0,
        realCount: 0
      }
    }
  },
  mounted() {
    this.loadRecords()
    this.updateStatistics()
  },
  methods: {
    /**
     * 기록 불러오기
     * 정렬 알고리즘을 사용하여 정렬된 기록 가져오기
     */
    loadRecords() {
      // 정렬 알고리즘 사용 (퀵 정렬)
      this.records = historyService.getSortedRecords(this.sortBy, this.sortOrder)
      this.filteredRecords = this.records
    },

    /**
     * 검색 처리
     * 선형 탐색 알고리즘 사용
     */
    handleSearch() {
      if (!this.searchQuery.trim()) {
        this.filteredRecords = this.records
        return
      }

      // 선형 탐색 알고리즘 사용 (O(n))
      this.filteredRecords = historyService.searchRecords(this.searchQuery, 'all')
      
      // 검색 결과도 정렬 적용
      this.applySort()
    },

    /**
     * 정렬 처리
     * 퀵 정렬 알고리즘 사용
     */
    handleSort() {
      this.applySort()
    },

    /**
     * 정렬 적용
     * 퀵 정렬 알고리즘 사용 (O(n log n))
     */
    applySort() {
      if (this.searchQuery.trim()) {
        // 검색 결과가 있으면 검색 결과를 정렬
        const allRecords = historyService.getAllRecords()
        const sorted = historyService.getSortedRecords(this.sortBy, this.sortOrder)
        // 검색어로 필터링
        this.filteredRecords = sorted.filter(record => {
          const lowerQuery = this.searchQuery.toLowerCase()
          return (record.url && record.url.toLowerCase().includes(lowerQuery)) ||
                 (record.data?.metadata?.publisher && 
                  record.data.metadata.publisher.toLowerCase().includes(lowerQuery))
        })
      } else {
        // 검색어가 없으면 전체 기록 정렬
        this.records = historyService.getSortedRecords(this.sortBy, this.sortOrder)
        this.filteredRecords = this.records
      }
    },

    /**
     * 기록 삭제
     */
    deleteRecord(id) {
      if (confirm('이 기록을 삭제하시겠습니까?')) {
        historyService.deleteRecord(id)
        this.loadRecords()
        this.updateStatistics()
      }
    },

    /**
     * 전체 삭제
     */
    clearAll() {
      if (confirm('모든 기록을 삭제하시겠습니까?')) {
        historyService.clearAllRecords()
        this.loadRecords()
        this.updateStatistics()
      }
    },

    /**
     * 통계 업데이트
     */
    updateStatistics() {
      this.statistics = historyService.getStatistics()
    },

    /**
     * 점수에 따른 색상 반환
     */
    getScoreColor(score) {
      if (score >= 70) return '#10b981' // 초록
      if (score >= 40) return '#f59e0b' // 노랑
      return '#ef4444' // 빨강
    },

    /**
     * 날짜 포맷팅
     */
    formatDate(dateString) {
      if (!dateString) return '날짜 없음'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('ko-KR', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return dateString
      }
    }
  }
}
</script>

<style scoped>
.history {
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

.nav-link.active {
  color: var(--black);
  background: var(--gray-lightest);
}

.nav-link.active::after {
  transform: translateX(-50%) scaleX(1);
}

.nav-link:hover {
  color: var(--black);
  background: var(--gray-lightest);
}

.nav-link:hover::after {
  transform: translateX(-50%) scaleX(1);
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  position: relative;
  z-index: 1;
}

.statistics-section {
  margin-bottom: 3rem;
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

.statistics-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 1.5rem;
  letter-spacing: -0.5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--gray-lighter);
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: var(--gray-light);
}

.stat-icon {
  font-size: 2.5rem;
  transition: transform var(--transition-fast);
}

.stat-card:hover .stat-icon {
  transform: scale(1.1);
}

.stat-content h3 {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--black);
}

.controls-section {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--gray-lighter);
  box-shadow: var(--shadow-md);
  margin-bottom: 2.5rem;
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

.search-box {
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 1rem 1.5rem;
  border: 1px solid var(--gray-lighter);
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: all var(--transition-normal);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-input:focus {
  border-color: var(--black);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
  background: var(--bg-secondary);
  transform: translateY(-1px);
}

.sort-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.sort-select {
  padding: 1rem 1.25rem;
  border: 1px solid var(--gray-lighter);
  border-radius: 12px;
  font-size: 0.95rem;
  outline: none;
  cursor: pointer;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  transition: all var(--transition-normal);
  font-weight: 500;
}

.sort-select:focus {
  border-color: var(--black);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.sort-select:hover {
  border-color: var(--gray-light);
  background: var(--bg-secondary);
}

.clear-btn {
  padding: 1rem 1.75rem;
  background: var(--error);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.clear-btn:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.history-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--black);
  margin-bottom: 1.5rem;
  letter-spacing: -0.5px;
  animation: fadeInUp 0.6s ease-out 0.2s backwards;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  color: var(--text-secondary);
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--gray-lighter);
  font-size: 1.1rem;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  animation: fadeInUp 0.6s ease-out 0.3s backwards;
}

.history-item {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 16px;
  border: 1px solid var(--gray-lighter);
  box-shadow: var(--shadow-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  transition: all var(--transition-normal);
}

.history-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-hover);
  border-color: var(--gray-light);
}

.item-header {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 160px;
}

.item-score {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--black);
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item-url {
  color: var(--text-primary);
  font-weight: 600;
  word-break: break-all;
  line-height: 1.5;
}

.item-details {
  display: flex;
  gap: 1.25rem;
  font-size: 0.95rem;
  flex-wrap: wrap;
}

.item-publisher {
  color: var(--text-secondary);
  font-weight: 500;
}

.item-status {
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.item-status.real {
  color: var(--success);
  background: rgba(16, 185, 129, 0.1);
}

.item-status.fake {
  color: var(--error);
  background: rgba(239, 68, 68, 0.1);
}

.delete-btn {
  padding: 0.75rem 1.25rem;
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--gray-lighter);
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  white-space: nowrap;
}

.delete-btn:hover {
  background: var(--error);
  color: white;
  border-color: var(--error);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

@media (max-width: 768px) {
  .content {
    padding: 2rem 1.5rem;
  }

  .history-item {
    flex-direction: column;
    align-items: flex-start;
    padding: 1.5rem;
  }

  .controls-section {
    flex-direction: column;
    gap: 1rem;
    padding: 1.5rem;
  }

  .search-box {
    width: 100%;
  }

  .sort-controls {
    width: 100%;
    flex-wrap: wrap;
  }

  .sort-select {
    flex: 1;
    min-width: 120px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .statistics-section h2,
  .history-section h2 {
    font-size: 1.5rem;
  }

  .delete-btn {
    width: 100%;
  }
}
</style>

