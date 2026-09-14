import json, os, datetime

with open('data/viewer_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

review_data = {
    'id': 'rev_systematic_review_2026',
    'name': 'Systematic Review Literature Review (2023-2026)',
    'description': 'Comprehensive literature review of papers with systematic review, scoping review, meta-analysis, umbrella review, and evidence synthesis in titles and abstracts across ISLS/CSCL/ICLS proceedings.',
    'created_at': datetime.datetime.now().isoformat(),
    'search_scope': 'Title and Abstract ONLY (Methods section checked for Databases Searched)',
    'extended_keywords': [
        'systematic review', 'systematic literature review', 'scoping review', 
        'meta-analysis', 'meta analysis', 'systematic scoping review',
        'umbrella review', 'systematic mapping', 'evidence synthesis'
    ],
    'total_matched_papers': len(papers),
    'papers': papers
}

os.makedirs('data/reviews', exist_ok=True)
with open('data/reviews/systematic_review_lit_review.json', 'w', encoding='utf-8') as f:
    json.dump(review_data, f, indent=2)

print('Updated data/reviews/systematic_review_lit_review.json successfully.')
