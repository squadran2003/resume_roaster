<template>
  <div ref="buttonRef" class="google-signin-container d-flex justify-center"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  clientId: { type: String, required: true },
})

const emit = defineEmits(['credential', 'error'])
const buttonRef = ref(null)

onMounted(async () => {
  await waitForGoogle()
  try {
    window.google.accounts.id.initialize({
      client_id: props.clientId,
      callback: (response) => {
        if (response.credential) {
          emit('credential', response.credential)
        } else {
          emit('error', 'No credential received')
        }
      },
    })
    window.google.accounts.id.renderButton(buttonRef.value, {
      theme: 'outline',
      size: 'large',
      width: 360,
      text: 'signin_with',
    })
  } catch (e) {
    emit('error', e.message)
  }
})

function waitForGoogle() {
  return new Promise((resolve) => {
    if (window.google?.accounts?.id) return resolve()
    const interval = setInterval(() => {
      if (window.google?.accounts?.id) {
        clearInterval(interval)
        resolve()
      }
    }, 100)
  })
}
</script>
