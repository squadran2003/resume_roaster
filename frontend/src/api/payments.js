import client from './client'

export const paymentApi = {
  createCheckout: (resumeId) => client.post('/payments/checkout/', { resume_id: resumeId }),
  getCreditPacks: () => client.get('/payments/credits/packs/'),
  createCreditCheckout: (packIndex) => client.post('/payments/credits/checkout/', { pack_index: packIndex }),
}
