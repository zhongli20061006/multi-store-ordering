<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ordersApi, type Order, type OrderDetail } from '@/api/orders'
import { useAsync } from '@/composables/useAsync'
import { useCurrentStore } from '@/stores/store'
import PriceText from '@/components/PriceText.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { centsToYuan } from '@/utils/format'

const store = useCurrentStore()
const orders = ref<Order[]>([])
const filter = reactive({ order_status: '' })
const { loading, run: load } = useAsync(async () => {
  if (!store.hasStore) return
  orders.value = await ordersApi.list({ store_id: store.id, order_status: filter.order_status || undefined })
})

const cancelDialog = ref(false)
const cancelOrderId = ref<number | null>(null)
const cancelReason = ref<'merchant_cancel_not_made' | 'merchant_cancel_made'>('merchant_cancel_not_made')

const detailDialog = ref(false)
const detail = ref<OrderDetail | null>(null)

function openCancel(order: Order) {
  cancelOrderId.value = order.id
  cancelReason.value = 'merchant_cancel_not_made'
  cancelDialog.value = true
}

async function submitCancel() {
  if (cancelOrderId.value === null) return
  await ordersApi.cancel(cancelOrderId.value, cancelReason.value)
  ElMessage.success('已取消')
  cancelDialog.value = false
  load()
}

async function accept(order: Order) {
  await ordersApi.updateStatus(order.id, 'accepted')
  ElMessage.success('已接单')
  load()
}

async function serve(order: Order) {
  await ordersApi.updateStatus(order.id, 'served')
  ElMessage.success('已出单')
  load()
}

async function markPaid(order: Order) {
  await ordersApi.markPaid(order.id)
  ElMessage.success('已标记付款')
  load()
}

async function showDetail(order: Order) {
  detail.value = await ordersApi.detail(order.id)
  detailDialog.value = true
}

let timer: number | undefined
onMounted(() => {
  load()
  timer = window.setInterval(load, 8000)
})
onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
watch(() => store.id, load)

const todayStart = new Date()
todayStart.setHours(0, 0, 0, 0)

const stats = computed(() => {
  const today = orders.value.filter((order) => {
    const d = new Date(order.created_at.replace(' ', 'T') + 'Z')
    return d >= todayStart
  })
  const completedToday = today.filter((order) => order.order_status === 'completed')
  return {
    today: today.length,
    pending: orders.value.filter((order) => order.order_status === 'pending').length,
    completed: orders.value.filter((order) => order.order_status === 'completed').length,
    revenueToday: completedToday.reduce((sum, order) => sum + order.total_cents, 0),
  }
})
</script>

<template>
  <div v-loading="loading">
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card>
          <div class="stat-num" style="color: var(--brand-primary)">{{ stats.today }}</div>
          <div class="stat-label">今日订单</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-num" style="color: #e6a23c">{{ stats.pending }}</div>
          <div class="stat-label">待接单</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-num" style="color: #67c23a">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card>
          <div class="stat-num" style="color: var(--brand-primary)">¥{{ centsToYuan(stats.revenueToday) }}</div>
          <div class="stat-label">今日营业额</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <div style="display: flex; justify-content: space-between; margin-bottom: 12px">
        <h3 style="margin: 0">订单管理：{{ store.name }}</h3>
        <div style="display: flex; gap: 8px">
          <el-select v-model="filter.order_status" placeholder="全部状态" clearable style="width: 140px" @change="load">
            <el-option label="待接单" value="pending" />
            <el-option label="已接单" value="accepted" />
            <el-option label="已出单" value="served" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button @click="load">刷新</el-button>
        </div>
      </div>

      <el-table :data="orders">
        <el-table-column prop="order_no" label="订单号" width="190" />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">{{ row.entry_type === 'dinein' ? '扫码' : '提前点' }}</template>
        </el-table-column>
        <el-table-column label="顾客" width="160">
          <template #default="{ row }">
            {{ row.customer_name }}（{{ row.customer_phone }}）
          </template>
        </el-table-column>
        <el-table-column prop="item_count" label="件数" width="70" />
        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            <PriceText :cents="row.total_cents" />
          </template>
        </el-table-column>
        <el-table-column label="订单状态" width="110">
          <template #default="{ row }">
            <StatusBadge :status="row.order_status" />
          </template>
        </el-table-column>
        <el-table-column label="付款" width="100">
          <template #default="{ row }">
            <StatusBadge :status="row.payment_status" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            <el-button v-if="row.order_status === 'pending'" link type="primary" @click="accept(row)">接单</el-button>
            <el-button v-if="row.order_status === 'accepted'" link type="success" @click="serve(row)">出单</el-button>
            <el-button v-if="row.order_status === 'pending' || row.order_status === 'accepted'" link type="danger" @click="openCancel(row)">
              取消
            </el-button>
            <el-button v-if="row.payment_status === 'unpaid' && row.order_status !== 'cancelled'" link type="warning" @click="markPaid(row)">
              标记付款
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="orders.length === 0" description="暂无订单" />
    </el-card>

    <el-dialog v-model="cancelDialog" title="取消订单" width="420px">
      <el-radio-group v-model="cancelReason">
        <el-radio value="merchant_cancel_not_made">未制作（回补库存）</el-radio>
        <el-radio value="merchant_cancel_made">已制作（不回补库存）</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="cancelDialog = false">再想想</el-button>
        <el-button type="danger" @click="submitCancel">确认取消</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialog" title="订单详情" width="640px">
      <template v-if="detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ detail.order_no }}</el-descriptions-item>
          <el-descriptions-item label="状态"><StatusBadge :status="detail.order_status" /></el-descriptions-item>
          <el-descriptions-item label="顾客">{{ detail.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ detail.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="总额">¥{{ centsToYuan(detail.total_cents) }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detail.remark || '无' }}</el-descriptions-item>
        </el-descriptions>
        <el-table :data="detail.items" style="margin-top: 12px">
          <el-table-column prop="item_name" label="商品" />
          <el-table-column label="单价" width="100">
            <template #default="{ row }">¥{{ centsToYuan(row.unit_price_cents) }}</template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column label="小计" width="110">
            <template #default="{ row }">¥{{ centsToYuan(row.subtotal_cents) }}</template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>
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
</style>
