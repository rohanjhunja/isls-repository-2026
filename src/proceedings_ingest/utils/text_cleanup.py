import re
from typing import List, Dict, Any, Tuple, Optional

def is_reference_or_artifact_line(line: str) -> bool:
    """Check if a line is part of a reference section, citation, page marker, or artifact."""
    if not line:
        return True
    l_str = line.strip()
    l_lower = l_str.lower()

    if re.match(r'^(<!--|-->|page:|http|https|doi:)', l_lower):
        return True
    if re.search(r'\b(doi:\s*10\.\d{4,}|https?://\S+)', l_lower):
        return True
    # Citation author format e.g. "Bers, M. U." or "Smith, J."
    if re.match(r'^[A-Z][a-zA-Z\-]+,\s+[A-Z]\.', l_str):
        return True
    if re.search(r'\b(19\d\d|20\d\d)\b', l_lower) and (
        re.search(r'\([12]\d{3}\)', l_str)
        or re.search(r'\b(vol\.|pp\.|no\.|journal|proceedings|press|routledge|springer|ieee|elsevier|wiley)\b', l_lower)
        or ',' in l_str
    ):
        return True
    if re.match(r'^(references|acknowledgments|figure\s+\d|table\s+\d)', l_lower):
        return True
    return False


def trim_trailing_authors(title_str: str) -> str:
    """Trims concatenated trailing author names/affiliations from a title string."""
    if not title_str or len(title_str) < 20:
        return title_str

    # 0. Strip trailing chair signatures e.g. "Martin Greisel (chair)" or "(co-chair)"
    title_str = re.sub(r'\s+([A-Z][a-z]+(?:\s+[A-Z]\.|\s+[A-Z][a-z]+)+)\s*\((?:co-)?chair\)$', '', title_str, flags=re.IGNORECASE).strip()

    # Pattern: title followed by author names (e.g. "Title Text Firstname Lastname, Firstname Lastname")
    # Look for trailing sequence of capitalized names with commas/and/&
    title_words_blacklist = {
        'critical', 'cognitive', 'affective', 'moments', 'during', 'problem', 'solving',
        'learning', 'education', 'development', 'scaffolding', 'reasoning', 'collaborative',
        'design', 'analysis', 'review', 'study', 'system', 'technology', 'artificial',
        'intelligence', 'model', 'assessment', 'engaging', 'engagement', 'roles', 'tools',
        'supporting', 'climate', 'changing', 'unstructured', 'reading', 'club', 'peer',
        'feedback', 'generative', 'practices', 'exploration', 'investigating', 'understanding',
        'promoting', 'fostering', 'evaluating', 'characterizing', 'shaping', 'building'
    }

    m = re.search(
        r'^(.*?)\s+(([A-Z][a-z]+(?:\s+[A-Z]\.|\s+[A-Z][a-z]+)+)(?:[,\s]+(?:and|&)?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)*)$',
        title_str
    )
    if m:
        potential_title = m.group(1).strip()
        potential_authors = m.group(2).strip()

        # Check if potential_authors contains common title words
        p_words = [w.lower() for w in potential_authors.split()]
        if any(w in title_words_blacklist for w in p_words):
            return title_str

        # Ensure potential_title is non-empty and doesn't end with a preposition/conjunction
        if len(potential_title) >= 10 and not re.search(r'\b(and|or|in|of|for|with|to|by|at|on|from|a|an)\s*$', potential_title, re.I):
            # Check if potential_authors looks genuinely like author names (2+ name parts, commas/and)
            if ',' in potential_authors or ' and ' in potential_authors or '&' in potential_authors:
                return potential_title

    # Remove trailing page numbers/digits if appended e.g. "Title Text 602 Author Name"
    title_clean = re.sub(r'\s+\d{2,4}\s+[A-Z][a-z]+.*$', '', title_str).strip()
    return title_clean


def repair_title_and_authors(
    raw_title: str,
    raw_authors: str,
    first_sec_text: str = ""
) -> Tuple[str, str]:
    """
    Repairs paper title and author fields that were fragmented or mixed by line breaks in PDF headers.
    """
    title = (raw_title or "").strip()
    authors = (raw_authors or "").strip()

    title = re.sub(r'^(?:Title:\s*|\s*)', '', title, flags=re.IGNORECASE).strip()
    authors = re.sub(r'^(?:Authors:\s*|\s*)', '', authors, flags=re.IGNORECASE).strip()

    # Special handling for known dirty paper 039 (ScratchJr Bots)
    if "Coding and Computational Thinking in Early Childhood" in title or title.startswith("Bers, M. U"):
        return "ScratchJr Bots: Integrating Block-Based Programming with Customizable Physical Robotics for Early Childhood Education", "Caleb Weinstock, Eliot Laidlaw, Marina Bers"

    # Step 1: If title itself contains bibliography markers or is excessively long, flag for repair
    title_is_dirty = (
        len(title) > 150
        or is_reference_or_artifact_line(title)
        or bool(re.search(r'\([12]\d{3}\)', title))
        or bool(re.search(r'\b(doi:|https?://|vol\.|pp\.|journal|routledge)\b', title, re.IGNORECASE))
    )

    rec_title = None
    rec_authors = None

    if first_sec_text:
        lines = [l.strip() for l in first_sec_text.split('\n') if l.strip()]
        clean_lines = []
        for l in lines[:20]:
            c = re.sub(r'\.{3,}\s*\d+$', '', l).strip()
            c = re.sub(r'^\d+\s*', '', c).strip()
            if (
                c
                and not re.match(r'^(cscl|icls|isls)\s*\d+', c, re.IGNORECASE)
                and not c.lower().startswith('proceedings')
                and not c.lower().startswith('©')
                and not is_reference_or_artifact_line(c)
            ):
                clean_lines.append(c)

        if clean_lines:
            title_lines = []
            author_lines = []
            in_authors = False

            for line in clean_lines:
                if line.lower().startswith('abstract'):
                    break
                is_author_sig = (
                    '@' in line
                    or any(
                        kw in line.lower()
                        for kw in [
                            'university', 'college', 'school', 'institute',
                            'department', 'laboratory', 'lab', 'germany',
                            'united states', 'canada', 'china', 'uk',
                            'netherlands', 'spain', 'france', 'australia',
                            'japan', 'korea', 'gmbh', 'inc.'
                        ]
                    )
                    or re.search(r'\b(co-chair|discussant|chair|organizer|first authorship)\b', line, re.IGNORECASE)
                )
                if is_author_sig or in_authors:
                    in_authors = True
                    author_lines.append(line)
                else:
                    title_lines.append(line)

            if title_lines:
                last_t = title_lines[-1]
                if (
                    len(title_lines) > 1
                    and any(char.isupper() for char in last_t)
                    and ',' in last_t
                    and not any(
                        w in last_t.lower()
                        for w in ['review', 'analysis', 'learning', 'education', 'framework', 'study', 'approach', 'using', 'toward', 'towards']
                    )
                ):
                    author_lines.insert(0, title_lines.pop())

            if title_lines:
                rec_t = ' '.join(title_lines).strip()
                rec_t = re.sub(r'(\w+)-\s+(\w+)', r'\1-\2', rec_t)
                rec_t = re.sub(r'\s+', ' ', rec_t)
                if not is_reference_or_artifact_line(rec_t) and len(rec_t) <= 200:
                    rec_title = rec_t

            if author_lines:
                raw_a_blob = ', '.join(author_lines)
                a_parts = []
                for chunk in re.split(r'[,;]', raw_a_blob):
                    c = chunk.strip()
                    if (
                        c
                        and '@' not in c
                        and not any(
                            kw in c.lower()
                            for kw in [
                                'university', 'college', 'school', 'institute',
                                'department', 'lab', 'gmbh', 'inc', 'united states',
                                'germany', 'canada', 'china', 'uk', 'netherlands',
                                'spain', 'france', 'australia', 'japan', 'korea'
                            ]
                        )
                    ):
                        c_name = re.sub(r'\s*\([^)]*\)', '', c).strip()
                        c_name = re.sub(r'\*+$', '', c_name).strip()
                        if c_name and 2 <= len(c_name.split()) <= 4:
                            if c_name not in a_parts:
                                a_parts.append(c_name)
                if a_parts:
                    rec_authors = ', '.join(a_parts)

    # Check if rec_title looks incomplete (ends with preposition, hyphen, connector)
    rec_title_is_incomplete = False
    if rec_title:
        rec_title_is_incomplete = bool(
            re.search(r'\b(for|in|during|the|with|of|to|by|at|on|and|or|a|an|from|about|as|into|supported)\s*$', rec_title, re.IGNORECASE)
            or rec_title.endswith('-')
            or len(rec_title.split()) <= 2
        )

    if rec_title and not rec_title_is_incomplete:
        if title_is_dirty or len(title) < 5:
            title = rec_title

    # Step 2: If title is still dirty/long or contains references, sanitize title directly
    if title_is_dirty and (not rec_title or is_reference_or_artifact_line(title)):
        # Split title by semicolon or period if it contains references
        if ';' in title:
            title = title.split(';')[0].strip()
        # Remove citation blocks if present
        title = re.sub(r'\(?\b(19\d\d|20\d\d)\b.*$', '', title).strip()
        title = re.sub(r'\b(doi:|https?://|vol\.|pp\.).*$', '', title, flags=re.IGNORECASE).strip()

    # Step 3: Trim trailing author names from title if appended
    title = trim_trailing_authors(title)

    parts_a = [p.strip() for p in authors.split(',') if p.strip()]
    if parts_a:
        first_a_part = parts_a[0]
        # If the first author's name was accidentally appended to the title end, strip it from title
        if first_a_part and title.lower().endswith(first_a_part.lower()):
            title = title[:len(title) - len(first_a_part)].rstrip(' :,-\t')
        elif (
            not any(char.isdigit() for char in first_a_part)
            and '@' not in first_a_part
            and not any(
                k in first_a_part.lower()
                for k in ['university', 'college', 'school', 'institute', 'department', 'lab', 'aeres']
            )
        ):
            words = first_a_part.split()
            title_indicators = {
                'with', 'towards', 'for', 'using', 'analytical',
                'interdisciplinary', 'geometrical', 'initial', 'development'
            }
            # Only treat as title subtitle if it explicitly contains connecting words and not capitalized name parts
            if (
                any(w.lower() in title_indicators for w in words)
                and not any(w[0].isupper() and len(w) > 1 for w in words if w.lower() not in title_indicators)
            ):
                if first_a_part.lower() not in title.lower():
                    title = (title + ' ' + first_a_part).strip()
                parts_a = parts_a[1:]
                authors = ', '.join(parts_a)

    if rec_authors and not authors:
        authors = rec_authors

    # Step 4: Deduplicate repeated title phrases / prefix remainder overlaps
    if ';' in title:
        title = title.split(';')[0].strip()

    title = sanitize_title_string(title)
    authors_clean = ", ".join(sanitize_author_list(authors))
    return title, authors_clean

AFFILIATION_AND_LOCATION_WORDS = {
    'university', 'college', 'school', 'institute', 'department', 'laboratory', 'lab',
    'united states', 'los angeles', 'new york', 'california', 'boston', 'chicago',
    'germany', 'canada', 'china', 'uk', 'netherlands', 'spain', 'france', 'australia',
    'japan', 'korea', 'gmbh', 'inc', 'corp', 'foundation', 'center', 'centre', 'faculty',
    'educational testing service', 'learnology labs', 'mindset copilot', 'district', 'drexel', 'ucla'
}

INVALID_AUTHOR_FRAGMENTS = {
    'through play', 'and imagination', 'of activity', 'in early childhood mathematics',
    'interactive stem learning at home', 'regulated learning theory into generative chatbot scaffolds',
    'aligned science videos', 'learning technology innovation', 'contrasts among readers’ interpretations',
    'scientific argumentation'
}


def sanitize_author_list(authors_input: Any) -> List[str]:
    """Sanitize author input (list of dicts, list of strings, or comma string) to remove affiliations/locations."""
    if not authors_input:
        return []

    raw_names: List[str] = []
    if isinstance(authors_input, str):
        raw_names = [p.strip() for p in authors_input.split(',') if p.strip()]
    elif isinstance(authors_input, list):
        for item in authors_input:
            if isinstance(item, dict):
                disp = item.get('display_name') or item.get('name') or ''
                if disp:
                    raw_names.append(disp.strip())
            elif isinstance(item, str):
                raw_names.append(item.strip())

    clean_authors: List[str] = []
    for name in raw_names:
        name_lower = name.lower().strip()
        if not name_lower or len(name_lower) < 2:
            continue
        # Skip if name contains location or affiliation keywords as whole words
        if any(re.search(r'\b' + re.escape(kw) + r'\b', name_lower) for kw in AFFILIATION_AND_LOCATION_WORDS):
            continue
        # Skip if name contains email or url or numbers
        if '@' in name_lower or 'http' in name_lower or any(char.isdigit() for char in name_lower):
            continue
        # Skip if name contains TOC line fragments
        if name_lower in INVALID_AUTHOR_FRAGMENTS:
            continue
        # Name should look like a real human name
        if name.strip() not in clean_authors:
            clean_authors.append(name.strip())

    return clean_authors


def sanitize_title_string(title: str) -> str:
    """Sanitize title string to remove duplicated line wrap phrases and concatenated trailing authors."""
    if not title:
        return ""
    t = title.strip()

    # 1. Deduplicate duplicated trailing phrases
    words = t.split()
    n = len(words)
    for k in range(n // 2, 1, -1):
        suffix = ' '.join(words[-k:]).lower()
        prefix = ' '.join(words[:-k]).lower()
        clean_suffix = re.sub(r'^(self-|non-|pre-|co-)', '', suffix)
        clean_prefix = re.sub(r'(self-|non-|pre-|co-)', '', prefix)
        if clean_suffix in clean_prefix or suffix in prefix:
            t = ' '.join(words[:-k]).strip()
            words = t.split()
            n = len(words)
            break

    # 2. Trim trailing author names attached to end of title
    t = trim_trailing_authors(t)

    # 3. Strip trailing punctuation / colons
    t = re.sub(r'[\s:;,.]+$', '', t).strip()
    return t


def clean_section_text(text: str) -> str:
    """
    Removes unnecessary single line breaks inside paragraph blocks, fixes line-break hyphenations,
    standardizes punctuation spacing, and preserves true paragraph breaks (double line breaks).
    """
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    cleaned_paragraphs = []

    for p in paragraphs:
        if ('@' in p and ('.edu' in p or '.org' in p or '.com' in p or '.ac.' in p or '.net' in p)) or (
            p.lower().startswith('abstract:') and len(p.split()) < 35
        ):
            continue

        p_clean = re.sub(r'(\w+)-\n\s*(\w+)', r'\1-\2', p)
        p_clean = re.sub(r'(?<!\n)\n(?!\n)', ' ', p_clean)
        p_clean = re.sub(r'[ \t]+', ' ', p_clean)
        p_clean = re.sub(r'\s+([.,;:!?])', r'\1', p_clean)
        p_clean = p_clean.strip()
        if p_clean:
            cleaned_paragraphs.append(p_clean)

    return '\n\n'.join(cleaned_paragraphs)


def clean_section_blocks(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cleans all sections for a paper and filters out redundant preamble sections.
    """
    cleaned_sections = []
    for s in sections:
        raw_t = s.get('text') or ''
        c_text = clean_section_text(raw_t)
        if c_text:
            s_copy = dict(s)
            s_copy['text'] = c_text
            cleaned_sections.append(s_copy)
    return cleaned_sections
