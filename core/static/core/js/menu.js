// Sections menu in the header (core/templates/includes/sections_menu.html).
// The menu is a <details> element and works without this module; here it
// also closes with Escape (focus back on the toggle) and on a click outside.

const menu = document.querySelector("[data-sections-menu]");

if (menu) {
  const toggle = menu.querySelector("summary");

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      toggle.focus();
    }
  });

  document.addEventListener("click", (event) => {
    if (menu.open && !menu.contains(event.target)) {
      menu.open = false;
    }
  });

  // On phones the open menu covers the page: keep the page from scrolling.
  menu.addEventListener("toggle", () => {
    document.documentElement.classList.toggle("menu-open", menu.open);
  });
}
