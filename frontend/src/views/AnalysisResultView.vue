<template>
  <v-container class="py-8">
    <!-- Polling -->
    <div v-if="polling" class="text-center py-16">
      <v-progress-circular indeterminate color="primary" size="72" class="mb-6" />
      <div class="text-h6">AI is analyzing your resume...</div>
      <div class="text-body-2 text-medium-emphasis mt-2">This usually takes 15-30 seconds.</div>
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

      <!-- Keyword Heatmap -->
      <v-card v-if="analysis.keyword_matches?.length" elevation="2" rounded="lg" class="mb-4 pa-4">
        <div class="text-h6 font-weight-bold mb-3">
          <v-icon icon="mdi-fire" color="deep-orange" class="mr-2" />Keyword Match Heatmap
        </div>
        <div class="text-body-2 text-medium-emphasis mb-3">
          {{ foundCount }}/{{ analysis.keyword_matches.length }} keywords found in your resume
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
      <v-card v-if="analysis.cover_letter" elevation="2" rounded="lg" class="pa-4 mb-4">
        <div class="text-h6 font-weight-bold mb-3">
          <v-icon icon="mdi-email-edit" color="primary" class="mr-2" />Cover Letter
        </div>
        <div class="text-body-2" style="white-space: pre-wrap">{{ analysis.cover_letter }}</div>
        <v-btn class="mt-4" variant="tonal" prepend-icon="mdi-content-copy" @click="copyText(analysis.cover_letter, 'coverCopied')">
          {{ coverCopied ? 'Copied!' : 'Copy' }}
        </v-btn>
      </v-card>

      <!-- Follow-up Emails -->
      <v-card v-if="analysis.follow_up_emails?.length" elevation="2" rounded="lg" class="pa-4 mb-4">
        <div class="text-h6 font-weight-bold mb-3">
          <v-icon icon="mdi-email-multiple" color="teal" class="mr-2" />Follow-Up Email Templates
        </div>
        <v-tabs v-model="emailTab" color="teal">
          <v-tab v-for="email in analysis.follow_up_emails" :key="email.type" :value="email.type">
            {{ emailLabel(email.type) }}
          </v-tab>
        </v-tabs>
        <v-tabs-window v-model="emailTab">
          <v-tabs-window-item v-for="email in analysis.follow_up_emails" :key="email.type" :value="email.type">
            <div class="pa-4">
              <div class="text-subtitle-2 font-weight-bold mb-2">Subject: {{ email.subject }}</div>
              <div class="text-body-2" style="white-space: pre-wrap">{{ email.body }}</div>
              <v-btn class="mt-3" size="small" variant="tonal" prepend-icon="mdi-content-copy" @click="copyText(email.body, 'emailCopied')">
                {{ emailCopied ? 'Copied!' : 'Copy' }}
              </v-btn>
            </div>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card>

      <!-- Premium Actions: Resume Rewrite + Interview Prep -->
      <v-row class="mb-4">
        <v-col cols="12" md="6">
          <v-card elevation="2" rounded="lg" class="pa-4 h-100">
            <div class="text-h6 font-weight-bold mb-2">
              <v-icon icon="mdi-file-document-edit" color="deep-purple" class="mr-2" />Full Resume Rewrite
            </div>
            <div class="text-body-2 text-medium-emphasis mb-4">
              AI rewrites your entire resume, optimized for this specific job description. Download as PDF.
            </div>
            <template v-if="analysis.rewritten_resume_text">
              <v-alert type="success" variant="tonal" density="compact" class="mb-3">Rewrite ready!</v-alert>
              <div class="d-flex ga-2">
                <v-btn color="deep-purple" variant="flat" prepend-icon="mdi-download" @click="downloadPDF" :loading="downloading">
                  Download PDF
                </v-btn>
                <v-btn variant="tonal" prepend-icon="mdi-eye" @click="showRewrite = !showRewrite">
                  {{ showRewrite ? 'Hide' : 'Preview' }}
                </v-btn>
              </div>
              <div v-if="showRewrite" class="mt-3 pa-3 rounded bg-grey-lighten-4" style="white-space:pre-wrap;font-size:0.85rem;">{{ analysis.rewritten_resume_text }}</div>
            </template>
            <template v-else-if="rewritePolling">
              <v-progress-linear indeterminate color="deep-purple" class="mb-2" />
              <div class="text-body-2">Generating rewrite...</div>
            </template>
            <template v-else>
              <v-btn color="deep-purple" variant="flat" prepend-icon="mdi-creation" @click="requestRewrite" :loading="rewriteLoading">
                Generate Rewrite (1 credit)
              </v-btn>
            </template>
            <v-alert v-if="rewriteError" type="error" density="compact" class="mt-2">{{ rewriteError }}</v-alert>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card elevation="2" rounded="lg" class="pa-4 h-100">
            <div class="text-h6 font-weight-bold mb-2">
              <v-icon icon="mdi-account-question" color="indigo" class="mr-2" />Interview Prep
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
              <v-progress-linear indeterminate color="indigo" class="mb-2" />
              <div class="text-body-2">Generating questions...</div>
            </template>
            <template v-else>
              <v-btn color="indigo" variant="flat" prepend-icon="mdi-creation" @click="requestInterviewPrep" :loading="interviewLoading">
                Generate Questions (1 credit)
              </v-btn>
            </template>
            <v-alert v-if="interviewError" type="error" density="compact" class="mt-2">{{ interviewError }}</v-alert>
          </v-card>
        </v-col>
      </v-row>

      <!-- Interview Questions Accordion -->
      <v-expansion-panels v-if="showInterview && analysis.interview_questions?.length" class="mb-4">
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
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalysisStore } from '../stores/analysis'
import { useAuthStore } from '../stores/auth'
import { analysisApi } from '../api/analysis'

const route = useRoute()
const analysisStore = useAnalysisStore()
const authStore = useAuthStore()

const analysis = computed(() => analysisStore.current)
const polling = ref(false)
const coverCopied = ref(false)
const emailCopied = ref(false)
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

function emailLabel(type) {
  const labels = {
    application_follow_up: 'Follow-Up',
    post_interview_thank_you: 'Thank You',
    networking_outreach: 'Outreach',
  }
  return labels[type] || type
}

async function copyText(text, flagName) {
  await navigator.clipboard.writeText(text)
  if (flagName === 'coverCopied') {
    coverCopied.value = true
    setTimeout(() => (coverCopied.value = false), 2000)
  } else {
    emailCopied.value = true
    setTimeout(() => (emailCopied.value = false), 2000)
  }
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
      await analysisStore.pollField(route.params.id, 'interview_questions')
      interviewPolling.value = false
      showInterview.value = true
    }
    await authStore.fetchMe()
  } catch (e) {
    interviewError.value = e.response?.data?.detail || 'Failed to generate questions.'
    interviewPolling.value = false
  } finally {
    interviewLoading.value = false
  }
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
