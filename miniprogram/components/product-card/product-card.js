const { BASE_URL } = require('../../config')

Component({
  properties: {
    item: { type: Object, value: null },
  },
  data: {
    imgBase: BASE_URL,
  },
  methods: {
    onAdd() {
      this.triggerEvent('add', this.data.item)
    },
  },
})
