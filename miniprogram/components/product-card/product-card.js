const { API_ORIGIN } = require('../../config')

Component({
  properties: {
    item: { type: Object, value: null },
  },
  data: {
    imgBase: API_ORIGIN,
  },
  methods: {
    onDetail() {
      this.triggerEvent('detail', { item: this.data.item })
    },
    onAdd() {
      this.triggerEvent('add', this.data.item)
    },
  },
})
