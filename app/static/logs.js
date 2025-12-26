async function fetchLogs() {
    const tbody = document.getElementById("logs-tbody");
    tbody.innerHTML = "<tr><td colspan='5'>Loading...</td></tr>";

    try {
        const response = await fetch("/jobs/logs?limit=50");
        if (!response.ok) {
            throw new Error("Failed to fetch logs");
        }

        const logs = await response.json();

        if (logs.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>No logs yet.</td></tr>";
            return;
        }

        tbody.innerHTML = "";
        for (const log of logs) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${log.id}</td>
                <td>${log.job_id}</td>
                <td>${log.status}</td>
                <td>${log.started_at ?? ""}</td>
                <td>${log.output ?? ""}</td>
            `;
            tbody.appendChild(tr);
        }
    } catch (err) {
        console.error(err);
        tbody.innerHTML = "<tr><td colspan='5'>Error loading logs</td></tr>";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document
        .getElementById("refresh-logs-btn")
        .addEventListener("click", fetchLogs);

    fetchLogs(); // load on page open
});
