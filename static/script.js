function toggleDarkMode() {
    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
    } else {
        localStorage.setItem("theme", "light");
    }
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

// load saved theme
window.onload = function () {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark");
    }
};