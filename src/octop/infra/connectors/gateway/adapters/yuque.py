"""Yuque (语雀) gateway — official OpenAPI v2 REST client.

Integrates the official Yuque OpenAPI (https://www.yuque.com/api/v2) using a
Personal Access Token (header ``X-Auth-Token``). Covers search, knowledge-base
(repo) listing, document read/create/update, and directory (TOC) browsing.

API reference: https://www.yuque.com/yuque/developer/api
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

API_BASE = "https://www.yuque.com/api/v2"
_TOKEN_RE = re.compile(r"^[A-Za-z0-9_\-]{16,}$")

TOOLS: list[dict[str, Any]] = [
    {
        "name": "yuque_search",
        "description": (
            "在语雀中通用搜索文档或知识库。type=doc 搜文档，type=repo 搜知识库；"
            "scope 可选（如 'group_a' 搜团队、'group_a/book_x' 搜知识库内文档）"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "搜索关键词",
                },
                "type": {
                    "type": "string",
                    "enum": ["doc", "repo"],
                    "description": "搜索类型，doc=文档，repo=知识库",
                },
                "scope": {
                    "type": "string",
                    "description": "搜索范围，如团队 login 或 '团队login/知识库slug'",
                },
                "page": {
                    "type": "integer",
                    "description": "页码，从 1 开始",
                },
            },
            "required": ["q"],
        },
    },
    {
        "name": "yuque_list_repos",
        "description": (
            "列出用户或团队的知识库。owner 为 login/ID（省略时用当前 Token 用户）；"
            "type 可选（Book=文档型, Design=画板型）"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "owner": {
                    "type": "string",
                    "description": "用户或团队 login / ID，省略时用当前 Token 用户",
                },
                "type": {
                    "type": "string",
                    "enum": ["Book", "Design"],
                    "description": "知识库类型筛选",
                },
                "offset": {"type": "integer", "description": "偏移量"},
                "limit": {"type": "integer", "description": "每页数量，最大 100"},
            },
            "required": [],
        },
    },
    {
        "name": "yuque_list_docs",
        "description": (
            "列出知识库中的文档列表。repo 为知识库 ID 或 '团队login/知识库slug'"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "知识库 ID 或 '团队login/知识库slug'",
                },
                "offset": {"type": "integer", "description": "偏移量"},
                "limit": {"type": "integer", "description": "每页数量，最大 100"},
            },
            "required": ["repo"],
        },
    },
    {
        "name": "yuque_get_doc",
        "description": "获取文档详情与正文。repo 为知识库 ID/slug，doc 为文档 ID 或 slug",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "知识库 ID 或 '团队login/知识库slug'",
                },
                "doc": {
                    "type": "string",
                    "description": "文档 ID 或 slug/路径",
                },
            },
            "required": ["repo", "doc"],
        },
    },
    {
        "name": "yuque_create_doc",
        "description": (
            "在知识库中创建文档（markdown 正文）。repo 为知识库 ID/slug。"
            "创建后不会自动加入目录，需另用 yuque_get_toc 查看/定位"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "知识库 ID 或 '团队login/知识库slug'",
                },
                "title": {"type": "string", "description": "标题"},
                "body": {"type": "string", "description": "markdown 正文"},
                "slug": {"type": "string", "description": "路径（可选）"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "lake"],
                    "description": "内容格式，默认 markdown",
                },
            },
            "required": ["repo", "title", "body"],
        },
    },
    {
        "name": "yuque_update_doc",
        "description": "更新已有文档的标题/正文。repo 为知识库 ID/slug，doc 为文档 ID 或 slug",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "知识库 ID 或 '团队login/知识库slug'",
                },
                "doc": {
                    "type": "string",
                    "description": "文档 ID 或 slug/路径",
                },
                "title": {"type": "string", "description": "新标题（可选）"},
                "body": {"type": "string", "description": "新 markdown 正文（可选）"},
                "format": {
                    "type": "string",
                    "enum": ["markdown", "html", "lake"],
                    "description": "内容格式，默认 markdown",
                },
            },
            "required": ["repo", "doc"],
        },
    },
    {
        "name": "yuque_get_toc",
        "description": "获取知识库的目录结构（TOC）。repo 为知识库 ID 或 '团队login/知识库slug'",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "知识库 ID 或 '团队login/知识库slug'",
                },
            },
            "required": ["repo"],
        },
    },
]


def list_tools() -> list[dict[str, Any]]:
    return TOOLS


def call_tool(creds: dict[str, Any], name: str, args: dict[str, Any]) -> str:
    handler = {
        "yuque_search": _search,
        "yuque_list_repos": _list_repos,
        "yuque_list_docs": _list_docs,
        "yuque_get_doc": _get_doc,
        "yuque_create_doc": _create_doc,
        "yuque_update_doc": _update_doc,
        "yuque_get_toc": _get_toc,
    }.get(name)
    if handler is None:
        raise ValueError(f"unknown tool: {name}")
    return handler(creds, args)


def probe_credentials(creds: dict[str, Any]) -> None:
    """Live probe: call GET /user to verify the token."""
    token = _token(creds)
    headers = {"X-Auth-Token": token, "User-Agent": "octop-connector/0.1"}
    with httpx.Client(timeout=20.0) as client:
        r = client.get(f"{API_BASE}/user", headers=headers)
        if r.status_code in (401, 403):
            raise ValueError("语雀 Token 无效或无权访问，请检查")
        r.raise_for_status()
        payload = r.json()
        user = (payload or {}).get("data") or {}
        if not user or not user.get("login"):
            raise ValueError("语雀 Token 探测失败：无法解析用户信息")


# --------------------------------------------------------------------------- #
# 内部实现
# --------------------------------------------------------------------------- #

def _token(creds: dict[str, Any]) -> str:
    token = str(
        creds.get("token") or creds.get("api_key") or creds.get("access_token") or ""
    ).strip()
    if not token:
        raise ValueError("请填写语雀 Token（Personal Access Token）")
    if not _TOKEN_RE.match(token):
        raise ValueError(
            "语雀 Token 格式不正确，请在 https://www.yuque.com/settings/tokens 创建后复制完整 Token"
        )
    return token


def _headers(creds: dict[str, Any]) -> dict[str, str]:
    return {
        "X-Auth-Token": _token(creds),
        "Content-Type": "application/json",
        "User-Agent": "octop-connector/0.1",
    }


def _get_json(client: httpx.Client, url: str, headers: dict[str, str]) -> Any:
    r = client.get(url, headers=headers)
    if r.status_code in (401, 403):
        raise ValueError("语雀 Token 无效或权限不足，请检查 Token 与账号权限")
    if r.status_code == 404:
        raise ValueError(f"语雀资源不存在: {url}")
    if r.status_code == 429:
        raise ValueError("语雀接口访问频率超限，请稍后重试")
    r.raise_for_status()
    return r.json()


def _post_json(
    client: httpx.Client, url: str, headers: dict[str, str], payload: dict[str, Any]
) -> Any:
    r = client.post(url, headers=headers, json=payload)
    if r.status_code in (401, 403):
        raise ValueError("语雀 Token 无效或权限不足，请检查 Token 与账号权限")
    r.raise_for_status()
    return r.json()


def _put_json(
    client: httpx.Client, url: str, headers: dict[str, str], payload: dict[str, Any]
) -> Any:
    r = client.put(url, headers=headers, json=payload)
    if r.status_code in (401, 403):
        raise ValueError("语雀 Token 无效或权限不足，请检查 Token 与账号权限")
    r.raise_for_status()
    return r.json()


def _repo_path(repo: str) -> str:
    """Normalize repo identifier: numeric ID stays, else group/slug form."""
    repo = str(repo or "").strip()
    if not repo:
        raise ValueError("repo 必填（知识库 ID 或 '团队login/知识库slug'）")
    return repo


def _search(creds: dict[str, Any], args: dict[str, Any]) -> str:
    q = str(args.get("q") or "").strip()
    if not q:
        raise ValueError("搜索关键词 q 必填")
    params: dict[str, Any] = {"q": q}
    if args.get("type"):
        params["type"] = args["type"]
    if args.get("scope"):
        params["scope"] = args["scope"]
    if args.get("page"):
        params["page"] = int(args["page"])
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{API_BASE}/search",
            headers=_headers(creds),
            params=params,
        )
        if r.status_code in (401, 403):
            raise ValueError("语雀 Token 无效或权限不足，请检查")
        r.raise_for_status()
        payload = r.json()
    meta = (payload or {}).get("meta") or {}
    items = (payload or {}).get("data") or []
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "type": item.get("type"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "url": item.get("url"),
                "info": item.get("info"),
            }
        )
    return json.dumps(
        {"total": meta.get("total"), "page": meta.get("pageNo"), "results": out},
        ensure_ascii=False,
        indent=2,
    )


def _list_repos(creds: dict[str, Any], args: dict[str, Any]) -> str:
    owner = str(args.get("owner") or "").strip()
    with httpx.Client(timeout=30.0) as client:
        if owner:
            url = f"{API_BASE}/groups/{owner}/repos"
            params = {}
            if args.get("type"):
                params["type"] = args["type"]
            if args.get("offset") is not None:
                params["offset"] = int(args["offset"])
            if args.get("limit") is not None:
                params["limit"] = int(args["limit"])
            r = client.get(url, headers=_headers(creds), params=params)
        else:
            # current user: first resolve user, then their repos
            up = _get_json(client, f"{API_BASE}/user", _headers(creds))
            user = (up or {}).get("data") or {}
            login = user.get("login")
            url = f"{API_BASE}/users/{login}/repos"
            params = {}
            if args.get("type"):
                params["type"] = args["type"]
            if args.get("offset") is not None:
                params["offset"] = int(args["offset"])
            if args.get("limit") is not None:
                params["limit"] = int(args["limit"])
            r = client.get(url, headers=_headers(creds), params=params)
        if r.status_code in (401, 403):
            raise ValueError("语雀 Token 无效或权限不足，请检查")
        r.raise_for_status()
        payload = r.json()
    repos = (payload or {}).get("data") or []
    out = [
        {
            "id": b.get("id"),
            "name": b.get("name"),
            "slug": b.get("slug"),
            "namespace": b.get("namespace"),
            "type": b.get("type"),
            "items_count": b.get("items_count"),
            "public": b.get("public"),
            "description": b.get("description"),
        }
        for b in repos
    ]
    return json.dumps(out, ensure_ascii=False, indent=2)


def _list_docs(creds: dict[str, Any], args: dict[str, Any]) -> str:
    repo = _repo_path(args.get("repo"))
    params: dict[str, Any] = {}
    if args.get("offset") is not None:
        params["offset"] = int(args["offset"])
    if args.get("limit") is not None:
        params["limit"] = int(args["limit"])
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{API_BASE}/repos/{repo}/docs",
            headers=_headers(creds),
            params=params,
        )
        if r.status_code in (401, 403):
            raise ValueError("语雀 Token 无效或权限不足，请检查")
        r.raise_for_status()
        payload = r.json()
    meta = (payload or {}).get("meta") or {}
    docs = (payload or {}).get("data") or []
    out = [
        {
            "id": d.get("id"),
            "slug": d.get("slug"),
            "title": d.get("title"),
            "status": d.get("status"),
            "word_count": d.get("word_count"),
            "updated_at": d.get("updated_at"),
            "content_updated_at": d.get("content_updated_at"),
        }
        for d in docs
    ]
    return json.dumps(
        {"total": meta.get("total"), "docs": out},
        ensure_ascii=False,
        indent=2,
    )


def _get_doc(creds: dict[str, Any], args: dict[str, Any]) -> str:
    repo = _repo_path(args.get("repo"))
    doc = str(args.get("doc") or "").strip()
    if not doc:
        raise ValueError("doc 必填（文档 ID 或 slug/路径）")
    with httpx.Client(timeout=30.0) as client:
        payload = _get_json(
            client,
            f"{API_BASE}/repos/{repo}/docs/{doc}",
            _headers(creds),
        )
    data = (payload or {}).get("data") or {}
    out = {
        "id": data.get("id"),
        "slug": data.get("slug"),
        "title": data.get("title"),
        "status": data.get("status"),
        "format": data.get("format"),
        "word_count": data.get("word_count"),
        "updated_at": data.get("updated_at"),
        "content_updated_at": data.get("content_updated_at"),
        "body": data.get("body"),
        "body_html": data.get("body_html"),
        "body_lake": data.get("body_lake"),
        "book_id": data.get("book_id"),
    }
    return json.dumps(out, ensure_ascii=False, indent=2)


def _create_doc(creds: dict[str, Any], args: dict[str, Any]) -> str:
    repo = _repo_path(args.get("repo"))
    title = str(args.get("title") or "").strip()
    body = str(args.get("body") or "").strip()
    if not title:
        raise ValueError("title 必填")
    payload: dict[str, Any] = {"title": title, "body": body}
    if args.get("slug"):
        payload["slug"] = str(args["slug"]).strip()
    if args.get("format"):
        payload["format"] = args["format"]
    with httpx.Client(timeout=30.0) as client:
        p = _post_json(
            client,
            f"{API_BASE}/repos/{repo}/docs",
            _headers(creds),
            payload,
        )
    data = (p or {}).get("data") or {}
    out = {
        "id": data.get("id"),
        "slug": data.get("slug"),
        "title": data.get("title"),
        "status": data.get("status"),
        "url": f"https://www.yuque.com/{repo}/docs/{data.get('slug', '')}"
        if data.get("slug")
        else None,
    }
    return json.dumps(out, ensure_ascii=False, indent=2)


def _update_doc(creds: dict[str, Any], args: dict[str, Any]) -> str:
    repo = _repo_path(args.get("repo"))
    doc = str(args.get("doc") or "").strip()
    if not doc:
        raise ValueError("doc 必填（文档 ID 或 slug/路径）")
    payload: dict[str, Any] = {}
    if args.get("title"):
        payload["title"] = str(args["title"]).strip()
    if args.get("body") is not None:
        payload["body"] = str(args["body"]).strip()
    if args.get("format"):
        payload["format"] = args["format"]
    if not payload:
        raise ValueError("至少提供一个待更新字段（title 或 body）")
    with httpx.Client(timeout=30.0) as client:
        p = _put_json(
            client,
            f"{API_BASE}/repos/{repo}/docs/{doc}",
            _headers(creds),
            payload,
        )
    data = (p or {}).get("data") or {}
    out = {
        "id": data.get("id"),
        "slug": data.get("slug"),
        "title": data.get("title"),
        "status": data.get("status"),
        "content_updated_at": data.get("content_updated_at"),
    }
    return json.dumps(out, ensure_ascii=False, indent=2)


def _get_toc(creds: dict[str, Any], args: dict[str, Any]) -> str:
    repo = _repo_path(args.get("repo"))
    with httpx.Client(timeout=30.0) as client:
        payload = _get_json(
            client,
            f"{API_BASE}/repos/{repo}/toc",
            _headers(creds),
        )
    items = (payload or {}).get("data") or []

    # TOC 返回扁平列表（用 prev/sibling/child/parent uuid 链接），此处按 order 展示。
    out = [
        {
            "uuid": n.get("uuid"),
            "type": n.get("type"),
            "title": n.get("title"),
            "slug": n.get("slug"),
            "doc_id": n.get("doc_id"),
            "level": n.get("level"),
        }
        for n in items
    ]
    return json.dumps(out, ensure_ascii=False, indent=2)
