from flask import Flask, jsonify, send_from_directory, send_file
from pathlib import Path
import subprocess

app = Flask(__name__)

PROJECT = Path.home() / "linux-security-dashboard"
FRONTEND = PROJECT / "frontend"
SCRIPT = PROJECT / "scripts" / "monitor.sh"
REPORT = PROJECT / "audit_report.txt"

ALLOWED_ACTIONS = {"logs", "security", "health", "report"}


def run_script(action):
    if action not in ALLOWED_ACTIONS:
        return "Invalid action", 400

    try:
        result = subprocess.run(
            [str(SCRIPT), action],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

        output = result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        if result.returncode != 0:
            return output or "Monitoring script failed.", 500

        return output, 200

    except subprocess.TimeoutExpired:
        return "The monitoring command timed out.", 504
    except OSError as error:
        return f"Unable to execute monitoring script: {error}", 500


@app.get("/")
def home():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(FRONTEND, "style.css")


@app.get("/script.js")
def javascript():
    return send_from_directory(FRONTEND, "script.js")


@app.get("/api/health")
def health():
    output, status = run_script("health")
    return jsonify({"output": output}), status


@app.get("/api/logs")
def logs():
    output, status = run_script("logs")
    return jsonify({"output": output}), status


@app.get("/api/security")
def security():
    output, status = run_script("security")
    return jsonify({"output": output}), status


@app.get("/download-report")
def download_report():
    output, status = run_script("report")

    if status != 200:
        return jsonify({"error": output}), status

    if not REPORT.is_file():
        return jsonify({"error": "Report file was not created."}), 500

    return send_file(
        REPORT,
        as_attachment=True,
        download_name="audit_report.txt"
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
