(() => {
    const root = document.documentElement;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    const markLoaded = () => {
        window.requestAnimationFrame(() => {
            window.requestAnimationFrame(() => {
                root.classList.add("app-loaded");
            });
        });
    };

    if (!prefersReducedMotion.matches) {
        if (document.readyState === "complete") {
            markLoaded();
        } else {
            window.addEventListener("load", markLoaded, { once: true });
        }
    } else {
        root.classList.add("app-loaded");
    }
})();
