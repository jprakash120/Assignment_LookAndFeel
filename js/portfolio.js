const portfolioData = {
  reason: {
    title: "Downtime by reason",
    labels: ["Machine adjustment", "Machine failure", "Inventory shortage", "Batch change", "Batch coding error", "Other", "Product spill", "Calibration error"],
    values: [332, 254, 225, 160, 145, 74, 57, 49]
  },
  product: {
    title: "Downtime by product",
    labels: ["CO-600", "CO-2L", "RB-600", "LE-600", "DC-600", "OR-600"],
    values: [494, 277, 258, 169, 115, 75]
  },
  shift: {
    title: "Downtime by shift",
    labels: ["Shift B", "Shift A", "Shift C"],
    values: [584, 534, 270]
  }
};

let downtimeChart;

function createDowntimeChart() {
  const canvas = document.getElementById("downtimeChart");
  if (!canvas || typeof Chart === "undefined") return;

  const initial = portfolioData.reason;
  downtimeChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: initial.labels,
      datasets: [{
        data: initial.values,
        backgroundColor: "#39c6b7",
        borderRadius: 7,
        borderSkipped: false,
        barThickness: 18
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 380 },
      plugins: {
        legend: { display: false },
        tooltip: {
          displayColors: false,
          callbacks: { label: (context) => `${context.raw.toLocaleString()} minutes` }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          border: { display: false },
          grid: { color: "rgba(31, 51, 76, .09)" },
          ticks: { color: "#75849a", font: { family: "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" } }
        },
        y: {
          border: { display: false },
          grid: { display: false },
          ticks: { color: "#273b55", font: { family: "-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", weight: "600" } }
        }
      }
    }
  });
}

function initializeChartTabs() {
  const title = document.getElementById("chart-title");
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      const view = portfolioData[button.dataset.view];
      if (!downtimeChart || !view) return;

      document.querySelectorAll("[data-view]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      title.textContent = view.title;
      downtimeChart.data.labels = view.labels;
      downtimeChart.data.datasets[0].data = view.values;
      downtimeChart.update();
    });
  });
}

function initializeTheme() {
  const root = document.documentElement;
  const saved = localStorage.getItem("portfolio-theme");
  if (saved === "light" || saved === "dark") root.dataset.theme = saved;

  document.querySelector(".theme-toggle")?.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
    localStorage.setItem("portfolio-theme", root.dataset.theme);
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
      "content",
      root.dataset.theme === "light" ? "#f6f8fa" : "#070b12"
    );
  });
}

function initializeNavigation() {
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");

  toggle?.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    nav?.classList.toggle("open", !isOpen);
  });

  nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle?.setAttribute("aria-expanded", "false");
  }));

  const header = document.querySelector(".site-header");
  const updateHeader = () => header?.classList.toggle("scrolled", window.scrollY > 12);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
}

function initializeCommandPalette() {
  const dialog = document.getElementById("commandPalette");
  const input = document.getElementById("commandSearch");
  const items = [...document.querySelectorAll("[data-command-item]")];
  const empty = document.querySelector(".command-empty");
  let selectedIndex = 0;

  const visibleItems = () => items.filter((item) => !item.hidden);
  const selectItem = (index) => {
    const visible = visibleItems();
    if (!visible.length) return;
    selectedIndex = (index + visible.length) % visible.length;
    items.forEach((item) => item.classList.remove("selected"));
    visible[selectedIndex].classList.add("selected");
    visible[selectedIndex].scrollIntoView({ block: "nearest" });
  };

  const open = () => {
    if (!dialog?.open) dialog?.showModal();
    input.value = "";
    items.forEach((item) => {
      item.hidden = false;
      item.classList.remove("selected");
    });
    empty.hidden = true;
    selectedIndex = 0;
    selectItem(0);
    setTimeout(() => input.focus(), 20);
  };

  const close = () => dialog?.close();

  document.querySelectorAll("[data-command-open]").forEach((button) => button.addEventListener("click", open));
  document.addEventListener("keydown", (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      dialog?.open ? close() : open();
    }
  });

  dialog?.addEventListener("click", (event) => {
    if (event.target === dialog) close();
  });
  items.forEach((item) => item.addEventListener("click", close));

  input?.addEventListener("input", () => {
    const query = input.value.toLowerCase().trim();
    items.forEach((item) => {
      item.hidden = !item.textContent.toLowerCase().includes(query);
    });
    empty.hidden = visibleItems().length > 0;
    selectedIndex = 0;
    selectItem(0);
  });

  input?.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      selectItem(selectedIndex + 1);
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      selectItem(selectedIndex - 1);
    }
    if (event.key === "Enter") {
      event.preventDefault();
      visibleItems()[selectedIndex]?.click();
    }
  });
}

function initializeReveal() {
  const targets = document.querySelectorAll(".reveal");
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) {
    targets.forEach((target) => target.classList.add("visible"));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .12 });

  targets.forEach((target) => observer.observe(target));
}

function initializeUtilities() {
  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  document.addEventListener("pointermove", (event) => {
    document.documentElement.style.setProperty("--pointer-x", `${event.clientX}px`);
    document.documentElement.style.setProperty("--pointer-y", `${event.clientY}px`);
  }, { passive: true });

  document.querySelectorAll("[data-copy]").forEach((button) => button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      const original = button.textContent;
      button.textContent = "copied";
      setTimeout(() => { button.textContent = original; }, 1200);
    } catch {
      button.textContent = "copy failed";
    }
  }));
}

document.addEventListener("DOMContentLoaded", () => {
  initializeTheme();
  initializeNavigation();
  createDowntimeChart();
  initializeChartTabs();
  initializeCommandPalette();
  initializeReveal();
  initializeUtilities();
});
