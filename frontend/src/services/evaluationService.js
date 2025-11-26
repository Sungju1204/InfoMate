import { supabase } from '../utils/supabase'

export const evaluationService = {
  // 1. 평가 저장 (Supabase)
  async addEvaluation(data) {
    // 통계를 위해 신뢰도 점수(reliability_score)와 가짜 여부(is_fake)도 같이 저장합니다.
    const { error } = await supabase
      .from('evaluations')
      .insert([
        {
          url: data.url,
          rating: data.rating,
          feedback: data.feedback || '',
          reliability_score: data.reliability_score || 0,
          is_fake: data.is_fake || false
        }
      ])

    if (error) throw error
    return { success: true }
  },

  // 2. 신고 저장 (Supabase)
  async addReport(data) {
    const { error } = await supabase
      .from('reports')
      .insert([
        {
          url: data.url,
          reason: data.reason,
          description: data.description || ''
        }
      ])

    if (error) throw error
    return { success: true }
  },

  // 3. 내 모든 평가 가져오기 (기록 페이지용)
  async getAllEvaluations() {
    const { data, error } = await supabase
      .from('evaluations')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error(error)
      return []
    }
    return data || []
  }
}
