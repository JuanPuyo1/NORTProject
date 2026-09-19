function animateBlogPosts() {
  if (typeof gsap === "undefined") return;

  gsap.from(".featured-post, .post-row", {
    opacity: 0,
    y: 20,
    duration: 0.45,
    stagger: 0.06,
    ease: "power2.out",
    clearProps: "all",
  });
}

document.addEventListener("DOMContentLoaded", animateBlogPosts);
document.body.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail.target.id === "blog-posts" || event.detail.target.id === "post-list-rows") {
    animateBlogPosts();
  }
});
