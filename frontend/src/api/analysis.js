import client from './client'

export const analysisApi = {
  create: (data) => client.post('/analysis/', data),
  get: (id) => client.get(`/analysis/${id}/`),
  delete: (id) => client.delete(`/analysis/${id}/`),
  list: (page = 1) => client.get(`/analysis/list/?page=${page}`),
  compare: (id1, id2) => client.get(`/analysis/compare/?ids=${id1},${id2}`),
  requestRewrite: (id) => client.post(`/analysis/${id}/rewrite/`),
  downloadRewritePDF: (id) => client.get(`/analysis/${id}/rewrite/pdf/`, { responseType: 'blob' }),
  downloadRewriteDOCX: (id) => client.get(`/analysis/${id}/rewrite/docx/`, { responseType: 'blob' }),
  requestInterviewPrep: (id) => client.post(`/analysis/${id}/interview-prep/`),
  getShareToken: (id) => client.post(`/analysis/${id}/share/`),
  getPublicShare: (token) => client.get(`/analysis/shared/${token}/`),
  linkedinAnalyze: (data) => client.post('/analysis/linkedin/', data),
  linkedinGet: (id) => client.get(`/analysis/linkedin/${id}/`),
}
