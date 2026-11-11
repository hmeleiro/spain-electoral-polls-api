(() => {
  const body = document.body;
  const apiBase = (body.dataset.apiBase || "").replace(/\/$/, "");
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".site-nav");

  toggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });

  document.querySelectorAll("[data-copy-target], [data-copy-text]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = button.dataset.copyTarget && document.getElementById(button.dataset.copyTarget);
      const value = button.dataset.copyText || target?.textContent || "";
      try {
        await navigator.clipboard.writeText(value);
        const original = button.textContent;
        button.textContent = "Copiado";
        setTimeout(() => { button.textContent = original; }, 1400);
      } catch (_) {
        button.textContent = "No disponible";
      }
    });
  });

  const healthIndicator = document.getElementById("health-indicator");
  const healthLabel = document.getElementById("health-label");
  if (healthIndicator && healthLabel && apiBase) {
    fetch(`${apiBase}/health`, { signal: AbortSignal.timeout(6000) })
      .then((response) => { if (!response.ok) throw new Error(); return response.json(); })
      .then((data) => {
        const ok = data.status === "ok" && data.database === "ok";
        healthIndicator.classList.add(ok ? "online" : "offline");
        healthLabel.textContent = ok ? "Operativa" : "Degradada";
      })
      .catch(() => {
        healthIndicator.classList.add("offline");
        healthLabel.textContent = "No verificable";
      });
  }

  const form = document.getElementById("api-explorer");
  if (!form) return;
  const endpoint = document.getElementById("explorer-endpoint");
  const election = document.getElementById("explorer-election");
  const party = document.getElementById("explorer-party");
  const pollster = document.getElementById("explorer-pollster");
  const limit = document.getElementById("explorer-limit");
  const requestUrl = document.getElementById("request-url");
  const responseOutput = document.getElementById("response-output");
  const responseMeta = document.getElementById("response-meta");

  const buildUrl = () => {
    const url = new URL(`${apiBase}${endpoint.value}`);
    if (endpoint.value !== "/health") {
      if (election.value.trim()) url.searchParams.set("election_key", election.value.trim());
      if (["/api/v1/results", "/api/v1/timeseries"].includes(endpoint.value) && party.value.trim()) url.searchParams.set("party", party.value.trim());
      if (["/api/v1/polls", "/api/v1/results", "/api/v1/timeseries"].includes(endpoint.value) && pollster.value.trim()) url.searchParams.set("pollster", pollster.value.trim());
      url.searchParams.set("limit", limit.value);
    }
    requestUrl.textContent = url.toString();
    document.querySelectorAll(".filter-field, .limit-field").forEach((field) => { field.hidden = endpoint.value === "/health"; });
    return url;
  };

  [endpoint, election, party, pollster, limit].forEach((control) => control.addEventListener("input", buildUrl));
  buildUrl();
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const url = buildUrl();
    responseOutput.classList.remove("error");
    responseOutput.textContent = "Consultando…";
    responseMeta.textContent = "Petición en curso";
    const started = performance.now();
    try {
      const response = await fetch(url, { headers: { Accept: "application/json" }, signal: AbortSignal.timeout(15000) });
      const text = await response.text();
      let payload;
      try { payload = JSON.parse(text); } catch (_) { payload = text; }
      responseOutput.textContent = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);
      responseMeta.textContent = `${response.status} ${response.statusText} · ${Math.round(performance.now() - started)} ms`;
      if (!response.ok) responseOutput.classList.add("error");
    } catch (error) {
      responseOutput.classList.add("error");
      responseOutput.textContent = JSON.stringify({ error: "No se pudo completar la petición", detalle: "Comprueba que la API esté disponible y que este origen esté autorizado por CORS." }, null, 2);
      responseMeta.textContent = "Error de conexión";
    }
  });
})();
