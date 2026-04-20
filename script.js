const topbar = document.querySelector("[data-topbar]");
const yearNode = document.querySelector("#current-year");
const revealNodes = document.querySelectorAll("[data-reveal]");
const copyButtons = document.querySelectorAll("[data-copy-code]");

if (yearNode) {
  yearNode.textContent = new Date().getFullYear();
}

const handleScroll = () => {
  if (!topbar) return;
  topbar.classList.toggle("is-scrolled", window.scrollY > 12);
};

const revealObserver =
  "IntersectionObserver" in window
    ? new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              revealObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.16 }
      )
    : null;

revealNodes.forEach((node) => {
  if (!revealObserver) {
    node.classList.add("is-visible");
    return;
  }

  revealObserver.observe(node);
});

window.setTimeout(() => {
  revealNodes.forEach((node) => node.classList.add("is-visible"));
}, 500);

copyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const targetId = button.getAttribute("data-copy-code");
    if (!targetId) return;

    const codeNode = document.getElementById(targetId);
    if (!codeNode) return;

    try {
      await navigator.clipboard.writeText(codeNode.textContent || "");
      const originalText = button.textContent;
      button.textContent = button.getAttribute("data-copy-success") || "Copied";
      window.setTimeout(() => {
        button.textContent = originalText;
      }, 1400);
    } catch (error) {
      button.textContent = button.getAttribute("data-copy-fallback") || "Copy failed";
      window.setTimeout(() => {
        button.textContent = button.getAttribute("data-copy-label") || "Copy";
      }, 1400);
    }
  });
});

window.addEventListener("scroll", handleScroll, { passive: true });
handleScroll();
