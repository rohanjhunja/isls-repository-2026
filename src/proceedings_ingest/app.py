import os
import streamlit as st
import pandas as pd
from proceedings_ingest.review_service import ReviewService
from proceedings_ingest.exporter import ReviewExporter

st.set_page_config(page_title="Antigravity Literature Review Tables", layout="wide")

data_dir = os.environ.get("PROCEEDINGS_DATA_DIR", os.path.join(os.getcwd(), "data"))
service = ReviewService(data_dir)
exporter = ReviewExporter(service)

st.title("📚 Antigravity Literature Review Tables")

reviews = service.list_reviews()
if not reviews:
    st.info("No saved literature reviews found in data/reviews.")
else:
    review_map = {f"{r.name} ({r.id})": r.id for r in reviews}
    selected_name = st.sidebar.selectbox("Select Review", list(review_map.keys()))
    review_id = review_map[selected_name]

    review = service.get_review(review_id)
    st.sidebar.markdown(f"**ID:** {review.id}")
    st.sidebar.markdown(f"**Created:** {review.created_at}")
    st.sidebar.markdown(f"**Total Papers:** {len(review.paper_ids)}")

    table_data = service.build_review_table(review_id)
    if table_data:
        # Build flattened display dataframe
        flat_rows = []
        for row in table_data:
            flat_row = {}
            for col, val in row.items():
                if isinstance(val, dict):
                    flat_row[col] = val.get("value")
                else:
                    flat_row[col] = val
            flat_rows.append(flat_row)

        df = pd.DataFrame(flat_rows)

        # Filters and Column selection
        cols = st.multiselect("Visible Columns", options=list(df.columns), default=list(df.columns))
        search = st.text_input("Search in Table", "")

        if search:
            mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
            df_filtered = df[mask]
        else:
            df_filtered = df

        if cols:
            st.dataframe(df_filtered[cols], use_container_width=True)

        st.markdown("### 📥 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            csv_data = exporter.export_literature_review_csv(review_id)
            st.download_button(
                "Download Main Table CSV",
                data=csv_data,
                file_name=f"{review.name}_literature_review.csv",
                mime="text/csv"
            )
        with col2:
            zip_path = os.path.join(data_dir, f"{review_id}_bundle.zip")
            exporter.export_bundle_zip(review_id, zip_path)
            if os.path.exists(zip_path):
                with open(zip_path, "rb") as fp:
                    st.download_button(
                        "Download All CSVs (ZIP Bundle)",
                        data=fp.read(),
                        file_name=f"{review.name}_review_bundle.zip",
                        mime="application/zip"
                    )

        st.markdown("### 🔍 Evidence Inspector")
        paper_choice = st.selectbox("Select Paper ID to inspect evidence", options=review.paper_ids)
        if paper_choice:
            for col in review.selected_columns:
                if col in ["paper_id", "title", "authors", "year", "abstract", "keywords", "filename"]:
                    continue
                obs = service._load_observation(paper_choice, col)
                if obs:
                    with st.expander(f"Property: {col} | Status: {obs.status}"):
                        st.markdown(f"**Value:** {obs.value}")
                        st.markdown(f"**Method:** {obs.method} | **Confidence:** {obs.confidence}")
                        if obs.evidence:
                            st.markdown("**Evidence Passages:**")
                            for ev in obs.evidence:
                                st.caption(f"Section: {ev.section_id or 'N/A'} | Page: {ev.pdf_page or 'N/A'}")
                                st.code(ev.supporting_text)
