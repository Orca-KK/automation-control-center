function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function fetchJobs() {
  const tbody = document.getElementById("jobs-body");
  tbody.innerHTML = `<tr><td colspan="7">Loading jobs…</td></tr>`;

  try {
    // ✅ absolute path (NOT "jobs")
    const response = await fetch("/jobs");
    if (!response.ok) throw new Error(`Failed to fetch jobs: ${response.status}`);

    const jobs = await response.json();

    if (!Array.isArray(jobs) || jobs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7">No jobs yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";

    for (const job of jobs) {
      const id = job.id;
      const name = escapeHtml(job.name);
      const type = escapeHtml(job.job_type);
      const schedule = escapeHtml(job.schedule);
      const active = job.is_active ? "Yes" : "No";
      const target = escapeHtml(job.target || "");

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${id}</td>
        <td>${name}</td>
        <td>${type}</td>
        <td>${schedule}</td>
        <td>${active}</td>
        <td>${target}</td>
        <td>
          <button class="run-btn" data-id="${id}">Run</button>
          <button class="delete-btn" data-id="${id}">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    }

    // Wire up Run
    document.querySelectorAll(".run-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.getAttribute("data-id");
        await runJob(id);
      });
    });

    // Wire up Delete
    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.getAttribute("data-id");
        await deleteJob(id);
      });
    });
  } catch (err) {
    console.error(err);
    tbody.innerHTML = `<tr><td colspan="7">Error loading jobs (check console).</td></tr>`;
  }
}

async function createJob(payload) {
  const res = await fetch("/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Create failed: ${res.status} ${txt}`);
  }
  return await res.json();
}

async function deleteJob(id) {
  const res = await fetch(`/jobs/${id}`, { method: "DELETE" });
  if (!res.ok) {
    const txt = await res.text();
    alert(`Delete failed: ${res.status}\n${txt}`);
    return;
  }
  await fetchJobs();
}

async function runJob(id) {
  const res = await fetch(`/jobs/${id}/run`, { method: "POST" });

  if (!res.ok) {
    const txt = await res.text();
    alert(`Run failed: ${res.status}\n${txt}`);
    return;
  }

  alert(`Job ${id} executed. Check logs page.`);
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("createJobForm");
  const refreshBtn = document.getElementById("refreshJobsBtn");

  refreshBtn.addEventListener("click", fetchJobs);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      name: document.getElementById("name").value.trim(),
      description: document.getElementById("description").value.trim() || null,
      schedule: document.getElementById("schedule").value.trim(),
      job_type: document.getElementById("job_type").value.trim(),
      target: document.getElementById("target").value.trim() || null,
      is_active: document.getElementById("is_active").checked,
    };

    try {
      await createJob(payload);
      form.reset();

      // restore defaults
      document.getElementById("schedule").value = "every_5_minutes";
      document.getElementById("job_type").value = "http_ping";
      document.getElementById("target").value = "https://example.com";
      document.getElementById("is_active").checked = true;

      await fetchJobs();
    } catch (err) {
      console.error(err);
      alert("Create failed. Check browser console + terminal logs.");
    }
  });

  fetchJobs();
});
