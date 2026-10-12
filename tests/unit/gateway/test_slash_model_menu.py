"""Tests for /model numbered menu of usable models."""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from octop.config import OctopConfig
from octop.infra.agents.manager import AgentManager
from octop.infra.db.migrate import run_migrations
from octop.infra.db.pool import SqlitePool
from octop.infra.db.repos.agents import AgentRepo
from octop.infra.db.repos.sessions import SessionRepo
from octop.infra.db.repos.threads import ThreadRepo
from octop.infra.db.repos.users import UserRepo
from octop.infra.db.services import build_shared_services
from octop.infra.gateway.slash import BufferSink, SlashCommand, build_default_dispatcher
from octop.infra.gateway.slash.ctx import SlashCtx
from octop.infra.gateway.slash.handlers import composite
from octop.infra.gateway.slash.handlers.composite import cmd_model
from octop.infra.gateway.threads import ThreadRegistry
from octop.infra.utils.paths import PathLayout


def _provider_row(name: str, model_ids: list[str]) -> MagicMock:
    row = MagicMock()
    row.name = name
    row.api_key = "key"
    row.get_models.return_value = [{"id": mid} for mid in model_ids]
    return row


@pytest.fixture
def ctx(tmp_path: Path) -> SlashCtx:
    db = SqlitePool(tmp_path / "x.db")
    run_migrations(db)
    UserRepo(db).create(username="u", password_hash="h", role="user")
    agent_repo = AgentRepo(db)
    agent_repo.create(agent_id="a1", user_id=1, name="bot")
    registry = ThreadRegistry(session_repo=SessionRepo(db), thread_repo=ThreadRepo(db))
    sk = ThreadRegistry.make_key(agent_id="a1", channel_type="ui", channel_subject_id="1")
    services = build_shared_services(db=db, paths=PathLayout(tmp_path), config=OctopConfig())
    manager = AgentManager(repos=services.repos, paths=services.paths, config=services.config)
    manager._harness_manager = MagicMock()
    manager.providers.iter_usable_rows = MagicMock(  # type: ignore[method-assign]
        return_value=[_provider_row("prov", ["m1", "m2"])]
    )
    manager.get_thread_model = MagicMock(return_value=None)  # type: ignore[method-assign]
    manager.set_thread_model = MagicMock()  # type: ignore[method-assign]
    return SlashCtx(
        agent_id="a1",
        user_id=1,
        channel_type="ui",
        session_key=sk,
        thread_registry=registry,
        agent_repo=agent_repo,
        agent_manager=manager,
    )


@pytest.fixture(autouse=True)
def _eligible_models(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(composite, "is_chat_eligible_model", lambda model, **kw: True)
    monkeypatch.setattr(composite, "_model_menu_cache", {})


async def _run(ctx: SlashCtx, args: str) -> str:
    sink = BufferSink()
    await cmd_model(build_default_dispatcher(), SlashCommand("model", args), ctx, sink)
    return "\n".join(sink.lines)


def _set_calls(ctx: SlashCtx) -> list[str]:
    assert ctx.agent_manager is not None
    return [str(c.args[2]) for c in ctx.agent_manager.set_thread_model.call_args_list]


@pytest.mark.asyncio
async def test_model_menu_lists_usable_models(ctx: SlashCtx) -> None:
    text = await _run(ctx, "")
    assert "可用模型" in text
    assert "1. `prov/m1`" in text
    assert "2. `prov/m2`" in text


@pytest.mark.asyncio
async def test_model_menu_number_selects_cached_ref(ctx: SlashCtx) -> None:
    await _run(ctx, "")
    text = await _run(ctx, "2")
    assert "prov/m2" in text
    assert _set_calls(ctx) == ["prov/m2"]
    # Menu is one-shot: a second numeric arg falls back to the literal name.
    await _run(ctx, "2")
    assert _set_calls(ctx) == ["prov/m2", "2"]


@pytest.mark.asyncio
async def test_model_menu_number_after_ttl_treated_as_literal(ctx: SlashCtx) -> None:
    await _run(ctx, "")
    composite._model_menu_cache[ctx.session_key] = (
        time.monotonic() - composite._MODEL_MENU_TTL - 1,
        {1: "prov/m1"},
    )
    text = await _run(ctx, "1")
    assert "prov/m1" not in text
    assert _set_calls(ctx) == ["1"]


@pytest.mark.asyncio
async def test_model_menu_marks_current(ctx: SlashCtx) -> None:
    assert ctx.agent_manager is not None
    ctx.agent_manager.get_thread_model = MagicMock(return_value="prov/m2")
    text = await _run(ctx, "")
    assert "2. `prov/m2`" in text
    assert "当前" in text.split("2. `prov/m2`", 1)[1].splitlines()[0]


@pytest.mark.asyncio
async def test_model_no_usable_models_falls_back_to_default_hint(
    ctx: SlashCtx, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ctx.agent_manager is not None
    ctx.agent_manager.providers.iter_usable_rows.return_value = []
    ctx.agent_manager.get_row = MagicMock(return_value=SimpleNamespace(default_model="prov/m1"))
    text = await _run(ctx, "")
    assert "可用模型" not in text
    assert "prov/m1" in text
    assert "Agent 默认" in text
