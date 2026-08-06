<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ordersApi, type AuditLog, type Order, type OrderDetail } from '@/api/orders'
import { useAsync } from '@/composables/useAsync'
import { useCurrentStore } from '@/stores/store'
import PriceText from '@/components/PriceText.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { centsToYuan } from '@/utils/format'
import { detectNewPending } from '@/utils/order-alert'
import { playAlertSound } from '@/utils/sound'
import { ensureNotifyPermission, notifyOrder } from '@/utils/desktop-notify'
import { buildExportFilename, downloadBlob } from '@/utils/csv-download'
import { auditActionText } from '@/utils/order-audit'

const store = useCurrentStore()
const orders = ref<Order[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const stats = ref({ today: 0, pending: 0, completed: 0, revenueToday: 0 })
const filter = reactive({ order_status: '', keyword: '', dateRange: null as [string, string] | null })
const lastIds = ref<number[]>([])
const baselineSet = ref(false)
const alertEnabled = ref(localStorage.getItem('admin_alert_enabled') === '1')
const { loading, run: load } = useAsync(async () => {
  if (!store.hasStore) return
  const data = await ordersApi.list({
    store_id: store.id,
    order_status: filter.order_status || undefined,
    keyword: filter.keyword || undefined,
    date_from: filter.dateRange?.[0] || undefined,
    date_to: filter.dateRange?.[1] || undefined,
    page: page.value,
    page_size: pageSize.value,
  })
  orders.value = data.items
  total.value = data.total
  stats.value = {
    today: data.stats.today,
    pending: data.stats.pending,
    completed: data.stats.completed,
    revenueToday: data.stats.revenue_today,
  }
  if (!baselineSet.value) {
    baselineSet.value = true
  } else if (alertEnabled.value && !filter.order_status && !filter.keyword && !filter.dateRange) {
    const fresh = detectNewPending(lastIds.value, data.items)
    if (fresh.length > 0) {
      const names = data.items.filter((o) => fresh.includes(o.id)).map((o) => o.order_no).join('、')
      playAlertSound()
      notifyOrder('新订单待接单', `订单 ${names}`)
      ElMessage.success(`新订单：${names}`)
    }
  }
  lastIds.value = data.items.map((o) => o.id)
})

function onFilterChange() {
  page.value = 1
  load()
}

function onSizeChange() {
  page.value = 1
  load()
}

const cancelDialog = ref(false)
const cancelOrderId = ref<number | null>(null)
const cancelReason = ref<'merchant_cancel_not_made' | 'merchant_cancel_made'>('merchant_cancel_not_made')

const detailDialog = ref(false)
const detail = ref<OrderDetail | null>(null)
const auditLogs = ref<AuditLog[]>([])
const exporting = ref(false)

async function exportCsv() {
  if (!store.hasStore || exporting.value) return
  exporting.value = true
  try {
    const blob = await ordersApi.exportCsv({
      store_id: store.id,
      order_status: filter.order_status || undefined,
      keyword: filter.keyword || undefined,
      date_from: filter.dateRange?.[0] || undefined,
      date_to: filter.dateRange?.[1] || undefined,
    })
    downloadBlob(blob, buildExportFilename(store.name))
  } finally {
    exporting.value = false
  }
}

async function enableAlert() {
  const ok = await ensureNotifyPermission()
  if (!ok) ElMessage.warning('桌面通知未授权，声音提醒仍可用')
  playAlertSound()
  alertEnabled.value = true
  localStorage.setItem('admin_alert_enabled', '1')
  ElMessage.success('新订单提醒已开启')
}

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
  auditLogs.value = await ordersApi.audit(order.id)
  detailDialog.value = true
}

function maskPhone(phone: string) {
  return phone.replace(/^(\d{3})\d{4}(\d{4})$/, '$1****$2')
}

function printReceipt(order: OrderDetail) {
  const win = window.open('', '_blank', 'width=340,height=520')
  if (!win) return
  const lines = order.items
    .map(
      (i) =>
        `<tr><td>${i.item_name} ×${i.quantity}</td><td style="text-align:right">¥${centsToYuan(i.subtotal_cents)}</td></tr>`,
    )
    .join('')
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>订单小票</title><style>
    body{font-family:monospace;width:280px;margin:0 auto;padding:16px}
    h2{font-size:16px;text-align:center;margin:0 0 8px}
    .meta{font-size:12px;line-height:1.7}
    table{width:100%;font-size:12px;border-collapse:collapse;margin-top:8px}
    td{padding:3px 0}
    .total{font-weight:bold;border-top:1px dashed #000;margin-top:4px;padding-top:6px}
    .remark{font-size:12px;margin-top:8px}
    .foot{font-size:11px;text-align:center;margin-top:12px;color:#666}
  </style></head><body>
    <h2>${store.name}</h2>
    <div class="meta">单号：${order.order_no}<br>时间：${order.created_at.replace('T', ' ')}<br>类型：${order.entry_type === 'dinein' ? '到店点单' : '提前点单'}<br>顾客：${order.customer_name}</div>
    <table><tbody>${lines}</tbody></table>
    <div class="total">合计：¥${centsToYuan(order.total_cents)}（共 ${order.item_count} 件）</div>
    ${order.remark ? `<div class="remark">备注：${order.remark}</div>` : ''}
    <div class="foot">${maskPhone(order.customer_phone)}</div>
  </body></html>`)
  win.document.close()
  win.print()
}

let timer: number | undefined
onMounted(() => {
  load()
  timer = window.setInterval(load, 8000)
})
onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
watch(() => store.id, () => {
  page.value = 1
  load()
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
        <div style="display: flex; gap: 8px; align-items: center">
          <el-input
            v-model="filter.keyword"
            placeholder="订单号/手机号/姓名"
            clearable
            style="width: 220px"
            @keyup.enter="onFilterChange"
            @clear="onFilterChange"
            @change="onFilterChange"
          />
          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 250px"
            @change="onFilterChange"
          />
          <el-select v-model="filter.order_status" placeholder="全部状态" clearable style="width: 140px" @change="onFilterChange">
            <el-option label="待接单" value="pending" />
            <el-option label="已接单" value="accepted" />
            <el-option label="已出单" value="served" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button @click="load">刷新</el-button>
          <el-button type="primary" plain :loading="exporting" @click="exportCsv">导出 CSV</el-button>
          <el-button v-if="!alertEnabled" type="warning" plain @click="enableAlert">开启提醒</el-button>
          <el-button v-else type="success" plain disabled>提醒已开启</el-button>
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
      <div style="display: flex; justify-content: flex-end; margin-top: 12px">
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
        <h4 style="margin: 16px 0 8px">操作记录</h4>
        <el-table :data="auditLogs" size="small">
          <el-table-column label="动作" width="120">
            <template #default="{ row }">{{ auditActionText(row.action) }}</template>
          </el-table-column>
          <el-table-column label="操作方" width="90">
            <template #default="{ row }">{{ row.actor_type === 'merchant' ? '商家' : '顾客' }}</template>
          </el-table-column>
          <el-table-column label="时间">
            <template #default="{ row }">{{ row.created_at.replace('T', ' ') }}</template>
          </el-table-column>
        </el-table>
      </template>
      <template #footer>
        <el-button @click="detailDialog = false">关闭</el-button>
        <el-button v-if="detail" type="primary" plain @click="printReceipt(detail)">打印小票</el-button>
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
