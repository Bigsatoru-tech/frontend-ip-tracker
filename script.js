const API_URL = "/api/visit"; // change to Sir Kelvin's real endpoint

const $ = (id) => document.getElementById(id);

// Basic device/browser detection from the user agent
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

  return { browser, os, type, userAgent: ua };
}

function showPopup(data) {
  $("ip").textContent = data.ip || "-";

  const loc = data.location || {};
  $("location").textContent =
    [loc.city, loc.region, loc.country].filter(Boolean).join(", ") || "-";

  const dev = data.device || {};
  $("browser").textContent = dev.browser || "-";
  $("os").textContent = dev.os || "-";
  $("device").textContent = dev.type || "-";

  $("visitedAt").textContent = data.visitedAt
    ? new Date(data.visitedAt).toLocaleString()
    : "-";

  $("loader").hidden = true;
  $("info").hidden = false;
}

async function trackVisit() {
  $("overlay").classList.add("show");
  const device = getDeviceInfo();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ device }),
    });
    if (!res.ok) throw new Error("Request failed");
    showPopup(await res.json());
  } catch (err) {
    // Backend not ready yet? Show demo data so the UI still works
    console.warn("Using demo data:", err.message);
    showPopup({
      ip: "102.89.0.0 (demo)",
      location: { city: "Port Harcourt", region: "Rivers", country: "Nigeria" },
      device,
      visitedAt: new Date().toISOString(),
    });
  }
}

$("closeBtn").addEventListener("click", () =>
  $("overlay").classList.remove("show")
);

window.addEventListener("load", trackVisit);