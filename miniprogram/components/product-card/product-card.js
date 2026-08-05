Component({
  properties: {
    item: { type: Object, value: null },
  },
  methods: {
    onAdd() {
      this.triggerEvent('add', this.data.item)
    },
  },
})
