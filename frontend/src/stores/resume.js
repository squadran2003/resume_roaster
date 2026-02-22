import { defineStore } from 'pinia'
import { ref } from 'vue'
import { resumeApi } from '../api/resumes'

export const useResumeStore = defineStore('resume', () => {
  const resumes = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchResumes() {
    loading.value = true
    error.value = null
    try {
      const { data } = await resumeApi.list()
      resumes.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to load resumes.'
    } finally {
      loading.value = false
    }
  }

  async function uploadResume(file) {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await resumeApi.upload(formData)
    resumes.value.unshift(data)
    return data
  }

  async function deleteResume(id) {
    await resumeApi.delete(id)
    resumes.value = resumes.value.filter((r) => r.id !== id)
  }

  return { resumes, loading, error, fetchResumes, uploadResume, deleteResume }
})
