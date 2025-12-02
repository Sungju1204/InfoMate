/**
 * 평가 및 신고 관리 서비스
 * 해시 테이블을 사용한 평가/신고 데이터 관리
 */

import { HashTable } from '../utils/dataStructures.js'

// 로컬 스토리지 키
const EVALUATION_STORAGE_KEY = 'infomate_evaluations'
const REPORT_STORAGE_KEY = 'infomate_reports'

/**
 * 평가 및 신고 관리 클래스
 */
class EvaluationService {
  constructor() {
    // 해시 테이블: URL을 키로 사용하여 빠른 조회
    // 시간 복잡도: O(1) 조회
    this.evaluationHashTable = new HashTable(100)
    this.reportHashTable = new HashTable(100)
    
    // 평가 및 신고 배열
    this.evaluations = []
    this.reports = []
    
    // 초기화: 로컬 스토리지에서 데이터 불러오기
    this.loadEvaluations()
    this.loadReports()
  }

  /**
   * 평가 데이터 불러오기
   * 시간 복잡도: O(n) - n: 평가 개수
   */
  loadEvaluations() {
    try {
      const stored = localStorage.getItem(EVALUATION_STORAGE_KEY)
      if (stored) {
        this.evaluations = JSON.parse(stored)
        
        // 해시 테이블에 URL 등록
        for (const evaluation of this.evaluations) {
          if (evaluation.url) {
            this.evaluationHashTable.set(evaluation.url, evaluation)
          }
        }
      }
    } catch (error) {
      console.error('평가 데이터 불러오기 실패:', error)
      this.evaluations = []
    }
  }

  /**
   * 신고 데이터 불러오기
   * 시간 복잡도: O(n) - n: 신고 개수
   */
  loadReports() {
    try {
      const stored = localStorage.getItem(REPORT_STORAGE_KEY)
      if (stored) {
        this.reports = JSON.parse(stored)
        
        // 해시 테이블에 URL 등록
        for (const report of this.reports) {
          if (report.url) {
            this.reportHashTable.set(report.url, report)
          }
        }
      }
    } catch (error) {
      console.error('신고 데이터 불러오기 실패:', error)
      this.reports = []
    }
  }

  /**
   * 평가 데이터 저장
   * 시간 복잡도: O(1)
   */
  saveEvaluations() {
    try {
      localStorage.setItem(EVALUATION_STORAGE_KEY, JSON.stringify(this.evaluations))
    } catch (error) {
      console.error('평가 데이터 저장 실패:', error)
    }
  }

  /**
   * 신고 데이터 저장
   * 시간 복잡도: O(1)
   */
  saveReports() {
    try {
      localStorage.setItem(REPORT_STORAGE_KEY, JSON.stringify(this.reports))
    } catch (error) {
      console.error('신고 데이터 저장 실패:', error)
    }
  }

  /**
   * 평가 추가 또는 업데이트
   * 해시 테이블을 사용하여 중복 검사 (O(1))
   * 
   * @param {Object} evaluationData - 평가 데이터
   * @param {string} evaluationData.url - 뉴스 URL
   * @param {number} evaluationData.rating - 평가 점수 (1-5)
   * @param {string} evaluationData.feedback - 피드백 텍스트
   * @returns {Object} 저장된 평가 데이터
   */
  addEvaluation(evaluationData) {
    const { url, rating, feedback } = evaluationData
    
    // 해시 테이블로 중복 검사 (O(1))
    const existingEvaluation = this.evaluationHashTable.get(url)
    
    if (existingEvaluation) {
      // 기존 평가 업데이트
      existingEvaluation.rating = rating
      existingEvaluation.feedback = feedback
      existingEvaluation.updatedAt = new Date().toISOString()
      
      // 배열에서도 업데이트
      const index = this.evaluations.findIndex(e => e.url === url)
      if (index !== -1) {
        this.evaluations[index] = existingEvaluation
      }
    } else {
      // 새 평가 추가
      const newEvaluation = {
        id: Date.now().toString(),
        url: url,
        rating: rating,
        feedback: feedback || '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      // 해시 테이블에 추가 (O(1))
      this.evaluationHashTable.set(url, newEvaluation)
      this.evaluations.push(newEvaluation)
    }
    
    this.saveEvaluations()
    return this.evaluationHashTable.get(url)
  }

  /**
   * 평가 조회
   * 해시 테이블 사용 - O(1)
   * 
   * @param {string} url - 뉴스 URL
   * @returns {Object|null} 평가 데이터
   */
  getEvaluation(url) {
    return this.evaluationHashTable.get(url) || null
  }

  /**
   * 신고 추가
   * 
   * @param {Object} reportData - 신고 데이터
   * @param {string} reportData.url - 뉴스 URL
   * @param {string} reportData.reason - 신고 사유
   * @param {string} reportData.description - 상세 설명
   * @returns {Object} 저장된 신고 데이터
   */
  addReport(reportData) {
    const { url, reason, description } = reportData
    
    // 중복 신고 방지 (같은 URL에 대한 신고가 이미 있는지 확인)
    const existingReport = this.reportHashTable.get(url)
    
    if (existingReport) {
      // 이미 신고된 경우 업데이트
      existingReport.reason = reason
      existingReport.description = description
      existingReport.updatedAt = new Date().toISOString()
      existingReport.count = (existingReport.count || 1) + 1
      
      return existingReport
    }
    
    // 새 신고 추가
    const newReport = {
      id: Date.now().toString(),
      url: url,
      reason: reason,
      description: description || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      count: 1
    }
    
    // 해시 테이블에 추가 (O(1))
    this.reportHashTable.set(url, newReport)
    this.reports.push(newReport)
    
    this.saveReports()
    return newReport
  }

  /**
   * 신고 조회
   * 해시 테이블 사용 - O(1)
   * 
   * @param {string} url - 뉴스 URL
   * @returns {Object|null} 신고 데이터
   */
  getReport(url) {
    return this.reportHashTable.get(url) || null
  }

  /**
   * 모든 평가 가져오기
   * 
   * @returns {Array} 평가 배열
   */
  getAllEvaluations() {
    return this.evaluations
  }

  /**
   * 모든 신고 가져오기
   * 
   * @returns {Array} 신고 배열
   */
  getAllReports() {
    return this.reports
  }
}

// 싱글톤 인스턴스 export
export const evaluationService = new EvaluationService()

