<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-inner">
        <router-link to="/" class="logo">置换社区</router-link>
        <el-menu
          mode="horizontal" :default-active="activeMenu" class="nav-menu"
          @select="onMenuSelect"
        >
          <el-menu-item index="home"><el-icon><House /></el-icon>首页</el-menu-item>
          <el-menu-item index="publish" v-if="userStore.isLogin"><el-icon><Upload /></el-icon>发布物品</el-menu-item>
          <el-menu-item index="my-items" v-if="userStore.isLogin"><el-icon><Goods /></el-icon>我的物品</el-menu-item>
          <el-menu-item index="exchanges" v-if="userStore.isLogin"><el-icon><RefreshRight /></el-icon>置换进度</el-menu-item>
          <el-menu-item index="messages" v-if="userStore.isLogin">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="badge-item">
              <el-icon><ChatDotRound /></el-icon>
            </el-badge>
            私信
          </el-menu-item>
        </el-menu>
        <div class="user-area">
          <template v-if="userStore.isLogin">
            <el-dropdown @command="onUserCommand">
              <span class="user-name">
                <el-avatar :size="32" :src="userStore.user?.avatar_url">{{ (userStore.user?.nickname || userStore.user?.username || 'U')[0] }}</el-avatar>
                {{ userStore.user?.nickname || userStore.user?.username }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="$router.push('/login')">登录</el-button>
            <el-button @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
    <el-footer class="app-footer">
      <span>© 2026 二手物品置换社区</span>
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.name || 'home')
const unreadCount = computed(() => userStore.unreadCount)

function onMenuSelect(index) {
  const map = {
    home: '/',
    publish: '/publish',
    'my-items': '/my-items',
    exchanges: '/exchanges',
    messages: '/messages'
  }
  if (map[index]) router.push(map[index])
}

function onUserCommand(cmd) {
  if (cmd === 'logout') {
    userStore.logout().then(() => router.push('/login'))
  } else if (cmd === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.app-container { min-height: 100vh; }
.app-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: sticky; top: 0; z-index: 100;
}
.header-inner {
  max-width: 1200px; margin: 0 auto;
  display: flex; align-items: center; gap: 24px;
}
.logo {
  font-size: 22px; font-weight: 700;
  color: #409EFF; text-decoration: none;
}
.nav-menu { flex: 1; border-bottom: none !important; }
.user-area { display: flex; align-items: center; gap: 12px; }
.user-name { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.app-main { max-width: 1200px; margin: 0 auto; padding: 24px; }
.app-footer { text-align: center; color: #999; font-size: 13px; padding: 20px; }
.badge-item .el-badge__content { border: none; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
