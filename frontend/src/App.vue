<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import AppHeader from '@/components/AppHeader.vue'
import { ref, onMounted } from 'vue'

const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme)
}

const setTheme = (theme) => {
  applyTheme(theme)
  localStorage.setItem('mms-theme', theme)
}

onMounted(() => {
  const saved = localStorage.getItem('mms-theme')
  applyTheme(saved === 'dark' ? 'dark' : 'light')
})

const collapsed = ref(false)
const mobileOpen = ref(false)
</script>

<template>
  <div class="shell" :class="{ 'is-collapsed': collapsed }">

    <AppSidebar
      :collapsed="collapsed"
      :mobile-open="mobileOpen"
      @toggle="collapsed = !collapsed"
      @close="mobileOpen = false"
    />

    <div
      v-if="mobileOpen"
      class="scrim"
      @click="mobileOpen = false"
    />

    <div class="main">

      <AppHeader @menu="mobileOpen = true" />

      <main class="content">
        <RouterView />
      </main>

    </div>

  </div>
</template>

<style>
.shell {
  min-height: 100vh;
  display: flex;
}

.main {
  flex: 1;
  min-width: 0;
  margin-left: var(--sb-width);
  transition: margin-left var(--t-base) var(--ease);
  display: flex;
  flex-direction: column;
}

.shell.is-collapsed .main {
  margin-left: var(--sb-width-collapsed);
}

.content {
  padding: 28px 32px 56px;
  max-width: 1480px;
  width: 100%;
  margin: 0 auto;
}

.scrim {
  position: fixed;
  inset: 0;
  background: rgba(14, 19, 32, 0.45);
  z-index: 40;
}

@media (max-width: 960px) {
  .main,
  .shell.is-collapsed .main {
    margin-left: 0;
  }

  .content {
    padding: 20px 16px 48px;
  }
}
</style>

