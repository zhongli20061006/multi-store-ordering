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
  <div v-loading="loading">
    <el-card style="margin-bottom: 16px">
      <h3 style="margin: 0 0 16px">数据看板：{{ store.name }}</h3>
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px">
        <el-card shadow="never">
          <div class="stat-num" style="color: var(--brand-primary)">{{ data?.today.order_count ?? 0 }}</div>
          <div class="stat-label">今日订单</div>
        </el-card>
        <el-card shadow="never">
          <div class="stat-num" style="color: #e6a23c">{{ data?.today.pending ?? 0 }}</div>
          <div class="stat-label">待接单</div>
        </el-card>
        <el-card shadow="never">
          <div class="stat-num" style="color: #67c23a">{{ data?.today.completed ?? 0 }}</div>
          <div class="stat-label">今日已完成</div>
        </el-card>
        <el-card shadow="never">
          <div class="stat-num" style="color: var(--brand-primary)"><PriceText :cents="data?.today.revenue_cents ?? 0" /></div>
          <div class="stat-label">今日营业额</div>
        </el-card>
      </div>
    </el-card>

    <el-card>
      <h3 style="margin: 0 0 16px">近 7 天营业额</h3>
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
    </el-card>

    <el-card style="margin-top: 16px">
      <h3 style="margin: 0 0 12px">近 7 天明细</h3>
      <el-table :data="data?.daily ?? []">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="order_count" label="订单数" width="120" />
        <el-table-column label="营业额">
          <template #default="{ row }"><PriceText :cents="row.revenue_cents" /></template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.stat-num {
  font-size: 24px;
  font-weight: 600;
}
.stat-label {
  margin-top: 4px;
  color: var(--text-secondary);
  font-size: 13px;
}
.chart {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 180px;
  padding: 0 8px;
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
</style>
