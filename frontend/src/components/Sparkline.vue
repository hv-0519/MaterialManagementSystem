<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },

  color: {
    type: String,
    default: 'currentColor',
  },

  width: {
    type: Number,
    default: 120,
  },

  height: {
    type: Number,
    default: 36,
  },

  fill: {
    type: Boolean,
    default: true,
  },
})

const validData = computed(() => {
  return Array.isArray(props.data)
    ? props.data
        .map(Number)
        .filter(Number.isFinite)
    : []
})

const hasData = computed(() => validData.value.length > 0)

const pts = computed(() => {

  const d = validData.value

  if (!d.length) {
    return []
  }

  if (d.length === 1) {
    return [[
      props.width,
      props.height / 2,
    ]]
  }

  const min = Math.min(...d)
  const max = Math.max(...d)
  const span = max - min || 1
  const pad = 3

  return d.map((v, i) => [
    (i / (d.length - 1)) * props.width,

    props.height -
      pad -
      ((v - min) / span) *
        (props.height - pad * 2),
  ])
})

const line = computed(() => {

  if (!pts.value.length) {
    return ''
  }

  return pts.value
    .map(
      (p, i) =>
        `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`
    )
    .join(' ')
})

const area = computed(() => {

  if (!line.value) {
    return ''
  }

  return `${line.value}
    L${props.width},${props.height}
    L0,${props.height}
    Z`
})

const last = computed(() => {
  return pts.value.length
    ? pts.value[pts.value.length - 1]
    : null
})

const gid = `sp-${Math.random()
  .toString(36)
  .slice(2, 8)}`
</script>

<template>

  <svg
    v-if="hasData"
    :viewBox="`0 0 ${width} ${height}`"
    :width="width"
    :height="height"
    :style="{ color }"
    aria-hidden="true"
    class="sp"
  >

    <defs>
      <linearGradient
        :id="gid"
        x1="0"
        y1="0"
        x2="0"
        y2="1"
      >
        <stop
          offset="0"
          stop-color="currentColor"
          stop-opacity="0.18"
        />

        <stop
          offset="1"
          stop-color="currentColor"
          stop-opacity="0"
        />
      </linearGradient>
    </defs>

    <path
      v-if="fill"
      :d="area"
      :fill="`url(#${gid})`"
    />

    <path
      :d="line"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    <circle
      v-if="last"
      :cx="last[0]"
      :cy="last[1]"
      r="2.6"
      fill="currentColor"
    />

  </svg>

</template>

<style scoped>
.sp {
  display: block;
  overflow: visible;
}
</style>
