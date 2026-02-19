document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // Sidebar Toggle
    // ========================================
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebarToggle && sidebar && mainContent) {
        const saved = localStorage.getItem('sidebarCollapsed');
        if (saved === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }

        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));

            const icon = sidebarToggle.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.className = 'bi bi-chevron-right';
            } else {
                icon.className = 'bi bi-chevron-left';
            }
        });

        // Set initial icon
        if (sidebar.classList.contains('collapsed')) {
            const icon = sidebarToggle.querySelector('i');
            if (icon) icon.className = 'bi bi-chevron-right';
        }
    }

    // ========================================
    // Toast Auto-dismiss
    // ========================================
    const toasts = document.querySelectorAll('.toast-modern');
    toasts.forEach(function(toast) {
        setTimeout(function() {
            toast.classList.add('toast-exit');
            setTimeout(function() { toast.remove(); }, 300);
        }, 5000);
    });

    // ========================================
    // Count-up Animation for Stat Values
    // ========================================
    const statValues = document.querySelectorAll('.stat-value[data-count]');
    statValues.forEach(function(el) {
        const target = parseInt(el.getAttribute('data-count'), 10);
        if (isNaN(target)) return;

        const duration = 800;
        const step = Math.max(1, Math.ceil(target / (duration / 16)));
        let current = 0;

        function update() {
            current += step;
            if (current >= target) {
                el.textContent = target;
                return;
            }
            el.textContent = current;
            requestAnimationFrame(update);
        }

        el.textContent = '0';
        requestAnimationFrame(update);
    });

    // ========================================
    // Fade-in Animations
    // ========================================
    const animateElements = document.querySelectorAll('.animate-in');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animateElements.forEach(function(el) {
            observer.observe(el);
        });
    }
});
