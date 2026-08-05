<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { storesApi, type Store } from '@/api/stores'
import { useAsync } from '@/composables/useAsync'
import StatusBadge from '@/components/StatusBadge.vue'

const list = ref<Store[]>([])
const { loading, run: load } = useAsync(async () => {
  list.value = await storesApi.listMine()
})

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: '', address: '', phone: '', sort_order: 0 })

function openCreate() {
  editingId.value = null
  form.name = ''
  form.address = ''
  form.phone = ''
  form.sort_order = 0
  dialogVisible.value = true
}

function openEdit(store: Store) {
  editingId.value = store.id
  form.name = store.name
  form.address = store.address
  form.phone = store.phone
  form.sort_order = store.sort_order
  dialogVisible.value = true
}

async function onSubmit() {
  if (!form.name || !form.address || !form.phone) return
  if (editingId.value === null) {
    await storesApi.create({ ...form })
    ElMessage.success('已创建')
  } else {
    await storesApi.update(editingId.value, { ...form })
    ElMessage.success('已保存')
  }
  dialogVisible.value = false
  load()
}

async function toggle(store: Store) {
  await storesApi.setStatus(store.id, store.status === 'open' ? 'closed' : 'open')
  ElMessage.success(store.status === 'open' ? '已打烊' : '已营业')
  load()
}

async function onDelete(store: Store) {
  await ElMessageBox.confirm(`确定删除「${store.name}」？`, '提示', { type: 'warning' })
  await storesApi.remove(store.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <el-card>
      <div style="display: flex; justify-content: space-between; margin-bottom: 12px">
        <h3 style="margin: 0">门店管理</h3>
        <el-button type="primary" @click="openCreate">新建门店</el-button>
      </div>
      <el-table :data="list">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="address" label="地址" />
        <el-table-column prop="phone" label="电话" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <StatusBadge :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link :type="row.status === 'open' ? 'warning' : 'success'" @click="toggle(row)">
              {{ row.status === 'open' ? '打烊' : '营业' }}
            </el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId === null ? '新建门店' : '编辑门店'" width="480px">
      <el-form :model="form" label-width="70px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
