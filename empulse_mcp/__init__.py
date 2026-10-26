"""empulse-mcp: a stdio bridge to the EMpulse Street FX Index MCP server.

Reads newline-delimited JSON-RPC messages from stdin, posts each one to the remote streamable-HTTP endpoint
(stateless: every request is a complete exchange) and writes the JSON answer to stdout. Notifications (messages
without an id) are forwarded and produce no output. Standard library only.

    EMPULSE_API_KEY   optional EMpulse key, sent as the X-API-Key header
    EMPULSE_MCP_URL   the server (default https://api.empulse.ai/mcp)
"""

import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://api.empulse.ai/mcp"
TIMEOUT = 60
PROTOCOL_HEADER = "MCP-Protocol-Version"


def forward(message: dict, url: str, api_key: str | None, protocol_version: str | None) -> dict | None:
    """POST one message; return the parsed answer (None for notifications / accepted without a body)."""
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if api_key:
        headers["X-API-Key"] = api_key
    if protocol_version and message.get("method") != "initialize":
        headers[PROTOCOL_HEADER] = protocol_version
    req = urllib.request.Request(url, data=json.dumps(message).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read()
            if not body or resp.status == 202:
                return None
            text = body.decode("utf-8", "replace")
            if resp.headers.get("Content-Type", "").startswith("text/event-stream"):
                text = _last_sse_data(text)
            return json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        return _error(message, -32000, f"HTTP {exc.code} from {url}: {detail}")
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return _error(message, -32001, f"could not reach {url}: {type(exc).__name__}")


def _last_sse_data(text: str) -> str:
    data = [ln[5:].strip() for ln in text.splitlines() if ln.startswith("data:")]
    return data[-1] if data else ""


def _error(message: dict, code: int, text: str) -> dict | None:
    if "id" not in message:
        return None
    return {"jsonrpc": "2.0", "id": message["id"], "error": {"code": code, "message": text}}


def main() -> None:
    url = os.environ.get("EMPULSE_MCP_URL", DEFAULT_URL)
    api_key = os.environ.get("EMPULSE_API_KEY") or None
    protocol_version = None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None,
                                         "error": {"code": -32700, "message": "Parse error"}}) + "\n")
            sys.stdout.flush()
            continue
        answer = forward(message, url, api_key, protocol_version)
        if message.get("method") == "initialize" and isinstance(answer, dict):
            protocol_version = (answer.get("result") or {}).get("protocolVersion") or protocol_version
        if answer is not None:
            sys.stdout.write(json.dumps(answer) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
