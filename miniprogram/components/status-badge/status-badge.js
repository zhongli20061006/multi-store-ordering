const { statusText, entryTypeText, paymentStatusText } = require('../../utils/status-map')

const COLOR = {
  order: { pending: 'warning', accepted: 'primary', completed: 'success', cancelled: 'info' },
  payment: { unpaid: 'warning', paid: 'success' },
  entry: {},
}

Component({
  properties: {
    status: { type: String, value: '' },
    type: { type: String, value: 'order' },
  },
  data: {
    text: '',
    cls: 'info',
  },
  observers: {
    'status, type': function (status, type) {
      const textMap = {
        order: statusText(status),
        payment: paymentStatusText(status),
        entry: entryTypeText(status),
      }
      const colorMap = COLOR[type] || {}
      this.setData({
        text: textMap[type] || status,
        cls: colorMap[status] || 'info',
      })
    },
  },
})
