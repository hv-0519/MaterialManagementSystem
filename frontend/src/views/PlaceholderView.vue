<script setup>
import { useRoute } from 'vue-router'
import { Construction } from 'lucide-vue-next'
const route = useRoute()
</script>

<template>
  <section class="ph">
    <div class="ph__ic"><Construction :size="22" :stroke-width="1.6" /></div>
    <h1>{{ route.meta.title }}</h1>
    <p>This page is queued. We're building the templates one at a time, starting with the Dashboard.</p>
  </section>
</template>

<style scoped>
.ph { margin: 80px auto; max-width: 420px; text-align: center; }
.ph__ic { width: 52px; height: 52px; margin: 0 auto 16px; display: grid; place-items: center; border-radius: 12px; color: var(--c-muted); background: var(--c-surface); border: 1px dashed var(--c-border-strong); }
h1 { font-size: 20px; letter-spacing: -0.01em; margin-bottom: 6px; }
p { color: var(--c-muted); }
</style>
