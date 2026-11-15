(() => {
  "use strict";
  const tools = document.querySelector(".catalog-tools");
  const search = tools.querySelector("input");
  const buttons = [...tools.querySelectorAll("button")];
  const groups = [...document.querySelectorAll(".lesson-group")];
  const empty = document.querySelector(".empty-state");
  const count = document.querySelector(".results-count");
  let topic = "all";

  function applyFilters() {
    const term = search.value.trim().toLocaleLowerCase();
    let matches = 0;
    for (const group of groups) {
      let groupTotal = 0;
      for (const row of group.querySelectorAll(".lesson-row")) {
        const text = row.dataset.search.toLocaleLowerCase();
        row.hidden = (topic !== "all" && group.dataset.topic !== topic) || !text.includes(term);
        if (!row.hidden) groupTotal++;
      }
      group.hidden = groupTotal === 0;
      matches += groupTotal;
    }
    for (const button of buttons) {
      button.setAttribute("aria-pressed", String(button.dataset.topic === topic));
    }
    count.textContent = `Showing ${matches} of 14 classes`;
    empty.hidden = matches !== 0;
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      topic = button.dataset.topic;
      applyFilters();
    });
  }
  search.addEventListener("input", applyFilters);
  empty.querySelector("button").addEventListener("click", () => {
    search.value = "";
    topic = "all";
    applyFilters();
    search.focus();
  });
  tools.hidden = false;
})();
