<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword, getMe } from '@/api/auth'
import { storesApi } from '@/api/stores'
import { useAsync } from '@/composables/useAsync'
import { useAuthStore } from '@/stores/auth'
import { useCurrentStore } from '@/stores/store'

const router = useRouter()
const auth = useAuthStore()
const current = useCurrentStore()

const me = ref<{ username: string; display_name: string } | null>(null)
const stores = ref<{ id: number; name: string }[]>([])
const { loading, run: load } = useAsync(async () => {
  me.value = await getMe()
  stores.value = await storesApi.listMine()
})

const pwd = reactive({ old_password: '', new_password: '', confirm: '' })
const submitting = ref(false)

function switchStore(id: number) {
  const found = stores.value.find((s) => s.id === id)
  if (found) {
    current.select(found)
    ElMessage.success(`已切换到「${found.name}」`)
  }
}

async function onSubmitPassword() {
  if (pwd.new_password !== pwd.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  submitting.value = true
  try {
    await changePassword(pwd.old_password, pwd.new_password)
    ElMessage.success('密码已修改')
    pwd.old_password = ''
    pwd.new_password = ''
    pwd.confirm = ''
  } finally {
    submitting.value = false
  }
}

function onLogout() {
  auth.logout()
  current.clear()
  router.push('/login')
}

onMounted(load)
</script>

<template>
  <div v-loading="loading" class="page">
    <el-row :gutter="16">
      <el-col :span="10">
        <div class="panel">
          <h3 class="panel-title">账号信息</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ me?.username }}</el-descriptions-item>
            <el-descriptions-item label="显示名">{{ me?.display_name }}</el-descriptions-item>
          </el-descriptions>
          <h4 class="panel-sub">绑定门店</h4>
          <div
            v-for="s in stores"
            :key="s.id"
            class="store-row"
          >
            <span>{{ s.name }}</span>
            <el-button size="small" :type="current.id === s.id ? 'primary' : 'default'" plain @click="switchStore(s.id)">
              {{ current.id === s.id ? '当前门店' : '切换' }}
            </el-button>
          </div>
          <el-button type="danger" plain class="logout-btn" @click="onLogout">退出登录</el-button>
        </div>
      </el-col>
      <el-col :span="14">
        <div class="panel">
          <h3 class="panel-title">修改密码</h3>
          <el-form :model="pwd" label-width="90px" class="pwd-form">
            <el-form-item label="旧密码">
              <el-input v-model="pwd.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码">
              <el-input v-model="pwd.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码">
              <el-input v-model="pwd.confirm" type="password" show-password />
            </el-form-item>
            <el-button type="primary" :loading="submitting" @click="onSubmitPassword">保存新密码</el-button>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.panel {
  background: var(--surface);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  box-shadow: var(--shadow-card);
}
.panel-title {
  margin: 0 0 var(--space-3);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}
.panel-sub {
  margin: var(--space-3) 0 var(--space-2);
  font-size: 14px;
  color: var(--text-main);
}
.store-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}
.logout-btn {
  margin-top: var(--space-3);
}
.pwd-form {
  max-width: 420px;
}
</style>
