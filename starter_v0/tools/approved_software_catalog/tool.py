from __future__ import annotations

import json
from typing import Any

from tools._shared import ROOT, err, fold_text, terms


CATALOG_FILE = ROOT / "helpdesk_data" / "software_catalog.json"


def approved_software_catalog(query: str = "", category: str = "all") -> dict[str, Any]:
    """Tra cứu danh mục phần mềm được phê duyệt tại Northstar Labs.

    Parameters:
        query: Tên phần mềm hoặc từ khóa tìm kiếm (ví dụ 'docker', 'vscode', 'figma').
        category: Nhóm phần mềm ('all', 'developer', 'communication', 'productivity', 'design', 'security', 'utilities').
    """
    try:
        data = json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
        items = data.get("software_list", [])

        query_raw = (query or "").strip()
        query_terms = terms(query_raw)
        folded_query = fold_text(query_raw)
        category_filter = (category or "all").strip().lower()

        matched: list[dict[str, Any]] = []

        for item in items:
            item_category = item.get("category", "").lower()
            if category_filter != "all" and item_category != category_filter:
                continue

            if not query_raw:
                matched.append(item)
                continue

            name = item.get("name", "")
            aliases = item.get("aliases", [])
            notes = item.get("notes", "")

            # Match exact/substring
            combined_search_text = f"{name} {' '.join(aliases)} {item_category} {notes}"
            folded_haystack = fold_text(combined_search_text)
            haystack_terms = terms(combined_search_text)

            if folded_query in folded_haystack or (query_terms and query_terms.issubset(haystack_terms)):
                matched.append(item)

        return {
            "tool": "approved_software_catalog",
            "query": query_raw,
            "category": category_filter,
            "count": len(matched),
            "results": matched,
            "trust_boundary": "local_mock_data",
        }
    except Exception as exc:
        return err("approved_software_catalog", exc)
