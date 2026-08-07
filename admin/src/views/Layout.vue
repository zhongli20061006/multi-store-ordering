<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { storesApi } from '@/api/stores'
import { useAuthStore } from '@/stores/auth'
import { useCurrentStore } from '@/stores/store'

const router = useRouter()
const auth = useAuthStore()
const current = useCurrentStore()
const stores = ref<{ id: number; name: string }[]>([])

onMounted(async () => {
  stores.value = await storesApi.listMine()
  if (!current.hasStore && stores.value.length > 0) {
    current.select(stores.value[0])
  }
})

function onStoreChange(id: number) {
  const found = stores.value.find((s) => s.id === id)
  if (found) current.select(found)
}

function onLogout() {
  auth.logout()
  current.clear()
  router.push('/login')
}

const menuIndex = computed(() => (current.hasStore ? `/stores/${current.id}/menu` : '/stores'))
const bannerIndex = computed(() => (current.hasStore ? `/stores/${current.id}/banners` : '/stores'))
</script>

<template>
  <el-container style="min-height: 100vh">
    <el-aside width="200px" style="background: #fff; border-right: 1px solid var(--border-color)">
      <div class="brand">
        <span style="width: 4px; height: 20px; border-radius: 2px; background: var(--brand-primary); display: inline-block"></span>
        <strong>多门店点单</strong>
      </div>
      <el-menu router class="side-menu">
        <el-menu-item index="/stores">门店管理</el-menu-item>
        <el-menu-item :index="menuIndex" :disabled="!current.hasStore">菜单管理</el-menu-item>
        <el-menu-item :index="bannerIndex" :disabled="!current.hasStore">轮播图</el-menu-item>
        <el-menu-item index="/dashboard">数据看板</el-menu-item>
        <el-menu-item index="/orders">订单管理</el-menu-item>
        <el-menu-item index="/audit">操作审计</el-menu-item>
        <el-menu-item index="/profile">个人中心</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="topbar">
        <div class="store-switch">
          当前门店：
          <el-select :model-value="current.id" style="width: 180px" @change="onStoreChange">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </div>
        <div class="account">
          <span class="username">{{ auth.username }}</span>
          <el-button link type="primary" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <div class="content">
          <router-view />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.brand {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
}
.side-menu {
  border-right: none;
  padding: 8px;
}
.side-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 4px 0;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}
.side-menu :deep(.el-menu-item:hover) {
  background: var(--brand-soft);
  color: var(--brand-primary);
}
.side-menu :deep(.el-menu-item.is-active) {
  background: var(--brand-soft);
  color: var(--brand-primary);
  font-weight: 600;
}
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface);
  border-bottom: 1px solid var(--border-color);
}
.store-switch {
  color: var(--text-secondary);
  font-size: 13px;
}
.account {
  display: flex;
  align-items: center;
  gap: 8px;
}
.username {
  color: var(--text-main);
  font-size: 14px;
}
.main {
  padding: var(--space-5);
}
.content {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
