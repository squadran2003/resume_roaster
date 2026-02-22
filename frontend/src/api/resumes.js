import client from './client'

export const resumeApi = {
  list: () => client.get('/resumes/'),
  upload: (formData) =>
    client.post('/resumes/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (id) => client.get(`/resumes/${id}/`),
  delete: (id) => client.delete(`/resumes/${id}/`),
}
