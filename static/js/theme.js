// themes.js
(function() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;
    
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    function applyTheme(theme) {
        if (theme === 'dark') {
            html.classList.add('dark');
            themeIcon.textContent = '☀️';
        } else {
            html.classList.remove('dark');
            themeIcon.textContent = '🌙';
        }
        localStorage.setItem('theme', theme);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = html.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        });
    }
})();
