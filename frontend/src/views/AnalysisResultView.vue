<template>
  <v-container class="py-8">
    <!-- Polling -->
    <div v-if="polling" class="text-center py-16">
      <v-progress-circular indeterminate color="primary" size="72" class="mb-6" />
      <div class="text-h6">AI is analyzing your resume…</div>
      <div class="text-body-2 text-medium-emphasis mt-2">This usually takes 15–30 seconds.</div>
    </div>

    <!-- Failed -->
    <v-alert
      v-else-if="analysis?.status === 'failed'"
      type="error"
      class="mb-4"
    >
      Analysis failed. Please try again from the
      <router-link to="/analysis/new">new analysis</router-link> page.
    </v-alert>

    <!-- Results -->
    <template v-else-if="analysis?.status === 'done'">
      <div class="d-flex align-center mb-6">
        <h1 class="text-h4 font-weight-bold">Analysis Results</h1>
        <v-spacer />
        <v-btn variant="tonal" prepend-icon="mdi-arrow-left" to="/dashboard">Dashboard</v-btn>
      </div>

      <!-- Score ring + hire probability -->
      <v-row class="mb-4">
        <v-col cols="12" sm="6">
          <v-card elevation="2" rounded="lg" class="text-center pa-6">
            <v-progress-circular
              :model-value="analysis.match_score"
              :size="120"
              :width="12"
              :color="scoreColor"
            >
              <span class="text-h4 font-weight-bold">{{ analysis.match_score }}</span>
            </v-progress-circular>
            <div class="text-h6 mt-4">Match Score</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6">
          <v-card elevation="2" rounded="lg" class="text-center pa-6">
            <v-progress-circular
              :model-value="Math.round(analysis.hire_probability * 100)"
              :size="120"
              :width="12"
              :color="hireColor"
            >
              <span class="text-h4 font-weight-bold">
                {{ Math.round(analysis.hire_probability * 100) }}%
              </span>
            </v-progress-circular>
            <div class="text-h6 mt-4">Hire Probability</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- ATS flags -->
      <v-card v-if="analysis.ats_flags?.length" elevation="2" rounded="lg" class="mb-4 pa-4">
        <div class="text-h6 font-weight-bold mb-3">
          <v-icon icon="mdi-robot-confused" color="orange" class="mr-2" />ATS Issues
        </div>
        <div class="d-flex flex-wrap ga-2">
          <v-chip
            v-for="flag in analysis.ats_flags"
            :key="flag"
            color="orange"
            variant="tonal"
            prepend-icon="mdi-alert"
          >
            {{ flag }}
          </v-chip>
        </div>
      </v-card>
      <v-alert v-else type="success" variant="tonal" class="mb-4">
        No ATS issues detected.
      </v-alert>

      <!-- Rewritten bullets -->
      <v-expansion-panels v-if="analysis.rewritten_bullets?.length" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <v-icon icon="mdi-pencil-box" color="primary" class="mr-2" />
            Rewritten Bullets ({{ analysis.rewritten_bullets.length }})
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-list>
              <v-list-item
                v-for="(bullet, i) in analysis.rewritten_bullets"
                :key="i"
                class="px-0"
              >
                <template #prepend>
                  <v-icon icon="mdi-check-circle" color="success" />
                </template>
                <v-list-item-title class="text-body-2 text-wrap">{{ bullet }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Cover letter -->
      <v-card v-if="analysis.cover_letter" elevation="2" rounded="lg" class="pa-4">
        <div class="text-h6 font-weight-bold mb-3">
          <v-icon icon="mdi-email-edit" color="primary" class="mr-2" />Cover Letter
        </div>
        <div class="text-body-2" style="white-space: pre-wrap">{{ analysis.cover_letter }}</div>
        <v-btn class="mt-4" variant="tonal" prepend-icon="mdi-content-copy" @click="copy">
          {{ copied ? 'Copied!' : 'Copy' }}
        </v-btn>
      </v-card>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '../stores/analysis'
import { analysisApi } from '../api/analysis'

const route = useRoute()
const analysisStore = useAnalysisStore()

const analysis = computed(() => analysisStore.current)
const polling = ref(false)
const copied = ref(false)

const scoreColor = computed(() => {
  const s = analysis.value?.match_score ?? 0
  if (s >= 75) return 'success'
  if (s >= 50) return 'warning'
  return 'error'
})

const hireColor = computed(() => {
  const p = (analysis.value?.hire_probability ?? 0) * 100
  if (p >= 60) return 'success'
  if (p >= 35) return 'warning'
  return 'error'
})

async function copy() {
  await navigator.clipboard.writeText(analysis.value.cover_letter)
  copied.value = true
  setTimeout(() => (copied.value = false), 2000)
}

onMounted(async () => {
  const id = route.params.id
  const { data } = await analysisApi.get(id)
  analysisStore.current = data

  if (data.status === 'pending' || data.status === 'processing') {
    polling.value = true
    try {
      await analysisStore.pollAnalysis(id)
    } finally {
      polling.value = false
    }
  }
})
</script>
