<template>
  <v-container class="py-8 d-flex justify-center">
    <v-card width="680" elevation="4" rounded="lg">
      <v-card-title class="pt-6 text-h5 font-weight-bold">New Analysis</v-card-title>
      <v-card-text>
        <v-alert v-if="credits < 1 && !isAdmin" type="warning" density="compact" class="mb-4">
          You have no credits remaining.
          <router-link to="/dashboard">Buy more credits</router-link> to run an analysis.
        </v-alert>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-form @submit.prevent="submit">
          <v-select
            v-model="selectedResume"
            :items="resumeStore.resumes"
            item-title="original_filename"
            item-value="id"
            label="Select resume"
            prepend-inner-icon="mdi-file-account"
            variant="outlined"
            :loading="resumeStore.loading"
            no-data-text="No resumes uploaded yet."
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
            :disabled="!selectedResume || !jobDescription || (credits < 1 && !isAdmin)"
          >
            Analyze Resume (1 credit)
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
const credits = computed(() => authStore.user?.profile?.credits_remaining ?? 0)

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
    // Refresh user to update credits
    await authStore.fetchMe()
    router.push(`/analysis/${result.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || analysisStore.error || 'Failed to start analysis.'
  } finally {
    loading.value = false
  }
}
</script>
