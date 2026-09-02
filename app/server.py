"""Small HTTP API and static server for the crime AI research prototype."""

from __future__ import annotations

import csv
import json
import os
import socket
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app.analysis import analyze_text


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DATA = ROOT / "data" / "processed"


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json({"status": "ok"})
            return
        if path == "/api/datasets":
            self.send_json(read_json(DATA / "dataset_manifest.json"))
            return
        if path == "/api/dashboard":
            self.send_json(read_json(PUBLIC / "data" / "dashboard.json"))
            return
        if path == "/api/india/cybercrime":
            self.send_json(read_csv(DATA / "india_cybercrime_ncrb_pib_2021_2023.csv"))
            return
        if path == "/api/gaps":
            dashboard = read_json(PUBLIC / "data" / "dashboard.json")
            self.send_json({"research_gaps": dashboard["research_gaps"]})
            return
        return super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/analyze":
            self.send_json({"error": "not_found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_json({"error": "invalid_json"}, status=400)
            return
        text = str(payload.get("text", ""))
        self.send_json(analyze_text(text))


def main() -> int:
    host = "127.0.0.1"
    requested_port = int(os.environ.get("PORT", "8000"))
    ports = [requested_port, 8765, 8787, 8088]
    server = None
    port = requested_port
    for candidate in dict.fromkeys(ports):
        try:
            server = ThreadingHTTPServer((host, candidate), Handler)
            port = candidate
            break
        except OSError as exc:
            if exc.errno not in {10013, 10048, socket.EACCES, socket.EADDRINUSE}:
                raise
    if server is None:
        raise RuntimeError(f"Could not bind to any candidate port: {ports}")
    print(f"Serving http://{host}:{port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
