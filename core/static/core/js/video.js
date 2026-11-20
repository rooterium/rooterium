// Two-click YouTube embed (ADR 0013): the iframe from youtube-nocookie.com
// is only created after the visitor clicks. Without JavaScript the link
// opens the video on YouTube.

function play(figure) {
  const iframe = document.createElement("iframe");
  const id = encodeURIComponent(figure.dataset.videoId);
  iframe.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;
  iframe.title = figure.dataset.videoTitle;
  iframe.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
  iframe.allowFullscreen = true;
  // YouTube embeds need a referrer; the site default (same-origin) sends
  // none to other origins.
  iframe.referrerPolicy = "strict-origin-when-cross-origin";
  const frame = figure.querySelector(".video-frame");
  frame.replaceChildren(iframe);
  iframe.focus();
}

document.querySelectorAll("[data-video]").forEach((figure) => {
  const link = figure.querySelector("[data-video-play]");
  link.setAttribute("role", "button");
  link.addEventListener("click", (event) => {
    event.preventDefault();
    play(figure);
  });
  link.addEventListener("keydown", (event) => {
    if (event.key === " ") {
      event.preventDefault();
      play(figure);
    }
  });
});
