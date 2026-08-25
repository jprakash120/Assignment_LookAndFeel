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

function makeChart() {
  const canvas = document.getElementById("downtimeChart");
  if (!canvas || typeof Chart === "undefined") return null;
  const initial = portfolioData.reason;
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels: initial.labels,
      datasets: [{
        data: initial.values,
        backgroundColor: "#3dd9c3",
        borderRadius: 6,
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
          ticks: { color: "#75849a", font: { family: "DM Sans" } }
        },
        y: {
          border: { display: false },
          grid: { display: false },
          ticks: { color: "#273b55", font: { family: "DM Sans", weight: "600" } }
        }
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const chart = makeChart();
  const title = document.getElementById("chart-title");
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      const view = portfolioData[button.dataset.view];
      if (!chart || !view) return;
      document.querySelectorAll("[data-view]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      title.textContent = view.title;
      chart.data.labels = view.labels;
      chart.data.datasets[0].data = view.values;
      chart.update();
    });
  });

  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  toggle?.addEventListener("click", () => {
    const open = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!open));
    nav?.classList.toggle("open", !open);
  });
  nav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle?.setAttribute("aria-expanded", "false");
  }));

  const year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
});
