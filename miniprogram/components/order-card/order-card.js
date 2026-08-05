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
    onCancel() {
      this.triggerEvent('cancel')
    },
  },
})
