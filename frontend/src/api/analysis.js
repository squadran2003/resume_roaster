import client from './client'

export const analysisApi = {
  create: (data) => client.post('/analysis/', data),
  get: (id) => client.get(`/analysis/${id}/`),
}
