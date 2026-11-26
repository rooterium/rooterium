// The descent from the chapel into a section (temple brief, section 6, A7).
//
// Picking a section plays its descent video full-screen, or, without one, a
// 1.2 s crossfade from the chapel still to the hall image with a slow zoom;
// then the browser goes to the section page, which starts with the same
// hall image in the same crop. The links stay plain links: new tabs,
// modified clicks, no JavaScript and reduced motion skip all of this.

const CROSSFADE_MS = 1200;

function makeVideo(src) {
  const video = document.createElement("video");
  video.className = "screen-media";
  video.muted = true;
  video.playsInline = true;
  video.preload = "auto";
  video.setAttribute("aria-hidden", "true");
  video.tabIndex = -1;
  video.src = src;
  return video;
}

export function initDescent(chapel, motion) {
  if (!motion) return;
  const links = [...chapel.querySelectorAll("[data-section-link]")];
  const videos = new Map();
  const skipLabel = chapel.dataset.labelSkip;

  // Fetch the descent videos only while the chapel is on screen (brief, 6).
  new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    for (const link of links) {
      const src = link.dataset.descent;
      if (src && !videos.has(src)) videos.set(src, makeVideo(src));
    }
  }).observe(chapel);

  // Back from the section page restores this page from the cache: remove
  // the layer that was left on screen.
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) document.querySelectorAll(".descent").forEach((el) => el.remove());
  });

  const descend = (link) => {
    const layer = document.createElement("div");
    layer.className = "descent";
    let gone = false;
    const go = () => {
      if (gone) return;
      gone = true;
      window.location.assign(link.href);
    };

    const src = link.dataset.descent;
    if (src) {
      const video = videos.get(src) || makeVideo(src);
      const skip = document.createElement("button");
      skip.type = "button";
      skip.className = "screen-control";
      skip.textContent = skipLabel;
      skip.addEventListener("click", go);
      layer.append(video, skip);
      document.body.append(layer);
      skip.focus();
      video.addEventListener("ended", go, { once: true });
      video.play().catch(go);
      return;
    }

    if (link.dataset.hall) {
      const image = new Image();
      image.alt = "";
      image.className = `screen-media descent-zoom ${link.dataset.hallFocus || ""}`;
      image.src = link.dataset.hall;
      layer.classList.add("is-crossfade");
      layer.append(image);
      document.body.append(layer);
      const start = () => {
        requestAnimationFrame(() => layer.classList.add("is-visible"));
        setTimeout(go, CROSSFADE_MS);
      };
      // Start once the hall image is there, but never wait long.
      image.decode().then(start, start);
      setTimeout(go, CROSSFADE_MS + 2500);
      return;
    }

    go();
  };

  for (const link of links) {
    link.addEventListener("click", (event) => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }
      event.preventDefault();
      descend(link);
    });
  }

  document.addEventListener("keydown", (event) => {
    const layer = document.querySelector(".descent");
    if (event.key === "Escape" && layer) layer.querySelector("button")?.click();
  });
}
