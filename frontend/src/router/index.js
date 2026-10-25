import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '@/views/DashboardView.vue'
import RequestsView from '@/views/RequestsView.vue'
import NewRequestView from '@/views/NewRequestView.vue'
import ApprovalView from '@/views/ApprovalView.vue'
import PlaceholderView from '@/views/PlaceholderView.vue'
import ConversionView from '@/views/ConversionView.vue'

export const navItems = [
  {
    path: '/dashboard',
    name: 'dashboard',
    label: 'Dashboard',
    icon: 'LayoutDashboard',
  },
  {
    path: '/requests',
    name: 'requests',
    label: 'Material Requests',
    icon: 'FileText',
  },
  {
    path: '/approval',
    name: 'approval',
    label: 'Purchase Approval',
    icon: 'ShieldCheck',
  },
  {
    path: '/purchase-orders',
    name: 'purchase-orders',
    label: 'Purchase Orders',
    icon: 'ShoppingCart',
  },
  {
    path: '/receiving',
    name: 'receiving',
    label: 'Material Receiving',
    icon: 'PackageCheck',
  },
  {
    path: '/inventory',
    name: 'inventory',
    label: 'Inventory',
    icon: 'Boxes',
  },
  {
    path: '/conversion',
    name: 'conversion',
    label: 'Material Conversion',
    icon: 'GitBranch',
  },
]

const router = createRouter({
  history: createWebHistory(),

  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },

    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: {
        title: 'Dashboard',
      },
    },

    {
      path: '/requests',
      name: 'requests',
      component: RequestsView,
      meta: {
        title: 'Material Requests',
      },
    },

    {
      path: '/requests/new',
      name: 'new-request',
      component: NewRequestView,
      meta: {
        title: 'New Material Request',
      },
    },
    {
      path: '/approval',
      name: 'approval',
      component: ApprovalView,
      meta: {
        title: 'Purchase Approval',
      },
    },

    {
      path: '/purchase-orders',
      name: 'purchase-orders',
      component: PlaceholderView,
      meta: {
        title: 'Purchase Orders',
      },
    },

    {
      path: '/receiving',
      name: 'receiving',
      component: PlaceholderView,
      meta: {
        title: 'Material Receiving',
      },
    },

    {
      path: '/inventory',
      name: 'inventory',
      component: PlaceholderView,
      meta: {
        title: 'Inventory',
      },
    },

    {
      path: '/conversion',
      name: 'conversion',
      component: ConversionView,
      meta: {
        title: 'Material Conversion',
      },
    },
  ],
})

export default router




