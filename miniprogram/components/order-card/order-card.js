const { formatTime } = require('../../utils/format')

Component({
  properties: {
    order: { type: Object, value: null },
  },
  data: {
    displayTime: '',
  },
  observers: {
    order(order) {
      if (order && order.created_at) {
        this.setData({ displayTime: formatTime(order.created_at) })
      }
    },
  },
  methods: {
    onDetail() {
      this.triggerEvent('detail', { order: this.properties.order })
    },
    onCancel() {
      this.triggerEvent('cancel', { order: this.properties.order })
    },
    onPickup() {
      this.triggerEvent('pickup', { order: this.properties.order })
    },
  },
})
