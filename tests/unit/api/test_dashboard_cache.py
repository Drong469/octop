"""Cache-Control for dashboard SPA shell vs hashed Vite assets."""

from __future__ import annotations

import mimetypes
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.testclient import TestClient

from octop.api.app import _dashboard_response, dashboard_cache_control, is_dashboard_asset_path


def test_shell_files_are_revalidated() -> None:
    assert dashboard_cache_control("") == "no-cache"
    assert dashboard_cache_control("index.html") == "no-cache"
    assert dashboard_cache_control("sw.js") == "no-cache"
    assert dashboard_cache_control("manifest.json") == "no-cache"


def test_hashed_assets_are_immutable() -> None:
    assert (
        dashboard_cache_control("assets/index.abc123.js") == "public, max-age=31536000, immutable"
    )
    assert (
        dashboard_cache_control("assets/vendor-utils.Xyz.css")
        == "public, max-age=31536000, immutable"
    )


def test_other_static_files_leave_cache_unset() -> None:
    assert dashboard_cache_control("logo_vertical_dark.svg") is None
    assert dashboard_cache_control("offline.html") is None


def test_only_hashed_assets_skip_the_spa_fallback() -> None:
    assert is_dashboard_asset_path("assets/index.abc123.js") is True
    assert is_dashboard_asset_path("chat") is False
    assert is_dashboard_asset_path("") is False


@pytest.mark.parametrize(
    ("filename", "media_type", "content"),
    [
        ("assets/index.abc123.js", "text/javascript", "export const ready = true;"),
        ("assets/worker.abc123.mjs", "text/javascript", "export default 1;"),
        ("sw.js", "text/javascript", "self.addEventListener('fetch', () => {});"),
        ("assets/index.abc123.css", "text/css", "body { margin: 0; }"),
        ("index.html", "text/html", "<!doctype html><html></html>"),
    ],
)
def test_dashboard_content_types_ignore_host_mime_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    media_type: str,
    content: str,
) -> None:
    # Windows registry entries can override the standard MIME associations.
    mimetypes.init()
    monkeypatch.setitem(mimetypes.types_map, Path(filename).suffix, "text/plain")
    path = tmp_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    app = FastAPI()

    @app.get("/asset")
    def asset() -> FileResponse:
        return _dashboard_response(path, filename)

    with TestClient(app) as client:
        response = client.get("/asset")
    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == media_type
    assert response.text == content
    assert response.headers["cache-control"] == dashboard_cache_control(filename)
