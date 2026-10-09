<script setup>
import { onMounted, ref } from 'vue'
import api from '@/services/api'
import { Check, X, RefreshCw, ShieldCheck } from 'lucide-vue-next'

const queue = ref([])
const approvedToday = ref(0)
const loading = ref(true)
const busyId = ref(null)
const error = ref('')
const notice = ref('')
const rejecting = ref(null)
const rejectionReason = ref('')

function formatDate(value) {
  if (!value) return 'Not recorded'
  const date = new Date(value)
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function loadQueue() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.get('/purchase-approval/queue')
    queue.value = response.data.queue || []
    approvedToday.value = response.data.approved_today || 0
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load the approval queue.'
  } finally {
    loading.value = false
  }
}

async function approveRequest(request) {
  if (!window.confirm(`Approve material request ${request.request_no}?`)) return
  busyId.value = request.id
  error.value = ''
  notice.value = ''
  try {
    const response = await api.post(`/material-requests/${request.id}/approve`)
    notice.value = response.data.message || `${request.request_no} approved.`
    await loadQueue()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Approval failed.'
  } finally {
    busyId.value = null
  }
}

function startReject(request) {
  rejecting.value = request
  rejectionReason.value = ''
  error.value = ''
  notice.value = ''
}

async function rejectRequest() {
  const request = rejecting.value
  const reason = rejectionReason.value.trim()
  if (!request || !reason) {
    error.value = 'Enter a rejection reason before continuing.'
    return
  }

  busyId.value = request.id
  error.value = ''
  notice.value = ''
  try {
    const response = await api.post(`/material-requests/${request.id}/reject`,
      { reason }
    )
    notice.value = response.data.message || `${request.request_no} rejected.`
    rejecting.value = null
    await loadQueue()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Rejection failed.'
  } finally {
    busyId.value = null
  }
}

onMounted(loadQueue)
</script>

<template>
  <section class="approval-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow"><ShieldCheck :size="15" /> PURCHASE WORKFLOW</div>
        <h1>Purchase Approval</h1>
        <p class="subtitle">Review receiver-verified material requests and record your decision.</p>
      </div>
      <button class="refresh-btn" :disabled="loading" @click="loadQueue">
        <RefreshCw :size="16" /> Refresh
      </button>
    </div>

    <div class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">Awaiting review</span>
        <strong>{{ queue.length }}</strong>
        <span class="summary-note">Verified requests pending decision</span>
      </article>
      <article class="summary-card">
        <span class="summary-label">Advance requests</span>
        <strong>{{ queue.filter(item => item.request_type === 'ADVANCE').length }}</strong>
        <span class="summary-note">Requests raised in advance</span>
      </article>
      <article class="summary-card">
        <span class="summary-label">Approved today</span>
        <strong>{{ approvedToday }}</strong>
        <span class="summary-note">Recorded by the backend today</span>
      </article>
    </div>

    <div v-if="error" class="feedback error" role="alert">{{ error }}</div>
    <div v-if="notice" class="feedback success" role="status">{{ notice }}</div>

    <div class="section-heading">
      <div>
        <h2>Review queue</h2>
        <p>Only receiver-verified requests awaiting approval are shown.</p>
      </div>
      <span class="queue-count">{{ queue.length }} requests</span>
    </div>

    <div v-if="loading" class="state-panel">Loading requests from the server…</div>
    <div v-else-if="queue.length === 0" class="state-panel">
      <ShieldCheck :size="28" />
      <h3>You're all caught up</h3>
      <p>There are no verified requests awaiting approval.</p>
    </div>

    <div v-else class="request-list">
      <article v-for="request in queue" :key="request.id" class="request-card">
        <div class="request-top">
          <div>
            <span class="request-number">{{ request.request_no }}</span>
            <span class="type-tag" :class="request.request_type === 'ADVANCE' ? 'advance' : 'new'">
              {{ request.request_type }}
            </span>
          </div>
          <span class="pending-tag">Pending review</span>
        </div>

        <h3>{{ request.material_name }}</h3>
        <div class="quantity">{{ request.quantity }} {{ request.unit }}</div>

        <div class="details-grid">
          <div>
            <span>Required date</span>
            <strong>{{ formatDate(request.required_date) }}</strong>
          </div>
          <div>
            <span>Requested by</span>
            <strong>{{ request.created_by_username || '—' }}</strong>
          </div>
          <div>
            <span>Verified by</span>
            <strong>{{ request.verified_by_username || 'Not recorded' }}</strong>
          </div>
          <div>
            <span>Verification date</span>
            <strong>{{ formatDate(request.verified_at) }}</strong>
          </div>
        </div>

        <div v-if="request.remarks" class="remarks">
          <span>Remarks</span>
          <p>{{ request.remarks }}</p>
        </div>

        <div class="card-actions">
          <button class="reject-btn" :disabled="busyId === request.id" @click="startReject(request)">
            <X :size="16" /> Reject
          </button>
          <button class="approve-btn" :disabled="busyId === request.id" @click="approveRequest(request)">
            <Check :size="16" /> {{ busyId === request.id ? 'Processing…' : 'Approve request' }}
          </button>
        </div>
      </article>
    </div>

    <div v-if="rejecting" class="modal-backdrop" @click.self="rejecting = null">
      <section class="reject-modal" role="dialog" aria-modal="true" aria-labelledby="reject-title">
        <h2 id="reject-title">Reject {{ rejecting.request_no }}</h2>
        <p>Please provide a reason for rejecting this material request.</p>
        <textarea v-model="rejectionReason" rows="4" maxlength="500"
          placeholder="Enter rejection reason…"></textarea>
        <div class="modal-actions">
          <button class="refresh-btn" @click="rejecting = null">Cancel</button>
          <button class="reject-btn" :disabled="!rejectionReason.trim() || busyId === rejecting.id"
            @click="rejectRequest">
            Confirm rejection
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.approval-page {
  --ap-bg: #F5F6F8;
  --ap-surface: #FFFFFF;
  --ap-border: #DFE3E8;
  --ap-text: #1A2233;
  --ap-muted: #5C6B7A;
  --ap-primary: #1F3B57;
  --ap-accent: #C77D2E;
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 8px 0 40px;
  color: var(--ap-text);
  animation: fadeUp .3s ease both;
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(7px); }
  to { opacity: 1; transform: translateY(0); }
}
.page-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 26px;
}
.eyebrow {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--ap-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .1em;
  margin-bottom: 10px;
}
h1 {
  color: var(--ap-text);
  font-size: 29px;
  font-weight: 700;
  letter-spacing: -.8px;
}
.subtitle, .section-heading p {
  color: var(--ap-muted);
  margin-top: 7px;
  font-size: 13px;
  line-height: 1.6;
}
button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  min-height: 39px;
  border-radius: 7px;
  padding: 9px 15px;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background .15s ease, border-color .15s ease, transform .15s ease;
}
button:active:not(:disabled) { transform: translateY(1px); }
button:disabled { opacity: .55; cursor: not-allowed; }
.refresh-btn {
  background: var(--ap-surface);
  border: 1px solid var(--ap-border);
  color: var(--ap-text);
}
.refresh-btn:hover:not(:disabled) { background: #EEF0F3; }
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 15px;
  margin-bottom: 32px;
}
.summary-card {
  position: relative;
  overflow: hidden;
  min-height: 132px;
  padding: 21px 22px;
  border: 1px solid var(--ap-border);
  border-radius: 9px;
  background: var(--ap-surface);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  box-shadow: 0 1px 2px rgba(26,34,51,.05);
}
.summary-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--ap-primary);
}
.summary-card:nth-child(2)::before { background: var(--ap-accent); }
.summary-card:nth-child(3)::before { background: #2F8F5B; }
.summary-label, .details-grid span, .remarks > span {
  color: var(--ap-muted);
  font-size: 12px;
  font-weight: 500;
}
.summary-card strong {
  color: var(--ap-text);
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -1px;
  line-height: 1.2;
}
.summary-note { font-size: 11px; color: #8A96A5; }
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 17px;
}
.section-heading h2 {
  color: var(--ap-text);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -.3px;
}
.queue-count {
  color: var(--ap-muted);
  font-size: 12px;
  white-space: nowrap;
  background: #EEF0F3;
  border-radius: 5px;
  padding: 6px 9px;
}
.request-list { display: grid; gap: 15px; }
.request-card {
  padding: 23px 24px;
  border: 1px solid var(--ap-border);
  background: var(--ap-surface);
  border-radius: 9px;
  box-shadow: 0 1px 2px rgba(26,34,51,.05);
  transition: border-color .18s ease, box-shadow .18s ease;
}
.request-card:hover {
  border-color: #BAC5D0;
  box-shadow: 0 4px 14px rgba(26,34,51,.07);
}
.request-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.request-number {
  color: var(--ap-primary);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  font-weight: 600;
  margin-right: 10px;
}
.type-tag, .pending-tag {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .045em;
}
.type-tag.new { background: #E9F1F5; color: #3B7A9E; }
.type-tag.advance { background: #ECEAFA; color: #6A5ACD; }
.pending-tag { background: #FBF0E2; color: #A7651F; }
.request-card h3 {
  color: var(--ap-text);
  font-size: 19px;
  font-weight: 700;
  letter-spacing: -.3px;
  margin: 19px 0 5px;
}
.quantity { font-size: 13px; color: var(--ap-muted); }
.details-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-top: 22px;
  padding: 18px 0;
  border-top: 1px solid var(--ap-border);
  border-bottom: 1px solid var(--ap-border);
}
.details-grid div { display: flex; flex-direction: column; gap: 7px; min-width: 0; }
.details-grid strong {
  color: var(--ap-text);
  font-size: 12px;
  font-weight: 600;
  overflow-wrap: anywhere;
}
.remarks { padding-top: 15px; }
.remarks p {
  color: var(--ap-muted);
  font-size: 13px;
  margin-top: 6px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  margin-top: 21px;
}
.approve-btn {
  background: var(--ap-primary);
  border: 1px solid var(--ap-primary);
  color: white;
}
.approve-btn:hover:not(:disabled) {
  background: #2C4F70;
  border-color: #2C4F70;
}
.reject-btn {
  background: var(--ap-surface);
  border: 1px solid #E2B8B3;
  color: #B64237;
}
.reject-btn:hover:not(:disabled) {
  background: #F8EAE8;
  border-color: #C97870;
}
.feedback {
  border-radius: 7px;
  padding: 12px 15px;
  font-size: 13px;
  margin-bottom: 17px;
}
.error { color: #B42318; background: #F8EAE8; border: 1px solid #EBC8C4; }
.success { color: #176B45; background: #E7F4ED; border: 1px solid #B6E4C8; }
.state-panel {
  text-align: center;
  padding: 50px 20px;
  border: 1px dashed var(--ap-border);
  border-radius: 9px;
  color: var(--ap-muted);
  background: var(--ap-surface);
}
.state-panel h3 { color: var(--ap-text); margin: 13px 0 7px; font-size: 17px; }
.state-panel p { font-size: 13px; }
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(17, 25, 38, .58);
  backdrop-filter: blur(3px);
}
.reject-modal {
  width: min(100%, 460px);
  background: var(--ap-surface);
  color: var(--ap-text);
  border: 1px solid var(--ap-border);
  border-radius: 11px;
  padding: 25px;
  box-shadow: 0 20px 70px rgba(0,0,0,.2);
  animation: fadeUp .2s ease both;
}
.reject-modal h2 { margin-bottom: 9px; font-size: 20px; font-weight: 700; }
.reject-modal p { color: var(--ap-muted); font-size: 13px; line-height: 1.6; margin-bottom: 16px; }
.reject-modal textarea {
  display: block;
  width: 100%;
  min-height: 105px;
  resize: vertical;
  border: 1px solid var(--ap-border);
  background: #F5F6F8;
  color: var(--ap-text);
  border-radius: 7px;
  padding: 12px;
  font: inherit;
  font-size: 13px;
}
.reject-modal textarea:focus { outline: 2px solid #8BA2B8; outline-offset: 1px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 19px; }
@media (max-width: 900px) {
  .details-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 760px) {
  .approval-page { padding-top: 4px; }
  .page-heading { align-items: flex-start; flex-direction: column; gap: 14px; }
  .summary-grid { grid-template-columns: 1fr; gap: 10px; margin-bottom: 24px; }
  .summary-card { min-height: auto; padding: 17px 18px; }
  .summary-card strong { font-size: 26px; }
  h1 { font-size: 25px; }
  .request-card { padding: 17px; }
  .request-card h3 { font-size: 18px; }
  .card-actions { flex-wrap: wrap; }
  .card-actions button { flex: 1; }
}
@media (max-width: 420px) {
  .details-grid { grid-template-columns: 1fr 1fr; gap: 14px 10px; }
  .section-heading { align-items: flex-start; }
  .request-top { align-items: flex-start; }
  .modal-actions button { flex: 1; }
}
</style>

