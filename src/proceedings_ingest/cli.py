import sys
import os
import json
import click

# Add src to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from proceedings_ingest.profiles import ProfileManager
from proceedings_ingest.review_models import PaperScope, PropertyDefinition, QueryDefinition, QueryConstraint
from proceedings_ingest.review_service import ReviewService
from proceedings_ingest.exporter import ReviewExporter
from proceedings_ingest.dipstick_engine import DipstickEngine
from proceedings_ingest.utils.memory import get_rss_memory_gb


@click.group()
def cli():
    """Antigravity Proceedings Research System CLI"""
    pass


@cli.command()
def doctor():
    """Check environment health and dependencies."""
    click.echo("=== Proceedings Research System Doctor ===")
    click.echo(f"Python Version: {sys.version.split()[0]}")
    click.echo(f"Working Directory: {os.getcwd()}")
    click.echo(f"Current Process Memory (RSS): {get_rss_memory_gb():.3f} GB")

    deps = ["pydantic", "yaml", "pdfplumber", "pypdf", "rapidfuzz", "sqlite3", "psutil"]
    missing = []
    for d in deps:
        try:
            __import__(d)
            click.echo(f"  [OK] {d}")
        except ImportError:
            click.echo(f"  [MISSING] {d}")
            missing.append(d)

    if missing:
        click.echo(f"\nWarning: Missing dependencies: {', '.join(missing)}")
    else:
        click.echo("\nAll system dependencies OK!")


@cli.command()
@click.argument("pdf_path")
def register(pdf_path):
    """Register a source PDF into the repository."""
    from proceedings_ingest.stages.register import RegisterStage
    base_dir = os.getcwd()
    reg = RegisterStage(os.path.join(base_dir, "data"))
    rec = reg.register_file(pdf_path)
    click.echo(f"Registered document {rec['id']}: SHA256={rec['sha256'][:16]}..., Pages={rec['pdf_page_count']}")


@cli.command()
@click.argument("pdf_path")
@click.option("--sample", is_flag=True, help="Sample pages layout")
def preflight(pdf_path, sample):
    """Run preflight analysis on a source PDF."""
    from proceedings_ingest.pipeline import Pipeline
    base_dir = os.getcwd()
    pipe = Pipeline(base_dir)
    res = pipe.preflight_stage.inspect(pdf_path)
    click.echo(f"Preflight Results for {pdf_path}:")
    click.echo(f"  Has usable text: {res['has_usable_text']}")
    click.echo(f"  TOC entries found: {len(res['toc_entries'])}")
    click.echo(f"  Suggested profile: {res['suggested_profile']}")


@cli.command()
@click.argument("pdf_path")
@click.option("--max-memory-gb", default=8.0, help="Maximum memory limit in GB before halting safely.")
def ingest(pdf_path, max_memory_gb):
    """Run full ingestion pipeline for a PDF."""
    from proceedings_ingest.pipeline import Pipeline
    base_dir = os.getcwd()
    pipe = Pipeline(base_dir, max_memory_gb=max_memory_gb)
    collection, report = pipe.run_ingestion(pdf_path)

    click.echo("\n=== Ingestion Complete ===")
    click.echo(f"Collection ID: {collection.id}")
    click.echo(f"Source PDF: {report.source_filename}")
    click.echo(f"PDF Pages: {report.pdf_page_count}")
    click.echo(f"Papers Detected: {report.detected_papers_count}")
    click.echo(f"Expected TOC Entries: {report.expected_toc_count}")
    click.echo(f"Average Boundary Confidence: {report.boundaries_confidence_avg}")
    click.echo(f"Missing Fields Summary: {report.missing_fields_summary}")
    click.echo(f"Final Memory (RSS): {get_rss_memory_gb():.3f} GB")


@cli.command("audit")
@click.argument("subcmd", type=click.Choice(["ingestion"]))
@click.argument("doc_id")
def audit(subcmd, doc_id):
    """Audit ingestion report for a document."""
    base_dir = os.getcwd()
    report_path = os.path.join(base_dir, "data", "reports", f"ingestion_{doc_id}.json")
    if not os.path.exists(report_path):
        click.echo(f"Error: Ingestion report for {doc_id} not found at {report_path}")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    click.echo(f"=== Audit Ingestion Report ({doc_id}) ===")
    for k, v in data.items():
        click.echo(f"  {k}: {v}")


# Literature Review Commands
@cli.group()
def review():
    """Manage literature reviews and scopes."""
    pass


@review.command("create")
@click.argument("name")
@click.option("--description", help="Review description")
@click.option("--prompt", help="Natural language scope prompt")
@click.option("--years", help="Comma-separated years (e.g. 2023,2024)")
@click.option("--conferences", help="Comma-separated conference acronyms/names")
@click.option("--keywords", help="Comma-separated search keywords")
@click.option("--search-fields", default="title,abstract", help="Fields to search across (default: title,abstract; use 'sections' for full paper)")
@click.option("--ai-search", is_flag=True, help="Enable AI semantic search instead of deterministic keyword search")
def review_create(name, description, prompt, years, conferences, keywords, search_fields, ai_search):
    """Create a new literature review with scope parameters."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    
    year_list = [int(y.strip()) for y in years.split(",")] if years else []
    conf_list = [c.strip() for c in conferences.split(",")] if conferences else []
    kw_list = [k.strip() for k in keywords.split(",")] if keywords else []
    fields_list = [f.strip() for f in search_fields.split(",")] if search_fields else ["title", "abstract"]

    scope = PaperScope(
        review_prompt=prompt,
        years=year_list,
        conferences=conf_list,
        keywords=kw_list,
        search_fields=fields_list,
        ai_search_enabled=ai_search
    )
    rev = service.create_review(name=name, description=description, scope=scope)
    click.echo(f"Created review {rev.id}: Name='{rev.name}', Papers={len(rev.paper_ids)}")
    click.echo(f"  Markdown view generated: data/reviews/{rev.id}.md")


@review.command("list")
def review_list():
    """List all saved literature reviews."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    revs = service.list_reviews()
    click.echo(f"=== Saved Literature Reviews ({len(revs)}) ===")
    for r in revs:
        click.echo(f"  [{r.id}] {r.name} - {len(r.paper_ids)} papers, {len(r.selected_columns)} columns")


@review.command("show")
@click.argument("review_id")
def review_show(review_id):
    """Show details for a literature review."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    r = service.get_review(review_id)
    if not r:
        click.echo(f"Error: Review '{review_id}' not found.")
        return
    click.echo(f"Review ID: {r.id}")
    click.echo(f"Name: {r.name}")
    click.echo(f"Description: {r.description}")
    click.echo(f"Papers ({len(r.paper_ids)}): {r.paper_ids}")
    click.echo(f"Columns ({len(r.selected_columns)}): {r.selected_columns}")


@review.command("add-papers")
@click.argument("review_id")
@click.argument("paper_ids", nargs=-1)
def review_add_papers(review_id, paper_ids):
    """Add papers to a review."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    r = service.add_papers_to_review(review_id, list(paper_ids))
    click.echo(f"Updated review {r.id}: Now contains {len(r.paper_ids)} papers.")


@review.command("dipstick")
@click.option("--name", default="", help="Name of the review (defaults to 'Dipstick Review - <keyword(s)>')")
@click.option("--keywords", help="Comma-separated keywords to evaluate (default: standard research set)")
def review_dipstick(name, keywords):
    """Run an ultra-fast dipstick review across 100% of papers (Title & Abstract scope)."""
    base_dir = os.getcwd()
    engine = DipstickEngine(os.path.join(base_dir, "data"))
    
    if keywords:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    else:
        kw_list = engine.DEFAULT_KEYWORDS

    manifest = engine.save_dipstick_review(name, kw_list)
    review_name = manifest['name']
    
    click.echo(f"=== Running Dipstick Review: '{review_name}' ===")
    click.echo(f"Scope: Title & Abstract Only (100% Repository Coverage)")
    click.echo(f"Keywords ({len(kw_list)}): {', '.join(kw_list)}")
    click.echo(f"\nCompleted! Scanned 100% of papers ({manifest['total_papers_scanned']} total).")
    click.echo(f"Matched Papers: {manifest['matched_paper_count']}")
    click.echo(f"Review ID: {manifest['id']}")
    click.echo(f"Saved manifest: {engine.reviews_dir}/{manifest['id']}.json")
    click.echo(f"Saved Markdown report: {engine.reviews_dir}/{manifest['id']}.md")
    click.echo(f"Tokens Used: 0 Tokens")


# Property Commands
@cli.group()
def property():
    """Manage property definitions and extractions."""
    pass


@property.command("find")
@click.argument("query")
def property_find(query):
    """Find matching canonical fields or property definitions."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    res = service.property_registry.find_matching_properties(query)
    click.echo(f"Query: '{query}'")
    click.echo(f"Has close match (>=80%): {res['has_close_match']}")
    click.echo("Matches found:")
    for m in res["matches"]:
        click.echo(f"  [{m['kind']}] ID={m['id']}, Label='{m['label']}', Score={m['score']}")
        click.echo(f"    Suggestion: {m['suggestion']}")


@property.command("define")
@click.argument("property_id")
@click.option("--label", required=True, help="Property display label")
@click.option("--description", required=True, help="Property description")
@click.option("--question", help="Query question")
def property_define(property_id, label, description, question):
    """Define a new reusable property schema."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"))
    query = QueryDefinition(question=question) if question else None
    prop = PropertyDefinition(
        id=property_id,
        label=label,
        description=description,
        query=query
    )
    file_path = service.property_registry.save_property(prop)
    click.echo(f"Property definition saved to {file_path}")


@property.command("extract")
@click.argument("property_id")
@click.option("--review", "review_id", required=True, help="Review ID")
@click.option("--max-memory-gb", default=8.0, help="Maximum memory limit in GB before halting safely.")
def property_extract(property_id, review_id, max_memory_gb):
    """Extract a property for all papers in a review."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"), max_memory_gb=max_memory_gb)
    obs_list = service.extract_property_for_review(review_id, property_id)
    click.echo(f"Extracted {len(obs_list)} observations for property '{property_id}' in review '{review_id}'.")
    click.echo(f"Final Memory (RSS): {get_rss_memory_gb():.3f} GB")


# Export Commands
@cli.group()
def export():
    """Export review tables into CSV format."""
    pass


@export.command("csv")
@click.argument("review_id")
@click.option("--output", help="Output file path (single CSV or ZIP bundle)")
@click.option("--bundle", is_flag=True, help="Export all tables as ZIP bundle")
@click.option("--max-memory-gb", default=8.0, help="Maximum memory limit in GB before halting safely.")
def export_csv(review_id, output, bundle, max_memory_gb):
    """Export review tables as CSV or multi-CSV ZIP bundle."""
    base_dir = os.getcwd()
    service = ReviewService(os.path.join(base_dir, "data"), max_memory_gb=max_memory_gb)
    exporter = ReviewExporter(service)

    if bundle:
        out_path = output or os.path.join(base_dir, f"{review_id}_bundle.zip")
        exporter.export_bundle_zip(review_id, out_path)
        click.echo(f"Exported review bundle to ZIP: {out_path}")
    else:
        out_path = output or os.path.join(base_dir, f"{review_id}_literature_review.csv")
        csv_str = exporter.export_literature_review_csv(review_id)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(csv_str)
        click.echo(f"Exported literature review CSV: {out_path}")
    click.echo(f"Final Memory (RSS): {get_rss_memory_gb():.3f} GB")


if __name__ == "__main__":
    cli()

