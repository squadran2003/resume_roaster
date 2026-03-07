import { defineStore } from 'pinia'
import { ref } from 'vue'
import { paymentApi } from '../api/payments'

export const usePaymentStore = defineStore('payment', () => {
  const loading = ref(false)
  const error = ref(null)
  const packs = ref([])

  async function fetchPacks() {
    try {
      const { data } = await paymentApi.getCreditPacks()
      packs.value = data.packs
    } catch (e) {
      error.value = 'Failed to load credit packs.'
    }
  }

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

  async function buyCreditPack(packIndex) {
    loading.value = true
    error.value = null
    try {
      const { data } = await paymentApi.createCreditCheckout(packIndex)
      window.location.href = data.checkout_url
    } catch (e) {
      error.value = e.response?.data?.detail || 'Payment initiation failed.'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, packs, fetchPacks, initiateCheckout, buyCreditPack }
})
