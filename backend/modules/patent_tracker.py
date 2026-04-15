"""
MODULE 11B: Patent Tracker
특허 인용/유사 특허 추적 모듈
Google Patents 공개 페이지 파싱 + KIPRIS API (선택적)

CitationTracker와 동일한 설계 패턴:
  parse_cited_patents() → fetch_from_google_patents() → download_pdf()
"""

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests

from config import GOOGLE_PATENTS_BASE, KIPRIS_API_KEY

logger = logging.getLogger(__name__)

# 특허 번호 정규식 (KR/US/JP/EP/WO)
_PATENT_NUMBER_RE = re.compile(
    r"(?P<country>KR|US|JP|EP|WO|CN|DE|FR|GB)"
    r"[\s\-]?"
    r"(?P<number>[\d\-,\.]+(?:[A-Z]\d?)?)"
)


@dataclass
class PatentInfo:
    """파싱된 특허 정보"""

    patent_id: str  # "KR10-2020-0012345" 등
    title: str = ""
    inventors: list[str] = field(default_factory=list)
    applicant: str = ""
    publication_date: str = ""
    abstract: str = ""
    pdf_url: str = ""
    fetched: bool = False
    fetch_error: Optional[str] = None


class PatentTracker:
    """특허 인용/유사 특허 추적"""

    def __init__(self):
        self.patents: list[PatentInfo] = []

    def parse_cited_patents(self, cited_text: str) -> list[PatentInfo]:
        """인용 특허/선행기술 섹션에서 특허 번호 추출

        지원 형식:
          - KR 10-2020-0012345
          - US 10,000,000
          - US2020/0123456A1
          - JP 2019-123456
          - EP 3123456
          - WO 2020/123456
        """
        patents = []
        seen = set()

        for match in _PATENT_NUMBER_RE.finditer(cited_text):
            country = match.group("country")
            number = match.group("number").replace(",", "").replace(" ", "")
            patent_id = f"{country}{number}"

            if patent_id in seen:
                continue
            seen.add(patent_id)

            # 특허 번호 주변 텍스트에서 제목 추출 시도
            start = max(0, match.start() - 5)
            end = min(len(cited_text), match.end() + 200)
            context = cited_text[start:end]

            title = self._extract_title_from_context(context, patent_id)

            patents.append(
                PatentInfo(
                    patent_id=patent_id,
                    title=title,
                )
            )

        self.patents = patents
        logger.info(f"Parsed {len(patents)} cited patents")
        return patents

    def _extract_title_from_context(self, context: str, patent_id: str) -> str:
        """특허 번호 주변에서 제목 추출 시도"""
        # 특허 번호 뒤의 텍스트에서 따옴표 내용이나 첫 문장 추출
        after_id = (
            context.split(patent_id, 1)[-1].strip() if patent_id in context else context
        )
        # 따옴표로 묶인 제목
        title_match = re.search(r'["""\'](.+?)["""\']', after_id)
        if title_match:
            return title_match.group(1).strip()[:200]
        # 첫 구/절을 제목으로
        first_part = after_id.split(".", 1)[0].strip()
        return first_part[:200] if first_part else patent_id

    def fetch_from_google_patents(self, patent: PatentInfo) -> PatentInfo:
        """Google Patents 공개 페이지에서 메타데이터 가져오기

        비공식 HTML 파싱이므로 구조 변경 시 실패 가능 → fetch_error로 표시.
        """
        url = f"{GOOGLE_PATENTS_BASE}/{patent.patent_id}"
        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; M-RAG/1.0; academic research)"
                },
            )

            if response.status_code == 404:
                patent.fetch_error = "patent_not_found"
                return patent

            response.raise_for_status()

            # BeautifulSoup로 파싱 시도
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")

                # 제목
                title_el = soup.find("span", {"itemprop": "title"})
                if title_el:
                    patent.title = title_el.get_text(strip=True)

                # 초록
                abstract_el = soup.find("div", {"class": "abstract"})
                if abstract_el:
                    patent.abstract = abstract_el.get_text(strip=True)[:1000]

                # 출원인
                applicant_el = soup.find("dd", {"itemprop": "assigneeOriginal"})
                if applicant_el:
                    patent.applicant = applicant_el.get_text(strip=True)

                # 발명자
                inventor_els = soup.find_all("dd", {"itemprop": "inventor"})
                patent.inventors = [el.get_text(strip=True) for el in inventor_els]

                # PDF 링크
                pdf_link = soup.find("a", href=re.compile(r"\.pdf$"))
                if pdf_link:
                    patent.pdf_url = pdf_link["href"]

                patent.fetched = True

            except ImportError:
                # BeautifulSoup 없으면 기본 메타데이터만
                patent.fetch_error = "beautifulsoup_not_installed"
                logger.warning(
                    "bs4 not installed — Google Patents HTML parsing skipped"
                )

        except requests.Timeout:
            patent.fetch_error = "timeout"
        except requests.HTTPError as e:
            patent.fetch_error = f"http_{e.response.status_code}"
        except Exception as e:
            patent.fetch_error = f"fetch_failed: {str(e)[:100]}"
            logger.warning(f"Google Patents fetch failed for {patent.patent_id}: {e}")

        return patent

    def fetch_from_kipris(self, patent: PatentInfo) -> PatentInfo:
        """KIPRIS Plus API에서 한국 특허 정보 가져오기 (API 키 필요)

        키 미설정 시 스킵.
        """
        if not KIPRIS_API_KEY:
            logger.debug("KIPRIS API key not configured — skipping")
            return patent

        try:
            # KIPRIS Plus REST API
            url = "http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/applicantNameSearchInfo"
            params = {
                "applicationNumber": patent.patent_id.replace("KR", "").replace(
                    "-", ""
                ),
                "accessKey": KIPRIS_API_KEY,
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            # XML 파싱 (KIPRIS는 XML 응답)
            import xml.etree.ElementTree as ET

            root = ET.fromstring(response.content)

            title_el = root.find(".//inventionTitle")
            if title_el is not None and title_el.text:
                patent.title = title_el.text

            applicant_el = root.find(".//applicantName")
            if applicant_el is not None and applicant_el.text:
                patent.applicant = applicant_el.text

            patent.fetched = True

        except Exception as e:
            logger.warning(f"KIPRIS fetch failed for {patent.patent_id}: {e}")

        return patent

    def search_similar_patents(
        self, claims_text: str, top_k: int = 5
    ) -> list[PatentInfo]:
        """청구항 키워드 기반 유사 특허 검색 (Google Patents 검색)

        청구항에서 핵심 키워드를 추출하여 Google Patents URL로 검색 결과 반환.
        실제 검색은 Google Patents 웹 검색에 의존 — HTML 파싱.
        """
        # 청구항에서 핵심 키워드 추출 (처음 300자에서)
        keywords = self._extract_keywords(claims_text[:300])
        if not keywords:
            return []

        query = " ".join(keywords[:5])
        search_url = (
            f"https://patents.google.com/?q={quote_plus(query)}&oq={quote_plus(query)}"
        )

        try:
            response = requests.get(
                search_url,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; M-RAG/1.0; academic research)"
                },
            )
            response.raise_for_status()

            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")

                results = []
                # Google Patents 검색 결과 파싱
                result_items = soup.find_all("search-result-item", limit=top_k)
                if not result_items:
                    # 대안 선택자
                    result_items = soup.find_all("article", limit=top_k)

                for item in result_items:
                    title_el = item.find("h3") or item.find("span", {"class": "title"})
                    id_el = item.find("a", href=re.compile(r"/patent/"))

                    patent_id = ""
                    if id_el:
                        href = id_el.get("href", "")
                        id_match = re.search(r"/patent/(\w+)", href)
                        if id_match:
                            patent_id = id_match.group(1)

                    results.append(
                        PatentInfo(
                            patent_id=patent_id or f"similar_{len(results)}",
                            title=title_el.get_text(strip=True) if title_el else "",
                            fetched=False,
                        )
                    )

                return results[:top_k]

            except ImportError:
                logger.warning("bs4 not installed — similar patent search unavailable")
                return []

        except Exception as e:
            logger.warning(f"Similar patent search failed: {e}")
            return []

    def _extract_keywords(self, text: str) -> list[str]:
        """텍스트에서 핵심 키워드 추출 (불용어 제거)"""
        # 한국어/영어 단어 추출
        words = re.findall(r"[가-힣]{2,}|[a-zA-Z]{3,}", text)

        # 기본 불용어
        stopwords = {
            "the",
            "and",
            "for",
            "are",
            "with",
            "that",
            "this",
            "from",
            "which",
            "has",
            "have",
            "been",
            "not",
            "but",
            "can",
            "will",
            "one",
            "more",
            "said",
            "each",
            "may",
            "also",
            "than",
            "상기",
            "하는",
            "있는",
            "위한",
            "따른",
            "의한",
            "포함하는",
            "구성된",
            "이루어진",
            "되는",
            "하여",
        }

        keywords = [w for w in words if w.lower() not in stopwords]
        # 빈도 기반 정렬
        from collections import Counter

        counter = Counter(keywords)
        return [word for word, _ in counter.most_common(10)]

    def fetch_all_patents(
        self, max_total: int = 5, delay: float = 1.0
    ) -> list[PatentInfo]:
        """모든 인용 특허 일괄 수집"""
        fetched = []
        for patent in self.patents[:max_total]:
            # 한국 특허는 KIPRIS 우선, 그 외는 Google Patents
            if patent.patent_id.startswith("KR") and KIPRIS_API_KEY:
                self.fetch_from_kipris(patent)
            if not patent.fetched:
                self.fetch_from_google_patents(patent)
            if patent.fetched:
                fetched.append(patent)
            time.sleep(delay)

        logger.info(f"Fetched {len(fetched)}/{len(self.patents)} patents")
        return fetched

    def download_pdf(self, patent: PatentInfo, output_dir: str) -> Optional[str]:
        """특허 PDF 다운로드"""
        if not patent.pdf_url:
            return None

        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            filename = f"{patent.patent_id}.pdf"
            filepath = output_path / filename

            response = requests.get(patent.pdf_url, timeout=30)
            response.raise_for_status()

            filepath.write_bytes(response.content)
            logger.info(f"Downloaded patent PDF: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.warning(f"Patent PDF download failed for {patent.patent_id}: {e}")
            return None

    def get_patent_summary(self) -> list[dict]:
        """특허 정보 요약 (UI 표시용)"""
        return [
            {
                "patent_id": p.patent_id,
                "title": p.title,
                "applicant": p.applicant,
                "inventors": ", ".join(p.inventors[:3]),
                "publication_date": p.publication_date,
                "fetched": p.fetched,
                "has_pdf": bool(p.pdf_url),
                "fetch_error": p.fetch_error,
            }
            for p in self.patents
        ]
