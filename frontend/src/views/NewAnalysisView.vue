<template>
  <v-container class="py-8 d-flex justify-center">
    <v-card width="680" elevation="4" rounded="lg">
      <v-card-title class="pt-6 text-h5 font-weight-bold">New Analysis</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-form @submit.prevent="submit">
          <v-select
            v-model="selectedResume"
            :items="paidResumes"
            item-title="original_filename"
            item-value="id"
            label="Select resume"
            prepend-inner-icon="mdi-file-account"
            variant="outlined"
            :loading="resumeStore.loading"
            :no-data-text="isAdmin ? 'No resumes uploaded yet.' : 'No paid resumes. Upload and pay for a resume first.'"
            class="mb-3"
          />
          <v-text-field
            v-model="jobTitle"
            label="Job title"
            variant="outlined"
            prepend-inner-icon="mdi-briefcase"
            class="mb-3"
          />
          <v-text-field
            v-model="company"
            label="Company (optional)"
            variant="outlined"
            prepend-inner-icon="mdi-domain"
            class="mb-3"
          />
          <v-textarea
            v-model="jobDescription"
            label="Paste job description"
            variant="outlined"
            rows="10"
            counter
            :rules="[rules.required, rules.minLength]"
            class="mb-4"
          />
          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="loading"
            :disabled="!selectedResume || !jobDescription"
          >
            Analyze Resume
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import { useAnalysisStore } from '../stores/analysis'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const resumeStore = useResumeStore()
const analysisStore = useAnalysisStore()
const authStore = useAuthStore()

const selectedResume = ref(route.query.resume || null)
const jobTitle = ref('')
const company = ref('')
const jobDescription = ref('')
const loading = ref(false)
const error = ref(null)

const isAdmin = computed(() => authStore.user?.is_staff)
const paidResumes = computed(() =>
  isAdmin.value ? resumeStore.resumes : resumeStore.resumes.filter((r) => r.is_paid),
)

const rules = {
  required: (v) => !!v || 'Job description is required.',
  minLength: (v) => !v || v.length >= 100 || 'Paste a full job description (min 100 characters).',
}

onMounted(() => resumeStore.fetchResumes())

async function submit() {
  loading.value = true
  error.value = null
  try {
    const result = await analysisStore.submitAnalysis(
      selectedResume.value,
      jobDescription.value,
      jobTitle.value,
      company.value,
    )
    router.push(`/analysis/${result.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || analysisStore.error || 'Failed to start analysis.'
  } finally {
    loading.value = false
  }
}
</script>
