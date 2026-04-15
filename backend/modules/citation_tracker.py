"""Reference parser and citation fetcher for arXiv-backed citation workflows."""

import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus, urlparse

import requests

from config import ARXIV_MAX_RESULTS

logger = logging.getLogger(__name__)


@dataclass
class CitationInfo:
    ref_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[str] = None
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    fetched: bool = False
    fetch_error: Optional[str] = None


class CitationTracker:
    ARXIV_API = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.citations: list[CitationInfo] = []
        raw_hosts = os.environ.get(
            "CITATION_PDF_ALLOWLIST",
            "arxiv.org,export.arxiv.org,patents.google.com,www.kipris.or.kr,kipris.or.kr",
        )
        self.allowed_pdf_hosts = {
            host.strip().lower() for host in raw_hosts.split(",") if host.strip()
        }

    def parse_references(self, reference_text: str) -> list[CitationInfo]:
        citations: list[CitationInfo] = []
        entries = re.split(r"\n\s*(?=\[\d+\]|\d+[.)])", reference_text.strip())

        ref_num = 0
        for entry in entries:
            item = entry.strip()
            if len(item) < 10:
                continue
            ref_num += 1
            parsed = self._parse_single_reference(item, str(ref_num))
            if parsed is not None:
                citations.append(parsed)

        self.citations = citations
        logger.info("Parsed %s references", len(citations))
        return citations

    def _parse_single_reference(self, text: str, ref_id: str) -> Optional[CitationInfo]:
        normalized = re.sub(r"^\[?\d+[\].)]?\s*", "", text).strip()
        if not normalized:
            return None

        arxiv_match = re.search(
            r"arXiv[:\s]*(\d{4}\.\d{4,5})", normalized, re.IGNORECASE
        )
        arxiv_id = arxiv_match.group(1) if arxiv_match else None

        year_match = re.search(r"\((\d{4})\)|,\s*(\d{4})", normalized)
        year = (year_match.group(1) or year_match.group(2)) if year_match else None

        author_match = re.match(r"^(.+?)[.,]", normalized)
        authors = [author_match.group(1).strip()] if author_match else []

        title_match = re.search(r"[\"“](.+?)[\"”]", normalized)
        if title_match:
            title = title_match.group(1).strip()
        else:
            parts = normalized.split(".", 2)
            title = parts[1].strip() if len(parts) > 1 else normalized[:160]

        return CitationInfo(
            ref_id=ref_id,
            title=title,
            authors=authors,
            year=year,
            arxiv_id=arxiv_id,
        )

    def fetch_from_arxiv(
        self, citation: CitationInfo, max_results: int = 1
    ) -> Optional[CitationInfo]:
        try:
            query = (
                f"id:{citation.arxiv_id}"
                if citation.arxiv_id
                else f"ti:{quote_plus(citation.title[:100])}"
            )
            params = {"search_query": query, "start": 0, "max_results": max_results}

            response = requests.get(self.ARXIV_API, params=params, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)
            if not entries:
                citation.fetch_error = "arxiv_not_found"
                return citation

            entry = entries[0]
            citation.title = entry.findtext("atom:title", citation.title, ns).strip()
            citation.abstract = entry.findtext("atom:summary", "", ns).strip()

            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    citation.pdf_url = link.get("href")
                    break

            arxiv_id_text = entry.findtext("atom:id", "", ns)
            if arxiv_id_text:
                id_match = re.search(r"(\d{4}\.\d{4,5})", arxiv_id_text)
                if id_match:
                    citation.arxiv_id = id_match.group(1)

            authors = entry.findall("atom:author", ns)
            citation.authors = [a.findtext("atom:name", "", ns) for a in authors]
            citation.fetched = True
            return citation
        except Exception as exc:
            logger.warning("arXiv fetch failed for '%s': %s", citation.title, exc)
            citation.fetch_error = f"fetch_failed: {exc}"
            return citation

    def fetch_all_citations(
        self, max_total: int = ARXIV_MAX_RESULTS, delay: float = 1.0
    ) -> list[CitationInfo]:
        fetched: list[CitationInfo] = []
        for citation in self.citations[:max_total]:
            result = self.fetch_from_arxiv(citation)
            if result is not None:
                fetched.append(result)
            time.sleep(delay)

        logger.info(
            "Fetched %s/%s citations from arXiv", len(fetched), len(self.citations)
        )
        return fetched

    def download_pdf(self, citation: CitationInfo, output_dir: str) -> Optional[str]:
        if not citation.pdf_url:
            return None

        try:
            parsed = urlparse(citation.pdf_url)
            host = (parsed.hostname or "").lower()
            if parsed.scheme not in {"http", "https"}:
                logger.warning("Rejected non-http citation URL: %s", citation.pdf_url)
                return None
            if host not in self.allowed_pdf_hosts:
                logger.warning("Rejected citation host outside allowlist: %s", host)
                return None

            head = requests.head(citation.pdf_url, timeout=10, allow_redirects=False)
            head.raise_for_status()
            content_type = (head.headers.get("Content-Type") or "").lower()
            if "application/pdf" not in content_type:
                logger.warning(
                    "Rejected non-pdf citation content type: %s", content_type
                )
                return None

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            filename = f"{citation.arxiv_id or citation.ref_id}.pdf"
            filepath = output_path / filename

            response = requests.get(citation.pdf_url, timeout=30, allow_redirects=False)
            response.raise_for_status()
            if not response.content.startswith(b"%PDF-"):
                logger.warning("Downloaded citation does not have PDF signature")
                return None

            filepath.write_bytes(response.content)
            logger.info("Downloaded citation PDF: %s", filepath)
            return str(filepath)
        except Exception as exc:
            logger.warning("PDF download failed for '%s': %s", citation.title, exc)
            return None

    def get_citation_summary(self) -> list[dict]:
        return [
            {
                "ref_id": c.ref_id,
                "title": c.title,
                "authors": ", ".join(c.authors[:3]),
                "year": c.year,
                "arxiv_id": c.arxiv_id,
                "fetched": c.fetched,
                "has_pdf": c.pdf_url is not None,
                "fetch_error": c.fetch_error,
            }
            for c in self.citations
        ]
