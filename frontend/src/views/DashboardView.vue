<template>
  <v-container class="py-8">
    <!-- Credits banner -->
    <v-card v-if="authStore.paymentsEnabled" elevation="2" rounded="lg" class="mb-6 pa-4">
      <div class="d-flex align-center flex-wrap ga-4">
        <div>
          <div class="text-h6 font-weight-bold">
            <v-icon icon="mdi-star-circle" color="amber" class="mr-1" />
            {{ credits }} credits remaining
          </div>
          <div class="text-body-2 text-medium-emphasis">Each analysis costs 1 credit. Resume rewrite and interview prep cost 1 credit each.</div>
        </div>
        <v-spacer />
        <v-btn color="success" variant="flat" prepend-icon="mdi-plus" @click="selectedPackIndex = null; showBuyDialog = true">
          Buy Credits
        </v-btn>
      </div>
    </v-card>

    <!-- Daily usage banner (free mode) -->
    <v-card v-if="!authStore.paymentsEnabled && !isAdmin" elevation="2" rounded="lg" class="mb-6 pa-4">
      <div class="d-flex align-center flex-wrap ga-4">
        <div>
          <div class="text-h6 font-weight-bold">
            <v-icon icon="mdi-lightning-bolt" color="primary" class="mr-1" />
            {{ dailyRemaining }} of {{ dailyLimit }} free analyses remaining today
          </div>
          <div class="text-body-2 text-medium-emphasis">Your limit resets on a rolling 24-hour basis.</div>
        </div>
      </div>
    </v-card>

    <!-- Quick actions -->
    <div class="d-flex align-center mb-6 flex-wrap ga-3">
      <h1 class="text-h4 font-weight-bold">Dashboard</h1>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-upload" to="/upload">Upload Resume</v-btn>
      <v-btn variant="tonal" prepend-icon="mdi-robot" to="/analysis/new">New Analysis</v-btn>
      <v-btn variant="tonal" prepend-icon="mdi-linkedin" to="/linkedin">LinkedIn</v-btn>
    </div>

    <!-- My Resumes -->
    <h2 class="text-h6 font-weight-bold mb-3">My Resumes</h2>
    <v-alert v-if="resumeStore.error" type="error" density="compact" class="mb-4">
      {{ resumeStore.error }}
    </v-alert>

    <v-card elevation="2" rounded="lg" class="mb-8">
      <v-data-table
        :headers="resumeHeaders"
        :items="resumeStore.resumes"
        :loading="resumeStore.loading"
        no-data-text="No resumes yet. Upload one to get started."
      >
        <template #item.original_filename="{ item }">
          <div class="d-flex align-center ga-2">
            <v-icon
              :icon="item.mime_type === 'application/pdf' ? 'mdi-file-pdf-box' : 'mdi-file-word'"
              color="red-darken-1"
            />
            {{ item.original_filename }}
          </div>
        </template>

        <template #item.uploaded_at="{ item }">
          {{ new Date(item.uploaded_at).toLocaleDateString() }}
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              size="small"
              color="primary"
              variant="tonal"
              prepend-icon="mdi-robot"
              :to="`/analysis/new?resume=${item.id}`"
            >
              Analyze
            </v-btn>
            <v-btn
              size="small"
              color="error"
              variant="text"
              icon="mdi-delete"
              @click="confirmDelete(item)"
            />
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Analysis History -->
    <div class="d-flex align-center mb-3">
      <h2 class="text-h6 font-weight-bold">Analysis History</h2>
      <v-spacer />
      <v-btn
        v-if="compareIds.length === 2"
        size="small"
        color="secondary"
        variant="tonal"
        prepend-icon="mdi-compare"
        :to="`/analysis/compare?ids=${compareIds.join(',')}`"
      >
        Compare Selected
      </v-btn>
    </div>

    <v-card elevation="2" rounded="lg">
      <v-data-table
        :headers="analysisHeaders"
        :items="analysisStore.analyses"
        :loading="analysisStore.loading"
        no-data-text="No analyses yet."
      >
        <template #item.select="{ item }">
          <v-checkbox
            v-if="item.status === 'done'"
            :model-value="compareIds.includes(item.id)"
            hide-details
            density="compact"
            @update:model-value="toggleCompare(item.id)"
          />
        </template>

        <template #item.match_score="{ item }">
          <v-chip
            v-if="item.match_score != null"
            :color="item.match_score >= 75 ? 'success' : item.match_score >= 50 ? 'warning' : 'error'"
            size="small"
            variant="tonal"
          >
            {{ item.match_score }}
          </v-chip>
          <span v-else class="text-medium-emphasis">—</span>
        </template>

        <template #item.status="{ item }">
          <v-chip
            :color="{ done: 'success', failed: 'error', pending: 'grey', processing: 'info' }[item.status]"
            size="small"
            variant="tonal"
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template #item.created_at="{ item }">
          {{ new Date(item.created_at).toLocaleDateString() }}
        </template>

        <template #item.actions="{ item }">
          <v-btn
            size="small"
            color="primary"
            variant="tonal"
            prepend-icon="mdi-eye"
            :to="`/analysis/${item.id}`"
          >
            View
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete resume?</v-card-title>
        <v-card-text>This action cannot be undone.</v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" :loading="deleting" @click="doDelete">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Buy Credits dialog -->
    <v-dialog v-if="authStore.paymentsEnabled" v-model="showBuyDialog" max-width="500">
      <v-card>
        <v-card-title class="pt-6 text-h6 font-weight-bold">Buy Credits</v-card-title>
        <v-card-text>
          <v-alert v-if="paymentStore.error" type="error" density="compact" class="mb-4">
            {{ paymentStore.error }}
          </v-alert>
          <v-list>
            <v-list-item
              v-for="(pack, i) in paymentStore.packs"
              :key="i"
              @click="selectedPackIndex = i"
              :disabled="paymentStore.loading"
              :active="selectedPackIndex === i"
              active-color="success"
              class="mb-2"
              rounded="lg"
              border
            >
              <template #prepend>
                <v-icon icon="mdi-star-circle" color="amber" />
              </template>
              <v-list-item-title class="font-weight-bold">{{ pack.label }}</v-list-item-title>
              <v-list-item-subtitle>${{ (pack.price_cents / 100).toFixed(2) }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showBuyDialog = false">Cancel</v-btn>
          <v-btn
            color="success"
            variant="flat"
            :disabled="selectedPackIndex === null"
            :loading="paymentStore.loading"
            @click="paymentStore.buyCreditPack(selectedPackIndex)"
          >
            Buy Now
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useAnalysisStore } from '../stores/analysis'
import { usePaymentStore } from '../stores/payment'
import { useAuthStore } from '../stores/auth'

const resumeStore = useResumeStore()
const analysisStore = useAnalysisStore()
const paymentStore = usePaymentStore()
const authStore = useAuthStore()

const credits = computed(() => authStore.user?.profile?.credits_remaining ?? 0)
const isAdmin = computed(() => authStore.user?.is_staff)
const dailyLimit = computed(() => authStore.user?.daily_analyses_limit ?? 3)
const dailyRemaining = computed(() => dailyLimit.value - (authStore.user?.daily_analyses_used ?? 0))

const resumeHeaders = [
  { title: 'File', key: 'original_filename' },
  { title: 'Uploaded', key: 'uploaded_at', width: 130 },
  { title: 'Actions', key: 'actions', sortable: false, width: 200 },
]

const analysisHeaders = [
  { title: '', key: 'select', sortable: false, width: 50 },
  { title: 'Job Title', key: 'job_title' },
  { title: 'Company', key: 'company' },
  { title: 'Score', key: 'match_score', width: 90 },
  { title: 'Status', key: 'status', width: 110 },
  { title: 'Date', key: 'created_at', width: 110 },
  { title: '', key: 'actions', sortable: false, width: 100 },
]

const deleteDialog = ref(false)
const selectedResume = ref(null)
const deleting = ref(false)
const showBuyDialog = ref(false)
const selectedPackIndex = ref(null)
const compareIds = ref([])

onMounted(async () => {
  await authStore.fetchMe()
  resumeStore.fetchResumes()
  analysisStore.fetchAnalyses()
  if (authStore.paymentsEnabled) paymentStore.fetchPacks()
})

function confirmDelete(item) {
  selectedResume.value = item
  deleteDialog.value = true
}

async function doDelete() {
  deleting.value = true
  try {
    await resumeStore.deleteResume(selectedResume.value.id)
    deleteDialog.value = false
  } finally {
    deleting.value = false
  }
}

function toggleCompare(id) {
  const idx = compareIds.value.indexOf(id)
  if (idx >= 0) {
    compareIds.value.splice(idx, 1)
  } else if (compareIds.value.length < 2) {
    compareIds.value.push(id)
  } else {
    compareIds.value = [compareIds.value[1], id]
  }
}
</script>
