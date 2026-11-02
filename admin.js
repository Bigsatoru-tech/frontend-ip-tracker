const ADMIN_URL = "http://127.0.0.1:8000/visits"; // GET endpoint

const $ = (id) => document.getElementById(id);

function cell(text) {
  const td = document.createElement("td");
  td.textContent = text ?? "-";
  return td;
}

function render(visits) {
  const tbody = $("tbody");
  tbody.innerHTML = "";

  visits.forEach((v, i) => {
    const tr = document.createElement("tr");
    tr.append(
      cell(v.id ?? i + 1),
      cell(v.ip_address),
      cell(v.location),
      cell(v.browser),
      cell(v.os),
      cell(v.device),
      cell(v.page_path),
      cell(v.visited_at ? new Date(v.visited_at).toLocaleString() : "-")
    );
    tbody.appendChild(tr);
  });

  $("count").textContent = visits.length + " visit" + (visits.length === 1 ? "" : "s");
  $("table").hidden = visits.length === 0;
  $("status").hidden = visits.length > 0;
  if (visits.length === 0) $("status").textContent = "No visits saved yet.";
}

async function loadVisits() {
  $("status").hidden = false;
  $("status").classList.remove("error");
  $("status").textContent = "Loading...";

  try {
    const res = await fetch(ADMIN_URL); // plain GET
    if (!res.ok) throw new Error("Request failed: " + res.status);

    const data = await res.json();
    // Works whether the backend returns a list or { visits: [...] }
    const visits = Array.isArray(data) ? data : data.visits || [];

    // Newest first
    visits.sort((a, b) => new Date(b.visited_at) - new Date(a.visited_at));
    render(visits);
  } catch (err) {
    console.warn(err);
    $("table").hidden = true;
    $("status").hidden = false;
    $("status").classList.add("error");
    $("status").textContent =
      "Couldn't load visits. Is the backend running, and is this page's origin in CORS_ORIGINS?";
  }
}

$("refreshBtn").addEventListener("click", loadVisits);
window.addEventListener("load", loadVisits);