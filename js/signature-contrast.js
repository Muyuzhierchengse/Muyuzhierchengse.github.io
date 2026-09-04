(() => {
    "use strict";

    function parseColour(value) {
        const numbers = value && value.match(/[\d.]+/g);
        if (!numbers || numbers.length < 3) return null;

        const channels = numbers.map(Number);
        return {
            r: channels[0],
            g: channels[1],
            b: channels[2],
            a: channels.length > 3 ? channels[3] : 1
        };
    }

    function renderedBackground(element) {
        let node = element;
        while (node) {
            const colour = parseColour(window.getComputedStyle(node).backgroundColor);
            if (colour && colour.a > 0.05) return colour;
            node = node.parentElement;
        }

        // The authored page is paper-white. Keeping this fallback light makes
        // the unmodified dark signature safe in restricted mobile browsers.
        return { r: 255, g: 255, b: 255, a: 1 };
    }

    function relativeLuminance({ r, g, b }) {
        const linear = (channel) => {
            const value = channel / 255;
            return value <= 0.04045
                ? value / 12.92
                : Math.pow((value + 0.055) / 1.055, 2.4);
        };

        return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b);
    }

    function updateSignatureInk() {
        const signature = document.querySelector(".profile-identity__signature");
        if (!signature) return;

        const background = renderedBackground(signature);
        document.documentElement.dataset.signatureInk =
            relativeLuminance(background) < 0.36 ? "light" : "dark";
    }

    function start() {
        updateSignatureInk();

        // Recheck after browser extensions and delayed styles have had time to
        // alter the page. Theme preference is only a trigger, never the source
        // used to choose the signature colour.
        window.setTimeout(updateSignatureInk, 250);
        window.setTimeout(updateSignatureInk, 1000);
        window.addEventListener("pageshow", updateSignatureInk);
        document.addEventListener("visibilitychange", () => {
            if (!document.hidden) updateSignatureInk();
        });

        const colourScheme = window.matchMedia("(prefers-color-scheme: dark)");
        if (colourScheme.addEventListener) {
            colourScheme.addEventListener("change", () => window.setTimeout(updateSignatureInk, 0));
        }

        const observer = new MutationObserver(() => {
            window.requestAnimationFrame(updateSignatureInk);
        });
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ["class", "style"]
        });
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ["class", "style"]
        });
        observer.observe(document.head, { childList: true });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
