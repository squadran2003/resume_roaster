<template>
  <div>
    <!-- Score Card Hero -->
    <section class="share-hero">
      <div class="share-glow" />
      <v-container class="py-12 text-center share-content">
        <div v-if="loading" class="py-12">
          <v-progress-circular indeterminate color="white" size="48" />
        </div>

        <div v-else-if="error" class="py-12">
          <v-icon icon="mdi-alert-circle" color="error" size="64" class="mb-4" />
          <div class="text-h5 text-white font-weight-bold">Score card not found</div>
          <p class="text-white mt-2" style="opacity: 0.7;">This link may have expired or be invalid.</p>
        </div>

        <template v-else>
          <v-chip color="primary" variant="flat" size="small" class="mb-5 text-uppercase font-weight-bold">
            AI Resume Analysis
          </v-chip>

          <v-row justify="center" class="mb-8">
            <v-col cols="12" sm="5">
              <v-card elevation="0" class="text-center pa-8 score-card-shared">
                <v-progress-circular
                  :model-value="data.match_score"
                  :size="140"
                  :width="14"
                  :color="scoreColor"
                >
                  <span class="text-h3 font-weight-bold text-white">{{ data.match_score }}</span>
                </v-progress-circular>
                <div class="text-h6 mt-4 mb-1 text-white">Match Score</div>
                <v-chip :color="scoreColor" variant="flat" size="small">
                  {{ data.match_score >= 75 ? 'Strong Match' : data.match_score >= 50 ? 'Partial Match' : 'Weak Match' }}
                </v-chip>
              </v-card>
            </v-col>
            <v-col cols="12" sm="5">
              <v-card elevation="0" class="text-center pa-8 score-card-shared">
                <v-progress-circular
                  :model-value="Math.round(data.hire_probability * 100)"
                  :size="140"
                  :width="14"
                  :color="hireColor"
                >
                  <span class="text-h3 font-weight-bold text-white">
                    {{ Math.round(data.hire_probability * 100) }}%
                  </span>
                </v-progress-circular>
                <div class="text-h6 mt-4 mb-1 text-white">Hire Probability</div>
                <v-chip :color="hireColor" variant="flat" size="small">
                  {{ Math.round(data.hire_probability * 100) >= 60 ? 'Good Odds' : Math.round(data.hire_probability * 100) >= 35 ? 'Fair Odds' : 'Needs Work' }}
                </v-chip>
              </v-card>
            </v-col>
          </v-row>

          <div v-if="data.job_title" class="text-h5 font-weight-bold text-white mb-2">
            {{ data.job_title }}
            <span v-if="data.company" style="opacity: 0.7;"> @ {{ data.company }}</span>
          </div>

          <div class="d-flex justify-center flex-wrap mt-6 mb-8" style="gap: 16px;">
            <v-chip variant="tonal" :color="data.keywords_total && data.keywords_found / data.keywords_total >= 0.7 ? 'success' : 'warning'" prepend-icon="mdi-key">
              {{ data.keywords_found }}/{{ data.keywords_total }} keywords matched
            </v-chip>
            <v-chip variant="tonal" :color="data.ats_issues === 0 ? 'success' : 'warning'" prepend-icon="mdi-robot-outline">
              {{ data.ats_issues }} ATS issues
            </v-chip>
          </div>

          <div class="mt-8">
            <h2 class="text-h5 font-weight-bold text-white mb-3">Want to score your resume?</h2>
            <p v-if="data.payments_enabled" class="text-white mb-6" style="opacity: 0.7;">Get your own AI-powered resume analysis — 2 free credits, no credit card required.</p>
            <v-btn to="/register" color="primary" size="x-large" variant="flat" class="font-weight-bold px-10 hero-cta">
              Roast My Resume
            </v-btn>
          </div>
        </template>
      </v-container>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useHead } from '@unhead/vue'
import { analysisApi } from '../api/analysis'

const route = useRoute()
const loading = ref(true)
const error = ref(false)
const data = ref({})

const scoreColor = computed(() => {
  const s = data.value?.match_score ?? 0
  if (s >= 75) return 'success'
  if (s >= 50) return 'warning'
  return 'error'
})

const hireColor = computed(() => {
  const p = (data.value?.hire_probability ?? 0) * 100
  if (p >= 60) return 'success'
  if (p >= 35) return 'warning'
  return 'error'
})

useHead(computed(() => ({
  title: data.value.match_score != null
    ? `Resume Score: ${data.value.match_score}/100 — Resume Roaster`
    : 'Resume Roaster',
  meta: data.value.match_score != null
    ? [
        { property: 'og:title', content: `I scored ${data.value.match_score}/100 on my resume match!` },
        { property: 'og:description', content: `${data.value.match_score}/100 match score for ${data.value.job_title || 'a job position'}. Roast your resume too!` },
        { property: 'og:image', content: `${window.location.origin}/api/v1/analysis/shared/${route.params.token}/image.png` },
        { property: 'og:type', content: 'website' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: `I scored ${data.value.match_score}/100 on my resume match!` },
        { name: 'twitter:image', content: `${window.location.origin}/api/v1/analysis/shared/${route.params.token}/image.png` },
      ]
    : [],
})))

onMounted(async () => {
  try {
    const res = await analysisApi.getPublicShare(route.params.token)
    data.value = res.data
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.share-hero {
  background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 40%, #0f3460 100%);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.share-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 700px;
  height: 700px;
  background: radial-gradient(ellipse, rgba(230, 74, 25, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.share-content {
  position: relative;
  z-index: 1;
}

.score-card-shared {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-cta {
  box-shadow: 0 0 32px rgba(230, 74, 25, 0.35);
}
</style>
