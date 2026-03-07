<template>
  <v-container class="py-8">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">LinkedIn Optimizer</h1>
      <v-spacer />
      <v-btn variant="tonal" prepend-icon="mdi-arrow-left" to="/dashboard">Dashboard</v-btn>
    </div>

    <!-- Form -->
    <v-card v-if="!result" width="700" class="mx-auto" elevation="4" rounded="lg">
      <v-card-title class="pt-6 text-h6 font-weight-bold">Optimize Your LinkedIn</v-card-title>
      <v-card-text>
        <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
        <v-alert type="info" variant="tonal" density="compact" class="mb-4">
          Costs 1 credit. Paste your current LinkedIn headline and About section, plus the job description you're targeting.
        </v-alert>
        <v-form @submit.prevent="submit">
          <v-text-field
            v-model="headline"
            label="Current LinkedIn Headline"
            variant="outlined"
            prepend-inner-icon="mdi-format-title"
            class="mb-3"
          />
          <v-textarea
            v-model="about"
            label="Current LinkedIn About section"
            variant="outlined"
            rows="6"
            :rules="[v => !v || v.length >= 50 || 'Min 50 characters']"
            class="mb-3"
          />
          <v-textarea
            v-model="jdText"
            label="Target job description"
            variant="outlined"
            rows="8"
            :rules="[v => !v || v.length >= 100 || 'Min 100 characters']"
            class="mb-4"
          />
          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="loading"
            :disabled="!headline || !about || !jdText"
          >
            Optimize LinkedIn (1 credit)
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Polling -->
    <div v-else-if="result.status === 'pending' || result.status === 'processing'" class="text-center py-16">
      <v-progress-circular indeterminate color="primary" size="72" class="mb-6" />
      <div class="text-h6">Optimizing your LinkedIn profile...</div>
    </div>

    <!-- Failed -->
    <v-alert v-else-if="result.status === 'failed'" type="error" class="mb-4">
      Analysis failed. Please try again.
      <v-btn class="ml-4" variant="tonal" @click="result = null">Try Again</v-btn>
    </v-alert>

    <!-- Results -->
    <template v-else-if="result.status === 'done'">
      <v-row>
        <v-col cols="12" md="4">
          <v-card elevation="2" rounded="lg" class="text-center pa-6">
            <v-progress-circular
              :model-value="result.score"
              :size="100"
              :width="10"
              :color="result.score >= 75 ? 'success' : result.score >= 50 ? 'warning' : 'error'"
            >
              <span class="text-h5 font-weight-bold">{{ result.score }}</span>
            </v-progress-circular>
            <div class="text-h6 mt-3">Profile Score</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="8">
          <v-card elevation="2" rounded="lg" class="pa-4 mb-4">
            <div class="text-h6 font-weight-bold mb-2">Optimized Headline</div>
            <div class="text-body-1 pa-3 rounded bg-grey-lighten-4">{{ result.headline_rewrite }}</div>
            <v-btn size="small" variant="tonal" class="mt-2" prepend-icon="mdi-content-copy" @click="copy(result.headline_rewrite)">Copy</v-btn>
          </v-card>
        </v-col>
      </v-row>

      <v-card elevation="2" rounded="lg" class="pa-4 mb-4">
        <div class="text-h6 font-weight-bold mb-2">Optimized About Section</div>
        <div class="text-body-2 pa-3 rounded bg-grey-lighten-4" style="white-space:pre-wrap">{{ result.about_rewrite }}</div>
        <v-btn size="small" variant="tonal" class="mt-2" prepend-icon="mdi-content-copy" @click="copy(result.about_rewrite)">Copy</v-btn>
      </v-card>

      <v-row class="mb-4">
        <v-col cols="12" md="6">
          <v-card elevation="2" rounded="lg" class="pa-4 h-100">
            <div class="text-h6 font-weight-bold mb-3">Suggested Skills</div>
            <v-chip v-for="skill in result.suggested_skills" :key="skill" color="primary" variant="tonal" class="mr-2 mb-2">
              {{ skill }}
            </v-chip>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card elevation="2" rounded="lg" class="pa-4 h-100">
            <div class="text-h6 font-weight-bold mb-3">Recruiter Search Keywords</div>
            <v-chip v-for="kw in result.recruiter_keywords" :key="kw" color="teal" variant="tonal" class="mr-2 mb-2">
              {{ kw }}
            </v-chip>
          </v-card>
        </v-col>
      </v-row>

      <v-card v-if="result.tips?.length" elevation="2" rounded="lg" class="pa-4 mb-4">
        <div class="text-h6 font-weight-bold mb-3">Tips</div>
        <v-list>
          <v-list-item v-for="(tip, i) in result.tips" :key="i" class="px-0">
            <template #prepend>
              <v-icon icon="mdi-lightbulb" color="amber" />
            </template>
            <v-list-item-title class="text-body-2 text-wrap">{{ tip }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>

      <v-btn variant="tonal" @click="result = null">Analyze Another</v-btn>
    </template>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { analysisApi } from '../api/analysis'

const authStore = useAuthStore()

const headline = ref('')
const about = ref('')
const jdText = ref('')
const loading = ref(false)
const error = ref(null)
const result = ref(null)

const POLL_INTERVAL = 3000
const MAX_ATTEMPTS = 60

async function submit() {
  loading.value = true
  error.value = null
  try {
    const { data } = await analysisApi.linkedinAnalyze({
      headline: headline.value,
      about: about.value,
      jd_text: jdText.value,
    })
    result.value = data
    await authStore.fetchMe()

    if (data.status === 'pending' || data.status === 'processing') {
      await pollLinkedIn(data.id)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to start LinkedIn analysis.'
  } finally {
    loading.value = false
  }
}

function pollLinkedIn(id) {
  let attempts = 0
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      attempts++
      try {
        const { data } = await analysisApi.linkedinGet(id)
        result.value = data
        if (data.status === 'done' || data.status === 'failed') {
          clearInterval(interval)
          resolve(data)
        } else if (attempts >= MAX_ATTEMPTS) {
          clearInterval(interval)
          reject(new Error('Timed out'))
        }
      } catch (e) {
        clearInterval(interval)
        reject(e)
      }
    }, POLL_INTERVAL)
  })
}

async function copy(text) {
  await navigator.clipboard.writeText(text)
}
</script>
