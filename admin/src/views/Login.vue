<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onSubmit() {
  if (!form.username || !form.password) return
  loading.value = true
  try {
    const data = await login(form)
    auth.setLogin(data.access_token, form.username, data.must_change_password)
    router.push(data.must_change_password ? '/force-password' : '/')
  } catch {
    // 错误提示由 http 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">商家后台</h2>
      <p class="login-sub">多门店点单 · 门店运营台</p>
      <el-form :model="form" @submit.prevent>
        <el-form-item label="账号">
          <el-input v-model="form.username" placeholder="admin1" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="admin123456" />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="login-btn" @click="onSubmit">登录</el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  position: relative;
}
.login-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, rgba(240, 100, 58, 0.12), transparent 60%);
  pointer-events: none;
}
.login-card {
  position: relative;
  width: 380px;
  padding: var(--space-5);
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
.login-title {
  margin: 0;
  color: var(--brand-primary);
  font-size: 20px;
  font-weight: 600;
}
.login-sub {
  margin: 4px 0 20px;
  color: var(--text-secondary);
  font-size: 13px;
}
.login-btn {
  width: 100%;
}
</style>
