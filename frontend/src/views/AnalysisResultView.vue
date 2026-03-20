<template>
  <v-container class="py-8">
    <!-- Polling / Loading -->
    <div v-if="polling" class="text-center py-12">
      <v-icon icon="mdi-fire" color="primary" size="64" class="mb-5 pulse-icon" />
      <div class="text-h5 font-weight-bold mb-4">Roasting your resume...</div>
      <div class="loading-steps mx-auto" style="max-width: 320px; text-align: left;">
        <div
          v-for="(step, i) in loadingSteps"
          :key="i"
          class="d-flex align-center mb-3"
          style="gap: 10px;"
        >
          <v-icon
            :icon="currentStep > i ? 'mdi-check-circle' : currentStep === i ? 'mdi-loading' : 'mdi-circle-outline'"
            :color="currentStep > i ? 'success' : currentStep === i ? 'primary' : 'grey-lighten-1'"
            :class="{ 'spin-icon': currentStep === i }"
            size="20"
          />
          <span :class="currentStep >= i ? 'font-weight-medium' : 'text-medium-emphasis'" class="text-body-2">
            {{ step }}
          </span>
        </div>
      </div>
      <div class="text-body-2 text-medium-emphasis mt-6">Usually takes 15-30 seconds</div>
    </div>

    <!-- Failed -->
    <v-alert v-else-if="analysis?.status === 'failed'" type="error" class="mb-4">
      Analysis failed. Please try again from the
      <router-link to="/analysis/new">new analysis</router-link> page.
    </v-alert>

    <!-- Results -->
    <template v-else-if="analysis?.status === 'done'">
      <div class="d-flex align-center mb-6 flex-wrap ga-3">
        <h1 class="text-h4 font-weight-bold">Analysis Results</h1>
        <v-spacer />
        <v-btn variant="tonal" prepend-icon="mdi-share-variant" :loading="shareLoading" @click="shareScoreCard">
          {{ shareToken ? 'Copy Share Link' : 'Share Score Card' }}
        </v-btn>
        <v-btn variant="tonal" prepend-icon="mdi-arrow-left" to="/dashboard">Dashboard</v-btn>
      </div>

      <!-- Share dialog -->
      <v-dialog v-model="shareDialog" max-width="520">
        <v-card class="pa-6">
          <div class="text-h6 font-weight-bold mb-4">Share Your Score Card</div>
          <v-img
            :src="shareImageUrl"
            class="rounded-lg mb-4"
            aspect-ratio="1.905"
            cover
          />
          <v-text-field
            :model-value="shareUrl"
            readonly
            density="compact"
            variant="outlined"
            append-inner-icon="mdi-content-copy"
            @click:append-inner="copyShareLink"
            class="mb-3"
          />
          <div class="d-flex ga-2 flex-wrap">
            <v-btn
              color="blue"
              variant="flat"
              size="small"
              prepend-icon="mdi-linkedin"
              :href="`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`"
              target="_blank"
            >
              LinkedIn
            </v-btn>
            <v-btn
              color="black"
              variant="flat"
              size="small"
              prepend-icon="mdi-twitter"
              :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`"
              target="_blank"
            >
              Twitter / X
            </v-btn>
            <v-spacer />
            <v-btn variant="tonal" size="small" @click="shareDialog = false">Close</v-btn>
          </div>
        </v-card>
      </v-dialog>

      <!-- Score hero row -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6">
          <v-card elevation="0" class="text-center pa-8 score-card">
            <v-progress-circular
              :model-value="analysis.match_score"
              :size="130"
              :width="14"
              :color="scoreColor"
            >
              <span class="text-h3 font-weight-bold">{{ analysis.match_score }}</span>
            </v-progress-circular>
            <div class="text-h6 mt-4 mb-1">Match Score</div>
            <v-chip :color="scoreColor" variant="tonal" size="small">
              {{ analysis.match_score >= 75 ? 'Strong Match' : analysis.match_score >= 50 ? 'Partial Match' : 'Weak Match' }}
            </v-chip>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6">
          <v-card elevation="0" class="text-center pa-8 score-card">
            <v-progress-circular
              :model-value="Math.round(analysis.hire_probability * 100)"
              :size="130"
              :width="14"
              :color="hireColor"
            >
              <span class="text-h3 font-weight-bold">
                {{ Math.round(analysis.hire_probability * 100) }}%
              </span>
            </v-progress-circular>
            <div class="text-h6 mt-4 mb-1">Hire Probability</div>
            <v-chip :color="hireColor" variant="tonal" size="small">
              {{ Math.round(analysis.hire_probability * 100) >= 60 ? 'Good Odds' : Math.round(analysis.hire_probability * 100) >= 35 ? 'Fair Odds' : 'Needs Work' }}
            </v-chip>
          </v-card>
        </v-col>
      </v-row>

      <!-- Premium Actions — positioned high for visibility -->
      <v-row class="mb-6">
        <v-col cols="12" md="6">
          <v-card elevation="0" class="pa-5 h-100 premium-card">
            <div class="d-flex align-center mb-3" style="gap: 8px;">
              <v-icon icon="mdi-file-document-edit" color="deep-purple" size="24" />
              <div class="text-h6 font-weight-bold">Full Resume Rewrite</div>
            </div>
            <div class="text-body-2 text-medium-emphasis mb-4">
              AI rewrites your entire resume, optimized for this specific job. Download as PDF.
            </div>
            <template v-if="analysis.rewritten_resume_text">
              <v-alert type="success" variant="tonal" density="compact" class="mb-3">Rewrite ready!</v-alert>
              <div class="d-flex ga-2 flex-wrap">
                <v-btn color="deep-purple" variant="flat" prepend-icon="mdi-download" @click="downloadPDF" :loading="downloading">
                  Download PDF
                </v-btn>
                <v-btn variant="tonal" prepend-icon="mdi-eye" @click="showRewrite = !showRewrite">
                  {{ showRewrite ? 'Hide' : 'Preview' }}
                </v-btn>
              </div>
              <div v-if="showRewrite" class="mt-3 pa-3 rounded-lg bg-surface-variant" style="white-space:pre-wrap;font-size:0.85rem;">{{ analysis.rewritten_resume_text }}</div>
            </template>
            <template v-else-if="rewritePolling">
              <v-progress-linear indeterminate color="deep-purple" class="mb-2" rounded />
              <div class="text-body-2 text-medium-emphasis">Generating rewrite...</div>
            </template>
            <template v-else>
              <v-btn color="deep-purple" variant="flat" prepend-icon="mdi-creation" @click="requestRewrite" :loading="rewriteLoading">
                {{ authStore.paymentsEnabled ? 'Generate Rewrite (1 credit)' : 'Generate Rewrite' }}
              </v-btn>
            </template>
            <v-alert v-if="rewriteError" type="error" density="compact" class="mt-2">{{ rewriteError }}</v-alert>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card elevation="0" class="pa-5 h-100 premium-card">
            <div class="d-flex align-center mb-3" style="gap: 8px;">
              <v-icon icon="mdi-account-question" color="indigo" size="24" />
              <div class="text-h6 font-weight-bold">Interview Prep</div>
            </div>
            <div class="text-body-2 text-medium-emphasis mb-4">
              Get 8-10 likely interview questions with STAR answer frameworks based on this JD.
            </div>
            <template v-if="analysis.interview_questions?.length">
              <v-alert type="success" variant="tonal" density="compact" class="mb-3">
                {{ analysis.interview_questions.length }} questions ready!
              </v-alert>
              <v-btn variant="tonal" prepend-icon="mdi-eye" @click="showInterview = !showInterview">
                {{ showInterview ? 'Hide' : 'Show Questions' }}
              </v-btn>
            </template>
            <template v-else-if="interviewPolling">
              <v-progress-linear indeterminate color="indigo" class="mb-2" rounded />
              <div class="text-body-2 text-medium-emphasis">Generating questions...</div>
            </template>
            <template v-else>
              <v-btn color="indigo" variant="flat" prepend-icon="mdi-creation" @click="requestInterviewPrep" :loading="interviewLoading">
                {{ authStore.paymentsEnabled ? 'Generate Questions (1 credit)' : 'Generate Questions' }}
              </v-btn>
            </template>
            <v-alert v-if="interviewError" type="error" density="compact" class="mt-2">{{ interviewError }}</v-alert>
          </v-card>
        </v-col>
      </v-row>

      <!-- Interview Questions Accordion -->
      <v-expansion-panels v-if="showInterview && analysis.interview_questions?.length" class="mb-6">
        <v-expansion-panel v-for="(q, i) in analysis.interview_questions" :key="i">
          <v-expansion-panel-title>
            <span class="font-weight-medium">{{ i + 1 }}. {{ q.question }}</span>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="mb-2">
              <span class="font-weight-bold text-indigo">Why they ask:</span>
              <span class="text-body-2 ml-1">{{ q.why_asked }}</span>
            </div>
            <div>
              <span class="font-weight-bold text-success">Answer framework:</span>
              <div class="text-body-2 mt-1" style="white-space:pre-wrap">{{ q.answer_framework }}</div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Keyword Heatmap -->
      <v-card v-if="analysis.keyword_matches?.length" elevation="0" class="mb-6 pa-5 section-card">
        <div class="d-flex align-center mb-3" style="gap: 8px;">
          <v-icon icon="mdi-fire" color="primary" size="24" />
          <div class="text-h6 font-weight-bold">Keyword Match Heatmap</div>
          <v-spacer />
          <v-chip variant="tonal" :color="foundRatio >= 0.7 ? 'success' : foundRatio >= 0.4 ? 'warning' : 'error'" size="small">
            {{ foundCount }}/{{ analysis.keyword_matches.length }} found
          </v-chip>
        </div>
        <div class="d-flex flex-wrap ga-2">
          <v-tooltip v-for="kw in analysis.keyword_matches" :key="kw.keyword" :text="kw.found ? 'Found in resume' : `Missing — add to: ${kw.section_hint}`" location="top">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                :color="kw.found ? 'success' : 'error'"
                variant="tonal"
                :prepend-icon="kw.found ? 'mdi-check-circle' : 'mdi-close-circle'"
              >
                {{ kw.keyword }}
              </v-chip>
            </template>
          </v-tooltip>
        </div>
      </v-card>

      <!-- ATS flags -->
      <v-card v-if="analysis.ats_flags?.length" elevation="0" class="mb-6 pa-5 section-card">
        <div class="d-flex align-center mb-3" style="gap: 8px;">
          <v-icon icon="mdi-robot-confused" color="warning" size="24" />
          <div class="text-h6 font-weight-bold">ATS Issues</div>
          <v-spacer />
          <v-chip color="warning" variant="tonal" size="small">{{ analysis.ats_flags.length }} found</v-chip>
        </div>
        <div class="d-flex flex-wrap ga-2">
          <v-chip
            v-for="flag in analysis.ats_flags"
            :key="flag"
            color="warning"
            variant="tonal"
            prepend-icon="mdi-alert"
          >
            {{ flag }}
          </v-chip>
        </div>
      </v-card>
      <v-alert v-else type="success" variant="tonal" class="mb-6" density="comfortable">
        <template #prepend>
          <v-icon icon="mdi-check-circle" />
        </template>
        No ATS issues detected — your resume formatting looks good!
      </v-alert>

      <!-- Rewritten bullets — visible by default -->
      <v-card v-if="analysis.rewritten_bullets?.length" elevation="0" class="mb-6 pa-5 section-card">
        <div class="d-flex align-center mb-3" style="gap: 8px;">
          <v-icon icon="mdi-pencil-box" color="primary" size="24" />
          <div class="text-h6 font-weight-bold">Rewritten Bullets</div>
          <v-spacer />
          <v-chip variant="tonal" color="primary" size="small">{{ analysis.rewritten_bullets.length }} improved</v-chip>
        </div>
        <v-list density="compact">
          <v-list-item
            v-for="(bullet, i) in analysis.rewritten_bullets"
            :key="i"
            class="px-0"
          >
            <template #prepend>
              <v-icon icon="mdi-check-circle" color="success" size="20" />
            </template>
            <v-list-item-title class="text-body-2 text-wrap">{{ bullet }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card>

      <!-- Cover letter -->
      <v-card v-if="analysis.cover_letter" elevation="0" class="pa-5 mb-6 section-card">
        <div class="d-flex align-center mb-3" style="gap: 8px;">
          <v-icon icon="mdi-email-edit" color="primary" size="24" />
          <div class="text-h6 font-weight-bold">Cover Letter</div>
        </div>
        <div class="text-body-2" style="white-space: pre-wrap">{{ analysis.cover_letter }}</div>
        <v-btn class="mt-4" variant="tonal" prepend-icon="mdi-content-copy" @click="copyText(analysis.cover_letter)">
          Copy
        </v-btn>
      </v-card>

      <!-- Follow-up Emails -->
      <v-card v-if="analysis.follow_up_emails?.length" elevation="0" class="pa-5 mb-6 section-card">
        <div class="d-flex align-center mb-3" style="gap: 8px;">
          <v-icon icon="mdi-email-multiple" color="teal" size="24" />
          <div class="text-h6 font-weight-bold">Follow-Up Email Templates</div>
        </div>
        <v-tabs v-model="emailTab" color="primary">
          <v-tab v-for="email in analysis.follow_up_emails" :key="email.type" :value="email.type">
            {{ emailLabel(email.type) }}
          </v-tab>
        </v-tabs>
        <v-tabs-window v-model="emailTab">
          <v-tabs-window-item v-for="email in analysis.follow_up_emails" :key="email.type" :value="email.type">
            <div class="pa-4">
              <div class="text-subtitle-2 font-weight-bold mb-2">Subject: {{ email.subject }}</div>
              <div class="text-body-2" style="white-space: pre-wrap">{{ email.body }}</div>
              <v-btn class="mt-3" size="small" variant="tonal" prepend-icon="mdi-content-copy" @click="copyText(email.body)">
                Copy
              </v-btn>
            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card>

      <!-- Bottom actions -->
      <div class="d-flex ga-3 flex-wrap">
        <v-btn variant="tonal" prepend-icon="mdi-arrow-left" to="/dashboard">Back to Dashboard</v-btn>
        <v-btn variant="tonal" prepend-icon="mdi-plus" to="/analysis/new">Run Another Analysis</v-btn>
      </div>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '../stores/analysis'
import { useAuthStore } from '../stores/auth'
import { analysisApi } from '../api/analysis'

const route = useRoute()
const analysisStore = useAnalysisStore()
const authStore = useAuthStore()
const notify = inject('notify', () => {})

const analysis = computed(() => analysisStore.current)
const polling = ref(false)
const emailTab = ref(null)

const showRewrite = ref(false)
const rewriteLoading = ref(false)
const rewritePolling = ref(false)
const rewriteError = ref(null)
const downloading = ref(false)

const showInterview = ref(false)
const interviewLoading = ref(false)
const interviewPolling = ref(false)
const interviewError = ref(null)

const shareLoading = ref(false)
const shareDialog = ref(false)
const shareToken = ref(null)

const backendUrl = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/api\/v1\/?$/, '')
const shareUrl = computed(() =>
  shareToken.value ? `${backendUrl}/share/${shareToken.value}/` : ''
)
const shareImageUrl = computed(() =>
  shareToken.value ? `${backendUrl}/api/v1/analysis/shared/${shareToken.value}/image.png` : ''
)
const shareText = computed(() => {
  const score = analysis.value?.match_score ?? 0
  const title = analysis.value?.job_title || 'a job'
  return `I just scored ${score}/100 on my resume match for ${title}. How does yours stack up?`
})

// Animated loading steps
const loadingSteps = [
  'Parsing your resume',
  'Reading job description',
  'Scoring keyword match',
  'Rewriting weak bullets',
  'Generating cover letter',
  'Finalizing report',
]
const currentStep = ref(0)
let stepTimer = null

function startLoadingSteps() {
  currentStep.value = 0
  stepTimer = setInterval(() => {
    if (currentStep.value < loadingSteps.length - 1) {
      currentStep.value++
    }
  }, 4000)
}

function stopLoadingSteps() {
  if (stepTimer) {
    clearInterval(stepTimer)
    stepTimer = null
  }
}

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

const foundCount = computed(() =>
  (analysis.value?.keyword_matches || []).filter(k => k.found).length
)

const foundRatio = computed(() => {
  const matches = analysis.value?.keyword_matches || []
  return matches.length ? foundCount.value / matches.length : 0
})

function emailLabel(type) {
  const labels = {
    application_follow_up: 'Follow-Up',
    post_interview_thank_you: 'Thank You',
    networking_outreach: 'Outreach',
  }
  return labels[type] || type
}

async function copyText(text) {
  await navigator.clipboard.writeText(text)
  notify('Copied to clipboard')
}

async function shareScoreCard() {
  shareLoading.value = true
  try {
    if (!shareToken.value) {
      const { data } = await analysisApi.getShareToken(route.params.id)
      shareToken.value = data.share_token
    }
    shareDialog.value = true
  } catch {
    notify('Failed to generate share link')
  } finally {
    shareLoading.value = false
  }
}

async function copyShareLink() {
  await navigator.clipboard.writeText(shareUrl.value)
  notify('Share link copied to clipboard')
}

async function requestRewrite() {
  rewriteLoading.value = true
  rewriteError.value = null
  try {
    const { data } = await analysisApi.requestRewrite(route.params.id)
    if (data.rewritten_resume_text) {
      analysisStore.current = { ...analysisStore.current, rewritten_resume_text: data.rewritten_resume_text }
    } else {
      rewritePolling.value = true
      await analysisStore.pollField(route.params.id, 'rewritten_resume_text')
      rewritePolling.value = false
    }
    await authStore.fetchMe()
  } catch (e) {
    rewriteError.value = e.response?.data?.detail || 'Failed to generate rewrite.'
    rewritePolling.value = false
  } finally {
    rewriteLoading.value = false
  }
}

async function downloadPDF() {
  downloading.value = true
  try {
    const { data } = await analysisApi.downloadRewritePDF(route.params.id)
    const url = window.URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'tailored-resume.pdf'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch {
    rewriteError.value = 'Failed to download PDF.'
  } finally {
    downloading.value = false
  }
}

async function requestInterviewPrep() {
  interviewLoading.value = true
  interviewError.value = null
  try {
    const { data } = await analysisApi.requestInterviewPrep(route.params.id)
    if (data.interview_questions) {
      analysisStore.current = { ...analysisStore.current, interview_questions: data.interview_questions }
      showInterview.value = true
    } else {
      interviewPolling.value = true
      const prevError = analysis.value?.error_message || ''
      await analysisStore.pollField(route.params.id, 'interview_questions', prevError)
      interviewPolling.value = false
      showInterview.value = true
    }
    await authStore.fetchMe()
  } catch (e) {
    interviewError.value = e.response?.data?.detail || e.message || 'Failed to generate questions.'
    interviewPolling.value = false
  } finally {
    interviewLoading.value = false
  }
}

onMounted(async () => {
  const id = route.params.id
  const { data } = await analysisApi.get(id)
  analysisStore.current = data

  if (data.share_token) {
    shareToken.value = data.share_token
  }

  if (data.status === 'pending' || data.status === 'processing') {
    polling.value = true
    startLoadingSteps()
    try {
      await analysisStore.pollAnalysis(id)
    } finally {
      polling.value = false
      stopLoadingSteps()
    }
  }
})

onUnmounted(() => {
  stopLoadingSteps()
})
</script>

<style scoped>
.score-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.section-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.premium-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(135deg, rgba(230, 74, 25, 0.02), rgba(63, 81, 181, 0.02));
}

.pulse-icon {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.08); opacity: 0.8; }
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
