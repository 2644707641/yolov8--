import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('请在.env文件中配置Supabase的URL和密钥')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
