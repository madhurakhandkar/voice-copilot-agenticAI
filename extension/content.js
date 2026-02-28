(function () {
  "use strict";

  let enabled = false;
  let pageEntryTime = Date.now();
  let lastScrollY = window.scrollY;
  let scrollThrottleTimer = null;
  let currentUrl = location.href;

  function sendEvent(event) {
    if (!enabled) return;
    try {
      chrome.runtime.sendMessage({ action: "track_event", event });
    } catch (_) {
      // Extension context invalidated (e.g. extension reloaded) — silently ignore
    }
  }

  function buildClickEvent(e) {
    const el = e.target;
    if (!el || !el.tagName) return null;

    const tag = el.tagName.toLowerCase();
    if (tag === "input" && (el.type === "password" || el.type === "hidden")) return null;

    const rect = el.getBoundingClientRect();

    return {
      type: "click",
      timestamp: Date.now(),
      url: location.href,
      data: {
        tagName: tag,
        id: el.id || null,
        className: (el.className && typeof el.className === "string")
          ? el.className.split(/\s+/).slice(0, 3).join(" ")
          : null,
        innerText: (el.innerText || "").trim().substring(0, 150) || null,
        href: el.href || el.closest("a")?.href || null,
        ariaLabel: el.getAttribute("aria-label") || null,
        role: el.getAttribute("role") || null,
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height),
        },
      },
    };
  }

  // --- Click Tracking (capture phase) ---
  document.addEventListener(
    "click",
    function (e) {
      const event = buildClickEvent(e);
      if (event) sendEvent(event);
    },
    true
  );

  // --- Navigation Tracking (SPA-aware) ---
  function onNavigate(toUrl) {
    const fromUrl = currentUrl;
    if (fromUrl === toUrl) return;

    // Send time-on-page for the page we're leaving
    sendEvent({
      type: "time_on_page",
      timestamp: Date.now(),
      url: fromUrl,
      data: { durationMs: Date.now() - pageEntryTime },
    });

    currentUrl = toUrl;
    pageEntryTime = Date.now();

    sendEvent({
      type: "navigation",
      timestamp: Date.now(),
      url: toUrl,
      data: { fromUrl, toUrl },
    });
  }

  // Override history.pushState
  const originalPushState = history.pushState;
  history.pushState = function () {
    originalPushState.apply(this, arguments);
    onNavigate(location.href);
  };

  // Override history.replaceState
  const originalReplaceState = history.replaceState;
  history.replaceState = function () {
    originalReplaceState.apply(this, arguments);
    onNavigate(location.href);
  };

  window.addEventListener("popstate", function () {
    onNavigate(location.href);
  });

  // Initial page load event
  sendEvent({
    type: "navigation",
    timestamp: Date.now(),
    url: location.href,
    data: { fromUrl: null, toUrl: location.href },
  });

  // --- Scroll Tracking (throttled to once every 2s) ---
  window.addEventListener("scroll", function () {
    if (scrollThrottleTimer) return;
    scrollThrottleTimer = setTimeout(function () {
      scrollThrottleTimer = null;

      const scrollTop = window.scrollY;
      const docHeight = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight
      );
      const winHeight = window.innerHeight;
      const scrollable = docHeight - winHeight;
      const scrollPercent = scrollable > 0 ? Math.round((scrollTop / scrollable) * 100) : 0;
      const direction = scrollTop >= lastScrollY ? "down" : "up";
      lastScrollY = scrollTop;

      sendEvent({
        type: "scroll",
        timestamp: Date.now(),
        url: location.href,
        data: { scrollPercent, direction },
      });
    }, 2000);
  });

  // --- Time on Page (visibility change) ---
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") {
      sendEvent({
        type: "time_on_page",
        timestamp: Date.now(),
        url: location.href,
        data: { durationMs: Date.now() - pageEntryTime },
      });
    }
    if (document.visibilityState === "visible") {
      pageEntryTime = Date.now();
    }
  });

  // --- Enable/Disable based on storage flag ---
  function checkEnabled() {
    try {
      chrome.storage.local.get("enabled", function (result) {
        enabled = result.enabled !== false; // default to true
      });
    } catch (_) {
      enabled = true;
    }
  }

  checkEnabled();

  try {
    chrome.storage.onChanged.addListener(function (changes, area) {
      if (area === "local" && changes.enabled) {
        enabled = changes.enabled.newValue !== false;
      }
    });
  } catch (_) {
    // Extension context may be invalidated
  }
})();
