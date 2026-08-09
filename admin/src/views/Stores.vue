<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { storesApi, type Store } from '@/api/stores'
import { useAsync } from '@/composables/useAsync'
import { apiOrigin } from '@/api/http'
import StatusBadge from '@/components/StatusBadge.vue'
import { THEME_OPTIONS } from '@/theme-options'

const list = ref<Store[]>([])
const { loading, run: load } = useAsync(async () => {
  list.value = await storesApi.listMine()
})

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const uploading = ref(false)
const form = reactive({
  name: '',
  address: '',
  phone: '',
  latitude: null as number | null,
  longitude: null as number | null,
  image_url: null as string | null,
  theme: 'warm' as 'warm' | 'white' | 'night' | 'berry',
  sort_order: 0,
  open_time: null as string | null,
  close_time: null as string | null,
})

function openCreate() {
  editingId.value = null
  form.name = ''
  form.address = ''
  form.phone = ''
  form.latitude = null
  form.longitude = null
  form.image_url = null
  form.theme = 'warm'
  form.sort_order = 0
  form.open_time = null
  form.close_time = null
  dialogVisible.value = true
}

function openEdit(store: Store) {
  editingId.value = store.id
  form.name = store.name
  form.address = store.address
  form.phone = store.phone
  form.latitude = store.latitude ?? null
  form.longitude = store.longitude ?? null
  form.image_url = store.image_url ?? null
  form.theme = store.theme ?? 'warm'
  form.sort_order = store.sort_order
  form.open_time = store.open_time ?? null
  form.close_time = store.close_time ?? null
  dialogVisible.value = true
}

async function onSubmit() {
  if (!form.name || !form.address || !form.phone) return
  const payload = { ...form, latitude: form.latitude ?? null, longitude: form.longitude ?? null }
  if (editingId.value === null) {
    await storesApi.create(payload)
    ElMessage.success('已创建')
  } else {
    await storesApi.update(editingId.value, payload)
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

async function onUploadImage(options: { file: File }) {
  if (editingId.value === null) return
  uploading.value = true
  try {
    const updated = await storesApi.uploadImage(editingId.value, options.file)
    form.image_url = updated.image_url ?? null
  } finally {
    uploading.value = false
  }
}

async function onClearImage() {
  if (editingId.value === null) return
  const updated = await storesApi.clearImage(editingId.value)
  form.image_url = updated.image_url ?? null
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
        <el-table-column label="主题" width="130">
          <template #default="{ row }">
            <span style="display: inline-flex; align-items: center; gap: 6px">
              <span
                :style="{
                  display: 'inline-block',
                  width: '10px',
                  height: '10px',
                  borderRadius: '3px',
                  background: THEME_OPTIONS.find((t) => t.value === row.theme)?.primary || '#ccc',
                }"
              ></span>
              {{ THEME_OPTIONS.find((t) => t.value === row.theme)?.label.split('（')[0] || row.theme }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="封面" width="80">
          <template #default="{ row }">
            <el-image
              v-if="row.image_url"
              :src="apiOrigin + row.image_url"
              :preview-src-list="[apiOrigin + row.image_url]"
              style="width: 48px; height: 48px; border-radius: 6px"
              fit="cover"
            />
            <span v-else style="color: var(--text-secondary)">—</span>
          </template>
        </el-table-column>
        <el-table-column label="经纬度" width="170">
          <template #default="{ row }">{{ row.latitude != null ? `${row.latitude}, ${row.longitude}` : '—' }}</template>
        </el-table-column>
        <el-table-column label="营业时间" width="150">
          <template #default="{ row }">{{ row.open_time ? `${row.open_time} - ${row.close_time}` : '全天' }}</template>
        </el-table-column>
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
        <el-form-item label="主题">
          <el-select v-model="form.theme" style="width: 100%">
            <el-option v-for="t in THEME_OPTIONS" :key="t.value" :label="t.label" :value="t.value">
              <span style="display: inline-flex; align-items: center; gap: 8px">
                <span
                  :style="{
                    display: 'inline-block',
                    width: '12px',
                    height: '12px',
                    borderRadius: '4px',
                    background: `linear-gradient(135deg, ${t.primary} 0%, ${t.bg} 100%)`,
                    border: '1px solid #e8e1d8',
                  }"
                ></span>
                {{ t.label }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="封面图">
          <div style="display: flex; align-items: center; gap: 8px">
            <el-image
              v-if="form.image_url"
              :src="apiOrigin + form.image_url"
              :preview-src-list="[apiOrigin + form.image_url]"
              style="width: 64px; height: 64px; border-radius: 8px"
              fit="cover"
            />
            <span v-else style="color: var(--text-secondary)">未上传</span>
            <el-upload
              :show-file-list="false"
              :http-request="onUploadImage"
              accept="image/jpeg,image/png,image/webp"
            >
              <el-button size="small" :disabled="editingId === null" :loading="uploading">上传</el-button>
            </el-upload>
            <el-button v-if="form.image_url" size="small" type="danger" plain @click="onClearImage">清除</el-button>
          </div>
        </el-form-item>
        <el-form-item label="纬度">
          <el-input-number v-model="form.latitude" :min="-90" :max="90" :precision="6" :step="0.000001" :controls="false" style="width: 180px" placeholder="如 30.2741" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input-number v-model="form.longitude" :min="-180" :max="180" :precision="6" :step="0.000001" :controls="false" style="width: 180px" placeholder="如 120.1551" />
        </el-form-item>
        <el-form-item>
          <span style="font-size: 12px; color: var(--text-secondary)">经纬度需同时填写；可在高德/腾讯地图拾取坐标获取（原型期手填）</span>
        </el-form-item>
        <el-form-item label="营业时间">
          <el-time-picker v-model="form.open_time" format="HH:mm" value-format="HH:mm" placeholder="开始" style="width: 120px" />
          <span style="margin: 0 8px">至</span>
          <el-time-picker v-model="form.close_time" format="HH:mm" value-format="HH:mm" placeholder="结束" style="width: 120px" />
          <div style="width: 100%; font-size: 12px; color: var(--text-secondary)">支持跨天，如 22:00-02:00</div>
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
