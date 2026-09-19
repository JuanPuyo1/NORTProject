document.addEventListener("DOMContentLoaded", () => {
  if (typeof gsap === "undefined") return;

  gsap.from(".collab-copy > *", {
    opacity: 0,
    y: 18,
    duration: 0.5,
    stagger: 0.08,
    ease: "power2.out",
  });

  gsap.from(".collab-form", {
    opacity: 0,
    y: 24,
    duration: 0.55,
    ease: "power2.out",
    delay: 0.15,
  });
});
