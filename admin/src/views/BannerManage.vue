<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bannersApi, type Banner } from '@/api/banners'
import { apiOrigin } from '@/api/http'
import { useAsync } from '@/composables/useAsync'
import { useCurrentStore } from '@/stores/store'

const store = useCurrentStore()
const list = ref<Banner[]>([])
const uploading = ref(false)
const { loading, run: load } = useAsync(async () => {
  if (!store.hasStore) return
  list.value = await bannersApi.list(store.id)
})

async function onUpload(options: { file: File }) {
  uploading.value = true
  try {
    await bannersApi.create(store.id, options.file)
    ElMessage.success('轮播图已上传')
    load()
  } finally {
    uploading.value = false
  }
}

async function onToggle(banner: Banner) {
  await bannersApi.update(store.id, banner.id, { is_active: !banner.is_active })
  ElMessage.success(banner.is_active ? '已下架' : '已上架')
  load()
}

async function onSort(banner: Banner) {
  await bannersApi.update(store.id, banner.id, { sort_order: banner.sort_order })
  ElMessage.success('已保存')
  load()
}

async function onDelete(banner: Banner) {
  await ElMessageBox.confirm('确定删除该轮播图？', '提示', { type: 'warning' })
  await bannersApi.remove(store.id, banner.id)
  ElMessage.success('已删除')
  load()
}

watch(() => store.id, load)
onMounted(load)
</script>

<template>
  <div v-loading="loading">
    <el-card>
      <div style="display: flex; justify-content: space-between; margin-bottom: 12px">
        <h3 style="margin: 0">轮播图管理：{{ store.name }}</h3>
        <el-upload :show-file-list="false" :http-request="onUpload" accept="image/jpeg,image/png,image/webp">
          <el-button type="primary" :loading="uploading">上传轮播图</el-button>
        </el-upload>
      </div>
      <el-table :data="list">
        <el-table-column label="图片" width="180">
          <template #default="{ row }">
            <el-image
              :src="apiOrigin + row.image_url"
              :preview-src-list="[apiOrigin + row.image_url]"
              style="width: 140px; height: 60px; border-radius: 6px"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column label="排序" width="160">
          <template #default="{ row }">
            <el-input-number v-model="row.sort_order" :min="0" size="small" @change="onSort(row)" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch :model-value="row.is_active" @change="onToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="list.length === 0" description="暂无轮播图，上传后小程序菜单页顶部展示" />
    </el-card>
  </div>
</template>
