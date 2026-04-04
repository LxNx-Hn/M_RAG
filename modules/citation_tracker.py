"""
MODULE 11: Citation Tracker
Reference 파싱 → 인용 논문 자동 수집 (arXiv API)
기반 논문: GraphRAG [9], HippoRAG2 [27]
"""
import logging
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import quote_plus

import requests

from config import ARXIV_MAX_RESULTS

logger = logging.getLogger(__name__)


@dataclass
class CitationInfo:
    """파싱된 인용 정보"""
    ref_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[str] = None
    arxiv_id: Optional[str] = None
    pdf_url: Optional[str] = None
    abstract: Optional[str] = None
    fetched: bool = False


class CitationTracker:
    """인용 논문 파싱 + arXiv API 수집"""

    ARXIV_API = "http://export.arxiv.org/api/query"

    def __init__(self):
        self.citations: list[CitationInfo] = []

    def parse_references(self, reference_text: str) -> list[CitationInfo]:
        """Reference 섹션 텍스트에서 인용 정보 추출"""
        citations = []

        # 줄 단위 분리 후 [번호] 또는 번호. 패턴으로 항목 구분
        entries = re.split(r'\n\s*(?=\[\d+\]|\d+[\.\)])', reference_text.strip())

        ref_num = 0
        for entry in entries:
            entry = entry.strip()
            if len(entry) < 10:
                continue

            ref_num += 1
            citation = self._parse_single_reference(entry, str(ref_num))
            if citation:
                citations.append(citation)

        self.citations = citations
        logger.info(f"Parsed {len(citations)} references")
        return citations

    def _parse_single_reference(self, text: str, ref_id: str) -> Optional[CitationInfo]:
        """단일 참고문헌 항목 파싱"""
        # 번호 제거
        text = re.sub(r'^\[?\d+[\].]?\s*', '', text).strip()

        # arXiv ID 추출
        arxiv_match = re.search(r'arXiv[:\s]*(\d{4}\.\d{4,5})', text)
        arxiv_id = arxiv_match.group(1) if arxiv_match else None

        # 연도 추출
        year_match = re.search(r'\((\d{4})\)|,\s*(\d{4})', text)
        year = (year_match.group(1) or year_match.group(2)) if year_match else None

        # 저자 추출 (첫 번째 콤마 또는 마침표까지)
        author_match = re.match(r'^(.+?)[.,]', text)
        authors = [author_match.group(1).strip()] if author_match else []

        # 제목 추출 (따옴표 안이나 이탤릭체)
        title_match = re.search(r'["""](.+?)["""]|["""](.+?)["""]', text)
        if title_match:
            title = (title_match.group(1) or title_match.group(2)).strip()
        else:
            # 저자 뒤의 첫 문장을 제목으로 추정
            parts = text.split(".", 2)
            title = parts[1].strip() if len(parts) > 1 else text[:100]

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
        """arXiv API로 논문 메타데이터 + PDF URL 가져오기"""
        try:
            if citation.arxiv_id:
                query = f"id:{citation.arxiv_id}"
            else:
                query = f"ti:{quote_plus(citation.title[:100])}"

            params = {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
            }

            response = requests.get(self.ARXIV_API, params=params, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            entries = root.findall("atom:entry", ns)
            if not entries:
                return None

            entry = entries[0]
            citation.title = entry.findtext("atom:title", citation.title, ns).strip()
            citation.abstract = entry.findtext("atom:summary", "", ns).strip()

            # PDF URL
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    citation.pdf_url = link.get("href")
                    break

            # arXiv ID
            arxiv_id_text = entry.findtext("atom:id", "", ns)
            if arxiv_id_text:
                id_match = re.search(r'(\d{4}\.\d{4,5})', arxiv_id_text)
                if id_match:
                    citation.arxiv_id = id_match.group(1)

            # 저자
            authors = entry.findall("atom:author", ns)
            citation.authors = [
                a.findtext("atom:name", "", ns) for a in authors
            ]

            citation.fetched = True
            return citation

        except Exception as e:
            logger.warning(f"arXiv fetch failed for '{citation.title}': {e}")
            return None

    def fetch_all_citations(
        self, max_total: int = ARXIV_MAX_RESULTS, delay: float = 1.0
    ) -> list[CitationInfo]:
        """모든 인용 논문 일괄 수집 (rate limit 고려)"""
        fetched = []
        for citation in self.citations[:max_total]:
            result = self.fetch_from_arxiv(citation)
            if result:
                fetched.append(result)
            time.sleep(delay)  # arXiv rate limit

        logger.info(f"Fetched {len(fetched)}/{len(self.citations)} citations from arXiv")
        return fetched

    def download_pdf(self, citation: CitationInfo, output_dir: str) -> Optional[str]:
        """인용 논문 PDF 다운로드"""
        if not citation.pdf_url:
            return None

        try:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            filename = f"{citation.arxiv_id or citation.ref_id}.pdf"
            filepath = output_path / filename

            response = requests.get(citation.pdf_url, timeout=30)
            response.raise_for_status()

            filepath.write_bytes(response.content)
            logger.info(f"Downloaded: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.warning(f"PDF download failed for '{citation.title}': {e}")
            return None

    def get_citation_summary(self) -> list[dict]:
        """인용 정보 요약 (UI 표시용)"""
        return [
            {
                "ref_id": c.ref_id,
                "title": c.title,
                "authors": ", ".join(c.authors[:3]),
                "year": c.year,
                "arxiv_id": c.arxiv_id,
                "fetched": c.fetched,
                "has_pdf": c.pdf_url is not None,
            }
            for c in self.citations
        ]
