<template>
  <v-container class="py-8">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">Compare Analyses</h1>
      <v-spacer />
      <v-btn variant="tonal" prepend-icon="mdi-arrow-left" to="/dashboard">Dashboard</v-btn>
    </div>

    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert>

    <div v-if="loading" class="text-center py-16">
      <v-progress-circular indeterminate color="primary" size="64" />
    </div>

    <template v-else-if="results.length === 2">
      <v-row>
        <v-col v-for="(r, idx) in results" :key="r.id" cols="12" md="6">
          <v-card elevation="0" class="pa-5 compare-card" :class="{ 'winner-card': winner === idx }">
            <!-- Winner badge -->
            <v-chip
              v-if="winner === idx"
              color="success"
              variant="flat"
              size="small"
              prepend-icon="mdi-trophy"
              class="mb-3"
            >
              Better Match
            </v-chip>

            <div class="text-subtitle-1 font-weight-bold mb-1">{{ r.job_title || 'Untitled' }}</div>
            <div class="text-body-2 text-medium-emphasis mb-4">{{ r.company || '—' }} | {{ new Date(r.created_at).toLocaleDateString() }}</div>

            <div class="text-center mb-4">
              <v-progress-circular
                :model-value="r.match_score"
                :size="100"
                :width="10"
                :color="r.match_score >= 75 ? 'success' : r.match_score >= 50 ? 'warning' : 'error'"
              >
                <span class="text-h5 font-weight-bold">{{ r.match_score }}</span>
              </v-progress-circular>
              <div class="text-body-2 mt-2">Match Score</div>
            </div>

            <v-divider class="mb-3" />

            <div class="d-flex justify-space-between mb-2">
              <span class="text-body-2">Hire Probability</span>
              <span class="font-weight-bold">{{ Math.round(r.hire_probability * 100) }}%</span>
            </div>

            <div class="d-flex justify-space-between mb-2">
              <span class="text-body-2">ATS Issues</span>
              <v-chip :color="r.ats_flags?.length ? 'warning' : 'success'" size="small" variant="tonal">
                {{ r.ats_flags?.length || 0 }}
              </v-chip>
            </div>

            <div class="d-flex justify-space-between mb-2">
              <span class="text-body-2">Keywords Found</span>
              <span class="font-weight-bold">
                {{ (r.keyword_matches || []).filter(k => k.found).length }}/{{ (r.keyword_matches || []).length }}
              </span>
            </div>

            <v-divider class="my-3" />
            <div class="text-body-2 font-weight-bold mb-2">Missing Keywords</div>
            <div class="d-flex flex-wrap ga-1">
              <v-chip
                v-for="kw in (r.keyword_matches || []).filter(k => !k.found)"
                :key="kw.keyword"
                color="error"
                variant="tonal"
                size="small"
              >
                {{ kw.keyword }}
              </v-chip>
              <span v-if="!(r.keyword_matches || []).filter(k => !k.found).length" class="text-medium-emphasis text-body-2">None</span>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Score comparison bar -->
      <v-card elevation="0" class="pa-5 mt-6 section-card">
        <div class="text-h6 font-weight-bold mb-4">Score Comparison</div>
        <div v-for="r in results" :key="r.id" class="mb-3">
          <div class="text-body-2 mb-1">{{ r.job_title || 'Untitled' }} @ {{ r.company || '—' }}</div>
          <v-progress-linear
            :model-value="r.match_score"
            :color="r.match_score >= 75 ? 'success' : r.match_score >= 50 ? 'warning' : 'error'"
            height="20"
            rounded
          >
            <strong>{{ r.match_score }}</strong>
          </v-progress-linear>
        </div>
      </v-card>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { analysisApi } from '../api/analysis'

const route = useRoute()
const results = ref([])
const loading = ref(true)
const error = ref(null)

const winner = computed(() => {
  if (results.value.length !== 2) return null
  const [a, b] = results.value
  if (a.match_score === b.match_score) return null
  return a.match_score > b.match_score ? 0 : 1
})

onMounted(async () => {
  const ids = (route.query.ids || '').split(',').filter(Boolean)
  if (ids.length !== 2) {
    error.value = 'Select exactly 2 analyses to compare.'
    loading.value = false
    return
  }
  try {
    const { data } = await analysisApi.compare(ids[0], ids[1])
    results.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load comparison.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.compare-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: border-color 0.2s;
}

.winner-card {
  border-color: #2E7D32 !important;
  box-shadow: 0 0 24px rgba(46, 125, 50, 0.08) !important;
}

.section-card {
  border: 1px solid rgba(0, 0, 0, 0.06);
}
</style>
