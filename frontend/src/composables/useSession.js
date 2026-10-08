import { reactive, computed } from 'vue'

// Single demo user (the client already owns user management).
// The role switcher exists only so the workflow can be demoed per role.
export const ROLES = {
  receiver: { key: 'receiver', label: 'Receiver', tone: 'info' },
  supervisor: { key: 'supervisor', label: 'Purchase Supervisor', tone: 'violet' },
  admin: { key: 'admin', label: 'Admin', tone: 'success' },
}

const state = reactive({
  user: { name: 'Jay Patel', email: 'jay.patel@company.com', initials: 'JP' },
  role: 'supervisor',
})

export function useSession() {
  return {
    user: computed(() => state.user),
    role: computed(() => ROLES[state.role]),
    roleKey: computed(() => state.role),
    setRole: (key) => { if (ROLES[key]) state.role = key },
  }
}
