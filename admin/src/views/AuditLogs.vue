<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { auditApi, type AuditLogRow } from '@/api/audit'
import { useCurrentStore } from '@/stores/store'
import { useAsync } from '@/composables/useAsync'
import { auditActionText } from '@/utils/order-audit'
import { buildAuditFilename, downloadBlob } from '@/utils/csv-download'

const store = useCurrentStore()
const logs = ref<AuditLogRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filter = reactive({ dateRange: null as [string, string] | null })
const exporting = ref(false)

const { loading, run: load } = useAsync(async () => {
  if (!store.hasStore) return
  const data = await auditApi.list({
    store_id: store.id,
    date_from: filter.dateRange?.[0] || undefined,
    date_to: filter.dateRange?.[1] || undefined,
    page: page.value,
    page_size: pageSize.value,
  })
  logs.value = data.items
  total.value = data.total
})

function onFilterChange() {
  page.value = 1
  load()
}

function onSizeChange() {
  page.value = 1
  load()
}

async function exportCsv() {
  if (!store.hasStore || exporting.value) return
  exporting.value = true
  try {
    const blob = await auditApi.exportCsv({
      store_id: store.id,
      date_from: filter.dateRange?.[0] || undefined,
      date_to: filter.dateRange?.[1] || undefined,
    })
    downloadBlob(blob, buildAuditFilename(store.name))
  } finally {
    exporting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-loading="loading" class="page">
    <div class="panel">
      <div class="panel-head">
        <h3 class="panel-title">操作审计：{{ store.name }}</h3>
        <div class="filter-row">
          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 250px"
            @change="onFilterChange"
          />
          <el-button type="primary" plain :loading="exporting" @click="exportCsv">导出 CSV</el-button>
          <el-button @click="load">刷新</el-button>
        </div>
      </div>
      <el-table :data="logs" class="data-table">
        <el-table-column label="时间" width="170">
          <template #default="{ row }">{{ row.created_at.replace('T', ' ') }}</template>
        </el-table-column>
        <el-table-column prop="order_no" label="订单号" width="100" />
        <el-table-column prop="store_name" label="门店" width="130" />
        <el-table-column label="动作" width="110">
          <template #default="{ row }">{{ auditActionText(row.action) }}</template>
        </el-table-column>
        <el-table-column label="操作方" width="90">
          <template #default="{ row }">{{ row.actor_type === 'merchant' ? '商家' : '顾客' }}</template>
        </el-table-column>
        <el-table-column label="详情">
          <template #default="{ row }">{{ row.detail ? JSON.stringify(row.detail) : '—' }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-if="logs.length === 0" description="暂无审计记录" />
      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="load"
          @size-change="onSizeChange"
        />
      </div>
    </div>
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
.filter-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-3);
}
.data-table {
  --el-table-header-bg-color: var(--surface-muted);
  --el-table-row-hover-bg-color: #fef4ef;
  --el-table-border-color: var(--border-color);
}
</style>
