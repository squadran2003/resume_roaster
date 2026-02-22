import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analysisApi } from '../api/analysis'

const POLL_INTERVAL_MS = 3000
const MAX_POLL_ATTEMPTS = 60

export const useAnalysisStore = defineStore('analysis', () => {
  const current = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function submitAnalysis(resumeId, jobDescription, jobTitle, company) {
    loading.value = true
    error.value = null
    current.value = null
    try {
      const { data } = await analysisApi.create({
        resume_id: resumeId,
        job_description: jobDescription,
        job_title: jobTitle,
        company,
      })
      current.value = data
      return data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to submit analysis.'
      throw e
    } finally {
      loading.value = false
    }
  }

  function pollAnalysis(id) {
    let attempts = 0
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        attempts++
        try {
          const { data } = await analysisApi.get(id)
          current.value = data
          if (data.status === 'done' || data.status === 'failed') {
            clearInterval(interval)
            resolve(data)
          } else if (attempts >= MAX_POLL_ATTEMPTS) {
            clearInterval(interval)
            reject(new Error('Analysis timed out.'))
          }
        } catch (e) {
          clearInterval(interval)
          reject(e)
        }
      }, POLL_INTERVAL_MS)
    })
  }

  return { current, loading, error, submitAnalysis, pollAnalysis }
})
