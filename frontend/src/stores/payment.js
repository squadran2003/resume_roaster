import { defineStore } from 'pinia'
import { ref } from 'vue'
import { paymentApi } from '../api/payments'

export const usePaymentStore = defineStore('payment', () => {
  const loading = ref(false)
  const error = ref(null)

  async function initiateCheckout(resumeId) {
    loading.value = true
    error.value = null
    try {
      const { data } = await paymentApi.createCheckout(resumeId)
      window.location.href = data.checkout_url
    } catch (e) {
      error.value = e.response?.data?.detail || 'Payment initiation failed.'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, initiateCheckout }
})
