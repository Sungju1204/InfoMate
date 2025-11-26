import { createClient } from '@supabase/supabase-js'

// .env 파일에서 키를 가져옵니다.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('⚠️ .env 파일 설정을 확인해주세요!')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
