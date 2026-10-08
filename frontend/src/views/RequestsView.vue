<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Search,
  RefreshCw,
  CheckCircle2,
  Clock3,
  FileText,
  Package,
} from 'lucide-vue-next'

import api from '@/services/api'

const requests = ref([])
const loading = ref(true)
const verifying = ref(null)
const search = ref('')
const error = ref('')

async function loadRequests() {
  loading.value = true
  error.value = ''

  try {
    const { data } = await api.get('/material-requests')
    requests.value = data
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load material requests.'
  } finally {
    loading.value = false
  }
}

async function verifyRequest(id) {
  verifying.value = id
  error.value = ''

  try {
    await api.put(`/material-requests/${id}/verify`)
    await loadRequests()
  } catch (err) {
    console.error(err)
    error.value =
      err.response?.data?.detail ||
      'Unable to verify this request.'
  } finally {
    verifying.value = null
  }
}

const filteredRequests = computed(() => {

  const q = search.value.trim().toLowerCase()

  if (!q) {
    return requests.value
  }

  return requests.value.filter((r) =>
    [
      r.request_no,
      r.material_name,
      r.request_type,
      r.status,
      r.created_by_username,
    ]
      .filter(Boolean)
      .some((value) =>
        String(value).toLowerCase().includes(q)
      )
  )
})

const pendingCount = computed(() =>
  requests.value.filter(
    r => r.status === 'PENDING_VERIFICATION'
  ).length
)

const verifiedCount = computed(() =>
  requests.value.filter(
    r => r.status === 'VERIFIED'
  ).length
)

function statusLabel(status) {
  return status === 'PENDING_VERIFICATION'
    ? 'Pending Verification'
    : status === 'VERIFIED'
      ? 'Verified'
      : status
}

function statusClass(status) {
  return status === 'PENDING_VERIFICATION'
    ? 'pending'
    : status === 'VERIFIED'
      ? 'verified'
      : 'other'
}

onMounted(loadRequests)
</script>

<template>
  <div class="requests-page">

    <header class="page-head">
      <div>
        <p class="eyebrow">Procurement workflow</p>
        <h1>Material Requests</h1>
        <p class="sub">
          Review and verify material requirements before purchase processing.
        </p>
      </div>

      <button class="refresh-btn" @click="loadRequests">
        <RefreshCw :size="16" />
        Refresh
      </button>
    </header>

    <div class="summary-row">

      <div class="summary-card">
        <span class="summary-icon warning">
          <Clock3 :size="18" />
        </span>
        <div>
          <span>Pending Verification</span>
          <strong>{{ pendingCount }}</strong>
        </div>
      </div>

      <div class="summary-card">
        <span class="summary-icon success">
          <CheckCircle2 :size="18" />
        </span>
        <div>
          <span>Verified</span>
          <strong>{{ verifiedCount }}</strong>
        </div>
      </div>

      <div class="summary-card">
        <span class="summary-icon info">
          <FileText :size="18" />
        </span>
        <div>
          <span>Total Requests</span>
          <strong>{{ requests.length }}</strong>
        </div>
      </div>

    </div>

    <div v-if="error" class="error-box">
      {{ error }}
    </div>

    <section class="panel">

      <div class="panel-head">

        <div>
          <h2>Request Queue</h2>
          <p>Live data from the MMS database</p>
        </div>

        <label class="search">
          <Search :size="16" />
          <input
            v-model="search"
            type="search"
            placeholder="Search requests, materials..."
          />
        </label>

      </div>

      <div v-if="loading" class="loading">
        <RefreshCw :size="20" class="spin" />
        Loading material requests...
      </div>

      <div v-else-if="!filteredRequests.length" class="empty">
        <Package :size="30" />
        <strong>No material requests found</strong>
        <span>Try another search or create a new request.</span>
      </div>

      <div v-else class="table-wrap">

        <table>

          <thead>
            <tr>
              <th>Request</th>
              <th>Material</th>
              <th>Quantity</th>
              <th>Type</th>
              <th>Required Date</th>
              <th>Created By</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>

            <tr
              v-for="request in filteredRequests"
              :key="request.id"
            >

              <td>
                <span class="request-no">
                  {{ request.request_no }}
                </span>
              </td>

              <td>
                <div class="material">
                  <span class="material-icon">
                    <Package :size="15" />
                  </span>
                  <div>
                    <strong>{{ request.material_name }}</strong>
                    <small>{{ request.unit }}</small>
                  </div>
                </div>
              </td>

              <td class="quantity">
                {{ request.quantity }}
                {{ request.unit }}
              </td>

              <td>
                <span
                  class="type"
                  :class="request.request_type.toLowerCase()"
                >
                  {{ request.request_type }}
                </span>
              </td>

              <td>
                {{ request.required_date || '—' }}
              </td>

              <td>
                {{ request.created_by_username }}
              </td>

              <td>
                <span
                  class="status"
                  :class="statusClass(request.status)"
                >
                  <i />
                  {{ statusLabel(request.status) }}
                </span>
              </td>

              <td>

                <button
                  v-if="request.status === 'PENDING_VERIFICATION'"
                  class="verify-btn"
                  :disabled="verifying === request.id"
                  @click="verifyRequest(request.id)"
                >
                  <RefreshCw
                    v-if="verifying === request.id"
                    :size="14"
                    class="spin"
                  />
                  <CheckCircle2
                    v-else
                    :size="14"
                  />

                  {{
                    verifying === request.id
                      ? 'Verifying...'
                      : 'Verify'
                  }}
                </button>

                <span
                  v-else
                  class="verified-label"
                >
                  <CheckCircle2 :size="15" />
                  Verified
                </span>

              </td>

            </tr>

          </tbody>

        </table>

      </div>

    </section>

  </div>
</template>

<style scoped>
.requests-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}

.page-head h1 {
  font-size: 26px;
  font-weight: 650;
  letter-spacing: -0.025em;
  margin: 4px 0;
}

.sub {
  color: var(--c-muted);
}

.refresh-btn,
.verify-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text-2);
  border-radius: var(--radius);
  padding: 9px 13px;
  font-size: 13px;
  font-weight: 550;
  cursor: pointer;
}

.refresh-btn:hover {
  border-color: var(--c-border-strong);
  background: var(--c-surface-2);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
}

.summary-card div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.summary-card span:not(.summary-icon) {
  color: var(--c-muted);
  font-size: 12px;
}

.summary-card strong {
  font-size: 24px;
  font-weight: 650;
}

.summary-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: grid;
  place-items: center;
}

.summary-icon.warning {
  color: var(--c-warning);
  background: var(--c-warning-bg);
}

.summary-icon.success {
  color: var(--c-success);
  background: var(--c-success-bg);
}

.summary-icon.info {
  color: var(--c-info);
  background: var(--c-info-bg);
}

.panel {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid var(--c-border);
}

.panel-head h2 {
  font-size: 15px;
  font-weight: 650;
}

.panel-head p {
  margin-top: 3px;
  color: var(--c-muted);
  font-size: 12px;
}

.search {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 300px;
  height: 36px;
  padding: 0 11px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  color: var(--c-muted);
}

.search:focus-within {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 3px var(--c-primary-100);
}

.search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--c-text);
  font: inherit;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

th {
  padding: 11px 16px;
  text-align: left;
  color: var(--c-muted);
  background: var(--c-surface-2);
  border-bottom: 1px solid var(--c-border);
  font-size: 11px;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: .05em;
}

td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--c-border);
  font-size: 13px;
  color: var(--c-text-2);
}

tbody tr:hover {
  background: var(--c-surface-2);
}

.request-no {
  font-weight: 650;
  font-family: var(--font-mono);
  color: var(--c-text);
}

.material {
  display: flex;
  align-items: center;
  gap: 9px;
}

.material-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: var(--c-primary);
  background: var(--c-primary-50);
}

.material div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.material strong {
  font-weight: 600;
  color: var(--c-text);
}

.material small {
  color: var(--c-muted);
  font-size: 11px;
}

.quantity {
  font-weight: 600;
}

.type,
.status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 99px;
  padding: 4px 8px;
}

.type.new {
  color: var(--c-info);
  background: var(--c-info-bg);
}

.type.advance {
  color: var(--c-violet);
  background: var(--c-violet-bg);
}

.status.pending {
  color: var(--c-warning);
  background: var(--c-warning-bg);
}

.status.verified {
  color: var(--c-success);
  background: var(--c-success-bg);
}

.status.other {
  color: var(--c-muted);
  background: var(--c-surface-2);
}

.status i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.verify-btn {
  color: #fff;
  background: var(--c-primary);
  border-color: var(--c-primary);
}

.verify-btn:hover:not(:disabled) {
  filter: brightness(.94);
}

.verify-btn:disabled {
  opacity: .6;
  cursor: wait;
}

.verified-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--c-success);
  font-size: 12px;
  font-weight: 600;
}

.error-box {
  padding: 12px 14px;
  border: 1px solid var(--c-danger);
  border-radius: var(--radius);
  color: var(--c-danger);
  background: var(--c-danger-bg);
  font-size: 13px;
}

.loading,
.empty {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--c-muted);
}

.empty strong {
  color: var(--c-text);
}

.spin {
  animation: spin .8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 800px) {
  .summary-row {
    grid-template-columns: 1fr;
  }

  .page-head {
    align-items: flex-start;
  }

  .panel-head {
    align-items: stretch;
    flex-direction: column;
  }

  .search {
    width: 100%;
  }
}
</style>
