<template>
  <v-container class="py-8">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">My Resumes</h1>
      <v-spacer />
      <v-btn color="primary" prepend-icon="mdi-upload" to="/upload">Upload Resume</v-btn>
    </div>

    <v-alert v-if="resumeStore.error" type="error" density="compact" class="mb-4">
      {{ resumeStore.error }}
    </v-alert>

    <v-card elevation="2" rounded="lg">
      <v-data-table
        :headers="headers"
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

        <template #item.is_paid="{ item }">
          <v-chip :color="item.is_paid ? 'success' : 'warning'" size="small" variant="tonal">
            {{ item.is_paid ? 'Paid' : 'Unpaid' }}
          </v-chip>
        </template>

        <template #item.uploaded_at="{ item }">
          {{ new Date(item.uploaded_at).toLocaleDateString() }}
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn
              v-if="!item.is_paid && !isAdmin"
              size="small"
              color="success"
              variant="tonal"
              prepend-icon="mdi-credit-card"
              :loading="payment.loading && selectedId === item.id"
              @click="pay(item)"
            >
              Pay
            </v-btn>
            <v-btn
              v-if="item.is_paid || isAdmin"
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
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useResumeStore } from '../stores/resume'
import { usePaymentStore } from '../stores/payment'
import { useAuthStore } from '../stores/auth'

const resumeStore = useResumeStore()
const payment = usePaymentStore()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.user?.is_staff)

const headers = [
  { title: 'File', key: 'original_filename' },
  { title: 'Status', key: 'is_paid', width: 100 },
  { title: 'Uploaded', key: 'uploaded_at', width: 130 },
  { title: 'Actions', key: 'actions', sortable: false, width: 200 },
]

const deleteDialog = ref(false)
const selectedResume = ref(null)
const selectedId = ref(null)
const deleting = ref(false)

onMounted(() => resumeStore.fetchResumes())

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

async function pay(item) {
  selectedId.value = item.id
  await payment.initiateCheckout(item.id)
  selectedId.value = null
}
</script>
