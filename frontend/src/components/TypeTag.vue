<script setup>
defineProps({
  type: { type: String, required: true }, // ADVANCE | NEW
})
</script>

<template>
  <span class="tag" :class="type === 'ADVANCE' ? 'adv' : 'new'">{{ type }}</span>
</template>

<style scoped>
.tag { display: inline-block; padding: 1px 7px; border-radius: 5px; font-size: 10.5px; font-weight: 700; letter-spacing: 0.06em; border: 1px solid; }
.adv { color: var(--c-violet); background: var(--c-violet-bg); border-color: color-mix(in srgb, var(--c-violet) 22%, transparent); }
.new { color: var(--c-accent); background: var(--c-accent-50); border-color: color-mix(in srgb, var(--c-accent) 25%, transparent); }
</style>
