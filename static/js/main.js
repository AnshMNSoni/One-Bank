// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Flash messages auto-dismiss
    const flashMessages = document.querySelectorAll(".flash-message")
    flashMessages.forEach((message) => {
      setTimeout(() => {
        message.style.opacity = "0"
        setTimeout(() => {
          message.remove()
        }, 300)
      }, 5000)
    })
  
    // Form validation
    const forms = document.querySelectorAll("form")
    forms.forEach((form) => {
      form.addEventListener("submit", (event) => {
        const requiredFields = form.querySelectorAll("[required]")
        let isValid = true
  
        requiredFields.forEach((field) => {
          if (!field.value.trim()) {
            isValid = false
            field.classList.add("error")
  
            // Create error message if it doesn't exist
            let errorMessage = field.nextElementSibling
            if (!errorMessage || !errorMessage.classList.contains("error-message")) {
              errorMessage = document.createElement("div")
              errorMessage.classList.add("error-message")
              errorMessage.textContent = "This field is required"
              field.parentNode.insertBefore(errorMessage, field.nextSibling)
            }
          } else {
            field.classList.remove("error")
  
            // Remove error message if it exists
            const errorMessage = field.nextElementSibling
            if (errorMessage && errorMessage.classList.contains("error-message")) {
              errorMessage.remove()
            }
          }
        })
  
        if (!isValid) {
          event.preventDefault()
        }
      })
    })
  
    // Password confirmation validation
    const passwordConfirmFields = document.querySelectorAll('input[name="password_confirm"]')
    passwordConfirmFields.forEach((field) => {
      field.addEventListener("input", function () {
        const passwordField = this.form.querySelector('input[name="password"]')
        if (passwordField.value !== this.value) {
          this.setCustomValidity("Passwords do not match")
        } else {
          this.setCustomValidity("")
        }
      })
    })
  
    // Account balance chart (placeholder)
    const balanceChartElement = document.getElementById("balance-chart")
    if (balanceChartElement) {
      // This would be replaced with actual chart library code
      console.log("Balance chart would be initialized here")
    }
  
    // Spending chart (placeholder)
    const spendingChartElement = document.getElementById("spending-chart")
    if (spendingChartElement) {
      // This would be replaced with actual chart library code
      console.log("Spending chart would be initialized here")
    }
  
    // Transaction filters
    const filterForm = document.querySelector(".filters-form")
    if (filterForm) {
      const resetButton = filterForm.querySelector('button[type="reset"]')
      if (resetButton) {
        resetButton.addEventListener("click", () => {
          setTimeout(() => {
            filterForm.submit()
          }, 10)
        })
      }
    }
  
    // Quick transfer form validation
    const quickTransferForm = document.querySelector(".quick-transfer-form")
    if (quickTransferForm) {
      quickTransferForm.addEventListener("submit", function (event) {
        const fromAccount = this.querySelector("#from_account_id")
        const toAccount = this.querySelector("#to_account_id")
  
        if (fromAccount.value === toAccount.value) {
          event.preventDefault()
          alert("From and To accounts cannot be the same")
        }
      })
    }
  
    // Mobile navigation toggle
    const navToggle = document.querySelector(".nav-toggle")
    const navMenu = document.querySelector("nav ul")
  
    if (navToggle && navMenu) {
      navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("show")
      })
    }
  
    // Notification system (placeholder)
    function checkNotifications() {
      // This would make an AJAX request to check for new notifications
      console.log("Checking for new notifications...")
    }
  
    // Check for notifications every 30 seconds
    setInterval(checkNotifications, 30000)
  
    // Initialize tooltips
    const tooltips = document.querySelectorAll("[title]")
    tooltips.forEach((tooltip) => {
      tooltip.addEventListener("mouseenter", function () {
        const title = this.getAttribute("title")
        this.setAttribute("data-title", title)
        this.removeAttribute("title")
  
        const tooltipEl = document.createElement("div")
        tooltipEl.classList.add("tooltip")
        tooltipEl.textContent = title
  
        document.body.appendChild(tooltipEl)
  
        const rect = this.getBoundingClientRect()
        tooltipEl.style.top = rect.top - tooltipEl.offsetHeight - 10 + "px"
        tooltipEl.style.left = rect.left + rect.width / 2 - tooltipEl.offsetWidth / 2 + "px"
  
        setTimeout(() => {
          tooltipEl.classList.add("show")
        }, 10)
  
        this.addEventListener("mouseleave", function onMouseLeave() {
          tooltipEl.classList.remove("show")
  
          setTimeout(() => {
            tooltipEl.remove()
            this.setAttribute("title", this.getAttribute("data-title"))
            this.removeAttribute("data-title")
          }, 200)
  
          this.removeEventListener("mouseleave", onMouseLeave)
        })
      })
    })
  })
  