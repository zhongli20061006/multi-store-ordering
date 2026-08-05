import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      children: [
        { path: '', redirect: '/stores' },
        { path: 'stores', component: () => import('@/views/Stores.vue') },
        { path: 'stores/:id/menu', component: () => import('@/views/MenuManage.vue') },
        { path: 'orders', component: () => import('@/views/Orders.vue') },
        { path: 'profile', component: () => import('@/views/Profile.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.isLoggedIn) return '/login'
  if (to.path === '/login' && auth.isLoggedIn) return '/'
  return true
})

export default router
