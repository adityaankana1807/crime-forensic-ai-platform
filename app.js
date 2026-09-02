const datasetGrid = document.querySelector("#datasetGrid");
const stats = document.querySelector("#stats");
const growthChart = document.querySelector("#growthChart");
const sourcePanel = document.querySelector("#sourcePanel");
const gapList = document.querySelector("#gapList");
const result = document.querySelector("#analysisResult");
const analyzeBtn = document.querySelector("#analyzeBtn");
const caseText = document.querySelector("#caseText");

function el(tag, className, html) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html !== undefined) node.innerHTML = html;
  return node;
}

function number(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toLocaleString("en-IN") : value;
}

async function getJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`${url} returned ${response.status}`);
  return response.json();
}

function localAnalyze(text) {
  const lower = text.toLowerCase();
  const indicators = {
    emails: [...new Set(text.match(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi) || [])],
    urls: [...new Set(text.match(/https?:\/\/[^\s,;]+|www\.[^\s,;]+/gi) || [])],
    phones_india: [...new Set(text.match(/(?:\+91[-\s]?)?[6-9]\d{9}\b/g) || [])],
    upi_or_handles: [...new Set(text.match(/\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b/g) || [])],
    ip_addresses: [...new Set(text.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g) || [])],
    hashes: [...new Set(text.match(/\b[a-fA-F0-9]{32,64}\b/g) || [])],
  };
  const categories = [
    ["financial_cyber_fraud", ["upi", "otp", "bank", "wallet", "kyc", "loan", "refund", "investment", "crypto", "payment"]],
    ["identity_social_engineering", ["impersonation", "fake profile", "phishing", "spoof", "sim swap", "credential", "password"]],
    ["sexual_extortion_abuse", ["sextortion", "blackmail", "morphed", "intimate", "harassment", "stalking"]],
    ["property_crime", ["burglary", "theft", "vehicle", "gold", "entry", "lock", "stolen"]],
    ["violent_threat", ["weapon", "knife", "gun", "assault", "threat", "murder", "kidnap"]],
  ]
    .map(([label, terms]) => ({ label, signals: terms.filter((term) => lower.includes(term)) }))
    .filter((row) => row.signals.length)
    .map((row) => ({ ...row, score: Math.min(1, row.signals.length / 3) }));
  const evidenceAreas = {
    device: ["mobile", "phone", "laptop", "desktop", "router", "cctv", "dvr", "sim"],
    network: ["ip", "domain", "url", "email header", "login", "geolocation", "cell id"],
    financial: ["utr", "upi", "account", "ifsc", "wallet", "transaction", "statement"],
    content: ["chat", "screenshot", "audio", "video", "image", "post", "message"],
    chain_of_custody: ["hash", "seizure", "panchnama", "seal", "clone", "image", "write blocker"],
  };
  const coverage = Object.entries(evidenceAreas).map(([area, terms]) => {
    const signals = terms.filter((term) => lower.includes(term));
    return { area, present: signals.length > 0, signals };
  });
  const indicatorCount = Object.values(indicators).reduce((sum, values) => sum + values.length, 0);
  return {
    language_hints: ["paisa", "paise", "dhokha", "otp", "phonepe", "paytm", "gpay", "fir", "cyber cell"].filter((term) => lower.includes(term)),
    extracted_indicators: indicators,
    crime_categories: categories,
    evidence_coverage: coverage,
    risk_score: text.trim() ? Math.min(100, 15 + categories.length * 12 + indicatorCount * 6) : 0,
  };
}

function renderStats(dashboard) {
  const datasetCount = dashboard.datasets.length;
  const indiaRows = dashboard.datasets.find((d) => d.id.includes("india_cybercrime"))?.rows ?? 0;
  const globalRows = dashboard.datasets.find((d) => d.id.includes("global_homicide"))?.rows ?? 0;
  const gaps = dashboard.research_gaps.length;
  stats.innerHTML = "";
  [
    [datasetCount, "curated datasets"],
    [indiaRows, "Indian State/UT cybercrime rows"],
    [globalRows, "global homicide records"],
    [gaps, "paper gaps tracked"],
  ].forEach(([value, label]) => stats.appendChild(el("div", "stat", `<strong>${number(value)}</strong><span>${label}</span>`)));
}

function renderDatasets(datasets) {
  datasetGrid.innerHTML = "";
  datasets.forEach((dataset) => {
    const card = el(
      "article",
      "card",
      `<h3>${dataset.title}</h3>
       <p>${dataset.limitations}</p>
       <div class="meta">
         <span class="pill">${dataset.granularity}</span>
         <span class="pill">${number(dataset.rows)} rows</span>
       </div>
       <p><a href="${dataset.public_file || dataset.file}" target="_blank" rel="noreferrer">Open CSV</a></p>`
    );
    datasetGrid.appendChild(card);
  });
}

function renderGrowth(rows) {
  growthChart.innerHTML = "";
  const max = Math.max(...rows.map((r) => Number(r.pct_change_2021_2023)));
  rows.forEach((row) => {
    const pct = Number(row.pct_change_2021_2023);
    const width = Math.max(3, (pct / max) * 100);
    growthChart.appendChild(
      el(
        "div",
        "bar-row",
        `<span>${row.state_ut}</span><div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div><strong>${pct}%</strong>`
      )
    );
  });
}

function renderSources(datasets) {
  const links = datasets
    .map((d) => `<li><a href="${d.source_url}" target="_blank" rel="noreferrer">${d.title}</a></li>`)
    .join("");
  sourcePanel.innerHTML = `<h3>Source Registry</h3><p>These are the exact source URLs recorded by the dataset builder.</p><ul class="list">${links}</ul>`;
}

function renderGaps(gaps) {
  gapList.innerHTML = "";
  gaps.forEach((gap) => gapList.appendChild(el("article", "gap-item", `<p>${gap}</p>`)));
}

function renderAnalysis(data) {
  const categories = data.crime_categories.map((item) => `<li>${item.label}: ${(item.score * 100).toFixed(0)}% signals ${item.signals.join(", ")}</li>`).join("");
  const indicators = Object.entries(data.extracted_indicators)
    .filter(([, values]) => values.length)
    .map(([key, values]) => `<li>${key}: ${values.join(", ")}</li>`)
    .join("");
  const evidence = data.evidence_coverage
    .map((item) => `<li>${item.area}: ${item.present ? "present" : "missing"} ${item.signals.length ? `(${item.signals.join(", ")})` : ""}</li>`)
    .join("");
  result.innerHTML = `
    <div class="risk">${data.risk_score}</div>
    <h3>Explainable Triage</h3>
    <p>Language hints: ${data.language_hints.length ? data.language_hints.join(", ") : "none detected"}</p>
    <h3>Crime Categories</h3>
    <ul class="list">${categories || "<li>No category dictionary match.</li>"}</ul>
    <h3>Digital Indicators</h3>
    <ul class="list">${indicators || "<li>No structured indicators extracted.</li>"}</ul>
    <h3>Evidence Coverage</h3>
    <ul class="list">${evidence}</ul>
  `;
}

async function analyze() {
  result.innerHTML = "<p>Analyzing...</p>";
  let data;
  try {
    data = await getJSON("api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: caseText.value }),
    });
  } catch (error) {
    data = localAnalyze(caseText.value);
  }
  renderAnalysis(data);
}

async function init() {
  let dashboard;
  try {
    dashboard = await getJSON("api/dashboard");
  } catch (error) {
    dashboard = await getJSON("data/dashboard.json");
  }
  renderStats(dashboard);
  renderDatasets(dashboard.datasets);
  renderGrowth(dashboard.india_cybercrime_top_growth);
  renderSources(dashboard.datasets);
  renderGaps(dashboard.research_gaps);
  analyzeBtn.addEventListener("click", analyze);
  await analyze();
}

init().catch((error) => {
  document.body.prepend(el("div", "panel", `<strong>Startup error:</strong> ${error.message}`));
});
