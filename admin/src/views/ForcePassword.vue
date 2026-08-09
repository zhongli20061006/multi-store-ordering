<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const submitting = ref(false)
const pwd = reactive({ old_password: '', new_password: '', confirm: '' })

async function onSubmit() {
  if (!pwd.old_password || !pwd.new_password) return
  if (pwd.new_password !== pwd.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  submitting.value = true
  try {
    await changePassword(pwd.old_password, pwd.new_password)
    auth.passwordChanged()
    ElMessage.success('密码已修改，请使用新密码继续使用后台')
    router.push('/')
  } catch {
    // 错误提示由 http 拦截器统一处理
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="force-page">
    <div class="force-card">
      <h2 class="force-title">首次登录需修改密码</h2>
      <p class="force-sub">当前账号使用默认演示密码，为安全起见请先设置新密码，之后才能进入后台。</p>
      <el-form :model="pwd" label-width="90px" @submit.prevent>
        <el-form-item label="当前密码">
          <el-input v-model="pwd.old_password" type="password" show-password placeholder="默认演示密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwd.new_password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwd.confirm" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
        <el-button type="primary" :loading="submitting" class="force-btn" @click="onSubmit">修改并进入后台</el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.force-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  position: relative;
}
.force-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, rgba(240, 100, 58, 0.12), transparent 60%);
  pointer-events: none;
}
.force-card {
  position: relative;
  width: 420px;
  padding: var(--space-5);
  background: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
.force-title {
  margin: 0;
  color: var(--brand-primary);
  font-size: 20px;
  font-weight: 600;
}
.force-sub {
  margin: 6px 0 20px;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}
.force-btn {
  width: 100%;
}
</style>
