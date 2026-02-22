import client from './client'

export const paymentApi = {
  createCheckout: (resumeId) => client.post('/payments/checkout/', { resume_id: resumeId }),
}
