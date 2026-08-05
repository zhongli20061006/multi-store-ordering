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
</script>

<template>
  <el-container style="min-height: 100vh">
    <el-aside width="200px" style="background: #fff; border-right: 1px solid var(--border-color)">
      <el-menu router>
        <el-menu-item index="/stores">门店管理</el-menu-item>
        <el-menu-item :index="menuIndex" :disabled="!current.hasStore">菜单管理</el-menu-item>
        <el-menu-item index="/orders">订单管理</el-menu-item>
        <el-menu-item index="/profile">个人中心</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header
        style="display: flex; align-items: center; justify-content: space-between; background: #fff; border-bottom: 1px solid var(--border-color)"
      >
        <div>
          当前门店：
          <el-select :model-value="current.id" style="width: 180px" @change="onStoreChange">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </div>
        <div>
          <span style="margin-right: 12px">{{ auth.username }}</span>
          <el-button link type="primary" @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
