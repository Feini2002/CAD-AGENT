from __future__ import annotations

import unittest
from unittest.mock import patch


class _FakeEntityDriver:
    def __init__(self) -> None:
        self.doc = type("Doc", (), {"Name": "hosted.dwg", "FullName": r"C:\cad\hosted.dwg"})()
        self.app = object()
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.entities = [
            {"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"},
            {"handle": "H2", "type": "line", "layer": "FORMAL"},
        ]

    def ensure_layer(self, layer: str, *, layer_role: str = "preview") -> None:
        self.calls.append(("ensure_layer", {"layer": layer, "layer_role": layer_role}))

    def draw_line(self, **kwargs: object) -> dict[str, str]:
        self.calls.append(("draw_line", dict(kwargs)))
        return {"handle": "H1"}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        self.calls.append(("snapshot_handles", {"handles": list(handles), "layer": layer or ""}))
        return [
            entity
            for entity in self.entities
            if entity["handle"] in handles and (layer is None or entity["layer"] == layer)
        ]


class CadSessionHostServiceTests(unittest.TestCase):
    def test_service_requires_token_and_dispatches_driver_methods(self) -> None:
        from core.cad_io.cad_session_host import CadSessionHostService

        driver = _FakeEntityDriver()
        service = CadSessionHostService(driver_factory=lambda: driver, token="secret")

        rejected = service.handle_request(
            {"command": "call", "method": "draw_line", "kwargs": {"layer": "CODEX_PREVIEW"}},
            token="wrong",
        )
        accepted = service.handle_request(
            {
                "command": "call",
                "method": "draw_line",
                "kwargs": {
                    "start_point": [0, 0, 0],
                    "end_point": [10, 0, 0],
                    "layer": "CODEX_PREVIEW",
                },
            },
            token="secret",
        )

        self.assertEqual(rejected["status"], "error")
        self.assertEqual(rejected["errorCode"], "unauthorized")
        self.assertEqual(accepted["schemaVersion"], "cad-session-host-response/v1")
        self.assertEqual(accepted["status"], "ok")
        self.assertEqual(accepted["result"], {"handle": "H1"})
        self.assertEqual(driver.calls[0][0], "draw_line")

    def test_service_blocks_unsupported_methods_and_formal_layers_before_driver_call(self) -> None:
        from core.cad_io.cad_session_host import CadSessionHostService

        driver = _FakeEntityDriver()
        service = CadSessionHostService(driver_factory=lambda: driver, token="secret")

        unsupported = service.handle_request(
            {"command": "call", "method": "delete_entity_by_handle", "kwargs": {"handle": "BAD"}},
            token="secret",
        )
        formal = service.handle_request(
            {"command": "call", "method": "draw_line", "kwargs": {"layer": "A-WALL"}},
            token="secret",
        )

        self.assertEqual(unsupported["status"], "error")
        self.assertEqual(unsupported["errorCode"], "unsupported_method")
        self.assertEqual(formal["status"], "error")
        self.assertEqual(formal["errorCode"], "preview_layer_required")
        self.assertEqual(driver.calls, [])

    def test_service_status_reports_active_document_without_writing_cad(self) -> None:
        from core.cad_io.cad_session_host import CadSessionHostService

        driver = _FakeEntityDriver()
        driver.attach_diagnostics = {"method": "RunningObjectTable", "displayName": "!AutoCAD.Application.25"}
        service = CadSessionHostService(driver_factory=lambda: driver, token="secret")

        result = service.handle_request({"command": "status"}, token="secret")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["ready"], True)
        self.assertEqual(result["activeDocument"]["name"], "hosted.dwg")
        self.assertEqual(result["attachDiagnostics"]["method"], "RunningObjectTable")
        self.assertEqual(driver.calls, [])

    def test_service_status_reports_attach_diagnostics_on_blocker(self) -> None:
        from core.cad_io.autocad_com import AutoCADAttachError
        from core.cad_io.cad_session_host import CadSessionHostService

        diagnostics = {
            "method": "none",
            "acadProcessRunning": True,
            "attempts": ["ROT inspected=0"],
            "blockerCode": "acad_process_running_without_visible_rot_object",
        }

        def driver_factory() -> object:
            raise AutoCADAttachError("No active AutoCAD.Application instance is available.", diagnostics=diagnostics)

        service = CadSessionHostService(driver_factory=driver_factory, token="secret")
        result = service.handle_request({"command": "status"}, token="secret")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["ready"], False)
        self.assertEqual(result["attachDiagnostics"], diagnostics)
        self.assertEqual(
            result["attachDiagnostics"]["blockerCode"],
            "acad_process_running_without_visible_rot_object",
        )
        self.assertIn("AutoCAD.Application", result["blocker"])

    def test_http_host_is_single_threaded_to_keep_autocad_com_on_one_sta_thread(self) -> None:
        from http.server import HTTPServer, ThreadingHTTPServer

        from core.cad_io.cad_session_host import CadSessionHostService, serve_cad_session_host

        driver = _FakeEntityDriver()
        service = CadSessionHostService(driver_factory=lambda: driver, token="secret")
        server = serve_cad_session_host(service=service, host="127.0.0.1", port=0)
        try:
            self.assertIsInstance(server, HTTPServer)
            self.assertNotIsInstance(server, ThreadingHTTPServer)
        finally:
            server.server_close()


class CadSessionHostClientTests(unittest.TestCase):
    def test_client_uses_host_status_for_phase9_driver_identity_and_rpc_calls(self) -> None:
        from core.cad_io.cad_session_host import CadSessionHostClient

        requests: list[dict[str, object]] = []

        def fake_send(self: CadSessionHostClient, payload: dict[str, object]) -> dict[str, object]:
            requests.append(payload)
            if payload["command"] == "status":
                return {
                    "schemaVersion": "cad-session-host-response/v1",
                    "status": "ok",
                    "ready": True,
                    "activeDocument": {"name": "hosted.dwg", "fullName": r"C:\cad\hosted.dwg"},
                }
            if payload["method"] == "draw_rectangle":
                return {"schemaVersion": "cad-session-host-response/v1", "status": "ok", "result": {"handles": ["H1", "H2"]}}
            if payload["method"] == "snapshot_handles":
                return {
                    "schemaVersion": "cad-session-host-response/v1",
                    "status": "ok",
                    "result": [{"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"}],
                }
            raise AssertionError(payload)

        with patch.object(CadSessionHostClient, "_send", fake_send):
            client = CadSessionHostClient(base_url="http://127.0.0.1:8765", token="secret")
            draw = client.draw_rectangle(corner1=[0, 0, 0], corner2=[10, 10, 0], layer="CODEX_PREVIEW")
            readback = client.snapshot_handles(handles=["H1", "H2"], layer="CODEX_PREVIEW")

        self.assertEqual(client.doc.Name, "hosted.dwg")
        self.assertEqual(client.doc.FullName, r"C:\cad\hosted.dwg")
        self.assertIsNotNone(client.app)
        self.assertEqual(draw, {"handles": ["H1", "H2"]})
        self.assertEqual(readback, [{"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"}])
        self.assertEqual([request["command"] for request in requests], ["status", "call", "call"])


class CadSessionHostCliTests(unittest.TestCase):
    def test_main_requires_token_before_starting_server(self) -> None:
        from core.cad_io import cad_session_host

        with patch.dict("os.environ", {}, clear=True), patch.object(
            cad_session_host,
            "serve_cad_session_host",
        ) as serve:
            code = cad_session_host.main(["--host", "127.0.0.1", "--port", "8765"])

        self.assertEqual(code, 2)
        serve.assert_not_called()

    def test_main_starts_localhost_server_with_token_and_connect_existing_driver_factory(self) -> None:
        from core.cad_io import cad_session_host

        class FakeServer:
            def __init__(self) -> None:
                self.served = False
                self.closed = False

            def serve_forever(self) -> None:
                self.served = True
                raise KeyboardInterrupt

            def server_close(self) -> None:
                self.closed = True

        fake_server = FakeServer()
        captured: dict[str, object] = {}

        def fake_serve(*, service: object, host: str, port: int) -> FakeServer:
            captured["service"] = service
            captured["host"] = host
            captured["port"] = port
            return fake_server

        with patch.dict("os.environ", {"CAD_SESSION_TOKEN": "secret"}, clear=True), patch.object(
            cad_session_host,
            "serve_cad_session_host",
            side_effect=fake_serve,
        ):
            code = cad_session_host.main(["--host", "127.0.0.1", "--port", "8765"])

        self.assertEqual(code, 0)
        self.assertEqual(captured["host"], "127.0.0.1")
        self.assertEqual(captured["port"], 8765)
        self.assertIsInstance(captured["service"], cad_session_host.CadSessionHostService)
        self.assertTrue(fake_server.served)
        self.assertTrue(fake_server.closed)


if __name__ == "__main__":
    unittest.main()
