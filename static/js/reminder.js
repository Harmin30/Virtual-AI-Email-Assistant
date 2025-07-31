// Sidebar toggle logic
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("collapsed");

    // Optional: save collapsed state in localStorage
    const isCollapsed = sidebar.classList.contains("collapsed");
    localStorage.setItem("sidebarCollapsed", isCollapsed);
}

// On page load, restore sidebar state
window.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";
    if (isCollapsed) {
        sidebar.classList.add("collapsed");
    }
});



  function toggleLegend() {
    const legend = document.getElementById('reminderLegend');
    legend.style.display = legend.style.display === 'block' ? 'none' : 'block';
  }




