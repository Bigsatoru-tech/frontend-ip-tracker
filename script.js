// Base address of the backend. Keep the /api ending, change the front part when you get Sir Kelvin's real address.
const API_BASE = "https://visitor-tracker-api.onrender.com/api";
const API_URL = API_BASE + "/visit";
const ADMIN_URL = API_BASE + "/visits?limit=100";

const $ = (id) => document.getElementById(id);

/* ============ VISITOR POP-UP ============ */

function getDeviceInfo() {
  const ua = navigator.userAgent;

  let browser = "Unknown";
  if (/Edg\//.test(ua)) browser = "Edge";
  else if (/OPR\//.test(ua)) browser = "Opera";
  else if (/Chrome\//.test(ua)) browser = "Chrome";
  else if (/Firefox\//.test(ua)) browser = "Firefox";
  else if (/Safari\//.test(ua)) browser = "Safari";

  let os = "Unknown";
  if (/Windows/.test(ua)) os = "Windows";
  else if (/Android/.test(ua)) os = "Android";
  else if (/iPhone|iPad/.test(ua)) os = "iOS";
  else if (/Mac OS/.test(ua)) os = "macOS";
  else if (/Linux/.test(ua)) os = "Linux";

  const type = /Mobi|Android|iPhone/.test(ua) ? "Mobile" : "Desktop";
  return { browser, os, type };
}

function showPopup(data) {
  $("ip").textContent = data.ip_address || "-";
  $("location").textContent = data.location || "-";
  $("browser").textContent = data.browser || "-";
  $("os").textContent = data.os || "-";
  $("device").textContent = data.device || "-";
  $("visitedAt").textContent = data.visited_at
    ? new Date(data.visited_at).toLocaleString()
    : "-";

  $("loader").hidden = true;
  $("info").hidden = false;
}

async function trackVisit() {
  $("overlay").classList.add("show");

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ page_path: window.location.pathname }),
    });
    if (!res.ok) throw new Error("Request failed: " + res.status);
    showPopup(await res.json());
  } catch (err) {
    console.warn("Using demo data:", err.message);
    const device = getDeviceInfo();
    showPopup({
      ip_address: "102.89.0.0 (demo)",
      location: "Port Harcourt, Rivers, Nigeria",
      browser: device.browser,
      os: device.os,
      device: device.type,
      visited_at: new Date().toISOString(),
    });
  }
}

$("closeBtn").addEventListener("click", () =>
  $("overlay").classList.remove("show")
);

/* ============ ADMIN POP-UP ============ */

let adminKey = ""; // kept in memory only, never saved in the browser

function showKeyView() {
  $("keyView").hidden = false;
  $("listView").hidden = true;
  $("keyError").textContent = "";
  $("keyInput").value = "";
  $("keyInput").focus();
}

function showListView() {
  $("keyView").hidden = true;
  $("listView").hidden = false;
}

function setStatus(text, isError) {
  const el = $("adminStatus");
  el.hidden = !text;
  el.textContent = text || "";
  el.classList.toggle("error", !!isError);
}

function pretty(key) {
  return key.replace(/_/g, " ");
}

function renderVisits(visits) {
  const head = $("visitHead");
  const body = $("visitBody");
  head.innerHTML = "";
  body.innerHTML = "";

  $("visitCount").textContent =
    visits.length + (visits.length === 1 ? " visit" : " visits");

  if (visits.length === 0) {
    $("visitTable").hidden = true;
    setStatus("No visits saved yet.");
    return;
  }

  // Columns come from whatever fields the backend sends
  const cols = Object.keys(visits[0]);

  const headRow = document.createElement("tr");
  cols.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = pretty(c);
    headRow.appendChild(th);
  });
  head.appendChild(headRow);

  visits.forEach((v) => {
    const tr = document.createElement("tr");
    cols.forEach((c) => {
      const td = document.createElement("td");
      let val = v[c];
      if (val && /_at$/.test(c)) val = new Date(val).toLocaleString();
      td.textContent = val ?? "-";
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });

  setStatus("");
  $("visitTable").hidden = false;
}

async function loadVisits() {
  showListView();
  $("visitTable").hidden = true;
  setStatus("Loading...");

  try {
    const res = await fetch(ADMIN_URL, {
      headers: { "X-API-Key": adminKey },
    });

    if (res.status === 401 || res.status === 403) {
      adminKey = "";
      showKeyView();
      $("keyError").textContent = "Wrong API key. Try again.";
      return;
    }
    if (!res.ok) throw new Error("Request failed: " + res.status);

    const data = await res.json();
    const visits = Array.isArray(data) ? data : data.visits || [];
    renderVisits(visits);
  } catch (err) {
    console.warn(err);
    setStatus(
      "Couldn't reach the backend. Check that it's running and that this page's address is allowed in CORS.",
      true
    );
  }
}

function openAdmin() {
  $("overlay").classList.remove("show"); // hide the visitor pop-up
  $("adminOverlay").classList.add("show");
  if (adminKey) loadVisits();
  else showKeyView();
}

$("adminBtn").addEventListener("click", openAdmin);

$("adminClose").addEventListener("click", () =>
  $("adminOverlay").classList.remove("show")
);

$("keyView").addEventListener("submit", (e) => {
  e.preventDefault();
  const key = $("keyInput").value.trim();
  if (!key) return;
  adminKey = key;
  loadVisits();
});

$("refreshBtn").addEventListener("click", loadVisits);

$("lockBtn").addEventListener("click", () => {
  adminKey = "";
  showKeyView();
});

window.addEventListener("load", trackVisit);
