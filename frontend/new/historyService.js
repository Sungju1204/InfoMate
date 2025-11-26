/**
 * 분석 기록 관리 서비스
 * 해시 테이블과 정렬 알고리즘을 사용한 기록 관리
 */

import { HashTable } from '../utils/dataStructures.js'
import { quickSort, mergeSort, binarySearch, linearSearch } from '../utils/algorithms.js'

// 로컬 스토리지 키
const STORAGE_KEY = 'infomate_analysis_history'

/**
 * 분석 기록 관리 클래스
 */
class HistoryService {
  constructor() {
    // 해시 테이블: URL을 키로 사용하여 중복 검사 및 빠른 조회
    // 시간 복잡도: O(1) 조회
    this.urlHashTable = new HashTable(100)
    
    // 분석 기록 배열
    this.history = []
    
    // 초기화: 로컬 스토리지에서 기록 불러오기
    this.loadHistory()
  }

  /**
   * 로컬 스토리지에서 기록 불러오기
   * 시간 복잡도: O(n) - n: 기록 개수
   */
  loadHistory() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        this.history = JSON.parse(stored)
        
        // 해시 테이블에 URL 등록 (중복 검사용)
        for (const record of this.history) {
          if (record.url) {
            this.urlHashTable.set(record.url, record)
          }
        }
      }
    } catch (error) {
      console.error('기록 불러오기 실패:', error)
      this.history = []
    }
  }

  /**
   * 로컬 스토리지에 기록 저장
   * 시간 복잡도: O(1)
   */
  saveHistory() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.history))
    } catch (error) {
      console.error('기록 저장 실패:', error)
    }
  }

  /**
   * 분석 기록 추가
   * 해시 테이블을 사용하여 중복 검사 (O(1))
   * 
   * @param {Object} analysisResult - 분석 결과
   * @param {string} analysisResult.url - 뉴스 URL
   * @param {Object} analysisResult.data - 분석 데이터
   * @returns {Object} 저장된 기록
   */
  addRecord(analysisResult) {
    const { url, data } = analysisResult
    
    // 해시 테이블로 중복 검사 (O(1))
    const existingRecord = this.urlHashTable.get(url)
    
    if (existingRecord) {
      // 기존 기록 업데이트
      existingRecord.data = data
      existingRecord.analyzedAt = new Date().toISOString()
      existingRecord.analyzeCount = (existingRecord.analyzeCount || 1) + 1
      
      // 배열에서도 업데이트
      const index = this.history.findIndex(r => r.url === url)
      if (index !== -1) {
        this.history[index] = existingRecord
      }
    } else {
      // 새 기록 추가
      const newRecord = {
        id: Date.now().toString(),
        url: url,
        data: data,
        analyzedAt: new Date().toISOString(),
        analyzeCount: 1
      }
      
      // 해시 테이블에 추가 (O(1))
      this.urlHashTable.set(url, newRecord)
      // 배열에 추가
      this.history.push(newRecord)
    }
    
    // 로컬 스토리지에 저장
    this.saveHistory()
    
    return existingRecord || this.history[this.history.length - 1]
  }

  /**
   * 모든 기록 조회
   * 
   * @returns {Array} 기록 배열
   */
  getAllRecords() {
    return this.history
  }

  /**
   * 기록 정렬 (퀵 정렬 사용)
   * 시간 복잡도: O(n log n)
   * 
   * @param {string} sortBy - 정렬 기준 ('date' | 'score' | 'count')
   * @param {string} order - 정렬 순서 ('asc' | 'desc')
   * @returns {Array} 정렬된 기록 배열
   */
  getSortedRecords(sortBy = 'date', order = 'desc') {
    // 원본 배열 복사 (원본 보존)
    const sorted = [...this.history]
    
    // 정렬 기준에 따른 비교 함수 정의
    let compareFn
    
    switch (sortBy) {
      case 'date':
        // 날짜 기준 정렬
        compareFn = (a, b) => {
          const dateA = new Date(a.analyzedAt).getTime()
          const dateB = new Date(b.analyzedAt).getTime()
          return order === 'asc' ? dateA - dateB : dateB - dateA
        }
        break
        
      case 'score':
        // 신뢰도 점수 기준 정렬
        compareFn = (a, b) => {
          const scoreA = a.data?.reliability_score || 0
          const scoreB = b.data?.reliability_score || 0
          return order === 'asc' ? scoreA - scoreB : scoreB - scoreA
        }
        break
        
      case 'count':
        // 분석 횟수 기준 정렬
        compareFn = (a, b) => {
          const countA = a.analyzeCount || 0
          const countB = b.analyzeCount || 0
          return order === 'asc' ? countA - countB : countB - countA
        }
        break
        
      default:
        // 기본: 날짜 기준
        compareFn = (a, b) => {
          const dateA = new Date(a.analyzedAt).getTime()
          const dateB = new Date(b.analyzedAt).getTime()
          return order === 'asc' ? dateA - dateB : dateB - dateA
        }
    }
    
    // 퀵 정렬 사용 (평균 O(n log n))
    return quickSort(sorted, compareFn)
  }

  /**
   * 기록 검색 (이진 탐색 - 정렬된 배열에서)
   * 시간 복잡도: O(log n)
   * 
   * @param {string} query - 검색어
   * @param {string} searchIn - 검색 대상 ('url' | 'publisher' | 'all')
   * @returns {Array} 검색 결과 배열
   */
  searchRecords(query, searchIn = 'all') {
    if (!query || query.trim() === '') {
      return this.history
    }
    
    const lowerQuery = query.toLowerCase()
    const results = []
    
    // 선형 탐색 사용 (정렬되지 않은 필드 검색)
    // 시간 복잡도: O(n)
    for (const record of this.history) {
      let match = false
      
      switch (searchIn) {
        case 'url':
          // URL에서 검색
          match = record.url && record.url.toLowerCase().includes(lowerQuery)
          break
          
        case 'publisher':
          // 언론사에서 검색
          match = record.data?.metadata?.publisher && 
                  record.data.metadata.publisher.toLowerCase().includes(lowerQuery)
          break
          
        case 'all':
        default:
          // 모든 필드에서 검색
          match = (record.url && record.url.toLowerCase().includes(lowerQuery)) ||
                  (record.data?.metadata?.publisher && 
                   record.data.metadata.publisher.toLowerCase().includes(lowerQuery))
          break
      }
      
      if (match) {
        results.push(record)
      }
    }
    
    return results
  }

  /**
   * URL로 기록 조회 (해시 테이블 사용)
   * 시간 복잡도: O(1) - 해시 테이블의 장점
   * 
   * @param {string} url - 조회할 URL
   * @returns {Object|null} 기록 또는 null
   */
  getRecordByURL(url) {
    return this.urlHashTable.get(url) || null
  }

  /**
   * 기록 삭제
   * 
   * @param {string} id - 삭제할 기록 ID
   * @returns {boolean} 삭제 성공 여부
   */
  deleteRecord(id) {
    const index = this.history.findIndex(r => r.id === id)
    
    if (index !== -1) {
      const record = this.history[index]
      
      // 해시 테이블에서도 삭제
      if (record.url) {
        this.urlHashTable.delete(record.url)
      }
      
      // 배열에서 삭제
      this.history.splice(index, 1)
      
      // 로컬 스토리지에 저장
      this.saveHistory()
      
      return true
    }
    
    return false
  }

  /**
   * 모든 기록 삭제
   */
  clearAllRecords() {
    this.history = []
    this.urlHashTable = new HashTable(100)
    this.saveHistory()
  }

  /**
   * 기록 통계
   * 
   * @returns {Object} 통계 정보
   */
  getStatistics() {
    const total = this.history.length
    const avgScore = this.history.length > 0
      ? this.history.reduce((sum, r) => sum + (r.data?.reliability_score || 0), 0) / total
      : 0
    
    const fakeCount = this.history.filter(r => r.data?.is_fake === true).length
    const realCount = total - fakeCount
    
    return {
      total,
      avgScore: Math.round(avgScore * 10) / 10,
      fakeCount,
      realCount,
      fakeRatio: total > 0 ? Math.round((fakeCount / total) * 100) : 0
    }
  }
}

// 싱글톤 인스턴스 생성 및 export
export const historyService = new HistoryService()

