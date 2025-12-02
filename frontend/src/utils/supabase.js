import { createClient } from '@supabase/supabase-js'

// 👇 환경 변수 싹 무시하고, 직접 주소와 키를 박아넣습니다.
const supabaseUrl = "https://kjjokcjnqfppyhvdqrdd.supabase.co"
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtqam9rY2pucWZwcHlodmRxcmRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzYwMTgsImV4cCI6MjA3OTY1MjAxOH0.4p1S4OQmOZ4QtpbwAnTYYVV8wWwXLq5GxMi2TjpgNDY"

// 클라이언트 생성
export const supabase = createClient(supabaseUrl, supabaseKey)