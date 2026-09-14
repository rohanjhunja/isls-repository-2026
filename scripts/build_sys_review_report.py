import json, os, shutil

with open('data/viewer_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

md = []
md.append('# Comprehensive Literature Review: Systematic Reviews in Learning Sciences (2023–2026)\n')
md.append('## Executive Overview')
md.append('This comprehensive literature review synthesizes papers across the ISLS proceedings (CSCL, ICLS, ISLS from 2023 to 2026) focusing on **systematic reviews, scoping reviews, meta-analyses, umbrella reviews, and evidence syntheses**. Property values (keywords, ~50-word summaries) were extracted strictly from **titles and abstracts**, and methods sections were inspected for **databases searched**.\n')

md.append('### Search Methodology & Extraction Rules')
md.append('- **Property Extraction Scope**: Title & Abstract ONLY (Methods section inspected specifically for Databases Searched)')
md.append('- **Databases Searched**: Extracted directly from methodology text (e.g. Scopus, Web of Science, ERIC, PsycINFO, ACM Digital Library, IEEE Xplore, Google Scholar)')
md.append('- **~50-Word Summary Structure**: Explicitly indicates **RQ/Objective**, **Finding**, and **Relevance to Real World**')
md.append('- **Keywords**: Pattern-extracted from title and abstract (up to 5 unique keywords, no generic filler repetitions)')
md.append(f'- **Total Matched Publications**: {len(papers)} papers across 2023–2026 proceedings.\n')

md.append('---\n')
md.append('## Literature Review Matrix\n')
md.append('| Paper Title & Author | Year | Databases Searched | Abstract | ~50-Word Summary (RQ, Finding, Relevance) | Keywords (Up to 5) |')
md.append('|---|---|---|---|---|---|')

for p in papers:
    title = p['title'].replace('|', '\\|')
    authors = p['authors'].replace('|', '\\|')
    year = str(p['year'])
    dbs = ", ".join(p.get('databases_searched', ['Not specified'])).replace('|', '\\|')
    abstract = p['abstract'].replace('|', '\\|').replace('\n', ' ')
    abstract_display = abstract[:280] + '...' if len(abstract) > 280 else abstract
        
    summary = p['summary'].replace('|', '\\|').replace('\n', ' ')
    keywords_str = ', '.join(p.get('keywords', [])).replace('|', '\\|')
    
    author_header = f"**{title}**<br>*Authors*: {authors}"
    
    md.append(f"| {author_header} | {year} | {dbs} | {abstract_display} | {summary} | {keywords_str} |")

md.append('\n---\n')
md.append('## Thematic Synthesis & Key Findings')
md.append('1. **Generative AI & LLMs in Education**: Rapid emergence of systematic and scoping reviews in 2024–2026 evaluating Large Language Models (LLMs), ChatGPT feedback mechanisms, and critical algorithmic literacy in K-12 and higher education.')
md.append('2. **CSCL & Collaborative Learning**: Meta-analyses and systematic reviews synthesizing empirical evidence on adaptive instructional support, group flow, intersubjectivity, and immersive VR collaborative learning.')
md.append('3. **Game-Based Learning & Executive Functions**: Multiple 2025–2026 systematic reviews investigating the impact of digital learning games on growth mindsets, executive functions, and embedded learning supports.')
md.append('4. **Database Coverage Patterns**: Web of Science, Scopus, ERIC, and PsycINFO represent the primary databases queried across systematic and scoping reviews in learning sciences.')

os.makedirs('data/reports', exist_ok=True)
report_path = 'data/reports/systematic_review_literature_review.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

print(f"Saved updated report to {report_path}")

# Copy to artifact folder
artifact_dir = '/Users/rohanjhunja/.gemini/antigravity/brain/de852235-0381-43bb-89b3-64b22a7717c6'
if os.path.exists(artifact_dir):
    artifact_path = os.path.join(artifact_dir, 'systematic_review_literature_review.md')
    shutil.copyfile(report_path, artifact_path)
    print(f"Updated artifact at {artifact_path}")
