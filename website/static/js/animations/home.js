document.addEventListener("DOMContentLoaded", () => {
  if (typeof gsap === "undefined") return;

  gsap.registerPlugin(ScrollTrigger);

  gsap.from(".hero-badge", {
    opacity: 0,
    y: 16,
    duration: 0.6,
    ease: "power2.out",
  });

  gsap.from(".hero-line", {
    opacity: 0,
    y: 24,
    duration: 0.7,
    stagger: 0.12,
    ease: "power2.out",
    delay: 0.1,
  });

  gsap.from(".hero-underline", {
    scaleX: 0,
    duration: 0.5,
    ease: "power2.out",
    delay: 0.35,
    transformOrigin: "left center",
  });

  gsap.from(".hero-copy, .hero-actions", {
    opacity: 0,
    y: 20,
    duration: 0.6,
    stagger: 0.1,
    ease: "power2.out",
    delay: 0.25,
  });

  gsap.utils.toArray(".stat-item, .approach-card, .news-card, .cta-card").forEach((el) => {
    gsap.from(el, {
      scrollTrigger: {
        trigger: el,
        start: "top 90%",
      },
      opacity: 0,
      y: 28,
      duration: 0.55,
      ease: "power2.out",
    });
  });
});
