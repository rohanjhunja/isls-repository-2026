import os
import re
import json
import logging
import html as html_module
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
from curl_cffi import requests

from proceedings_ingest.models import GroundTruthPaper, GroundTruthRegistry

logger = logging.getLogger(__name__)

BASE_URL = "https://repository.isls.org"

COLLECTIONS = {
    2016: [("/handle/1/98", "ICLS 2016")],
    2017: [("/handle/1/191", "CSCL 2017")],
    2018: [("/handle/1/473", "ICLS 2018")],
    2019: [("/handle/1/1546", "CSCL 2019")],
    2020: [("/handle/1/6286", "ICLS 2020")],
    2021: [("/handle/1/7295", "ISLS Annual Meeting 2021")],
    2022: [("/handle/1/8262", "ISLS Annual Meeting 2022")],
    2023: [("/handle/1/9088", "ISLS Annual Meeting 2023")],
    2024: [("/handle/1/10493", "ISLS Annual Meeting 2024")],
    2025: [("/handle/1/11211", "ISLS Annual Meeting 2025"), ("/handle/1/11210", "ICLS 2025")],
}


def parse_page_range(citation: str, pdf_url: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract start and end page numbers from citation text or PDF filename."""
    if citation:
        m = re.search(r'pp?\.\s*(\d+)\s*[-–—]\s*(\d+)', citation, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(2))
        m_single = re.search(r'pp?\.\s*(\d+)', citation, re.IGNORECASE)
        if m_single:
            p = int(m_single.group(1))
            return p, p

    if pdf_url:
        m_pdf = re.search(r'_(\d+)[-_](\d+)\.pdf', pdf_url, re.IGNORECASE)
        if m_pdf:
            return int(m_pdf.group(1)), int(m_pdf.group(2))

    return None, None


def parse_paper_type(title: str, citation: str, start_page: Optional[int], end_page: Optional[int]) -> str:
    """Infer paper type (Full Paper, Short Paper, Poster, Symposium, Workshop)."""
    text = f"{title} {citation}".lower()
    if "symposium" in text:
        return "Symposium"
    if "poster" in text:
        return "Poster"
    if "workshop" in text:
        return "Workshop"
    if "short paper" in text:
        return "Short Paper"

    if start_page is not None and end_page is not None:
        num_pages = end_page - start_page + 1
        if num_pages >= 6:
            return "Full Paper"
        elif num_pages in [3, 4, 5]:
            return "Short Paper"
        elif num_pages in [1, 2]:
            return "Poster / Short Note"

    return "Paper"


class DSpaceHarvester:
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session(impersonate="chrome120")

    def harvest_collection_item_handles(self, collection_handle: str) -> List[str]:
        """Harvest all item handle paths for a given collection handle."""
        items: List[str] = []
        offset = 0
        while True:
            url = f"{BASE_URL}{collection_handle}?offset={offset}"
            try:
                r = self.session.get(url, timeout=15)
                if r.status_code != 200:
                    logger.error(f"Failed to fetch {url}: HTTP {r.status_code}")
                    break

                page_items = re.findall(r'href=\"(/handle/1/(\d+))\"', r.text)
                new_handles = [h for h, _ in page_items if h != collection_handle]
                unique_new = [h for h in new_handles if h not in items]

                if not unique_new:
                    break

                items.extend(unique_new)
                logger.info(f"Collection {collection_handle} offset {offset}: found {len(unique_new)} new items (total: {len(items)})")
                offset += 20

                if f"offset={offset}" not in r.text:
                    break
            except Exception as e:
                logger.error(f"Error fetching collection page {url}: {e}")
                break

        return items

    def harvest_item_metadata(self, handle_path: str, default_year: int, default_conf: str) -> Optional[GroundTruthPaper]:
        """Fetch and parse metadata for a single item handle page."""
        url = f"{BASE_URL}{handle_path}"
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code != 200:
                logger.error(f"Failed to fetch item {url}: HTTP {r.status_code}")
                return None

            html = r.text

            # Title extraction & unescaping
            raw_title = re.search(r'<meta\s+name=\"DC\.title\"\s+content=\"([^\"]+)\"', html)
            if not raw_title:
                raw_title = re.search(r'<title>([^<]+)</title>', html)
            
            title = ""
            if raw_title:
                title = raw_title.group(1).replace("&#x20;", " ").strip()
                title = html_module.unescape(title)

            if not title:
                logger.warning(f"No title found for item {handle_path}")
                return None

            # Authors
            authors = [html_module.unescape(a.strip()) for a in re.findall(r'<meta\s+name=\"DC\.creator\"\s+content=\"([^\"]+)\"', html)]

            # Issued year
            year_match = re.search(r'<meta\s+name=\"DCTERMS\.issued\"\s+content=\"(\d{4})[^\"]*\"', html)
            year = int(year_match.group(1)) if year_match else default_year

            # Bibliographic citation
            cit_match = re.search(r'<meta\s+name=\"DCTERMS\.bibliographicCitation\"\s+content=\"([^\"]+)\"', html)
            citation = html_module.unescape(cit_match.group(1)).strip() if cit_match else None

            # DOI
            doi_match = re.search(r'https?://doi\.org/([^\"]+)', html)
            doi = doi_match.group(1) if doi_match else None

            # Abstract
            abstract_match = re.search(r'<meta\s+name=\"(?:DCTERMS\.abstract|DC\.description\.abstract|description)\"\s+content=\"([^\"]+)\"', html, re.IGNORECASE)
            abstract = html_module.unescape(abstract_match.group(1)).strip() if abstract_match else None

            # PDF Bitstream URL
            pdf_match = re.search(r'href=\"([^\"]*bitstream/1/[^\"]+\.pdf[^\"]*)\"', html)
            pdf_url = f"{BASE_URL}{pdf_match.group(1)}" if pdf_match else None

            # Pages & paper type
            start_page, end_page = parse_page_range(citation or "", pdf_url or "")
            paper_type = parse_paper_type(title, citation or "", start_page, end_page)

            clean_handle = handle_path.lstrip("/handle/")
            paper_id = f"handle_{clean_handle.replace('/', '_')}"

            return GroundTruthPaper(
                id=paper_id,
                handle=clean_handle,
                handle_url=url,
                title=title,
                authors=authors,
                year=year,
                conference=default_conf,
                doi=doi,
                citation=citation,
                start_page=start_page,
                end_page=end_page,
                paper_type=paper_type,
                abstract=abstract,
                pdf_url=pdf_url,
            )
        except Exception as e:
            logger.error(f"Error parsing item {handle_path}: {e}")
            return None

    def harvest_all_years(self, years: Optional[List[int]] = None) -> GroundTruthRegistry:
        """Harvest ground truth registry across specified years."""
        if years is None:
            years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
        all_papers: List[GroundTruthPaper] = []
        papers_by_year: Dict[int, int] = {}

        for year in years:
            collections_list = COLLECTIONS.get(year, [])
            year_papers: List[GroundTruthPaper] = []
            for handle_path, conf_name in collections_list:
                logger.info(f"Harvesting handles for {conf_name} ({handle_path})...")
                item_handles = self.harvest_collection_item_handles(handle_path)
                logger.info(f"Found {len(item_handles)} item handles in {conf_name}. Extracting metadata...")

                for idx, item_handle in enumerate(item_handles):
                    p = self.harvest_item_metadata(item_handle, year, conf_name)
                    if p:
                        year_papers.append(p)
                    if (idx + 1) % 50 == 0:
                        logger.info(f"Processed {idx + 1}/{len(item_handles)} items for {conf_name}")

            papers_by_year[year] = len(year_papers)
            all_papers.extend(year_papers)
            logger.info(f"Finished Year {year}: harvested {len(year_papers)} valid paper metadata records.")

        registry = GroundTruthRegistry(
            created_at=datetime.now(timezone.utc).isoformat(),
            total_papers=len(all_papers),
            papers_by_year=papers_by_year,
            papers=all_papers,
        )
        return registry


def save_ground_truth_registry(registry: GroundTruthRegistry, output_path: str = "data/derived/ground_truth_registry.json") -> str:
    """Save GroundTruthRegistry to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(registry.model_dump_json(indent=2))
    logger.info(f"Saved ground-truth registry to {output_path} ({registry.total_papers} papers)")
    return output_path
