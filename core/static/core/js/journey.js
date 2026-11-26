// The temple journey on the home page (ADR 0017, temple brief section 6).
//
// The page works without this module: the portal shows a still, "Enter" is
// a link to #chapel, and every section is a plain link. Here the videos are
// added, but only when motion is welcome (no reduced motion, no data saver):
// - the portal loop, with a pause button (WCAG 2.2.2, kept for the session);
// - the entrance video after "Enter" (or a click anywhere on the portal),
//   with "Skip"; it ends on the chapel still, and the chapel fades in;
// - the descent into a section (descent.js).

import { initDescent } from "./descent.js";

const PAUSED_KEY = "rooterium:portal-paused";

const portal = document.querySelector("[data-portal]");
const chapel = document.querySelector("[data-chapel]");

function motionAllowed() {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const saveData = navigator.connection?.saveData === true;
  return !reduced && !saveData;
}

function storedPaused() {
  try {
    return sessionStorage.getItem(PAUSED_KEY) === "1";
  } catch {
    return false;
  }
}

function storePaused(paused) {
  try {
    sessionStorage.setItem(PAUSED_KEY, paused ? "1" : "0");
  } catch {
    // Storage blocked: the choice simply is not remembered.
  }
}

function initLoop(loop, button) {
  let paused = storedPaused();
  let visible = true;

  const render = () => {
    button.textContent = paused ? button.dataset.labelPlay : button.dataset.labelPause;
  };
  const apply = () => {
    if (paused || !visible) {
      loop.pause();
    } else {
      loop.play().catch(() => {
        // Autoplay refused: stay on the still.
        loop.hidden = true;
        button.hidden = true;
      });
    }
  };

  loop.hidden = false;
  button.hidden = false;
  render();
  apply();

  button.addEventListener("click", (event) => {
    event.stopPropagation();
    paused = !paused;
    storePaused(paused);
    render();
    apply();
  });

  // No need to play the loop while the portal is out of sight.
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    apply();
  }).observe(portal);
}

function initEntrance(layer, loop) {
  const video = layer.querySelector("[data-entrance-video]");
  const skip = layer.querySelector("[data-skip]");
  const heading = chapel.querySelector("#chapel-heading");
  let playing = false;

  // Fetch the entrance only after the portal is on screen (brief, 8).
  const preload = () => {
    video.preload = "auto";
    video.load();
  };
  if (document.readyState === "complete") {
    setTimeout(preload, 500);
  } else {
    window.addEventListener("load", () => setTimeout(preload, 500), { once: true });
  }

  const finish = () => {
    if (!playing) return;
    playing = false;
    document.removeEventListener("keydown", onKey);
    // A history entry, so "back" returns to the portal.
    history.pushState(null, "", "#chapel");
    chapel.scrollIntoView({ behavior: "instant" });
    chapel.classList.add("is-arriving");
    heading.focus({ preventScroll: true });
    layer.classList.add("is-leaving");
    setTimeout(() => {
      layer.hidden = true;
      layer.classList.remove("is-leaving");
      video.pause();
    }, 900);
  };

  const onKey = (event) => {
    if (event.key === "Escape") finish();
  };

  const play = () => {
    if (playing) return;
    playing = true;
    loop?.pause();
    video.currentTime = 0;
    layer.hidden = false;
    skip.focus();
    document.addEventListener("keydown", onKey);
    video.addEventListener("ended", finish, { once: true });
    video.play().catch(finish);
  };

  skip.addEventListener("click", finish);
  return play;
}

function init() {
  const motion = motionAllowed();
  const loop = portal.querySelector("[data-portal-video]");
  const pause = portal.querySelector("[data-pause]");
  const layer = document.querySelector("[data-entrance]");
  const enter = portal.querySelector("[data-enter]");

  if (motion && loop && pause) initLoop(loop, pause);
  const playEntrance = motion && layer ? initEntrance(layer, loop) : null;

  enter.addEventListener("click", (event) => {
    if (!playEntrance) return; // plain link to #chapel
    event.preventDefault();
    playEntrance();
  });

  // A click anywhere on the portal does the same as "Enter".
  portal.addEventListener("click", (event) => {
    if (event.target.closest("a, button")) return;
    enter.click();
  });

  // "Back" from the chapel: return to the top, where the portal is.
  window.addEventListener("popstate", () => {
    if (!window.location.hash) window.scrollTo({ top: 0, behavior: "instant" });
  });

  initDescent(chapel, motion);
}

if (portal && chapel) {
  init();
}
