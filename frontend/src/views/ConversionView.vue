<script setup>
import { onMounted, ref, computed } from "vue";
import api from "@/services/api";
import { RefreshCw, GitBranch, AlertTriangle } from "lucide-vue-next";

const materials = ref([]);
const stockMap = ref({});
const selectedMaterialId = ref("");
const outputQty = ref("");
const bomRows = ref([]);
const packingRows = ref([]);
const recipeLoading = ref(false);
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const notice = ref("");

const history = ref([]);
const historyLoading = ref(true);
const detailId = ref(null);
const detailLines = ref(null);

const safeQty = computed(() => {
  const n = Number(outputQty.value);
  return n > 0 ? n : 0;
});

const canSubmit = computed(
  () =>
    selectedMaterialId.value &&
    safeQty.value > 0 &&
    (bomRows.value.length || packingRows.value.length),
);

function stockFor(materialId) {
  return stockMap.value[materialId] ?? "—";
}

function packagesFor(rule) {
  return Math.floor(safeQty.value / rule.units_per_package);
}

function remainderNote(rule) {
  const rem = safeQty.value % rule.units_per_package;
  return rem > 0
    ? `${rem} unit(s) left over, unpackaged (below the ${rule.units_per_package}-unit threshold).`
    : "Exact multiple — no leftover.";
}

function isShort(materialId, neededQty) {
  const have = stockMap.value[materialId];
  return have !== undefined && have < neededQty;
}

function formatDateTime(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return (
    d.toLocaleDateString("en-IN", { day: "2-digit", month: "short" }) +
    ", " +
    d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })
  );
}

async function loadMaterials() {
  loading.value = true;
  error.value = "";
  try {
    const [matRes, invRes] = await Promise.all([
      api.get("/materials"),
      api.get("/inventory"),
    ]);
    materials.value = matRes.data;
    const items = Array.isArray(invRes.data)
      ? invRes.data
      : invRes.data.items || [];
    const map = {};
    items.forEach((i) => {
      map[i.material_id] = Number(i.available_quantity);
    });
    stockMap.value = map;
  } catch (err) {
    error.value =
      err.response?.data?.detail || "Could not load materials or stock.";
  } finally {
    loading.value = false;
  }
}

async function loadRecipe() {
  error.value = "";
  bomRows.value = [];
  packingRows.value = [];
  if (!selectedMaterialId.value) return;
  recipeLoading.value = true;
  try {
    const [bomRes, packRes] = await Promise.all([
      api.get(`/bom-components/${selectedMaterialId.value}`),
      api.get(`/packing-rules/${selectedMaterialId.value}`),
    ]);
    bomRows.value = bomRes.data;
    packingRows.value = packRes.data;
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      "Could not load the recipe for this material.";
  } finally {
    recipeLoading.value = false;
  }
}

async function submitConversion() {
  if (!canSubmit.value) return;
  if (!window.confirm(`Run conversion: produce ${safeQty.value} unit(s)?`))
    return;

  submitting.value = true;
  error.value = "";
  notice.value = "";
  try {
    const response = await api.post("/conversions", {
      output_material_id: Number(selectedMaterialId.value),
      output_qty: safeQty.value,
    });
    notice.value = `Conversion #${response.data.transaction_id} complete — produced ${safeQty.value} unit(s).`;
    outputQty.value = "";
    await Promise.all([loadMaterials(), loadHistory(), loadRecipe()]);
  } catch (err) {
    error.value = err.response?.data?.detail || "Conversion failed.";
  } finally {
    submitting.value = false;
  }
}

async function loadHistory() {
  historyLoading.value = true;
  try {
    const response = await api.get("/conversions");
    history.value = response.data;
  } catch (err) {
    error.value =
      err.response?.data?.detail || "Could not load conversion history.";
  } finally {
    historyLoading.value = false;
  }
}

async function openDetail(id) {
  detailId.value = id;
  try {
    const response = await api.get(`/conversions/${id}`);
    detailLines.value = response.data.lines || [];
  } catch (err) {
    error.value =
      err.response?.data?.detail || "Could not load conversion detail.";
  }
}

function closeDetail() {
  detailId.value = null;
  detailLines.value = null;
}

onMounted(() => {
  loadMaterials();
  loadHistory();
});
</script>

<template>
  <section class="conversion-page">
    <div class="page-heading">
      <div>
        <div class="eyebrow"><GitBranch :size="15" /> STOCK</div>
        <h1>Material Conversion</h1>
        <p class="subtitle">
          Produce a kitted item from bulk stock using its recipe and packing
          rule.
        </p>
      </div>
      <button class="refresh-btn" :disabled="loading" @click="loadMaterials">
        <RefreshCw :size="16" /> Refresh
      </button>
    </div>

    <div v-if="error" class="feedback error" role="alert">{{ error }}</div>
    <div v-if="notice" class="feedback success" role="status">{{ notice }}</div>

    <div class="layout-grid">
      <article class="panel">
        <h2>New Conversion</h2>

        <div class="field">
          <label>Output Material</label>
          <select v-model="selectedMaterialId" @change="loadRecipe">
            <option value="" disabled>Select a material…</option>
            <option v-for="m in materials" :key="m.id" :value="m.id">
              {{ m.material_name }} ({{ m.unit }})
            </option>
          </select>
        </div>

        <div class="field">
          <label>Output Quantity</label>
          <input
            type="number"
            min="1"
            step="1"
            v-model="outputQty"
            placeholder="e.g. 10"
          />
        </div>

        <template v-if="selectedMaterialId">
          <div v-if="recipeLoading" class="state-panel small">
            Loading recipe…
          </div>
          <template v-else>
            <div class="preview-section" v-if="bomRows.length">
              <div class="preview-label">Will consume (recipe)</div>
              <div
                v-for="b in bomRows"
                :key="b.id"
                class="preview-row"
                :class="{
                  short: isShort(
                    b.component_material_id,
                    b.qty_per_unit * safeQty,
                  ),
                }"
              >
                <span>{{ b.material_name }}</span>
                <strong
                  >{{ (b.qty_per_unit * safeQty).toFixed(2) }}
                  {{ b.unit }}</strong
                >
              </div>
            </div>
            <div class="preview-section" v-if="packingRows.length">
              <div class="preview-label">Will consume (packaging)</div>
              <div
                v-for="p in packingRows"
                :key="p.id"
                class="preview-row"
                :class="{
                  short: isShort(p.package_material_id, packagesFor(p)),
                }"
              >
                <span>{{ p.material_name }}</span>
                <strong>{{ packagesFor(p) }} {{ p.unit }}</strong>
              </div>
              <p class="remainder-note">{{ remainderNote(packingRows[0]) }}</p>
            </div>
            <p
              class="preview-empty"
              v-if="!bomRows.length && !packingRows.length"
            >
              No BOM or packing rule defined for this material yet.
            </p>
          </template>
        </template>
        <p class="preview-empty" v-else>
          Select a material to preview what it will consume.
        </p>

        <button
          class="run-btn"
          :disabled="submitting || !canSubmit"
          @click="submitConversion"
        >
          {{ submitting ? "Converting…" : "Run Conversion" }}
        </button>
      </article>

      <article class="panel">
        <h2>Current Stock</h2>
        <div v-if="loading" class="state-panel small">Loading stock…</div>
        <div v-else class="preview-row" v-for="m in materials" :key="m.id">
          <span>{{ m.material_name }}</span>
          <strong>{{ stockFor(m.id) }} {{ m.unit }}</strong>
        </div>
      </article>
    </div>

    <div class="section-heading">
      <h2>Conversion History</h2>
    </div>

    <div v-if="historyLoading" class="state-panel">Loading history…</div>
    <div v-else-if="!history.length" class="state-panel">
      <AlertTriangle :size="28" />
      <h3>No conversions yet</h3>
      <p>Run your first conversion above to see it here.</p>
    </div>
    <table v-else class="history-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Output Material</th>
          <th>Qty Produced</th>
          <th>Run By</th>
          <th>When</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="h in history" :key="h.id" @click="openDetail(h.id)">
          <td class="mono">#{{ h.id }}</td>
          <td>{{ h.output_material }}</td>
          <td class="mono">{{ h.output_qty }}</td>
          <td>{{ h.created_by_username }}</td>
          <td>{{ formatDateTime(h.created_at) }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="detailId" class="modal-backdrop" @click.self="closeDetail">
      <section class="detail-modal" role="dialog" aria-modal="true">
        <h2>Conversion #{{ detailId }}</h2>
        <div
          v-for="(l, i) in detailLines"
          :key="i"
          class="preview-row"
          :style="{ color: l.qty_change < 0 ? '#C04A3D' : '#2F8F5B' }"
        >
          <span
            >{{ l.material_name }} <small>({{ l.line_type }})</small></span
          >
          <strong
            >{{ l.qty_change > 0 ? "+" : "" }}{{ l.qty_change }}
            {{ l.unit }}</strong
          >
        </div>
        <div class="modal-actions">
          <button class="refresh-btn" @click="closeDetail">Close</button>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.conversion-page {
  --cv-bg: #f5f6f8;
  --cv-surface: #ffffff;
  --cv-border: #dfe3e8;
  --cv-text: #1a2233;
  --cv-muted: #5c6b7a;
  --cv-primary: #1f3b57;
  --cv-accent: #c77d2e;
  width: 100%;
  max-width: 1180px;
  margin: 0 auto;
  padding: 8px 0 40px;
  color: var(--cv-text);
  animation: fadeUp 0.3s ease both;
}
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(7px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  color: var(--cv-accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin-bottom: 10px;
}
h1 {
  font-size: 29px;
  font-weight: 700;
  letter-spacing: -0.8px;
}
.subtitle {
  color: var(--cv-muted);
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
  transition:
    background 0.15s ease,
    border-color 0.15s ease,
    transform 0.15s ease;
}
button:active:not(:disabled) {
  transform: translateY(1px);
}
button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.refresh-btn {
  background: var(--cv-surface);
  border: 1px solid var(--cv-border);
  color: var(--cv-text);
}
.refresh-btn:hover:not(:disabled) {
  background: #eef0f3;
}
.feedback {
  border-radius: 7px;
  padding: 12px 15px;
  font-size: 13px;
  margin-bottom: 17px;
}
.error {
  color: #b42318;
  background: #f8eae8;
  border: 1px solid #ebc8c4;
}
.success {
  color: #176b45;
  background: #e7f4ed;
  border: 1px solid #b6e4c8;
}

.layout-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  align-items: start;
  margin-bottom: 30px;
}
.panel {
  padding: 21px 22px;
  border: 1px solid var(--cv-border);
  border-radius: 9px;
  background: var(--cv-surface);
  box-shadow: 0 1px 2px rgba(26, 34, 51, 0.05);
}
.panel h2 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}
.field {
  margin-bottom: 14px;
}
.field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--cv-muted);
  margin-bottom: 6px;
}
.field select,
.field input {
  width: 100%;
  padding: 9px 11px;
  border: 1px solid var(--cv-border);
  border-radius: 7px;
  font: inherit;
  font-size: 13px;
  background: var(--cv-bg);
  color: var(--cv-text);
}
.field select:focus,
.field input:focus {
  outline: 2px solid #8ba2b8;
  outline-offset: 1px;
}

.preview-section {
  margin-bottom: 16px;
}
.preview-label {
  font-size: 10.5px;
  font-weight: 700;
  color: #8a96a5;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 8px;
}
.preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #eef0f3;
  border-radius: 6px;
  margin-bottom: 6px;
  font-size: 13px;
}
.preview-row strong {
  font-family: "IBM Plex Mono", monospace;
}
.preview-row.short {
  background: #f8eae8;
  color: #c04a3d;
}
.preview-row.short strong {
  color: #c04a3d;
}
.remainder-note {
  font-size: 11.5px;
  color: #8a96a5;
  margin-top: 4px;
}
.preview-empty {
  font-size: 12.5px;
  color: #8a96a5;
  padding: 20px 0;
  text-align: center;
}

.run-btn {
  width: 100%;
  margin-top: 16px;
  background: var(--cv-primary);
  border: 1px solid var(--cv-primary);
  color: #fff;
}
.run-btn:hover:not(:disabled) {
  background: #2c4f70;
  border-color: #2c4f70;
}

.section-heading {
  margin: 10px 0 16px;
}
.section-heading h2 {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.state-panel {
  text-align: center;
  padding: 50px 20px;
  border: 1px dashed var(--cv-border);
  border-radius: 9px;
  color: var(--cv-muted);
  background: var(--cv-surface);
}
.state-panel.small {
  padding: 20px;
}
.state-panel h3 {
  margin: 13px 0 7px;
  font-size: 17px;
  color: var(--cv-text);
}
.state-panel p {
  font-size: 13px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: var(--cv-surface);
  border: 1px solid var(--cv-border);
  border-radius: 9px;
  overflow: hidden;
}
.history-table thead th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  color: #8a96a5;
  background: #eef0f3;
  padding: 11px 16px;
  border-bottom: 1px solid var(--cv-border);
}
.history-table tbody tr {
  border-bottom: 1px solid var(--cv-border);
  cursor: pointer;
}
.history-table tbody tr:last-child {
  border-bottom: none;
}
.history-table tbody tr:hover {
  background: #eef0f3;
}
.history-table td {
  padding: 12px 16px;
}
.mono {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12.5px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(17, 25, 38, 0.58);
  backdrop-filter: blur(3px);
}
.detail-modal {
  width: min(100%, 440px);
  max-height: 85vh;
  overflow-y: auto;
  background: var(--cv-surface);
  border: 1px solid var(--cv-border);
  border-radius: 11px;
  padding: 25px;
  box-shadow: 0 20px 70px rgba(0, 0, 0, 0.2);
  animation: fadeUp 0.2s ease both;
}
.detail-modal h2 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 700;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

@media (max-width: 900px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .page-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;
  }
  h1 {
    font-size: 25px;
  }
}
</style>
