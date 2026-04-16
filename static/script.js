function toggleDarkMode() {
    document.body.classList.toggle("dark");

    const isDark = document.body.classList.contains("dark");

    // Save preference
    localStorage.setItem("theme", isDark ? "dark" : "light");

    applyPlotlyTheme(isDark);
}

function setThemeInput() {
    const input = document.getElementById("theme-input");
    if (!input) return;

    if (document.body.classList.contains("dark")) {
        input.value = "dark";
    } else {
        input.value = "light";
    }
}

function applyPlotlyTheme(isDark) {
    const template = isDark ? "plotly_dark" : "simple_white";

    const charts = document.querySelectorAll(".js-plotly-plot");

    charts.forEach(chart => {
        Plotly.relayout(chart, {
            template: template,
            paper_bgcolor: isDark ? "#1c1b18" : "#ffffff",
            plot_bgcolor: isDark ? "#1c1b18" : "#ffffff",
            font: {
                color: isDark ? "#e8e6e3" : "#1e1b16"
            },
            transition: { duration: 300, easing: "cubic-in-out" }
        });
    });
}

// load saved theme
window.onload = function () {
    const isDark = localStorage.getItem("theme") === "dark";

    if (isDark) {
        document.body.classList.add("dark");
    }

    // Apply theme to charts on load
    applyPlotlyTheme(isDark);
};