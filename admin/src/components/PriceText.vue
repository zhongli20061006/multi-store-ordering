<script setup lang="ts">
import { computed } from 'vue'
import { centsToYuan } from '@/utils/format'

const props = defineProps<{ cents: number }>()
const text = computed(() => `¥${centsToYuan(props.cents)}`)
</script>

<template>{{ text }}</template>
