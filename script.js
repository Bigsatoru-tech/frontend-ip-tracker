// Backend address (FastAPI). Change this if the backend runs on another port or host.
const API_URL = "https://visitor-tracker-api.onrender.com/api/visit";
const $ = (id) => document.getElementById(id);

// Browser-side detection, only used for the demo fallback
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

// Fills the pop-up using the backend's flat response format
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
    // Backend offline or blocked by CORS? Show demo data so the UI still works
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

window.addEventListener("load", trackVisit);
