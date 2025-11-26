<template>
  <div class="history">
    <header class="header">
      <div class="header-content">
        <div class="logo" @click="goHome">
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
      <section class="statistics-section">
        <h2>나의 분석 통계</h2>
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
              <p class="stat-value">{{ statistics.avgScore }}점</p>
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
        
        <div v-if="mergedRecords.length > 0" class="chart-grid">
          <div class="chart-card">
            <h3>신뢰도 분포</h3>
            <div class="chart-container">
              <BarChart :data="scoreDistributionChartData" :options="chartOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>신뢰 vs. 의심 비율</h3>
            <div class="chart-container">
              <PieChart :data="fakeRealRatioChartData" :options="chartOptions" />
            </div>
          </div>
        </div>
      </section>

      <section class="controls-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="URL 또는 언론사명으로 검색..." 
            class="search-input"
          />
        </div>
        <div class="sort-controls">
          <select v-model="sortBy" class="sort-select">
            <option value="date">최신순</option>
            <option value="score">신뢰도순</option>
            <option value="rating">내 별점순</option>
          </select>
          <select v-model="sortOrder" class="sort-select">
            <option value="desc">내림차순</option>
            <option value="asc">오름차순</option>
          </select>
          <button @click="clearAll" class="clear-btn">전체 삭제</button>
        </div>
      </section>

      <section class="history-section">
        <div class="section-header">
          <h2>
            분석 및 평가 기록 
            <span class="count-badge">({{ processedRecords.length }}개)</span>
          </h2>
          <button @click="loadAndMergeRecords" class="refresh-btn" :disabled="isLoading">
            {{ isLoading ? '로딩 중...' : '새로고침' }}
          </button>
        </div>

        <div v-if="processedRecords.length === 0" class="empty-state">
          <p v-if="searchQuery">검색 결과가 없습니다.</p>
          <p v-else>아직 기록이 없습니다.</p>
        </div>

        <div v-else class="history-list">
          <div v-for="record in processedRecords" :key="record.id" class="history-item">
            
            <div class="item-header">
              <div class="item-score" :style="{ color: getScoreColor(record.data?.reliability_score || 0) }">
                {{ record.data?.reliability_score || 0 }}점
              </div>
              <div class="item-meta">
                <span class="item-date">{{ formatDate(record.analyzedAt) }}</span>
                <div v-if="record.myEvaluation" class="my-rating-badge">
                  내 평가: {{ getStarString(record.myEvaluation.rating) }}
                </div>
              </div>
            </div>

            <div class="item-content">
              <a :href="record.url" target="_blank" class="item-url">{{ record.url }}</a>
              
              <div class="item-details">
                <span v-if="record.data?.metadata?.publisher" class="item-publisher">
                  📰 {{ record.data.metadata.publisher }}
                </span>
                <span :class="['item-status', record.data?.is_fake ? 'fake' : 'real']">
                  {{ record.data?.is_fake ? '⚠️ 의심됨' : '✓ 신뢰함' }}
                </span>
              </div>

              <div v-if="record.myEvaluation?.feedback" class="my-feedback">
                💬 {{ record.myEvaluation.feedback }}
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
import { evaluationService } from '../services/evaluationService.js'

// ⭐ Chart.js 관련 import
import { Bar as BarChart, Pie as PieChart } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js'

// Chart.js 등록
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

export default {
  name: 'History',
  components: { BarChart, PieChart },
  data() {
    return {
      mergedRecords: [],
      statistics: { total: 0, avgScore: 0, fakeCount: 0, realCount: 0 },
      isLoading: false,
      
      searchQuery: '',
      sortBy: 'date',
      sortOrder: 'desc',

      // ⭐ 차트 옵션 (중요: 크기 자동 조절 해제)
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false, // 이게 있어야 높이 조절이 됩니다!
        plugins: {
          legend: { position: 'bottom' },
          title: { display: false }
        }
      }
    }
  },
  mounted() {
    this.loadAndMergeRecords()
  },
  computed: {
    // 1. 목록 가공 로직
    processedRecords() {
      let result = [...this.mergedRecords]
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(record => 
          (record.url && record.url.toLowerCase().includes(query)) ||
          (record.data?.metadata?.publisher && record.data.metadata.publisher.toLowerCase().includes(query)) ||
          (record.myEvaluation?.feedback && record.myEvaluation.feedback.toLowerCase().includes(query))
        )
      }
      
      result.sort((a, b) => {
        let valA, valB
        if (this.sortBy === 'date') {
          valA = new Date(a.analyzedAt).getTime()
          valB = new Date(b.analyzedAt).getTime()
        } else if (this.sortBy === 'score') {
          valA = a.data?.reliability_score || 0
          valB = b.data?.reliability_score || 0
        } else if (this.sortBy === 'rating') {
          valA = a.myEvaluation?.rating || -1
          valB = b.myEvaluation?.rating || -1
        }
        if (this.sortOrder === 'asc') return valA - valB
        return valB - valA
      })
      return result
    },

    // 2. 신뢰도 분포 차트 데이터
    scoreDistributionChartData() {
      const scores = this.mergedRecords.map(r => r.data?.reliability_score || 0)
      let low = 0; let mid = 0; let high = 0;

      scores.forEach(score => {
        if (score >= 70) high++
        else if (score >= 40) mid++
        else low++
      })

      return {
        labels: ['위험 (0~39점)', '주의 (40~69점)', '안전 (70~100점)'],
        datasets: [
          {
            label: '분석 건수',
            backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
            data: [low, mid, high]
          }
        ]
      }
    },

    // 3. 신뢰 vs 의심 비율 차트 데이터
    fakeRealRatioChartData() {
      return {
        labels: ['신뢰 가능 (✓)', '의심 (⚠️)'],
        datasets: [
          {
            backgroundColor: ['#10b981', '#ef4444'],
            data: [this.statistics.realCount, this.statistics.fakeCount]
          }
        ]
      }
    }
  }, // computed 닫기 (여기가 중요!)

  methods: {
    // 홈 이동 함수 (안전장치)
    goHome() {
      this.$router.push('/').catch(err => {})
    },

    async loadAndMergeRecords() {
      this.isLoading = true
      try {
        const localHistory = historyService.getAllRecords()
        let remoteEvaluations = []
        try {
          remoteEvaluations = await evaluationService.getAllEvaluations()
        } catch (e) {
          console.error('Supabase 연결 실패:', e)
        }

        this.mergedRecords = localHistory.map(localItem => {
          const matchingEval = remoteEvaluations.find(r => r.url === localItem.url)
          return {
            ...localItem,
            myEvaluation: matchingEval || null
          }
        })

        this.statistics = historyService.getStatistics(this.mergedRecords)

      } catch (error) {
        console.error(error)
      } finally {
        this.isLoading = false
      }
    },

    deleteRecord(id) {
      if (confirm('이 기록을 삭제하시겠습니까?')) {
        historyService.deleteRecord(id)
        this.loadAndMergeRecords()
      }
    },

    clearAll() {
      if (confirm('정말로 모든 분석 기록을 삭제하시겠습니까?')) {
        historyService.clearAllRecords()
        this.loadAndMergeRecords()
      }
    },

    getScoreColor(score) {
      if (score >= 70) return '#10b981'
      if (score >= 40) return '#f59e0b'
      return '#ef4444'
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('ko-KR')
    },

    getStarString(rating) {
      return '★'.repeat(rating) + '☆'.repeat(5 - rating)
    }
  }
}
</script>

<style scoped>
/* 기존 스타일 유지 */
.history { min-height: 100vh; background: #f8fafc; }
.header { background: white; padding: 1rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; padding: 0 2rem; align-items: center; }
.logo { display: flex; gap: 0.5rem; align-items: center; cursor: pointer; }
.logo-icon { background: #3b82f6; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
.logo-text { font-size: 1.5rem; font-weight: bold; color: #1f2937; }
.nav { display: flex; gap: 2rem; }
.nav-link { color: #6b7280; text-decoration: none; font-weight: 500; }
.nav-link.active { color: #3b82f6; }
.content { max-width: 1200px; margin: 0 auto; padding: 2rem; }

.statistics-section { margin-bottom: 2rem; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; gap: 1rem; align-items: center; }
.stat-icon { font-size: 2rem; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #1f2937; }

/* ⭐ 차트 관련 스타일 (높이 지정 필수!) */
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
.chart-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.chart-card h3 { margin-top: 0; margin-bottom: 1rem; font-size: 1.1rem; color: #374151; border-bottom: 1px solid #f3f4f6; padding-bottom: 0.5rem; }
.chart-container { 
  position: relative; 
  height: 250px; /* ⭐ 차트 높이 고정 (이게 없으면 차트가 안 보임) */
  width: 100%; 
}

/* 컨트롤 섹션 */
.controls-section { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 2rem; display: flex; gap: 1rem; flex-wrap: wrap; align-items: center; }
.search-box { flex: 1; min-width: 200px; }
.search-input { width: 100%; padding: 0.75rem 1rem; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 1rem; outline: none; }
.sort-controls { display: flex; gap: 0.5rem; align-items: center; }
.sort-select { padding: 0.75rem 1rem; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 0.9rem; outline: none; cursor: pointer; }
.clear-btn { padding: 0.75rem 1.5rem; background: #ef4444; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
.count-badge { font-size: 1rem; color: #6b7280; font-weight: normal; margin-left: 0.5rem; }

/* 목록 스타일 */
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.refresh-btn { background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.history-list { display: flex; flex-direction: column; gap: 1rem; }
.empty-state { text-align: center; padding: 4rem 2rem; color: #6b7280; }
.history-item { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.item-header { display: flex; flex-direction: column; align-items: center; min-width: 120px; text-align: center; }
.item-score { font-size: 1.5rem; font-weight: bold; }
.item-meta { font-size: 0.85rem; color: #6b7280; display: flex; flex-direction: column; gap: 0.2rem; }
.item-content { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
.item-url { color: #1f2937; font-weight: 500; word-break: break-all; text-decoration: none; }
.item-url:hover { text-decoration: underline; color: #2563eb; }
.item-details { display: flex; gap: 1rem; font-size: 0.9rem; }
.item-status.real { color: #10b981; }
.item-status.fake { color: #ef4444; }
.my-rating-badge { color: #d97706; background: #fffbeb; padding: 2px 6px; border-radius: 4px; border: 1px solid #fcd34d; font-size: 0.8rem; margin-top: 5px; }
.my-feedback { background: #f3f4f6; padding: 0.5rem; border-radius: 6px; font-size: 0.9rem; color: #4b5563; margin-top: 0.5rem; }
.delete-btn { background: #fee2e2; color: #dc2626; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
</style>