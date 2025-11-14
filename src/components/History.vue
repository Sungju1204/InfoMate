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

.nav-link.active {
  color: #3b82f6;
}

.nav-link:hover {
  color: #3b82f6;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.statistics-section {
  margin-bottom: 2rem;
}

.statistics-section h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content h3 {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.controls-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
}

.search-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.sort-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.sort-select {
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
}

.sort-select:focus {
  border-color: #3b82f6;
}

.clear-btn {
  padding: 0.75rem 1.5rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.clear-btn:hover {
  background: #dc2626;
}

.history-section h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.item-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.item-score {
  font-size: 1.5rem;
  font-weight: bold;
}

.item-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #6b7280;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-url {
  color: #1f2937;
  font-weight: 500;
  word-break: break-all;
}

.item-details {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.item-publisher {
  color: #6b7280;
}

.item-status {
  font-weight: 600;
}

.item-status.real {
  color: #10b981;
}

.item-status.fake {
  color: #ef4444;
}

.delete-btn {
  padding: 0.5rem 1rem;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.delete-btn:hover {
  background: #fecaca;
}

@media (max-width: 768px) {
  .history-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls-section {
    flex-direction: column;
  }

  .search-box {
    width: 100%;
  }
}
</style>

