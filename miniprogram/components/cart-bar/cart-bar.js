Component({
  properties: {
    count: { type: Number, value: 0 },
    totalCents: { type: Number, value: 0 },
  },
  methods: {
    onToggle() {
      this.triggerEvent('toggle')
    },
    onCheckout() {
      this.triggerEvent('checkout')
    },
  },
})
