// sidebar.js
document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const sidebar = document.getElementById("sidebar");

    /* ---- Desktop Collapse (Mini Sidebar) ---- */
    document.getElementById("desktop-toggle")?.addEventListener("click", () => {
        if (!sidebar) return;

        // Toggle class on body
        body.classList.toggle("sidebar-collapsed");

        // Optional: toggle padding inside sidebar
        sidebar.classList.toggle("px-4"); // Tailwind padding example
    });


    /* ---- Mobile Slide In ---- */
    const mobileMenu = document.getElementById("mobile-menu");
    const mobileSidebar = document.getElementById("mobile-sidebar");
    const openBtn = document.getElementById("mobile-open");
    const closeBtn = document.getElementById("mobile-close");

    openBtn?.addEventListener("click", () => {
        mobileMenu.classList.remove("hidden");
        mobileSidebar.classList.remove("-translate-x-full");
    });

    closeBtn?.addEventListener("click", () => {
        mobileSidebar.classList.add("-translate-x-full");
        setTimeout(() => mobileMenu.classList.add("hidden"), 300);
    });

    mobileMenu?.addEventListener("click", (e) => {
        if (e.target === mobileMenu) {
            mobileSidebar.classList.add("-translate-x-full");
            setTimeout(() => mobileMenu.classList.add("hidden"), 300);
        }
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('#messages-container .alert');
    alerts.forEach(alert => {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s ease-out';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Sidebar Toggle (off-canvas)
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('-translate-x-full');
        document.documentElement.classList.add('overflow-hidden');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('hidden');
    }

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('-translate-x-full');
        document.documentElement.classList.remove('overflow-hidden');
        if (sidebarBackdrop) sidebarBackdrop.classList.add('hidden');
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            if (window.innerWidth < 1024 && window.mobileMenuAPI) {
                if (window.mobileMenuAPI.isOpen()) window.mobileMenuAPI.close();
                else window.mobileMenuAPI.open();
                return;
            }
            if (sidebar.classList.contains('-translate-x-full')) openSidebar(); 
            else closeSidebar();
        });
    }

    sidebarBackdrop?.addEventListener('click', closeSidebar);

    const sidebarLinks = sidebar.querySelectorAll('a, form button');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 1024) closeSidebar();
        });
    });
});
