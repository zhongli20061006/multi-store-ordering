<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { dashboardApi, type DashboardData } from '@/api/dashboard'
import { useAsync } from '@/composables/useAsync'
import { useCurrentStore } from '@/stores/store'
import PriceText from '@/components/PriceText.vue'
import { centsToYuan } from '@/utils/format'

const store = useCurrentStore()
const data = ref<DashboardData | null>(null)
const { loading, run: load } = useAsync(async () => {
  if (!store.hasStore) return
  data.value = await dashboardApi.get(store.id)
})

const maxRevenue = computed(() => Math.max(1, ...(data.value?.daily.map((d) => d.revenue_cents) ?? [0])))

watch(() => store.id, load)
onMounted(load)
</script>

<template>
  <div class="page">
    <div class="panel">
      <h3 class="panel-title">数据看板：{{ store.name }}</h3>
      <el-skeleton v-if="loading" :rows="2" animated />
      <div v-else class="stat-grid">
        <div class="stat-card">
          <div class="stat-num tabular">{{ data?.today.order_count ?? 0 }}</div>
          <div class="stat-label">今日订单</div>
        </div>
        <div class="stat-card">
          <div class="stat-num warning tabular">{{ data?.today.pending ?? 0 }}</div>
          <div class="stat-label">待接单</div>
        </div>
        <div class="stat-card">
          <div class="stat-num success tabular">{{ data?.today.completed ?? 0 }}</div>
          <div class="stat-label">今日已完成</div>
        </div>
        <div class="stat-card">
          <div class="stat-num accent tabular"><PriceText :cents="data?.today.revenue_cents ?? 0" /></div>
          <div class="stat-label">今日营业额</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <h3 class="panel-title">近 7 天营业额</h3>
      <div class="chart">
        <div v-for="d in data?.daily ?? []" :key="d.date" class="bar-col">
          <div class="bar-wrap">
            <div class="bar" :style="{ height: Math.max(2, (d.revenue_cents / maxRevenue) * 120) + 'px' }">
              <span class="bar-val">¥{{ centsToYuan(d.revenue_cents) }}</span>
            </div>
          </div>
          <div class="bar-date">{{ d.date }}</div>
          <div class="bar-count">{{ d.order_count }} 单</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <h3 class="panel-title">近 7 天明细</h3>
      <el-table :data="data?.daily ?? []" class="data-table">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="order_count" label="订单数" width="120" />
        <el-table-column label="营业额">
          <template #default="{ row }"><PriceText :cents="row.revenue_cents" /></template>
        </el-table-column>
      </el-table>
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
.panel-title {
  margin: 0 0 var(--space-3);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}
.stat-card {
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  box-shadow: var(--shadow-card);
}
.stat-num {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
  color: var(--text-main);
}
.stat-num.accent {
  color: var(--brand-primary);
}
.stat-num.warning {
  color: var(--warning);
}
.stat-num.success {
  color: var(--success);
}
.stat-label {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 13px;
}
.tabular {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}
.chart {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  height: 180px;
  padding: var(--space-3);
  background: var(--surface-muted);
  border-radius: var(--radius-md);
}
.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bar-wrap {
  display: flex;
  align-items: flex-end;
  height: 140px;
}
.bar {
  width: 36px;
  background: var(--brand-primary);
  border-radius: 6px 6px 0 0;
  position: relative;
  transition: background 200ms ease;
}
.bar:hover {
  background: var(--brand-strong);
}
.bar-val {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}
.bar-date {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-main);
}
.bar-count {
  font-size: 11px;
  color: var(--text-disabled);
}
.data-table {
  --el-table-header-bg-color: var(--surface-muted);
  --el-table-row-hover-bg-color: #fef4ef;
  --el-table-border-color: var(--border-color);
}
</style>
