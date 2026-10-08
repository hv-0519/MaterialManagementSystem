<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowLeft,
  CheckCircle2,
  FilePlus2,
  Package,
  Save,
  Loader2,
} from 'lucide-vue-next'

import api from '@/services/api'

const router = useRouter()

const materials = ref([])
const loadingMaterials = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  material_id: '',
  quantity: '',
  request_type: 'NEW',
  required_date: '',
  remarks: '',
})

async function loadMaterials() {

  loadingMaterials.value = true
  error.value = ''

  try {
    const { data } = await api.get('/materials')
    materials.value = data
  } catch (err) {
    console.error(err)

    error.value =
      err.response?.data?.detail ||
      'Unable to load materials.'
  } finally {
    loadingMaterials.value = false
  }
}

async function createRequest() {

  error.value = ''
  success.value = ''

  if (!form.value.material_id) {
    error.value = 'Please select a material.'
    return
  }

  if (
    !form.value.quantity ||
    Number(form.value.quantity) <= 0
  ) {
    error.value = 'Please enter a valid quantity.'
    return
  }

  saving.value = true

  try {

    const { data } = await api.post(
      '/material-requests',
      {
        material_id: Number(form.value.material_id),
        quantity: Number(form.value.quantity),
        request_type: form.value.request_type,
        required_date:
          form.value.required_date || null,
        remarks:
          form.value.remarks.trim() || null,
      }
    )

    success.value =
      `Material request ${data.request_no} created successfully.`

    setTimeout(() => {
      router.push('/requests')
    }, 700)

  } catch (err) {

    console.error(err)

    error.value =
      err.response?.data?.detail ||
      'Unable to create material request.'

  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/requests')
}

onMounted(loadMaterials)
</script>

<template>
  <div class="new-request">

    <!-- Header -->

    <header class="page-head">

      <div>

        <button
          class="back-btn"
          type="button"
          @click="goBack"
        >
          <ArrowLeft :size="15" />
          Material Requests
        </button>

        <p class="eyebrow">
          Procurement workflow
        </p>

        <h1>
          New Material Request
        </h1>

        <p class="sub">
          Add a material requirement for receiver verification.
        </p>

      </div>

    </header>


    <!-- Form -->

    <section class="form-panel">

      <div class="form-head">

        <div class="form-icon">
          <FilePlus2 :size="21" />
        </div>

        <div>
          <h2>Request Details</h2>
          <p>
            Enter the material requirement below.
          </p>
        </div>

      </div>


      <div
        v-if="error"
        class="message error"
      >
        {{ error }}
      </div>


      <div
        v-if="success"
        class="message success"
      >
        <CheckCircle2 :size="17" />
        {{ success }}
      </div>


      <form
        class="form"
        @submit.prevent="createRequest"
      >

        <!-- Material -->

        <div class="field">

          <label>
            Material
            <span>*</span>
          </label>

          <div class="input-wrap">

            <Package :size="17" />

            <select
              v-model="form.material_id"
              :disabled="loadingMaterials || saving"
            >

              <option
                value=""
                disabled
              >
                {{
                  loadingMaterials
                    ? 'Loading materials...'
                    : 'Select material'
                }}
              </option>

              <option
                v-for="material in materials"
                :key="material.id"
                :value="material.id"
              >
                {{ material.material_name }}
                — {{ material.unit }}
              </option>

            </select>

          </div>

        </div>


        <!-- Quantity + Type -->

        <div class="two-col">

          <div class="field">

            <label>
              Quantity
              <span>*</span>
            </label>

            <input
              v-model="form.quantity"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Enter quantity"
              :disabled="saving"
            />

          </div>


          <div class="field">

            <label>
              Request Type
              <span>*</span>
            </label>

            <div class="type-options">

              <label
                class="type-option"
                :class="{
                  active:
                    form.request_type === 'NEW'
                }"
              >

                <input
                  v-model="form.request_type"
                  type="radio"
                  value="NEW"
                />

                <span>
                  <strong>New</strong>
                  <small>
                    Current requirement
                  </small>
                </span>

              </label>


              <label
                class="type-option"
                :class="{
                  active:
                    form.request_type === 'ADVANCE'
                }"
              >

                <input
                  v-model="form.request_type"
                  type="radio"
                  value="ADVANCE"
                />

                <span>
                  <strong>Advance</strong>
                  <small>
                    Future requirement
                  </small>
                </span>

              </label>

            </div>

          </div>

        </div>


        <!-- Required Date -->

        <div class="field">

          <label>
            Required Date
          </label>

          <input
            v-model="form.required_date"
            type="date"
            :disabled="saving"
          />

          <small class="hint">
            When the material is expected to be required.
          </small>

        </div>


        <!-- Remarks -->

        <div class="field">

          <label>
            Remarks
          </label>

          <textarea
            v-model="form.remarks"
            rows="4"
            maxlength="500"
            placeholder="Add any additional requirement details..."
            :disabled="saving"
          />

        </div>


        <!-- Footer -->

        <div class="form-footer">

          <span class="required-note">
            * Required fields
          </span>

          <div class="actions">

            <button
              type="button"
              class="btn secondary"
              :disabled="saving"
              @click="goBack"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="btn primary"
              :disabled="saving || loadingMaterials"
            >

              <Loader2
                v-if="saving"
                :size="16"
                class="spin"
              />

              <Save
                v-else
                :size="16"
              />

              {{
                saving
                  ? 'Creating...'
                  : 'Create Material Request'
              }}

            </button>

          </div>

        </div>

      </form>

    </section>

  </div>
</template>

<style scoped>
.new-request {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px;
}

.page-head {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: var(--c-muted);
  padding: 0;
  margin-bottom: 13px;
  font-size: 12.5px;
  cursor: pointer;
}

.back-btn:hover {
  color: var(--c-primary);
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

.form-panel {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xs);
  overflow: hidden;
}

.form-head {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 20px 22px;
  border-bottom: 1px solid var(--c-border);
}

.form-icon {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: var(--c-primary);
  background: var(--c-primary-50);
}

.form-head h2 {
  font-size: 15px;
  font-weight: 650;
}

.form-head p {
  margin-top: 3px;
  color: var(--c-muted);
  font-size: 12px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 24px 22px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.field label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--c-text-2);
}

.field label span {
  color: var(--c-danger);
}

.field input:not([type="radio"]),
.field select,
.field textarea {
  width: 100%;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  background: var(--c-surface);
  color: var(--c-text);
  padding: 10px 12px;
  outline: none;
  font: inherit;
  font-size: 13px;
  transition:
    border-color var(--t-fast),
    box-shadow var(--t-fast);
}

.field input:not([type="radio"]):focus,
.field select:focus,
.field textarea:focus {
  border-color: var(--c-primary);
  box-shadow: 0 0 0 3px var(--c-primary-100);
}

.field textarea {
  resize: vertical;
  min-height: 100px;
}

.field input:disabled,
.field select:disabled,
.field textarea:disabled {
  opacity: .65;
  cursor: not-allowed;
}

.input-wrap {
  position: relative;
}

.input-wrap > svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--c-muted);
  pointer-events: none;
}

.input-wrap select {
  padding-left: 38px;
  appearance: auto;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.type-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 62px;
  padding: 10px 12px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  cursor: pointer;
  transition:
    border-color var(--t-fast),
    background var(--t-fast);
}

.type-option:hover {
  background: var(--c-surface-2);
}

.type-option.active {
  border-color: var(--c-primary);
  background: var(--c-primary-50);
}

.type-option input {
  accent-color: var(--c-primary);
}

.type-option span {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.type-option strong {
  font-size: 12.5px;
}

.type-option small {
  color: var(--c-muted);
  font-size: 11px;
}

.hint {
  color: var(--c-muted);
  font-size: 11px;
}

.message {
  margin: 18px 22px 0;
  padding: 11px 13px;
  border-radius: var(--radius);
  font-size: 12.5px;
}

.message.error {
  color: var(--c-danger);
  background: var(--c-danger-bg);
  border: 1px solid var(--c-danger);
}

.message.success {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--c-success);
  background: var(--c-success-bg);
  border: 1px solid var(--c-success);
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  padding-top: 5px;
  border-top: 1px solid var(--c-border);
}

.required-note {
  color: var(--c-muted);
  font-size: 11px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 9px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 38px;
  padding: 0 14px;
  border-radius: var(--radius);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background var(--t-fast),
    border-color var(--t-fast),
    opacity var(--t-fast);
}

.btn.secondary {
  border: 1px solid var(--c-border);
  color: var(--c-text-2);
  background: var(--c-surface);
}

.btn.secondary:hover:not(:disabled) {
  background: var(--c-surface-2);
}

.btn.primary {
  border: 1px solid var(--c-primary);
  color: #fff;
  background: var(--c-primary);
}

.btn.primary:hover:not(:disabled) {
  filter: brightness(.94);
}

.btn:disabled {
  opacity: .55;
  cursor: not-allowed;
}

.spin {
  animation: spin .8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 700px) {
  .two-col {
    grid-template-columns: 1fr;
  }

  .type-options {
    grid-template-columns: 1fr;
  }

  .form-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .actions {
    width: 100%;
  }

  .actions .btn {
    flex: 1;
  }
}
</style>
