document.addEventListener("alpine:init", () => {
  document.body.addEventListener("click", (event) => {
    const link = event.target.closest("#mobile-menu-panel a");
    if (link) {
      document.body.dispatchEvent(new CustomEvent("close-mobile-menu"));
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const panel = document.getElementById("mobile-menu-panel");
  if (!panel || typeof gsap === "undefined") return;

  document.body.addEventListener("close-mobile-menu", () => {
    const root = document.querySelector("[x-data]");
    if (root && root._x_dataStack) {
      root._x_dataStack[0].menuOpen = false;
    }
  });

  const observer = new MutationObserver(() => {
    const menuRoot = document.querySelector('[x-show="menuOpen"]');
    if (!menuRoot || menuRoot.style.display === "none") return;

    gsap.fromTo(
      panel,
      { opacity: 0, y: 12 },
      { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }
    );
  });

  observer.observe(document.body, {
    attributes: true,
    subtree: true,
    attributeFilter: ["style", "class"],
  });
});
