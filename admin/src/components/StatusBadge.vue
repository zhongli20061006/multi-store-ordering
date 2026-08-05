<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ status: string }>()

const map: Record<string, { type: 'primary' | 'success' | 'warning' | 'info' | 'danger'; text: string }> = {
  pending: { type: 'warning', text: '待接单' },
  accepted: { type: 'primary', text: '已接单' },
  completed: { type: 'success', text: '已完成' },
  cancelled: { type: 'info', text: '已取消' },
  open: { type: 'success', text: '营业中' },
  closed: { type: 'info', text: '已打烊' },
  unpaid: { type: 'warning', text: '未付款' },
  paid: { type: 'success', text: '已付款' },
}

const item = computed(() => map[props.status] || { type: 'info' as const, text: props.status })
</script>

<template>
  <el-tag :type="item.type">{{ item.text }}</el-tag>
</template>
