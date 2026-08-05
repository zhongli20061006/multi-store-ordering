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
  <div v-loading="loading">
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card>
          <h3 style="margin-top: 0">账号信息</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ me?.username }}</el-descriptions-item>
            <el-descriptions-item label="显示名">{{ me?.display_name }}</el-descriptions-item>
          </el-descriptions>
          <h4 style="margin-bottom: 8px">绑定门店</h4>
          <div
            v-for="s in stores"
            :key="s.id"
            style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0"
          >
            <span>{{ s.name }}</span>
            <el-button size="small" :type="current.id === s.id ? 'primary' : 'default'" plain @click="switchStore(s.id)">
              {{ current.id === s.id ? '当前门店' : '切换' }}
            </el-button>
          </div>
          <el-button type="danger" plain style="margin-top: 12px" @click="onLogout">退出登录</el-button>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card>
          <h3 style="margin-top: 0">修改密码</h3>
          <el-form :model="pwd" label-width="90px" style="max-width: 420px">
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
