(function () {
  var script = document.currentScript;
  var glossaryUrl = new URL("glossary.json", script && script.src ? script.src : window.location.href);

  function showTip(term, tip) {
    tip.hidden = false;
    term.setAttribute("aria-expanded", "true");
  }

  function hideTip(term, tip) {
    tip.hidden = true;
    term.setAttribute("aria-expanded", "false");
  }

  function bindGlossary(entries) {
    var terms = document.querySelectorAll(".glossary-term");
    for (var i = 0; i < terms.length; i++) {
      var term = terms[i];
      var key = term.getAttribute("data-term");
      var entry = entries[key];
      if (!entry) continue;
      var tip = document.createElement("span");
      tip.className = "glossary-tip";
      tip.setAttribute("role", "tooltip");
      tip.hidden = true;
      tip.textContent = entry.definition;
      term.setAttribute("aria-expanded", "false");
      term.appendChild(tip);
      term.addEventListener("mouseenter", function (node, bubble) {
        return function () { showTip(node, bubble); };
      }(term, tip));
      term.addEventListener("mouseleave", function (node, bubble) {
        return function () { hideTip(node, bubble); };
      }(term, tip));
      term.addEventListener("focus", function (node, bubble) {
        return function () { showTip(node, bubble); };
      }(term, tip));
      term.addEventListener("blur", function (node, bubble) {
        return function () { hideTip(node, bubble); };
      }(term, tip));
    }
  }

  function bindQuickChecks() {
    var forms = document.querySelectorAll("form.quick-check");
    for (var i = 0; i < forms.length; i++) {
      forms[i].addEventListener("submit", function (event) {
        event.preventDefault();
        var form = event.currentTarget;
        var answer = form.getAttribute("data-answer");
        var chosen = form.querySelector("input[type='radio']:checked");
        var out = form.querySelector(".quick-check-feedback");
        if (!out) return;
        out.classList.remove("is-correct", "is-incorrect");
        if (!chosen) {
          out.textContent = "Choose an answer, then check it.";
          return;
        }
        var ok = chosen.value === answer;
        out.textContent = ok
          ? (form.getAttribute("data-correct") || "That's the reading this page expects.")
          : (form.getAttribute("data-incorrect") || "Not this one. Look back at the assumption the slider moves.");
        out.classList.add(ok ? "is-correct" : "is-incorrect");
      });
    }
  }

  bindQuickChecks();

  fetch(glossaryUrl)
    .then(function (response) {
      if (!response.ok) throw new Error("glossary " + response.status);
      return response.json();
    })
    .then(bindGlossary)
    .catch(function () {
      /* Terms stay readable if the glossary file is missing. */
    });
})();
