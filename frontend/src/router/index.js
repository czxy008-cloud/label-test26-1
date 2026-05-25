import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { guest: true } },
  { path: '/register', name: 'register', component: () => import('@/views/Register.vue'), meta: { guest: true } },
  { path: '/publish', name: 'publish', component: () => import('@/views/Publish.vue'), meta: { requiresAuth: true } },
  { path: '/item/:id', name: 'item-detail', component: () => import('@/views/ItemDetail.vue') },
  { path: '/my-items', name: 'my-items', component: () => import('@/views/MyItems.vue'), meta: { requiresAuth: true } },
  { path: '/exchanges', name: 'exchanges', component: () => import('@/views/Exchanges.vue'), meta: { requiresAuth: true } },
  { path: '/messages', name: 'messages', component: () => import('@/views/Messages.vue'), meta: { requiresAuth: true } },
  { path: '/messages/:userId', name: 'messages-chat', component: () => import('@/views/Messages.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/Profile.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (to.meta.requiresAuth && !userStore.isLogin) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && userStore.isLogin) {
    next('/')
  } else {
    next()
  }
})

export default router
