#!/usr/bin/env python3
"""Create paper metadata, queue entry, and note skeleton for real-search."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from workspace_layout import process_path


USER_AGENT = "real-search-skill/0.2"


@dataclass
class PaperMeta:
    title: str
    url: str
    pdf_url: str
    authors: list[str]
    published: str
    summary: str
    citation: str
    source_status: str


@dataclass
class PdfInspection:
    status: str
    quality: str
    page_count: int | None
    size_bytes: int
    notes: list[str]


@dataclass
class TextExtraction:
    path: Path | None
    sections: list[str]
    status: str
    quality: str
    char_count: int
    notes: list[str]


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value.strip())
    value = re.sub(r"\s+", "-", value)
    return value.strip("-")[:120] or "未命名论文"


def md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    return fetch_bytes(url, timeout=timeout).decode("utf-8", errors="replace")


def arxiv_id(value: str) -> str | None:
    match = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})(?:v\d+)?", value, re.I)
    if match:
        return match.group(1)
    match = re.fullmatch(r"[0-9]{4}\.[0-9]{4,5}(?:v\d+)?", value.strip())
    return match.group(0) if match else None


def arxiv_meta(value: str) -> PaperMeta | None:
    paper_id = arxiv_id(value)
    if not paper_id:
        return None
    api = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(paper_id)}"
    try:
        root = ET.fromstring(fetch_text(api))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError):
        return PaperMeta(
            title=f"arXiv {paper_id}",
            url=f"https://arxiv.org/abs/{paper_id}",
            pdf_url=f"https://arxiv.org/pdf/{paper_id}",
            authors=[],
            published="",
            summary="",
            citation=f"arXiv:{paper_id}",
            source_status="arXiv 元数据获取失败，仅保留 ID 和 PDF 链接。",
        )

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return None
    title = " ".join((entry.findtext("atom:title", default="", namespaces=ns) or "").split())
    authors = [
        " ".join((author.findtext("atom:name", default="", namespaces=ns) or "").split())
        for author in entry.findall("atom:author", ns)
    ]
    published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
    summary = " ".join((entry.findtext("atom:summary", default="", namespaces=ns) or "").split())
    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    year = published[:4] if published else "n.d."
    first_author = authors[0].split()[-1] if authors else "Unknown"
    return PaperMeta(
        title=title or f"arXiv {paper_id}",
        url=f"https://arxiv.org/abs/{paper_id}",
        pdf_url=pdf_url,
        authors=authors,
        published=published,
        summary=summary,
        citation=f"{first_author} et al., {year}, arXiv:{paper_id}",
        source_status="arXiv 元数据已获取。",
    )


def generic_meta(value: str, title: str | None) -> PaperMeta:
    path = Path(value).expanduser()
    is_pdf_url = value.lower().startswith(("http://", "https://")) and value.lower().split("?")[0].endswith(".pdf")
    inferred_title = title or (path.stem if path.exists() else value.rstrip("/").split("/")[-1] or "未命名论文")
    return PaperMeta(
        title=inferred_title,
        url=value,
        pdf_url=value if is_pdf_url or path.exists() else "",
        authors=[],
        published="",
        summary="",
        citation=f"{inferred_title}, 待补充引用信息",
        source_status="非 arXiv 来源，元数据需人工/Codex 补全。",
    )


def ensure_queue(workspace: Path) -> Path:
    queue = process_path(workspace, "论文阅读队列.md")
    if not queue.exists():
        queue.write_text(
            """# 论文阅读队列

| 状态 | 标题 | 链接 | PDF/本地路径 | 引用 | 备注 |
| --- | --- | --- | --- | --- | --- |
""",
            encoding="utf-8",
        )
    return queue


def append_queue(queue: Path, meta: PaperMeta, pdf_path: Path | None) -> None:
    append_queue_with_status(queue, meta, pdf_path, meta.source_status, "待抽取")


def append_queue_with_status(queue: Path, meta: PaperMeta, pdf_path: Path | None, pdf_status: str, text_quality: str) -> None:
    text = queue.read_text(encoding="utf-8")
    if meta.url and meta.url in text:
        return
    pdf_cell = str(pdf_path) if pdf_path else meta.pdf_url
    remark = f"{meta.source_status}；PDF：{pdf_status}；正文：{text_quality}"
    row = (
        f"| 待读 | {md_cell(meta.title)} | {md_cell(meta.url)} | {md_cell(pdf_cell)} | "
        f"{md_cell(meta.citation)} | {md_cell(remark)} |\n"
    )
    with queue.open("a", encoding="utf-8") as f:
        f.write(row)


def get_pdf(meta: PaperMeta, workspace: Path) -> tuple[Path | None, str]:
    pdf_dir = process_path(workspace, "论文PDF")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    local = Path(meta.pdf_url).expanduser()
    if local.exists():
        return local.resolve(), "使用本地 PDF。"
    if meta.pdf_url.lower().startswith(("http://", "https://")):
        target = pdf_dir / f"{safe_name(meta.title)}.pdf"
        if target.exists():
            return target, "PDF 已存在。"
        try:
            target.write_bytes(fetch_bytes(meta.pdf_url, timeout=60))
            return target, "PDF 已下载。"
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            return None, f"PDF 下载失败：{exc}"
    return None, "没有可下载 PDF 链接。"


def inspect_pdf(pdf_path: Path | None) -> PdfInspection:
    if not pdf_path:
        return PdfInspection(
            status="缺少 PDF，待人工补充。",
            quality="待人工阅读",
            page_count=None,
            size_bytes=0,
            notes=["没有可检查的 PDF 文件。"],
        )

    notes: list[str] = []
    if not pdf_path.exists():
        return PdfInspection(
            status="PDF 路径不存在，待人工补充。",
            quality="待人工阅读",
            page_count=None,
            size_bytes=0,
            notes=[str(pdf_path)],
        )

    size = pdf_path.stat().st_size
    if size < 512:
        notes.append(f"文件大小异常小：{size} bytes。")

    try:
        with pdf_path.open("rb") as f:
            header = f.read(5)
    except OSError as exc:
        return PdfInspection(
            status=f"PDF 读取失败：{exc}",
            quality="待人工阅读",
            page_count=None,
            size_bytes=size,
            notes=notes,
        )

    if header != b"%PDF-":
        notes.append("文件头不是 %PDF-，可能不是标准 PDF。")

    page_count: int | None = None
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        try:
            result = subprocess.run([pdfinfo, str(pdf_path)], check=True, capture_output=True, text=True)
            match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.M)
            if match:
                page_count = int(match.group(1))
        except subprocess.CalledProcessError as exc:
            notes.append(f"pdfinfo 读取失败：{exc.stderr.strip() or exc}")
    else:
        notes.append("本机未发现 pdfinfo，跳过页数检查。")

    if header != b"%PDF-" or size < 512:
        quality = "疑似损坏/待人工阅读"
    else:
        quality = "PDF 文件可检查"

    status = "PDF 基础检查完成。"
    if notes:
        status += " " + "；".join(notes)
    return PdfInspection(status=status, quality=quality, page_count=page_count, size_bytes=size, notes=notes)


def classify_text_quality(char_count: int, section_count: int) -> str:
    if char_count < 200:
        return "疑似扫描版/待 OCR"
    if char_count < 1000 or section_count < 2:
        return "抽取质量低/需复核"
    return "正常"


def extract_text(pdf_path: Path | None, workspace: Path, title: str) -> TextExtraction:
    if not pdf_path:
        return TextExtraction(None, [], "未抽取正文：缺少 PDF。", "待人工阅读", 0, ["缺少 PDF。"])
    binary = shutil.which("pdftotext")
    if not binary:
        return TextExtraction(None, [], "未抽取正文：本机未发现 pdftotext。", "待抽取", 0, ["可安装 poppler/pdftotext 后重试。"])
    text_dir = process_path(workspace, "论文正文")
    text_dir.mkdir(parents=True, exist_ok=True)
    target = text_dir / f"{safe_name(title)}.txt"
    try:
        subprocess.run([binary, "-layout", str(pdf_path), str(target)], check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or exc)
        return TextExtraction(None, [], f"pdftotext 抽取失败：{detail.strip()}", "待人工阅读", 0, [detail.strip()])
    text = target.read_text(encoding="utf-8", errors="replace")
    sections = detect_sections(text)
    char_count = len(text.strip())
    quality = classify_text_quality(char_count, len(sections))
    status = f"PDF 正文已抽取：{char_count} 字符，识别章节 {len(sections)} 个。"
    notes = []
    if quality != "正常":
        notes.append("抽取结果需要人工/Codex 复核，不应直接视为已完整阅读。")
    return TextExtraction(target, sections, status, quality, char_count, notes)


def detect_sections(text: str) -> list[str]:
    sections: list[str] = []
    pattern = re.compile(r"^\s*(?:\d+(?:\.\d+)*\s+)?([A-Z][A-Za-z][A-Za-z \-/]{2,80})\s*$")
    common = {"abstract", "introduction", "related work", "method", "methods", "experiments", "evaluation", "conclusion", "references"}
    for line in text.splitlines():
        clean = " ".join(line.strip().split())
        lower = clean.lower()
        if lower in common or pattern.match(clean):
            if clean not in sections:
                sections.append(clean)
        if len(sections) >= 24:
            break
    return sections


def write_note(workspace: Path, meta: PaperMeta, pdf_path: Path | None, pdf_info: PdfInspection, extraction: TextExtraction, pdf_status: str) -> Path:
    note_dir = process_path(workspace, "论文调研记录")
    note_dir.mkdir(parents=True, exist_ok=True)
    note = note_dir / f"{safe_name(meta.title)}论文笔记.md"
    text_path = extraction.path
    sections = extraction.sections
    section_lines = "\n".join(f"- {section}" for section in sections) if sections else "- 待阅读正文后补充"
    authors = "、".join(meta.authors) if meta.authors else "待补充"
    page_count = pdf_info.page_count if pdf_info.page_count is not None else "待补充"
    pending_lines = "\n".join(
        f"- {item}" for item in [
            pdf_status,
            pdf_info.status,
            extraction.status,
            *pdf_info.notes,
            *extraction.notes,
        ] if item
    )
    if not note.exists():
        note.write_text(
            f"""# {meta.title}论文笔记

## 元数据

| 字段 | 内容 |
| --- | --- |
| 标题 | {meta.title} |
| 作者 | {authors} |
| 日期 | {meta.published or '待补充'} |
| 链接 | {meta.url} |
| PDF | {pdf_path or meta.pdf_url or '待补充'} |
| PDF 处理状态 | {pdf_info.status} |
| PDF 页数 | {page_count} |
| 正文抽取 | {text_path or '待抽取'} |
| 正文字符数 | {extraction.char_count} |
| 正文抽取质量 | {extraction.quality} |
| 引用 | {meta.citation} |
| 状态 | 待读 |

## 摘要/来源说明

{meta.summary or meta.source_status}

## 章节骨架

{section_lines}

## 解决的问题

## 方法结构

## 实验与结论

## 工程启发

## 关联代码/项目

## 局限

## 和当前目标的关系

## 不确定/待验证

{pending_lines or '- 待阅读正文后补充'}
""",
            encoding="utf-8",
        )
    return note


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a paper URL/PDF for real-search.")
    parser.add_argument("paper")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    meta = arxiv_meta(args.paper) or generic_meta(args.paper, args.title)
    pdf_path, pdf_status = get_pdf(meta, workspace)
    pdf_info = inspect_pdf(pdf_path)
    extraction = extract_text(pdf_path, workspace, meta.title)
    queue = ensure_queue(workspace)
    append_queue_with_status(queue, meta, pdf_path, pdf_info.quality, extraction.quality)
    note = write_note(workspace, meta, pdf_path, pdf_info, extraction, pdf_status)
    print(note)


if __name__ == "__main__":
    main()
