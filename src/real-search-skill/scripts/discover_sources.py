#!/usr/bin/env python3
"""Discover candidate sources for a real-search research workspace."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path


USER_AGENT = "real-search-skill/0.2"


@dataclass
class Candidate:
    type: str
    name: str
    url: str
    evidence: str
    status: str
    priority: int
    source: str
    value: str
    reason: str


def fetch_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def shorten(text: str, limit: int = 180) -> str:
    text = " ".join((text or "").split())
    return text[:limit]


def md_cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def openalex_abstract_snippet(index: object, limit: int = 180) -> str:
    if not isinstance(index, dict):
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int):
                words.append((position, word))
    if not words:
        return ""
    return shorten(" ".join(word for _, word in sorted(words)[:80]), limit)


def normalize_url(url: str) -> str:
    return url.strip().rstrip("/")


def add_unique(items: list[Candidate], seen: set[str], item: Candidate) -> None:
    key = normalize_url(item.url).lower() or item.name.lower()
    if key in seen:
        return
    seen.add(key)
    items.append(item)


def topic_queries(topic: str) -> list[str]:
    topic = topic.strip()
    return [
        topic,
        f"{topic} framework",
        f"{topic} survey",
        f"{topic} benchmark",
        f"awesome {topic}",
    ]


def github_candidates(topic: str, limit: int) -> tuple[list[Candidate], list[str]]:
    candidates: list[Candidate] = []
    errors: list[str] = []
    seen: set[str] = set()
    per_query = max(1, min(5, limit))

    for query in topic_queries(topic):
        params = urllib.parse.urlencode({
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_query,
        })
        url = f"https://api.github.com/search/repositories?{params}"
        try:
            payload = json.loads(fetch_text(url))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"GitHub 搜索失败：{query} -> {exc}")
            continue

        for repo in payload.get("items", []):
            name = repo.get("full_name") or repo.get("name") or "unknown"
            html_url = repo.get("html_url") or ""
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language") or "未知语言"
            description = repo.get("description") or ""
            is_awesome = "awesome" in name.lower()
            add_unique(
                candidates,
                seen,
                Candidate(
                    type="Awesome列表" if is_awesome else "源码",
                    name=name,
                    url=html_url,
                    evidence="A-源码/官方",
                    status="待读",
                    priority=90 if stars >= 10_000 else 80 if stars >= 1_000 else 65,
                    source="GitHub Search",
                    value=f"{stars} stars；{language}；{description}".strip("；"),
                    reason=f"由查询 `{query}` 发现，按 star 排序靠前。",
                ),
            )
        time.sleep(0.2)

    return candidates[:limit], errors


def arxiv_candidates(topic: str, limit: int) -> tuple[list[Candidate], list[str]]:
    candidates: list[Candidate] = []
    errors: list[str] = []
    seen: set[str] = set()
    query = urllib.parse.quote(f'all:"{topic}"')
    url = f"https://export.arxiv.org/api/query?search_query={query}&start=0&max_results={limit}&sortBy=relevance&sortOrder=descending"
    try:
        text = fetch_text(url, timeout=30)
        root = ET.fromstring(text)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError) as exc:
        return [], [f"arXiv 搜索失败：{topic} -> {exc}"]

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
        title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
        link = entry.findtext("atom:id", default="", namespaces=ns) or ""
        summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
        published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
        add_unique(
            candidates,
            seen,
            Candidate(
                type="论文",
                name=title or link,
                url=link,
                evidence="B-论文/技术报告",
                status="待读",
                priority=85,
                source="arXiv API",
                value=f"{published}；{summary[:180]}",
                reason="arXiv relevance 搜索结果，需阅读正文确认价值。",
            ),
        )

    return candidates, errors


def generated_search_candidates(topic: str) -> list[Candidate]:
    encoded = urllib.parse.quote(topic)
    docs_query = urllib.parse.quote(f"{topic} official docs")
    products_query = urllib.parse.quote(f"{topic} product platform SaaS")
    benchmark_query = urllib.parse.quote(f"{topic} benchmark evaluation comparison")
    awesome_query = urllib.parse.quote(f"awesome {topic}")
    return [
        Candidate(
            type="论文索引",
            name=f"Papers with Code 搜索：{topic}",
            url=f"https://paperswithcode.com/search?q={encoded}",
            evidence="D-待验证",
            status="待读",
            priority=60,
            source="Generated Search",
            value="用于发现论文、任务榜单和关联代码。",
            reason="Papers with Code 没有稳定无密钥公开搜索接口，先生成检索入口。",
        ),
        Candidate(
            type="官方文档搜索",
            name=f"官方文档搜索：{topic}",
            url=f"https://www.google.com/search?q={docs_query}",
            evidence="D-待验证",
            status="待读",
            priority=58,
            source="Generated Search",
            value="用于发现官方文档、规范和产品主页。",
            reason="官方文档需要人工/Codex 二次确认，避免把 SEO 页面当官方来源。",
        ),
        Candidate(
            type="商业产品搜索",
            name=f"商业产品/平台搜索：{topic}",
            url=f"https://www.google.com/search?q={products_query}",
            evidence="D-待验证",
            status="待读",
            priority=57,
            source="Generated Search",
            value="用于发现非开源产品、SaaS、企业方案和官网资料。",
            reason="商业产品资料常来自官网/定价页/文档页，必须二次确认，不可直接当正式证据。",
        ),
        Candidate(
            type="Benchmark搜索",
            name=f"Benchmark/Evaluation 搜索：{topic}",
            url=f"https://www.google.com/search?q={benchmark_query}",
            evidence="D-待验证",
            status="待读",
            priority=56,
            source="Generated Search",
            value="用于发现评测榜单、横向对比和公开 benchmark。",
            reason="benchmark 入口用于建立候选清单，正式结论仍需回到原始评测或论文。",
        ),
        Candidate(
            type="Awesome列表搜索",
            name=f"Awesome list 搜索：{topic}",
            url=f"https://github.com/search?q={awesome_query}&type=repositories&s=stars&o=desc",
            evidence="D-待验证",
            status="待读",
            priority=55,
            source="Generated Search",
            value="用于发现社区整理的成熟项目清单。",
            reason="作为广度扫描入口，后续需回到原始项目和论文验证。",
        ),
        Candidate(
            type="社区讨论搜索",
            name=f"Hacker News 搜索：{topic}",
            url=f"https://hn.algolia.com/?q={encoded}",
            evidence="C-社区/博客",
            status="待读",
            priority=45,
            source="Generated Search",
            value="用于发现社区讨论、产品趋势和反例。",
            reason="社区信号只能作为辅助，不可作为正式结论的唯一证据。",
        ),
    ]


def openalex_candidates(topic: str, limit: int) -> tuple[list[Candidate], list[str]]:
    params = urllib.parse.urlencode({
        "search": topic,
        "per-page": max(1, min(limit, 20)),
        "sort": "cited_by_count:desc",
    })
    url = f"https://api.openalex.org/works?{params}"
    try:
        payload = json.loads(fetch_text(url, timeout=30))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return [], [f"OpenAlex 搜索失败：{topic} -> {exc}"]

    candidates: list[Candidate] = []
    seen: set[str] = set()
    for work in payload.get("results", []):
        title = work.get("title") or work.get("display_name") or "Untitled OpenAlex work"
        link = (work.get("primary_location") or {}).get("landing_page_url") or work.get("doi") or work.get("id") or ""
        year = work.get("publication_year") or "n.d."
        cited = work.get("cited_by_count") or 0
        add_unique(
            candidates,
            seen,
            Candidate(
                type="论文/技术报告",
                name=title,
                url=link,
                evidence="B-论文/技术报告",
                status="待读",
                priority=82 if cited >= 500 else 72 if cited >= 50 else 62,
                source="OpenAlex API",
                value=f"{year}；cited_by={cited}；{openalex_abstract_snippet(work.get('abstract_inverted_index'))}",
                reason="OpenAlex 公开检索结果，适合补足 arXiv 之外的论文/报告候选。",
            ),
        )
    return candidates, []


def crossref_candidates(topic: str, limit: int) -> tuple[list[Candidate], list[str]]:
    params = urllib.parse.urlencode({
        "query": topic,
        "rows": max(1, min(limit, 20)),
        "sort": "relevance",
        "order": "desc",
    })
    url = f"https://api.crossref.org/works?{params}"
    try:
        payload = json.loads(fetch_text(url, timeout=30))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return [], [f"Crossref 搜索失败：{topic} -> {exc}"]

    candidates: list[Candidate] = []
    seen: set[str] = set()
    for item in (payload.get("message") or {}).get("items", []):
        title = " ".join((item.get("title") or ["Untitled Crossref work"])[0].split())
        doi = item.get("DOI") or ""
        link = f"https://doi.org/{doi}" if doi else (item.get("URL") or "")
        year_parts = (((item.get("published-print") or item.get("published-online") or {}).get("date-parts")) or [[]])[0]
        year = year_parts[0] if year_parts else "n.d."
        add_unique(
            candidates,
            seen,
            Candidate(
                type="论文/出版物",
                name=title,
                url=link,
                evidence="B-论文/技术报告",
                status="待读",
                priority=66,
                source="Crossref API",
                value=f"{year}；publisher={item.get('publisher', '未知')}",
                reason="Crossref 公开元数据结果，可补足 ACM/IEEE/出版社论文线索，需访问原文确认。",
            ),
        )
    return candidates, []


def semantic_scholar_candidates(topic: str, limit: int) -> tuple[list[Candidate], list[str]]:
    params = urllib.parse.urlencode({
        "query": topic,
        "limit": max(1, min(limit, 20)),
        "fields": "title,url,year,citationCount,abstract,venue",
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    try:
        payload = json.loads(fetch_text(url, timeout=30))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return [], [f"Semantic Scholar 搜索失败：{topic} -> {exc}"]

    candidates: list[Candidate] = []
    seen: set[str] = set()
    for paper in payload.get("data", []):
        title = paper.get("title") or "Untitled Semantic Scholar paper"
        cited = paper.get("citationCount") or 0
        add_unique(
            candidates,
            seen,
            Candidate(
                type="论文",
                name=title,
                url=paper.get("url") or "",
                evidence="B-论文/技术报告",
                status="待读",
                priority=84 if cited >= 500 else 74 if cited >= 50 else 64,
                source="Semantic Scholar API",
                value=f"{paper.get('year', 'n.d.')}；{paper.get('venue', '未知 venue')}；citations={cited}；{shorten(paper.get('abstract', ''))}",
                reason="Semantic Scholar 公开检索结果，适合发现高引用论文和相关工作线索。",
            ),
        )
    return candidates, []


def write_outputs(workspace: Path, topic: str, candidates: list[Candidate], errors: list[str]) -> None:
    out_dir = workspace / "自动发现"
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl = out_dir / "候选资料.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for item in sorted(candidates, key=lambda c: c.priority, reverse=True):
            f.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")

    md = out_dir / "候选资料.md"
    rows = []
    for item in sorted(candidates, key=lambda c: c.priority, reverse=True):
        rows.append(
            f"| {md_cell(item.type)} | {md_cell(item.name)} | {item.priority} | {md_cell(item.evidence)} | "
            f"{md_cell(item.status)} | {md_cell(item.source)} | {md_cell(item.url)} | {md_cell(item.value)} | {md_cell(item.reason)} |"
        )
    error_block = "\n".join(f"- {error}" for error in errors) if errors else "- 无"
    md.write_text(
        f"""# 候选资料

## 主题

{topic}

## 候选列表

| 类型 | 名称 | 优先级 | 证据等级 | 阅读状态 | 来源 | 链接 | 信号 | 入选原因 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## 获取失败/待验证

{error_block}

## 使用提醒

- 这是自动发现结果，不等于正式结论。
- 先用它建立广度地图，再选择少量高价值来源深读。
- `D-待验证` 条目必须回到官方文档、论文正文或源码后才能进入正式判断。
""",
        encoding="utf-8",
    )
    print(md)


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover candidate sources for deep research.")
    parser.add_argument("topic")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--max-github", type=int, default=12)
    parser.add_argument("--max-arxiv", type=int, default=10)
    parser.add_argument("--max-openalex", type=int, default=8)
    parser.add_argument("--max-crossref", type=int, default=8)
    parser.add_argument("--max-semantic-scholar", type=int, default=8)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    candidates: list[Candidate] = []
    errors: list[str] = []
    seen: set[str] = set()

    for item in generated_search_candidates(args.topic):
        add_unique(candidates, seen, item)

    github_items, github_errors = github_candidates(args.topic, args.max_github)
    arxiv_items, arxiv_errors = arxiv_candidates(args.topic, args.max_arxiv)
    openalex_items, openalex_errors = openalex_candidates(args.topic, args.max_openalex)
    crossref_items, crossref_errors = crossref_candidates(args.topic, args.max_crossref)
    semantic_items, semantic_errors = semantic_scholar_candidates(args.topic, args.max_semantic_scholar)
    errors.extend(github_errors)
    errors.extend(arxiv_errors)
    errors.extend(openalex_errors)
    errors.extend(crossref_errors)
    errors.extend(semantic_errors)
    for item in github_items + arxiv_items + openalex_items + crossref_items + semantic_items:
        add_unique(candidates, seen, item)

    write_outputs(workspace, args.topic, candidates, errors)


if __name__ == "__main__":
    main()
