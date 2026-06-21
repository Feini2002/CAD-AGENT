"""CAD session host bridge for user-session AutoCAD control."""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace
from typing import Any, Callable
from urllib import request

from core.safety.policy import PREVIEW_LAYER

REQUEST_SCHEMA_VERSION = "cad-session-host-request/v1"
RESPONSE_SCHEMA_VERSION = "cad-session-host-response/v1"

ALLOWED_CALL_METHODS = {
    "ensure_layer",
    "draw_rectangle",
    "draw_line",
    "draw_polyline",
    "draw_circle",
    "draw_arc",
    "draw_text",
    "add_dimension",
    "insert_block_alpha",
    "snapshot_handles",
    "snapshot_modelspace",
    "refresh_view",
    "zoom_to_handles",
}

WRITE_METHODS = {
    "ensure_layer",
    "draw_rectangle",
    "draw_line",
    "draw_polyline",
    "draw_circle",
    "draw_arc",
    "draw_text",
    "add_dimension",
    "insert_block_alpha",
}


class CadSessionHostService:
    """Token-protected dispatcher around a CAD preview driver."""

    def __init__(self, *, driver_factory: Callable[[], Any], token: str) -> None:
        if not str(token):
            raise ValueError("CAD session host token is required.")
        self._driver_factory = driver_factory
        self._token = str(token)
        self._driver: Any | None = None

    def handle_request(self, payload: dict[str, Any], *, token: str | None) -> dict[str, Any]:
        if str(token or "") != self._token:
            return _error("unauthorized", "CAD session host token mismatch.")

        command = str(payload.get("command") or "")
        if command == "status":
            return self._status()
        if command == "call":
            return self._call(payload)
        return _error("unsupported_command", f"Unsupported CAD session host command: {command!r}")

    def _driver_instance(self) -> Any:
        if self._driver is None:
            self._driver = self._driver_factory()
        return self._driver

    def _status(self) -> dict[str, Any]:
        try:
            driver = self._driver_instance()
            doc = getattr(driver, "doc", None)
            return _ok(
                {
                    "ready": True,
                    "activeDocument": {
                        "name": str(getattr(doc, "Name", getattr(doc, "name", "")) or ""),
                        "fullName": str(getattr(doc, "FullName", getattr(doc, "fullName", "")) or ""),
                    },
                    "attachDiagnostics": dict(getattr(driver, "attach_diagnostics", {}) or {}),
                }
            )
        except Exception as exc:
            return _ok(
                {
                    "ready": False,
                    "activeDocument": {},
                    "blocker": f"{type(exc).__name__}: {exc}",
                    "attachDiagnostics": dict(getattr(exc, "diagnostics", {}) or {}),
                }
            )

    def _call(self, payload: dict[str, Any]) -> dict[str, Any]:
        method_name = str(payload.get("method") or "")
        if method_name not in ALLOWED_CALL_METHODS:
            return _error("unsupported_method", f"Unsupported CAD session host method: {method_name!r}")

        kwargs = payload.get("kwargs") or {}
        if not isinstance(kwargs, dict):
            return _error("invalid_kwargs", "CAD session host kwargs must be an object.")
        layer_error = _preview_layer_error(method_name, kwargs)
        if layer_error:
            return _error("preview_layer_required", layer_error)

        try:
            driver = self._driver_instance()
            method = getattr(driver, method_name)
            result = method(**kwargs)
            return _ok({"result": result})
        except Exception as exc:
            return _error("driver_error", f"{type(exc).__name__}: {exc}")


class CadSessionHostClient:
    """Driver-compatible RPC client for Phase 9 preview runners."""

    def __init__(self, *, base_url: str, token: str, timeout_seconds: float = 30.0) -> None:
        if not str(token):
            raise ValueError("CAD session host token is required.")
        self.base_url = str(base_url).rstrip("/")
        self.token = str(token)
        self.timeout_seconds = float(timeout_seconds)

        status = self._send({"command": "status"})
        if status.get("status") != "ok" or not bool(status.get("ready")):
            blocker = str(status.get("blocker") or status.get("message") or "CAD session host is not ready")
            raise RuntimeError(blocker)
        active = status.get("activeDocument") if isinstance(status.get("activeDocument"), dict) else {}
        self.doc = SimpleNamespace(
            Name=str(active.get("name") or ""),
            FullName=str(active.get("fullName") or ""),
        )
        self.app = SimpleNamespace(hostReady=True, Documents=SimpleNamespace(Count=1))

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> Any:
        return self._call("ensure_layer", layer=layer, layer_role=layer_role)

    def draw_rectangle(self, **kwargs: object) -> Any:
        return self._call("draw_rectangle", **kwargs)

    def draw_line(self, **kwargs: object) -> Any:
        return self._call("draw_line", **kwargs)

    def draw_polyline(self, **kwargs: object) -> Any:
        return self._call("draw_polyline", **kwargs)

    def draw_circle(self, **kwargs: object) -> Any:
        return self._call("draw_circle", **kwargs)

    def draw_arc(self, **kwargs: object) -> Any:
        return self._call("draw_arc", **kwargs)

    def draw_text(self, **kwargs: object) -> Any:
        return self._call("draw_text", **kwargs)

    def add_dimension(self, **kwargs: object) -> Any:
        return self._call("add_dimension", **kwargs)

    def insert_block_alpha(self, **kwargs: object) -> Any:
        return self._call("insert_block_alpha", **kwargs)

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
        result = self._call("snapshot_handles", handles=list(handles), layer=layer)
        return [dict(item) for item in result if isinstance(item, dict)] if isinstance(result, list) else []

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, Any]]:
        result = self._call("snapshot_modelspace", layer=layer)
        return [dict(item) for item in result if isinstance(item, dict)] if isinstance(result, list) else []

    def refresh_view(self) -> Any:
        return self._call("refresh_view")

    def zoom_to_handles(
        self,
        *,
        handles: list[str],
        layer: str | None = None,
        padding_ratio: float = 0.15,
    ) -> Any:
        return self._call(
            "zoom_to_handles",
            handles=list(handles),
            layer=layer,
            padding_ratio=padding_ratio,
        )

    def _call(self, method: str, **kwargs: object) -> Any:
        payload = {"schemaVersion": REQUEST_SCHEMA_VERSION, "command": "call", "method": method, "kwargs": kwargs}
        response = self._send(payload)
        if response.get("status") != "ok":
            raise RuntimeError(str(response.get("message") or response.get("errorCode") or "CAD session host call failed"))
        return response.get("result")

    def _send(self, payload: dict[str, object]) -> dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(
            f"{self.base_url}/rpc",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "X-CAD-Session-Token": self.token,
            },
        )
        with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            return dict(json.loads(response.read().decode("utf-8")))


def serve_cad_session_host(
    *,
    service: CadSessionHostService,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> HTTPServer:
    # AutoCAD COM objects are STA/thread-affine; keep all RPC handling on the
    # server thread so the lazily created driver is never reused cross-thread.
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/rpc":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except json.JSONDecodeError:
                payload = {}
            response_payload = service.handle_request(
                payload if isinstance(payload, dict) else {},
                token=self.headers.get("X-CAD-Session-Token"),
            )
            body = json.dumps(response_payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = HTTPServer((host, int(port)), Handler)
    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local CAD Session Host bridge.")
    parser.add_argument("--host", default=os.environ.get("CAD_SESSION_HOST_BIND", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("CAD_SESSION_HOST_PORT", "8765")))
    parser.add_argument("--token", default=os.environ.get("CAD_SESSION_TOKEN", ""))
    args = parser.parse_args(argv)

    token = str(args.token or "").strip()
    if not token:
        print("CAD_SESSION_TOKEN is required before starting CAD Session Host.", file=sys.stderr)
        return 2

    service = CadSessionHostService(driver_factory=_default_autocad_driver, token=token)
    server = serve_cad_session_host(service=service, host=str(args.host), port=int(args.port))
    print(
        json.dumps(
            {
                "schemaVersion": "cad-session-host-started/v1",
                "status": "listening",
                "host": str(args.host),
                "port": int(args.port),
                "connectExistingOnly": True,
                "previewLayerOnly": PREVIEW_LAYER,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def _default_autocad_driver() -> Any:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def _preview_layer_error(method_name: str, kwargs: dict[str, Any]) -> str:
    if method_name in WRITE_METHODS:
        layer = str(kwargs.get("layer") or "")
        if layer != PREVIEW_LAYER:
            return f"{method_name} only allows layer={PREVIEW_LAYER}."
    if method_name in {"snapshot_handles", "snapshot_modelspace", "zoom_to_handles"}:
        layer = kwargs.get("layer")
        if layer not in (None, "", PREVIEW_LAYER):
            return f"{method_name} only allows layer={PREVIEW_LAYER} or no layer filter."
    return ""


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    return {"schemaVersion": RESPONSE_SCHEMA_VERSION, "status": "ok", **payload}


def _error(error_code: str, message: str) -> dict[str, Any]:
    return {
        "schemaVersion": RESPONSE_SCHEMA_VERSION,
        "status": "error",
        "errorCode": error_code,
        "message": message,
    }
