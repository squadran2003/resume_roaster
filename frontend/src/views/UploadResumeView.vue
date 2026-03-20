<template>
  <v-container class="py-8 d-flex justify-center">
    <div style="width: 100%; max-width: 560px;">
      <h1 class="text-h5 font-weight-bold mb-1">Upload Resume</h1>
      <p class="text-body-2 text-medium-emphasis mb-6">PDF or DOCX, max 5 MB</p>

      <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
      <v-alert v-if="success" type="success" density="compact" class="mb-4">
        Resume uploaded!
        <router-link to="/analysis/new">Run an analysis</router-link> or
        <router-link to="/dashboard">go to dashboard</router-link>
      </v-alert>

      <v-form ref="formRef" @submit.prevent="submit">
        <!-- Drop zone -->
        <div
          class="drop-zone mb-5"
          :class="{
            'drop-zone--active': isDragging,
            'drop-zone--has-file': !!file,
            'drop-zone--error': fileError,
          }"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="fileInputRef?.click()"
          tabindex="0"
          role="button"
          @keydown.enter.space.prevent="fileInputRef?.click()"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept=".pdf,.docx"
            style="display: none"
            @change="onFileChange"
          />
          <v-icon
            :icon="file ? 'mdi-file-check' : 'mdi-cloud-upload-outline'"
            :size="52"
            :color="file ? 'success' : 'primary'"
            class="mb-3"
          />
          <div class="text-h6 font-weight-medium">
            {{ file ? file.name : 'Drop your resume here' }}
          </div>
          <div class="text-body-2 text-medium-emphasis mt-1">
            {{ file ? formatSize(file.size) : 'or click to browse — PDF or DOCX, max 5 MB' }}
          </div>
          <div v-if="fileError" class="text-error text-body-2 mt-2">{{ fileError }}</div>
        </div>

        <v-progress-linear v-if="uploading" indeterminate color="primary" class="mb-4" rounded />

        <v-btn
          type="submit"
          color="primary"
          block
          size="large"
          :loading="uploading"
          :disabled="!file"
          prepend-icon="mdi-upload"
        >
          Upload Resume
        </v-btn>
      </v-form>
    </div>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useResumeStore } from '../stores/resume'

const resumeStore = useResumeStore()
const formRef = ref(null)
const fileInputRef = ref(null)
const file = ref(null)
const uploading = ref(false)
const error = ref(null)
const success = ref(false)
const isDragging = ref(false)
const fileError = ref(null)

const MAX_SIZE = 5 * 1024 * 1024
const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function validateFile(f) {
  if (!f) return 'No file selected.'
  if (!ALLOWED_TYPES.includes(f.type)) return 'Only PDF or DOCX allowed.'
  if (f.size > MAX_SIZE) return 'File must be under 5 MB.'
  return null
}

function setFile(f) {
  const err = validateFile(f)
  if (err) {
    fileError.value = err
    file.value = null
  } else {
    fileError.value = null
    file.value = f
  }
}

function onFileChange(e) {
  setFile(e.target.files[0])
}

function onDrop(e) {
  isDragging.value = false
  setFile(e.dataTransfer.files[0])
}

async function submit() {
  if (!file.value) return

  uploading.value = true
  error.value = null
  success.value = false
  try {
    await resumeStore.uploadResume(file.value)
    success.value = true
    file.value = null
  } catch (e) {
    const data = e.response?.data
    error.value = data ? Object.values(data).flat().join(' ') : 'Upload failed.'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed rgba(0, 0, 0, 0.15);
  border-radius: 16px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.15s;
}

.drop-zone:hover {
  border-color: rgba(230, 74, 25, 0.4);
  background: rgba(230, 74, 25, 0.02);
}

.drop-zone--active {
  border-color: #E64A19 !important;
  background: rgba(230, 74, 25, 0.06) !important;
  transform: scale(1.01);
}

.drop-zone--has-file {
  border-color: #2E7D32;
  border-style: solid;
  background: rgba(46, 125, 50, 0.04);
}

.drop-zone--error {
  border-color: #D32F2F;
}
</style>
