/* Checklist persistence for the FFXIV Relic Weapon Roadmap Guide.
 * Stores checkbox state in localStorage, adds a progress counter,
 * and offers reset/advanced options. No network calls, local-only. */
(function () {
  "use strict";

  var STORAGE_PREFIX = "relic-guide:checklist:";
  var pageKey = STORAGE_PREFIX + (window.location.pathname.split("/").pop() || "index.html");

  function load() {
    try {
      return JSON.parse(window.localStorage.getItem(pageKey) || "{}");
    } catch (e) {
      return {};
    }
  }

  function save(state) {
    try {
      window.localStorage.setItem(pageKey, JSON.stringify(state));
    } catch (e) {
      /* storage unavailable (private mode etc.) — checkboxes still work live */
    }
  }

  var state = load();
  var boxes = Array.prototype.slice.call(
    document.querySelectorAll('li.check-item input[type="checkbox"]')
  );

  if (boxes.length === 0) return;

  var counter = document.createElement("p");
  counter.className = "check-progress";
  var firstList = document.querySelector("ul.checklist");
  if (firstList && firstList.parentNode) {
    firstList.parentNode.insertBefore(counter, firstList);
  } else {
    counter.style.display = "none";
  }

  function refresh() {
    var done = boxes.filter(function (b) { return b.checked; }).length;
    counter.textContent = "Checklist: " + done + " of " + boxes.length + " done";
    return done;
  }

  function clearedPorted(state) {
    /* A checklist reset should never require deleting anything else. */
    return state;
  }

  boxes.forEach(function (box, i) {
    var key = box.getAttribute("data-key") || String(i);
    if (key in state) {
      box.checked = !!state[key];
    } else if (box.defaultChecked) {
      box.checked = true;
      state[key] = true;
    }
    box.addEventListener("change", function () {
      state[key] = box.checked;
      save(clearedPorted(state));
      refresh();
    });
  });

  save(state);
  refresh();

  var reset = document.createElement("button");
  reset.type = "button";
  reset.textContent = "Reset checklist";
  reset.style.cssText =
    "margin:0.25rem 0 1rem;background:var(--soft,#ece5d8);border:1px solid #d5c9b4;" +
    "border-radius:6px;padding:0.25rem 0.8rem;font:inherit;font-size:0.85rem;cursor:pointer;";
  reset.addEventListener("click", function () {
    boxes.forEach(function (b) { b.checked = false; });
    state = clearedPorted({});
    save(state);
    refresh();
  });
  if (counter.parentNode) {
    counter.parentNode.insertBefore(reset, counter.nextSibling);
  }
})();
