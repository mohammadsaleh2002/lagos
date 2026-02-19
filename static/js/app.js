document.addEventListener('DOMContentLoaded', function() {

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
