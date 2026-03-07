import client from './client'

export const analysisApi = {
  create: (data) => client.post('/analysis/', data),
  get: (id) => client.get(`/analysis/${id}/`),
  list: (page = 1) => client.get(`/analysis/list/?page=${page}`),
  compare: (id1, id2) => client.get(`/analysis/compare/?ids=${id1},${id2}`),
  requestRewrite: (id) => client.post(`/analysis/${id}/rewrite/`),
  downloadRewritePDF: (id) => client.get(`/analysis/${id}/rewrite/pdf/`, { responseType: 'blob' }),
  requestInterviewPrep: (id) => client.post(`/analysis/${id}/interview-prep/`),
  linkedinAnalyze: (data) => client.post('/analysis/linkedin/', data),
  linkedinGet: (id) => client.get(`/analysis/linkedin/${id}/`),
}
