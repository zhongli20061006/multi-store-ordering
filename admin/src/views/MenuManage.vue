<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { menusApi, type Category, type Item } from '@/api/menus'
import { useAsync } from '@/composables/useAsync'
import { apiOrigin } from '@/api/http'
import { useCurrentStore } from '@/stores/store'
import { centsToYuan } from '@/utils/format'

const store = useCurrentStore()
const categories = ref<Category[]>([])
const items = ref<Item[]>([])
const { loading, run: loadAll } = useAsync(async () => {
  if (!store.hasStore) return
  categories.value = await menusApi.categories(store.id)
  items.value = await menusApi.items(store.id)
})

const categoryDialog = ref(false)
const categoryId = ref<number | null>(null)
const categoryForm = reactive({ name: '', sort_order: 0 })

const itemDialog = ref(false)
const itemId = ref<number | null>(null)
const uploading = ref(false)
const itemForm = reactive({
  name: '',
  description: '',
  price_yuan: 0,
  stock: '',
  image_url: null as string | null,
  category_id: null as number | null,
  sort_order: 0,
  is_active: true,
})

function openCategoryCreate() {
  categoryId.value = null
  categoryForm.name = ''
  categoryForm.sort_order = 0
  categoryDialog.value = true
}

function openCategoryEdit(category: Category) {
  categoryId.value = category.id
  categoryForm.name = category.name
  categoryForm.sort_order = category.sort_order
  categoryDialog.value = true
}

async function submitCategory() {
  if (!categoryForm.name) return
  const payload = { name: categoryForm.name, sort_order: categoryForm.sort_order, is_active: true }
  if (categoryId.value === null) {
    await menusApi.createCategory(store.id, payload)
    ElMessage.success('分类已创建')
  } else {
    await menusApi.updateCategory(store.id, categoryId.value, payload)
    ElMessage.success('分类已保存')
  }
  categoryDialog.value = false
  loadAll()
}

async function onDeleteCategory(category: Category) {
  await ElMessageBox.confirm(`删除分类「${category.name}」会连带下架该分类下的商品，确定？`, '提示', { type: 'warning' })
  await menusApi.deleteCategory(store.id, category.id)
  ElMessage.success('分类已删除')
  loadAll()
}

function openItemCreate() {
  itemId.value = null
  itemForm.name = ''
  itemForm.description = ''
  itemForm.price_yuan = 0
  itemForm.stock = ''
  itemForm.image_url = null
  itemForm.category_id = categories.value[0]?.id ?? null
  itemForm.sort_order = 0
  itemForm.is_active = true
  itemDialog.value = true
}

function openItemEdit(item: Item) {
  itemId.value = item.id
  itemForm.name = item.name
  itemForm.description = item.description || ''
  itemForm.price_yuan = item.price_cents / 100
  itemForm.stock = item.stock === null || item.stock === undefined ? '' : String(item.stock)
  itemForm.image_url = item.image_url ?? null
  itemForm.category_id = item.category_id ?? null
  itemForm.sort_order = item.sort_order
  itemForm.is_active = item.is_active
  itemDialog.value = true
}

async function submitItem() {
  if (!itemForm.name || itemForm.price_yuan <= 0) return
  const stock = itemForm.stock === '' ? null : Number(itemForm.stock)
  if (stock !== null && (!Number.isInteger(stock) || stock < 0)) {
    ElMessage.warning('库存必须是 ≥0 的整数或留空')
    return
  }
  const payload = {
    name: itemForm.name,
    description: itemForm.description || null,
    price_cents: Math.round(itemForm.price_yuan * 100),
    stock,
    category_id: itemForm.category_id,
    sort_order: itemForm.sort_order,
    is_active: itemForm.is_active,
  }
  if (itemId.value === null) {
    await menusApi.createItem(store.id, payload)
    ElMessage.success('商品已创建')
  } else {
    await menusApi.updateItem(store.id, itemId.value, payload)
    ElMessage.success('商品已保存')
  }
  itemDialog.value = false
  loadAll()
}

async function onUploadImage(options: { file: File }) {
  if (itemId.value === null) return
  uploading.value = true
  try {
    const updated = await menusApi.uploadItemImage(store.id, itemId.value, options.file)
    itemForm.image_url = updated.image_url ?? null
    ElMessage.success('图片已上传')
  } finally {
    uploading.value = false
  }
}

async function onClearImage() {
  if (itemId.value === null || !itemForm.image_url) return
  const updated = await menusApi.clearItemImage(store.id, itemId.value)
  itemForm.image_url = updated.image_url ?? null
  ElMessage.success('图片已清除')
}

async function toggleItem(item: Item) {
  await menusApi.updateItem(store.id, item.id, { is_active: !item.is_active })
  ElMessage.success(item.is_active ? '已下架' : '已上架')
  loadAll()
}

async function onDeleteItem(item: Item) {
  await ElMessageBox.confirm(`下架「${item.name}」？`, '提示', { type: 'warning' })
  await menusApi.deleteItem(store.id, item.id)
  ElMessage.success('已下架')
  loadAll()
}

watch(() => store.id, loadAll)
onMounted(loadAll)
</script>

<template>
  <div v-loading="loading" class="page">
    <div class="panel">
      <div class="panel-head">
        <h3 class="panel-title">菜单管理：{{ store.name }}</h3>
        <el-button type="primary" @click="openCategoryCreate">新建分类</el-button>
      </div>

      <div class="menu-layout">
        <div class="cat-col">
          <div class="cat-panel">
            <div v-for="category in categories" :key="category.id" class="cat-row">
              <span>{{ category.name }}</span>
              <span>
                <el-button link type="primary" size="small" @click="openCategoryEdit(category)">编辑</el-button>
                <el-button link type="danger" size="small" @click="onDeleteCategory(category)">删除</el-button>
              </span>
            </div>
            <el-empty v-if="categories.length === 0" description="暂无分类" :image-size="60" />
          </div>
        </div>

        <div class="item-col">
          <div class="item-head">
            <el-button type="primary" plain @click="openItemCreate">新增商品</el-button>
          </div>
          <el-table :data="items" class="data-table">
            <el-table-column label="图片" width="80">
              <template #default="{ row }">
                <el-image
                  v-if="row.image_url"
                  :src="apiOrigin + row.image_url"
                  :preview-src-list="[apiOrigin + row.image_url]"
                  style="width: 40px; height: 40px; border-radius: 4px"
                  fit="cover"
                />
                <span v-else style="color: var(--text-secondary)">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" />
            <el-table-column label="分类" width="140">
              <template #default="{ row }">
                {{ categories.find((c) => c.id === row.category_id)?.name || '未分类' }}
              </template>
            </el-table-column>
            <el-table-column label="价格" width="110">
              <template #default="{ row }">¥{{ centsToYuan(row.price_cents) }}</template>
            </el-table-column>
            <el-table-column label="库存" width="130">
              <template #default="{ row }">
                <template v-if="row.stock !== null && row.stock !== undefined && row.stock <= 5">
                  <el-tag type="danger" size="small">{{ row.stock }}</el-tag>
                  <span class="low-stock">低库存</span>
                </template>
                <template v-else>{{ row.stock === null || row.stock === undefined ? '不限' : row.stock }}</template>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch :model-value="row.is_active" @change="toggleItem(row)" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button link type="primary" @click="openItemEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="onDeleteItem(row)">下架</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <el-dialog v-model="categoryDialog" :title="categoryId === null ? '新建分类' : '编辑分类'" width="420px">
      <el-form :model="categoryForm" label-width="70px">
        <el-form-item label="名称"><el-input v-model="categoryForm.name" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="categoryForm.sort_order" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="itemDialog" :title="itemId === null ? '新增商品' : '编辑商品'" width="520px">
      <el-form :model="itemForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="itemForm.name" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="itemForm.category_id" style="width: 100%">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="价格(元)">
          <el-input-number v-model="itemForm.price_yuan" :min="0.01" :precision="2" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存">
          <el-input v-model="itemForm.stock" placeholder="留空=不限量" />
        </el-form-item>
        <el-form-item label="图片">
          <div style="display: flex; align-items: center; gap: 8px">
            <el-image
              v-if="itemForm.image_url"
              :src="apiOrigin + itemForm.image_url"
              :preview-src-list="[apiOrigin + itemForm.image_url]"
              style="width: 64px; height: 64px; border-radius: 6px"
              fit="cover"
            />
            <span v-else style="color: var(--text-secondary)">未上传</span>
            <el-upload
              :show-file-list="false"
              :http-request="onUploadImage"
              accept="image/jpeg,image/png,image/webp"
            >
              <el-button size="small" :disabled="itemId === null" :loading="uploading">上传</el-button>
            </el-upload>
            <el-button v-if="itemForm.image_url" size="small" type="danger" plain @click="onClearImage">清除</el-button>
          </div>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="itemForm.sort_order" :min="0" /></el-form-item>
        <el-form-item label="上架"><el-switch v-model="itemForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialog = false">取消</el-button>
        <el-button type="primary" @click="submitItem">保存</el-button>
      </template>
    </el-dialog>
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
.panel-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}
.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}
.menu-layout {
  display: flex;
  gap: var(--space-3);
}
.cat-col {
  width: 220px;
  flex-shrink: 0;
}
.cat-panel {
  background: var(--surface-muted);
  border-radius: var(--radius-md);
  padding: var(--space-2);
}
.cat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
}
.item-col {
  flex: 1;
}
.item-head {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--space-3);
}
.low-stock {
  color: var(--danger);
  margin-left: 4px;
  font-size: 12px;
}
.data-table {
  --el-table-header-bg-color: var(--surface-muted);
  --el-table-row-hover-bg-color: #fef4ef;
  --el-table-border-color: var(--border-color);
}
</style>
