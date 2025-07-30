// Main JavaScript for QLKTX Application

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  var popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Auto-hide alerts after 5 seconds
  setTimeout(function () {
    var alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
    alerts.forEach(function (alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);

  // Add fade-in animation to cards
  var cards = document.querySelectorAll(".card");
  cards.forEach(function (card, index) {
    card.style.animationDelay = index * 0.1 + "s";
    card.classList.add("fade-in");
  });

  // Form validation enhancements
  var forms = document.querySelectorAll(".needs-validation");
  Array.prototype.slice.call(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });

  // Loading spinner utility
  window.showLoadingSpinner = function () {
    var spinner = document.createElement("div");
    spinner.className = "spinner-overlay";
    spinner.innerHTML =
      '<div class="spinner-border spinner-border-lg text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    document.body.appendChild(spinner);
  };

  window.hideLoadingSpinner = function () {
    var spinner = document.querySelector(".spinner-overlay");
    if (spinner) {
      spinner.remove();
    }
  };

  // Confirm delete utility
  window.confirmDelete = function (message) {
    return confirm(message || "Bạn có chắc chắn muốn xóa?");
  };

  // Format currency utility
  window.formatCurrency = function (amount) {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(amount);
  };

  // Format date utility
  window.formatDate = function (dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString("vi-VN");
  };

  // AJAX utility
  window.makeRequest = function (url, options = {}) {
    showLoadingSpinner();

    const defaultOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const finalOptions = { ...defaultOptions, ...options };

    return fetch(url, finalOptions)
      .then((response) => {
        hideLoadingSpinner();
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .catch((error) => {
        hideLoadingSpinner();
        console.error("Error:", error);
        throw error;
      });
  };

  // Sidebar toggle for mobile
  var sidebarToggle = document.querySelector("#sidebarToggle");
  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      var sidebar = document.querySelector("#sidebar");
      if (sidebar) {
        sidebar.classList.toggle("active");
      }
    });
  }

  // Search functionality
  var searchInput = document.querySelector("#searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      var searchTerm = this.value.toLowerCase();
      var searchableItems = document.querySelectorAll(".searchable-item");

      searchableItems.forEach(function (item) {
        var text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
          item.style.display = "";
        } else {
          item.style.display = "none";
        }
      });
    });
  }

  // Auto refresh data every 5 minutes for dashboard
  if (window.location.pathname.includes("/dashboard")) {
    setInterval(function () {
      // Refresh dashboard data silently
      var dashboardCards = document.querySelectorAll("[data-refresh-url]");
      dashboardCards.forEach(function (card) {
        var url = card.getAttribute("data-refresh-url");
        if (url) {
          fetch(url)
            .then((response) => response.json())
            .then((data) => {
              // Update card content with new data
              var countElement = card.querySelector(".refresh-count");
              if (countElement && data.count !== undefined) {
                countElement.textContent = data.count;
              }
            })
            .catch((error) => console.log("Refresh error:", error));
        }
      });
    }, 300000); // 5 minutes
  }
});

// Handle navigation active state
document.addEventListener('DOMContentLoaded', function() {
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
            
            // If it's in a dropdown, also activate the parent
            var dropdown = link.closest('.dropdown');
            if (dropdown) {
                var dropdownToggle = dropdown.querySelector('.dropdown-toggle');
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
});
