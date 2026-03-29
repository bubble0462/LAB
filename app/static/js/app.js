(() => {
    const root = document.documentElement;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    const syncInvoicePreview = () => {
        const unitPriceInput = document.querySelector("[data-invoice-unit-price]");
        const quantityInput = document.querySelector("[data-invoice-quantity]");
        const totalTarget = document.querySelector("[data-invoice-total]");

        if (!unitPriceInput || !quantityInput || !totalTarget) {
            return;
        }

        const renderTotal = () => {
            const unitPrice = Number.parseFloat(unitPriceInput.value || "0");
            const quantity = Number.parseInt(quantityInput.value || "0", 10);
            const total = (Number.isFinite(unitPrice) ? unitPrice : 0) * (Number.isFinite(quantity) ? quantity : 0);
            totalTarget.textContent = `¥ ${total.toFixed(2)}`;
        };

        unitPriceInput.addEventListener("input", renderTotal);
        quantityInput.addEventListener("input", renderTotal);
        renderTotal();
    };

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

    syncInvoicePreview();
})();
