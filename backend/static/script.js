document.addEventListener("DOMContentLoaded", () => {
  // ------------------- Elements -------------------
  const loginBtn = document.getElementById("loginBtn");
  const registerBtn = document.getElementById("registerBtn");
  const publicBookNow = document.getElementById("publicBookNow");
  const authSidebar = document.getElementById("authSidebar");
  const closeBtn = document.querySelector("#authSidebar .close-sidebar");
  const showLoginBtn = document.getElementById("showLoginSidebar");
  const showRegisterBtn = document.getElementById("showRegisterSidebar");
  const loginForm = document.getElementById("loginFormSidebar");
  const registerForm = document.getElementById("registerFormSidebar");
  const authOverlay = document.getElementById("authOverlay");

  const publicSection = document.getElementById("publicSection");
  const protectedSection = document.getElementById("protectedSection");
  const myAppointmentsSection = document.getElementById("myAppointmentsSection");
  const centresSection = document.getElementById("centresSection");

  const navHomeWrapper = document.getElementById("navHomeWrapper");
  const navCentersWrapper = document.getElementById("navCentersWrapper");
  const navDashboardWrapper = document.getElementById("navDashboardWrapper");
  const navReportsWrapper = document.getElementById("navReportsWrapper");
  const loginWrapper = document.getElementById("loginWrapper");
  const registerWrapper = document.getElementById("registerWrapper");
  const profileDropdown = document.getElementById("profileDropdown");
  const logoutBtn = document.getElementById("logoutBtn");
  const logoutWrapper = document.getElementById("logoutWrapper");
  const params = new URLSearchParams(window.location.search);
  const openSection = params.get("open");

  let isLoggedIn = false;

// ------------------- HARD RESET UI (PUBLIC ONLY) -------------------
  if (publicSection) publicSection.style.display = "block";
  if (protectedSection) protectedSection.style.display = "none";
  if (centresSection) centresSection.style.display = "none";

  if (loginWrapper) loginWrapper.style.display = "inline-block";
  if (registerWrapper) registerWrapper.style.display = "inline-block";
  if (profileDropdown) profileDropdown.style.display = "none";

  if (navHomeWrapper) navHomeWrapper.style.display = "inline-block";
  if (navDashboardWrapper) navDashboardWrapper.style.display = "none";
  if (navReportsWrapper) navReportsWrapper.style.display = "none";



  //--------logout button --------------
  if (logoutBtn) {
    logoutBtn.onclick = async () => {
      try {
        const res = await fetch("/api/logout", {
          method: "GET",
          credentials: "same-origin"
        });

        const data = await res.json();

        if (data.success) {
          isLoggedIn = false;

          // Reset UI
          updateNavLinks();

          // Optional: go back to home
          if (protectedSection) protectedSection.style.display = "none";
          if (centresSection) centresSection.style.display = "none";
          if (publicSection) publicSection.style.display = "block";

          alert("✅ Logged out successfully");
        }
      } catch (err) {
        console.error("Logout error:", err);
        alert("❌ Logout failed");
      }
    };
  }

  // ------------------- Sidebar -------------------
  function openSidebar() {
    authSidebar.classList.add("active");
    if (authOverlay) authOverlay.style.display = "block";
  }
  function closeSidebar() {
    authSidebar.classList.remove("active");
    if (authOverlay) authOverlay.style.display = "none";
  }

  if (loginBtn) {
    loginBtn.onclick = () => {
      openSidebar();
      showLogin();
    };
  }

  if (registerBtn) {
    registerBtn.onclick = () => {
      openSidebar();
      showRegister();
    };
  }

  if (publicBookNow) {
    publicBookNow.onclick = () => {
      if (!isLoggedIn) {
        openSidebar();
        showLogin();
      }
    };
  }

  if (closeBtn) closeBtn.onclick = closeSidebar;
  if (authOverlay) authOverlay.onclick = closeSidebar;

  // ------------------- Toggle Forms -------------------
  function showLogin() {
    loginForm.classList.add("active-form");
    registerForm.classList.remove("active-form");
    showLoginBtn.classList.add("active");
    showRegisterBtn.classList.remove("active");
  }
  function showRegister() {
    registerForm.classList.add("active-form");
    loginForm.classList.remove("active-form");
    showRegisterBtn.classList.add("active");
    showLoginBtn.classList.remove("active");
  }
  if (showLoginBtn) showLoginBtn.onclick = showLogin;
  if (showRegisterBtn) showRegisterBtn.onclick = showRegister;


  // ------------------- Register -------------------
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("regNameSidebar").value;
    const email = document.getElementById("regEmailSidebar").value;
    const password = document.getElementById("regPasswordSidebar").value;
    const phone = document.getElementById("regPhoneSidebar")?.value || "";
    const address = document.getElementById("regAddressSidebar").value;

    try {
      const res = await fetch("/api/register", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, phone, address })
      });

      const data = await res.json();

      if (data.success) {
        alert("✅ Registration successful! Please login.");
        showLogin();
      } else {
        alert("❌ " + (data.message || "Registration failed"));
      }
    } catch (err) {
      console.error("Registration error:", err);
      alert("❌ Server error during registration");
    }
  });

  // ------------------- Login -------------------
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("loginEmailSidebar").value;
      const password = document.getElementById("loginPasswordSidebar").value;

      try {
        const res = await fetch("/api/login", {
          method: "POST",
          credentials: "same-origin", // 🔑 VERY IMPORTANT
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (data.success) {
          isLoggedIn = true; // UI state
          alert("✅ Login successful!");
          closeSidebar();

          // ✅ Updated: open Centres section after login
          updateNavLinks(true);

        } else {
          alert("❌ Invalid email or password");
        }
      } catch (err) {
        console.error("Login error:", err);
        alert("❌ Server error during login");
      }
    });
  }

  // ------------------- Check login on page load -------------------
  async function checkLogin() {
    try {
      const res = await fetch("/api/check_login", { credentials: "same-origin" });
      const data = await res.json();

      if (data.logged_in === true) {
        isLoggedIn = true;
        updateNavLinks();

        if (openSection === "dashboard") {
          // Open dashboard automatically
          if (publicSection) publicSection.style.display = "none";
          if (centresSection) centresSection.style.display = "none";
          if (protectedSection) protectedSection.style.display = "block";
          if (myAppointmentsSection) myAppointmentsSection.style.display = "block";
          loadMyAppointments();
        }
      }
    } catch (err) {
      console.error("Login check failed:", err);
    }
  }


// ==================== UI & Navbar Management ====================
  function updateNavLinks(openCentres = false) {
    if (navCentersWrapper) navCentersWrapper.style.display = "inline-block";

    if (isLoggedIn) {
      if (navHomeWrapper) navHomeWrapper.style.display = "none";
      if (navDashboardWrapper) navDashboardWrapper.style.display = "inline-block";
      if (navReportsWrapper) navReportsWrapper.style.display = "inline-block";

      if (loginWrapper) loginWrapper.style.display = "none";
      if (registerWrapper) registerWrapper.style.display = "none";
      if (logoutWrapper) logoutWrapper.style.display = "inline-block";
      

      if (publicSection) publicSection.style.display = "none";
      if (protectedSection) protectedSection.style.display = "none";
      if (myAppointmentsSection) myAppointmentsSection.style.display = "none";

      if (centresSection) centresSection.style.display = openCentres ? "block" : "none";
    } else {
      if (navHomeWrapper) navHomeWrapper.style.display = "inline-block";
      if (navDashboardWrapper) navDashboardWrapper.style.display = "none";
      if (navReportsWrapper) navReportsWrapper.style.display = "none";

      if (loginWrapper) loginWrapper.style.display = "inline-block";
      if (registerWrapper) registerWrapper.style.display = "inline-block";
      if (logoutWrapper) logoutWrapper.style.display = "none";

      if (publicSection) publicSection.style.display = "block";
      if (protectedSection) protectedSection.style.display = "none";
      if (myAppointmentsSection) myAppointmentsSection.style.display = "none";
      if (centresSection) centresSection.style.display = "none";
    }
  }
  // ------------------- Navbar Click Handlers -------------------
  const navCenters = document.getElementById("navCenters");
  if (navCenters) {
    navCenters.addEventListener("click", (e) => {
      e.preventDefault();
      currentSection = "centres";
      updateSearchBarDisplay(isLoggedIn, currentSection);

      if (publicSection) publicSection.style.display = "none";
      if (protectedSection) protectedSection.style.display = "none";
      if (myAppointmentsSection) myAppointmentsSection.style.display = "none";
      if (centresSection) centresSection.style.display = "block";
      loadCategories();
    });
  }

  const navDashboard = document.getElementById("navDashboard");
  if (navDashboard) {
    navDashboard.addEventListener("click", (e) => {
      e.preventDefault();
      currentSection = "dashboard";
      updateSearchBarDisplay(isLoggedIn, currentSection);

      if (publicSection) publicSection.style.display = "none";
      if (centresSection) centresSection.style.display = "none";
      if (protectedSection) protectedSection.style.display = "block";

      const dashboardContent = document.getElementById("dashboardContent");
      const reportsContent = document.getElementById("reportsContent");
      if (dashboardContent) dashboardContent.style.display = "block";
      if (reportsContent) reportsContent.style.display = "none";

      if (myAppointmentsSection) myAppointmentsSection.style.display = "block";
      loadMyAppointments();
    });
  }

  const navReports = document.getElementById("navReports");
  if (navReports) {
    navReports.addEventListener("click", (e) => {
      e.preventDefault();
      currentSection = "reports";
      updateSearchBarDisplay(isLoggedIn, currentSection);

      if (publicSection) publicSection.style.display = "none";
      if (centresSection) centresSection.style.display = "none";
      if (protectedSection) protectedSection.style.display = "block";

      const dashboardContent = document.getElementById("dashboardContent");
      const reportsContent = document.getElementById("reportsContent");
      if (dashboardContent) dashboardContent.style.display = "none";
      if (reportsContent) {
        reportsContent.style.display = "block";
        reportsContent.innerHTML = "<p style='font-size:16px;'>📄 You do not have any reports yet.</p>";
      }
    });
  }

  const globalSearchWrapper = document.getElementById("globalSearchWrapper");
  let currentSection = "public"; // default

  function updateSearchBarDisplay(isLoggedIn, currentSection) {
    if (!globalSearchWrapper) return;

    if (!isLoggedIn) {
      globalSearchWrapper.style.display = "flex";
      return;
    }

    if (currentSection === "centres") {
      globalSearchWrapper.style.display = "flex";
    } else {
      globalSearchWrapper.style.display = "none";
    }
  }

  updateSearchBarDisplay(isLoggedIn, currentSection);


// My Appointments--------------------

function loadMyAppointments() {
  const container = document.getElementById("myAppointmentsCards");
  if (!container) {
    console.warn("myAppointmentsCards container not found");
    return;
  }

  container.innerHTML = "<p>Loading appointments...</p>";

  fetch("/api/my-appointments")
    .then(res => {
      if (!res.ok) throw new Error("Unauthorized or server error");
      return res.json();
    })
    .then(data => {
      container.innerHTML = "";

      if (!Array.isArray(data) || data.length === 0) {
        container.innerHTML = "<p>You have no appointments yet.</p>";
        return;
      }

      let hasVisible = false;

      data.forEach(appt => {
        if (!appt || appt.booking === "Cancelled") return;

        hasVisible = true;

        const bookingStatus = appt.booking || "Confirmed";
        const statusClass = bookingStatus.toLowerCase();

        const card = document.createElement("div");
        card.className = "appointment-summary-card";
        card.dataset.appointmentId = appt.appointment_id;

        card.innerHTML = `
          <div class="appointment-header">
            <h4>${appt.test_name || "Test"}</h4>
          </div>

          <span class="status-badge ${statusClass}">
            ${bookingStatus}
          </span>

          <div class="appointment-body">
            <p><i class="fa-solid fa-calendar-days"></i>
              <b>Date:</b> ${appt.appointment_date || "-"}
            </p>

            <p><i class="fa-solid fa-clock"></i>
              <b>Time:</b> ${appt.time_slot || "-"}
            </p>

            <p><i class="fa-solid fa-bell"></i>
              <b>Reminder:</b>
              ${appt.reminder_enabled
                ? `ON (${appt.reminder_before_minutes || 60} mins before)`
                : "OFF"}
            </p>

            <p><i class="fa-solid fa-hospital"></i>
              <b>Centre:</b> ${appt.center_name || "View details"}
            </p>
          </div>

          <div class="appointment-footer">
            👉 Click to view details
          </div>
        `;
        container.appendChild(card);
      });

      if (!hasVisible) {
        container.innerHTML = "<p>You have no appointments yet.</p>";
      }
    })
    .catch(err => {
      console.error("Appointments load failed:", err);
      container.innerHTML = "<p>Please login to view your appointments.</p>";
    });
}


// ================= Click handler for appointment cards (SIDE PANEL) =================
document.addEventListener("click", function (e) {
  const card = e.target.closest(".appointment-summary-card");
  if (!card) return;

  const appointmentId = card.dataset.appointmentId;
  if (!appointmentId) return;

  const sidePanel = document.getElementById("appointmentSidePanel");
  const sidePanelContent = document.getElementById("sidePanelContent");
  const overlay = document.getElementById("sidePanelOverlay");
  if (!sidePanel || !sidePanelContent || !overlay) return;

  // Reset panel content
  sidePanelContent.innerHTML = "<p>Loading appointment details...</p>";

  // Open panel
  sidePanel.classList.add("open");
  overlay.classList.add("show");

  // Fetch appointment details from API
  fetch(`/api/appointment/${appointmentId}`)
    .then(res => {
      if (!res.ok) throw new Error("Failed to load appointment");
      return res.json();
    })
    .then(data => {
      if (!data || data.success === false) {
        sidePanelContent.innerHTML = "<p>Unable to load details.</p>";
        return;
      }

      // Destructure data for clarity
      const {
        test_name,
        center_name,
        center_address,
        appointment_date,
        time_slot,
        home_service,
        booking
      } = data;

      // Normalize booking status
      const statusText = booking || "Confirmed";
      const statusClass = statusText.toLowerCase();

      // Populate side panel content
      sidePanelContent.innerHTML = `
        <h4>
          <i class="fa fa-vial icon-test"></i>
          ${test_name || "Test"}
        </h4>

        <p>
          <i class="fa fa-hospital icon-centre"></i>
          <b>Centre:</b> ${center_name || "-"}
        </p>

        <p>
          <i class="fa fa-location-dot icon-address"></i>
          <b>Address:</b> ${center_address || "Not available"}
        </p>

        <hr>

        <p>
          <i class="fa fa-calendar icon-date"></i>
          <b>Date:</b> ${appointment_date}
        </p>

        <p>
          <i class="fa fa-clock icon-time"></i>
          <b>Time:</b> ${time_slot}
        </p>

        <p>
          <i class="fa fa-circle-info icon-status"></i>
          <b>Status:</b>
          <span class="status-badge ${statusClass}">
            ${statusText}
          </span>
        </p>

        <p>
          <i class="fa fa-house-medical icon-home"></i>
          <b>Sample Collection:</b> ${home_service || "No"}
        </p>

        ${statusText !== "Cancelled" ? `
          <button id="cancelAppointmentBtn" class="cancel-btn">
            <i class="fa fa-xmark"></i> Cancel Appointment
          </button>
        ` : ""}
      `;
      // Add animation class for smooth content appearance
      sidePanelContent.classList.remove("animate"); // reset
      void sidePanelContent.offsetWidth;           // trigger reflow
      sidePanelContent.classList.add("animate");  // start animation


      // Cancel appointment handler (overwrite previous handlers to avoid duplication)
      const cancelBtn = document.getElementById("cancelAppointmentBtn");
      if (cancelBtn) {
        cancelBtn.onclick = () => {
          if (!confirm("Are you sure you want to cancel this appointment?")) return;

          fetch(`/api/appointment/${appointmentId}/cancel`, { method: "POST" })
            .then(res => res.json())
            .then(resp => {
              alert(resp.message || "Appointment cancelled ✅");
              loadMyAppointments(); // refresh dashboard cards
              closeSidePanel();
            })
            .catch(() => alert("Server error ❌"));
        };
      }
    })
    .catch(() => {
      sidePanelContent.innerHTML = "<p>Error loading appointment details.</p>";
    });
});

// ================= Close side panel =================
function closeSidePanel() {
  const sidePanel = document.getElementById("appointmentSidePanel");
  const overlay = document.getElementById("sidePanelOverlay");
  if (!sidePanel || !overlay) return;

  sidePanel.classList.remove("open");
  overlay.classList.remove("show");
}

// ================= Close panel when overlay clicked =================
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("sidePanelOverlay")?.addEventListener("click", closeSidePanel);
});


// ================= Optional: Close panel with ESC key =================
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") closeSidePanel();
});





  // ===========================
// FINAL CENTRES SECTION LOGIC
// ===========================
const centersContainer = document.getElementById("centersContainer");
const centresTitle = document.getElementById("centresTitle");
const centresBackBtn = document.getElementById("centresBackBtn");

let currentCategoryId = null;

const categoryIcons = {
  "Pathology Labs": "🧪",
  "Radiology": "☢️",
  "Cardiology Diagnostic Centers": "🫀",
  "Neurology Diagnostic Centers": "🧠",
  "Gastroenterology Diagnostic Centers": "🍽️",
  "Urology Diagnostic Centers": "💧",
  "Endocrinology Diagnostic Centers": "🧬",
  "Pulmonology Diagnostic Centers": "🫁",
  "Dermatology Diagnostic Labs": "🧴",
  "ENT Diagnostic Centers": "👂",
  "Ophthalmology Diagnostic Centers": "👁️",
  "Orthopedic Diagnostic Centers": "🦴",
  "Obstetric Diagnostic Centers": "🤰",
  "Cancer Diagnostic Centers": "🎗️",
  "Dental Diagnostic Centers": "🦷",
  "Genetic Diagnostic Labs": "🔬",
  "Wellness & Health Checkup Centers": "⚕️"
};

async function loadCategories() {
  centresTitle.innerText = "Diagnostic Categories";
  centresBackBtn.style.display = "none";
  centersContainer.innerHTML = "";
  currentCategoryId = null;

  const res = await fetch("/api/categories");
  const categories = await res.json();

  categories.forEach((cat, index) => {
    const card = document.createElement("div");
    card.className = "info-card";
    card.innerHTML = `
      <div class="icon"  style="animation-delay: ${index * 0.15}s">${categoryIcons[cat.name] || "🏥"}</div>
      <h3>${cat.name}</h3>
      <p>Select category</p>
    `;
    card.onclick = () => loadCenters(cat.id, cat.name);
    centersContainer.appendChild(card);

    // Animate card
    setTimeout(() => card.classList.add("show"), index * 100);
  });
}

async function loadCenters(categoryId, categoryName) {
  currentCategoryId = categoryId;
  centresTitle.innerText = categoryName;
  centresBackBtn.style.display = "inline-block";
  centersContainer.innerHTML = "";

  const res = await fetch(`/api/centers/${categoryId}`);
  const centers = await res.json();

  centers.forEach((center, index) => {
    const card = document.createElement("div");
    card.className = "info-card";
    card.innerHTML = `
      <div class="icon"  style="animation-delay: ${index * 0.15}s">🏥</div>
      <h3>${center.name}</h3>
      <p>${center.location}</p>
      <p>⭐ ${center.rating} | ${center.years_experience} yrs</p>
    `;
    card.onclick = () => loadTests(center.id, center.name);
    centersContainer.appendChild(card);

    // Animate card
    setTimeout(() => card.classList.add("show"), index * 100);
  });
}

async function loadTests(centerId, centerName) {
  centresTitle.innerText = centerName;
  centersContainer.innerHTML = "";

  const res = await fetch(`/api/center_tests/${centerId}`);
  const tests = await res.json();

  tests.forEach((test, index) => {
    const card = document.createElement("div");
    card.className = "info-card";
    card.innerHTML = `
      <div class="icon"  style="animation-delay: ${index * 0.15}s">🧾</div>
      <h3>${test.test_name}</h3>
      <p>₹ ${test.price}</p>
      <p>TAT: ${test.tat_hours} hrs</p>
      <button type="button" class="book-btn">Book</button>
    `;
    centersContainer.appendChild(card);

    // Animate card
    setTimeout(() => card.classList.add("show"), index * 100);

    // Book button click
    card.querySelector(".book-btn").addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();

      if (!isLoggedIn) { openSidebar(); return; }

      const testName = encodeURIComponent(test.test_name);
      const center = encodeURIComponent(centerName);
      const homeAvailable = test.home_service === 1;

      window.location.href = `/book?test_id=${test.test_id}&center_id=${centerId}&test=${testName}&center=${center}&home=${homeAvailable}`;
    });
  });
}

// Back button
if (centresBackBtn) {
  centresBackBtn.onclick = () => {
    if (centresSection) centresSection.style.display = "block";
    loadCategories();
  };
}


  // ✅ FINAL STEP: decide UI after everything is wired
  checkLogin();

  // Side panel close handlers
document.getElementById("closeSidePanel")?.addEventListener("click", closeSidePanel);
document.getElementById("sidePanelOverlay")?.addEventListener("click", closeSidePanel);

});


