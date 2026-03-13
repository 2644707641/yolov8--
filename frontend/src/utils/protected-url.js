import { supabase } from '../config/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const getAccessToken = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  if (error || !session?.access_token) {
    throw new Error('未检测到有效的登录会话，请重新登录后重试')
  }
  return session.access_token
}

export const buildProtectedApiUrl = async (pathOrUrl) => {
  if (!pathOrUrl) {
    return pathOrUrl
  }

  const apiOrigin = new URL(API_URL).origin
  const resolvedUrl = /^https?:\/\//.test(pathOrUrl)
    ? new URL(pathOrUrl)
    : new URL(pathOrUrl, API_URL)

  if (resolvedUrl.origin !== apiOrigin) {
    return pathOrUrl
  }

  resolvedUrl.searchParams.set('token', await getAccessToken())
  return resolvedUrl.toString()
}
