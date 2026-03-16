import { defineStore } from 'pinia'
import { ref } from 'vue'
import { analysisApi } from '../api/analysis'

const POLL_INTERVAL_MS = 3000
const MAX_POLL_ATTEMPTS = 60

export const useAnalysisStore = defineStore('analysis', () => {
  const current = ref(null)
  const analyses = ref([])
  const loading = ref(false)
  const error = ref(null)
  const pagination = ref({ count: 0, next: null, previous: null })

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

  async function fetchAnalyses(page = 1) {
    loading.value = true
    error.value = null
    try {
      const { data } = await analysisApi.list(page)
      analyses.value = data.results
      pagination.value = { count: data.count, next: data.next, previous: data.previous }
    } catch (e) {
      error.value = 'Failed to load analysis history.'
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

  function pollField(id, field, prevErrorMessage = '') {
    let attempts = 0
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        attempts++
        try {
          const { data } = await analysisApi.get(id)
          current.value = data
          const val = data[field]
          if ((Array.isArray(val) && val.length > 0) || (typeof val === 'string' && val.length > 0)) {
            clearInterval(interval)
            resolve(data)
          } else if (data.error_message && data.error_message !== prevErrorMessage) {
            clearInterval(interval)
            reject(new Error(data.error_message))
          } else if (attempts >= MAX_POLL_ATTEMPTS) {
            clearInterval(interval)
            reject(new Error('Generation timed out.'))
          }
        } catch (e) {
          clearInterval(interval)
          reject(e)
        }
      }, POLL_INTERVAL_MS)
    })
  }

  async function deleteAnalysis(id) {
    await analysisApi.delete(id)
    analyses.value = analyses.value.filter(a => a.id !== id)
  }

  return { current, analyses, loading, error, pagination, submitAnalysis, fetchAnalyses, pollAnalysis, pollField, deleteAnalysis }
})
