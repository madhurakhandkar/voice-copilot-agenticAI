const toggle = document.getElementById("toggle");
const dot = document.getElementById("dot");
const label = document.getElementById("label");

function updateUI(isEnabled) {
  toggle.checked = isEnabled;
  dot.classList.toggle("active", isEnabled);
  label.textContent = isEnabled ? "Tracking" : "Inactive";
}

chrome.storage.local.get("enabled", function (result) {
  const isEnabled = result.enabled !== false; // default to true
  updateUI(isEnabled);
});

toggle.addEventListener("change", function () {
  const isEnabled = toggle.checked;
  chrome.storage.local.set({ enabled: isEnabled });
  updateUI(isEnabled);
});
