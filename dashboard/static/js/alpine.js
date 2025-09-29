document.addEventListener("alpine:init", () => {
  Alpine.store("sidebar", {
    isOpen: false,
    open() {
      this.isOpen = true
    },
    close() {
      this.isOpen = false
    }
  })
  Alpine.store("rupiah", {
    input: None,
    format(values) {
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(values)
    }
  })
})