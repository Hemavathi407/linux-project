async function runAction(action) {
    const output = document.getElementById("output");
    const status = document.getElementById("status");
    const buttons = document.querySelectorAll("button");

    buttons.forEach(button => button.disabled = true);
    status.textContent = "Collecting system information...";
    output.textContent = "Please wait...";

    try {
        const response = await fetch("/api/" + action);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }

        output.textContent = data.output || "No matching information found.";
        status.textContent = "Completed at " + new Date().toLocaleTimeString();
    } catch (error) {
        output.textContent = "Error: " + error.message;
        status.textContent = "Operation failed";
    } finally {
        buttons.forEach(button => button.disabled = false);
    }
}

async function downloadReport() {
    const status = document.getElementById("status");

    status.textContent = "Generating report...";

    try {
        const response = await fetch("/download-report");

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || "Report generation failed");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = "audit_report.txt";
        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(url);
        status.textContent = "Report downloaded successfully";
    } catch (error) {
        status.textContent = "Error: " + error.message;
    }
}
