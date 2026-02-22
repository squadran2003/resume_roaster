<template>
  <v-container class="py-8 d-flex justify-center">
    <v-card width="560" elevation="4" rounded="lg">
      <v-card-title class="pt-6 text-h5 font-weight-bold">Upload Resume</v-card-title>
      <v-card-subtitle>PDF or DOCX, max 5 MB</v-card-subtitle>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-alert v-if="success" type="success" density="compact" class="mb-4">
          Resume uploaded! <router-link to="/dashboard">Go to dashboard</router-link>
        </v-alert>
        <v-form ref="formRef" @submit.prevent="submit">
          <v-file-input
            v-model="file"
            label="Choose file"
            accept=".pdf,.docx"
            prepend-icon="mdi-paperclip"
            variant="outlined"
            :rules="[rules.required, rules.size, rules.type]"
            show-size
            class="mb-4"
          />
          <v-progress-linear v-if="uploading" indeterminate color="primary" class="mb-4" />
          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="uploading"
            :disabled="!file"
          >
            Upload
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useResumeStore } from '../stores/resume'

const resumeStore = useResumeStore()
const formRef = ref(null)
const file = ref(null)
const uploading = ref(false)
const error = ref(null)
const success = ref(false)

const MAX_SIZE = 5 * 1024 * 1024
const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

const rules = {
  required: (v) => !!v || 'File is required.',
  size: (v) => !v || v.size <= MAX_SIZE || 'File must be under 5 MB.',
  type: (v) => !v || ALLOWED_TYPES.includes(v.type) || 'Only PDF or DOCX allowed.',
}

async function submit() {
  const { valid } = await formRef.value.validate()
  if (!valid || !file.value) return

  uploading.value = true
  error.value = null
  success.value = false
  try {
    await resumeStore.uploadResume(file.value)
    success.value = true
    file.value = null
    formRef.value.reset()
  } catch (e) {
    const data = e.response?.data
    error.value = data ? Object.values(data).flat().join(' ') : 'Upload failed.'
  } finally {
    uploading.value = false
  }
}
</script>
