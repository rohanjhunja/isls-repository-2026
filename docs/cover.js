/**
 * ISLS Research Repository & Agentic Review System - Cover Page Script
 * Generates the 20 Pastel Outlier Silhouette Figures in perspective depth,
 * initializes Mermaid diagrams, handles interactive HUD popovers, prompt copy, and APA citations.
 */

(function() {
  "use strict";

  const OUTLIERS_DATA = [{"title": "Community-Wide Infrastructuring: Extending Infrastructure Theories Toward Learning Ecosystems", "authors": "Wade Berger; Ronni Hayden", "year": 2025, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very High", "section": "Abstract & Introduction", "tokens": 5155, "pct_of_paper": 84.4, "total_tokens": 6110, "section_tokens": {"Abstract & Introduction": 5155, "Methodology & Context": 0, "Results & Findings": 0, "Discussion & Conclusion": 5}, "context": "Extensive theoretical grounding and front-matter distillation dedicating comprehensive framing and foundational literature."}, {"title": "Teacher Attention and Improving Student Reasoning in Classroom Discussions", "authors": "Richard Correnti; Benjamin Pierce", "year": 2024, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very Low", "section": "Abstract & Introduction", "tokens": 46, "pct_of_paper": 0.8, "total_tokens": 5705, "section_tokens": {"Abstract & Introduction": 46, "Methodology & Context": 453, "Results & Findings": 250, "Discussion & Conclusion": 4854}, "context": "Concise, rapid problem statement that transitions immediately into experimental or pedagogical design."}, {"title": "Expanding the Borders of Music-Based Qualitative Research Methods Through Graphic Scores", "authors": "Peter J. Woods; Karis Jones", "year": 2020, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very High", "section": "Methodology & Context", "tokens": 4909, "pct_of_paper": 80.9, "total_tokens": 6069, "section_tokens": {"Abstract & Introduction": 156, "Methodology & Context": 4909, "Results & Findings": 0, "Discussion & Conclusion": 358}, "context": "Comprehensive multi-framework methodological architecture detailing mechanisms, empirical data pipelines, and analytical rubrics."}, {"title": "Toward Onto-epistemic Heterogeneity through Culinary Making: Insights from a Learning Narrative", "authors": "Phebe Chew; Aakriti Bisht", "year": 2024, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very Low", "section": "Methodology & Context", "tokens": 48, "pct_of_paper": 0.8, "total_tokens": 5973, "section_tokens": {"Abstract & Introduction": 3820, "Methodology & Context": 48, "Results & Findings": 0, "Discussion & Conclusion": 1639}, "context": "Highly condensed, minimalist design brief that summarizes iterative methodology in under two paragraphs."}, {"title": "Fostering Inclusive Practices in Educational Policy Reform", "authors": "Dian Mawene; Elizabeth Schrader", "year": 2025, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very High", "section": "Results & Findings", "tokens": 5268, "pct_of_paper": 44.6, "total_tokens": 11807, "section_tokens": {"Abstract & Introduction": 1874, "Methodology & Context": 1805, "Results & Findings": 5268, "Discussion & Conclusion": 1619}, "context": "In-depth qualitative and quantitative empirical findings presenting extensive interaction transcripts and multi-case observations."}, {"title": "Triggering Social-Emotional and Ethical Learning: A Case Study in a PBL Course", "authors": "Sahana Murthy; Sridhar Iyer; Navneet Kaur; Angelina S. Philip", "year": 2024, "conference": "ICLS", "paper_type": "Full Paper", "outlier_type": "Very Low", "section": "Results & Findings", "tokens": 73, "pct_of_paper": 1.3, "total_tokens": 5473, "section_tokens": {"Abstract & Introduction": 1379, "Methodology & Context": 21, "Results & Findings": 73, "Discussion & Conclusion": 3530}, "context": "Short conceptual piece that embeds preliminary findings directly into theoretical arguments, leaving a minimal standalone results section."}, {"title": "Bridging Curriculum and Creativity: NLP-Powered Semantic Analysis for Knowledge Building", "authors": "Ahmad Khanlari", "year": 2026, "conference": "CSCL", "paper_type": "Full Paper", "outlier_type": "Very Low", "section": "Discussion & Conclusion", "tokens": 31, "pct_of_paper": 0.6, "total_tokens": 5283, "section_tokens": {"Abstract & Introduction": 2310, "Methodology & Context": 588, "Results & Findings": 2095, "Discussion & Conclusion": 31}, "context": "Laser-focused concluding remarks delivering immediate takeaways in a single summary paragraph."}, {"title": "Designing at the Speed of Trust: Unearthing Implicit Values and Vibes", "authors": "Ananda Marin", "year": 2026, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very High", "section": "Abstract & Introduction", "tokens": 3344, "pct_of_paper": 89.2, "total_tokens": 3750, "section_tokens": {"Abstract & Introduction": 3344, "Methodology & Context": 0, "Results & Findings": 0, "Discussion & Conclusion": 0}, "context": "Extensive theoretical grounding and front-matter distillation dedicating comprehensive framing and foundational literature."}, {"title": "Teachers\u2019 Uptake on Artificial Intelligence (AI) Tools in the Context of Environmental and Climate Change", "authors": "Asli Sezen-Barrie; Arya Karumanthra", "year": 2026, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very Low", "section": "Abstract & Introduction", "tokens": 53, "pct_of_paper": 1.7, "total_tokens": 3204, "section_tokens": {"Abstract & Introduction": 53, "Methodology & Context": 1177, "Results & Findings": 1330, "Discussion & Conclusion": 188}, "context": "Concise, rapid problem statement that transitions immediately into experimental or pedagogical design."}, {"title": "Methods for Analyzing Ideological Sensemaking in Interaction", "authors": "Ashlyn Pierson; Bethany Daniel; D. Teo Keifert", "year": 2024, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very High", "section": "Methodology & Context", "tokens": 2271, "pct_of_paper": 85.0, "total_tokens": 2671, "section_tokens": {"Abstract & Introduction": 0, "Methodology & Context": 2271, "Results & Findings": 0, "Discussion & Conclusion": 158}, "context": "Comprehensive multi-framework methodological architecture detailing mechanisms, empirical data pipelines, and analytical rubrics."}, {"title": "Advancing Dialogic Leadership through AI-Enabled Training: Insights from a Design-Based Research Project", "authors": "Rupert Wegerif; Xuanning Chen; Imogen Casebourne; Pedro Salinas", "year": 2026, "conference": "CSCL", "paper_type": "Short Paper", "outlier_type": "Very Low", "section": "Methodology & Context", "tokens": 30, "pct_of_paper": 1.0, "total_tokens": 2952, "section_tokens": {"Abstract & Introduction": 1653, "Methodology & Context": 30, "Results & Findings": 353, "Discussion & Conclusion": 308}, "context": "Highly condensed, minimalist design brief that summarizes iterative methodology in under two paragraphs."}, {"title": "Contradictions of Decolonial Literacy in an ESL Writing Space", "authors": "Gautam Bisht", "year": 2023, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very High", "section": "Results & Findings", "tokens": 3658, "pct_of_paper": 72.9, "total_tokens": 5018, "section_tokens": {"Abstract & Introduction": 1360, "Methodology & Context": 0, "Results & Findings": 3658, "Discussion & Conclusion": 0}, "context": "In-depth qualitative and quantitative empirical findings presenting extensive interaction transcripts and multi-case observations."}, {"title": "Toward Productive Multivocality in AI Development: Excavating Ethics Concerns among an Interdisciplinary Team", "authors": "X. Christine Wang; Grace Xing; Sanaz Ahmadzadeh Siyahrood; Jinjun Xiong", "year": 2024, "conference": "CSCL", "paper_type": "Short Paper", "outlier_type": "Very Low", "section": "Results & Findings", "tokens": 38, "pct_of_paper": 1.5, "total_tokens": 2575, "section_tokens": {"Abstract & Introduction": 450, "Methodology & Context": 335, "Results & Findings": 38, "Discussion & Conclusion": 1474}, "context": "Short conceptual piece that embeds preliminary findings directly into theoretical arguments, leaving a minimal standalone results section."}, {"title": "Emotion Recognition in Educational Written Dialogues on Civic and Social Issues", "authors": "Efrat Firer; Baruch B. Schwarz", "year": 2023, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very High", "section": "Discussion & Conclusion", "tokens": 2129, "pct_of_paper": 63.5, "total_tokens": 3352, "section_tokens": {"Abstract & Introduction": 468, "Methodology & Context": 0, "Results & Findings": 755, "Discussion & Conclusion": 2129}, "context": "Broad theoretical discussion synthesizing systemic implications, relational ontologies, and educational justice."}, {"title": "AI for Climate Justice: Assessing Large Language Models from an Intersectional Lens", "authors": "Ha Nguyen; Rossella Santagata; Victoria Nguyen; Hunter King; Sara Ludovise", "year": 2024, "conference": "ICLS", "paper_type": "Short Paper", "outlier_type": "Very Low", "section": "Discussion & Conclusion", "tokens": 29, "pct_of_paper": 1.1, "total_tokens": 2664, "section_tokens": {"Abstract & Introduction": 702, "Methodology & Context": 425, "Results & Findings": 1148, "Discussion & Conclusion": 29}, "context": "Laser-focused concluding remarks delivering immediate takeaways in a single summary paragraph."}, {"title": "Google, AI Literacy, and the Learning Sciences: Multiple Modes of Research, Industry, and Practice Partnerships", "authors": "Victor R. Lee; Michael Madaio; Kristen Pilner Blair; Ben Garside; Aimee Welch; Ibrahim Oluwajoba", "year": 2026, "conference": "ICLS", "paper_type": "Symposium", "outlier_type": "Very High", "section": "Abstract & Introduction", "tokens": 6835, "pct_of_paper": 84.8, "total_tokens": 8063, "section_tokens": {"Abstract & Introduction": 6835, "Methodology & Context": 0, "Results & Findings": 0, "Discussion & Conclusion": 0}, "context": "Extensive theoretical grounding and front-matter distillation dedicating comprehensive framing and foundational literature."}, {"title": "Long and Winding Road to Coconstructing Knowledge in Design-Based Research Practice Partnerships", "authors": "Matan Barak", "year": 2025, "conference": "ICLS", "paper_type": "General", "outlier_type": "Very Low", "section": "Abstract & Introduction", "tokens": 57, "pct_of_paper": 3.0, "total_tokens": 1923, "section_tokens": {"Abstract & Introduction": 57, "Methodology & Context": 900, "Results & Findings": 62, "Discussion & Conclusion": 271}, "context": "Concise, rapid problem statement that transitions immediately into experimental or pedagogical design."}, {"title": "Towards a Robust Theory Toolbox for CSCL: Mechanisms, Models, and AI", "authors": "Peter Reimann; Alyssa Wise; Sten Ludvigsen; Davinia Hern\u00e1ndez-Leo; Fanjie Li; Hans C. Arnseth", "year": 2026, "conference": "CSCL", "paper_type": "Symposium", "outlier_type": "Very High", "section": "Methodology & Context", "tokens": 5789, "pct_of_paper": 66.3, "total_tokens": 8725, "section_tokens": {"Abstract & Introduction": 453, "Methodology & Context": 5789, "Results & Findings": 994, "Discussion & Conclusion": 169}, "context": "Comprehensive multi-framework methodological architecture detailing mechanisms, empirical data pipelines, and analytical rubrics."}, {"title": "Designing Supports for Science Teachers to Integrate Mathematics into Storyline Science Units", "authors": "William R. Penuel; Kevin W. McElhaney; Kate Henson; Nicola M. Hodkowski; Lauren McMahon; Jennifer Jacobs; Anthony Baker", "year": 2025, "conference": "ICLS", "paper_type": "General", "outlier_type": "Very Low", "section": "Methodology & Context", "tokens": 37, "pct_of_paper": 2.3, "total_tokens": 1580, "section_tokens": {"Abstract & Introduction": 352, "Methodology & Context": 37, "Results & Findings": 190, "Discussion & Conclusion": 667}, "context": "Highly condensed, minimalist design brief that summarizes iterative methodology in under two paragraphs."}, {"title": "Cultivating Wellbeing in Learning Environments: Storywork, Kinship and Affect With Lands and Waters", "authors": "Megan Bang; Jordan Sherry-Wagner; Forrest Bruce; Kaleb Germinaro; Miguel Angel Ovies-Bocanegra; Cece Hoffman; Nikki Barry; Anna Lees", "year": 2025, "conference": "ICLS", "paper_type": "Symposium", "outlier_type": "Very High", "section": "Results & Findings", "tokens": 4310, "pct_of_paper": 69.7, "total_tokens": 6182, "section_tokens": {"Abstract & Introduction": 879, "Methodology & Context": 310, "Results & Findings": 4310, "Discussion & Conclusion": 0}, "context": "In-depth qualitative and quantitative empirical findings presenting extensive interaction transcripts and multi-case observations."}];
  const CROWD_CONFIGS = [{"idx": 0, "layer": "bg", "left": 3, "bottom": 190, "scale": 0.78, "opacity": 0.5, "stroke": "#2563eb", "fill": "#dbeafe"}, {"idx": 1, "layer": "bg", "left": 19, "bottom": 210, "scale": 0.82, "opacity": 0.55, "stroke": "#0d9488", "fill": "#ccfbf1"}, {"idx": 2, "layer": "bg", "left": 37, "bottom": 225, "scale": 0.76, "opacity": 0.45, "stroke": "#ea580c", "fill": "#ffedd5"}, {"idx": 3, "layer": "bg", "left": 55, "bottom": 205, "scale": 0.84, "opacity": 0.55, "stroke": "#9333ea", "fill": "#f3e8ff"}, {"idx": 4, "layer": "bg", "left": 73, "bottom": 215, "scale": 0.8, "opacity": 0.48, "stroke": "#059669", "fill": "#d1fae5"}, {"idx": 5, "layer": "bg", "left": 89, "bottom": 195, "scale": 0.82, "opacity": 0.52, "stroke": "#e11d48", "fill": "#ffe4e6"}, {"idx": 6, "layer": "mg", "left": 8, "bottom": 105, "scale": 1.1, "opacity": 0.8, "stroke": "#0d9488", "fill": "#ccfbf1"}, {"idx": 7, "layer": "mg", "left": 23, "bottom": 130, "scale": 1.14, "opacity": 0.84, "stroke": "#2563eb", "fill": "#dbeafe"}, {"idx": 8, "layer": "mg", "left": 41, "bottom": 145, "scale": 1.08, "opacity": 0.78, "stroke": "#9333ea", "fill": "#f3e8ff"}, {"idx": 9, "layer": "mg", "left": 59, "bottom": 120, "scale": 1.15, "opacity": 0.84, "stroke": "#ea580c", "fill": "#ffedd5"}, {"idx": 10, "layer": "mg", "left": 77, "bottom": 135, "scale": 1.1, "opacity": 0.8, "stroke": "#2563eb", "fill": "#dbeafe"}, {"idx": 11, "layer": "mg", "left": 91, "bottom": 110, "scale": 1.12, "opacity": 0.82, "stroke": "#059669", "fill": "#d1fae5"}, {"idx": 12, "layer": "mg", "left": 2, "bottom": 75, "scale": 1.05, "opacity": 0.74, "stroke": "#e11d48", "fill": "#ffe4e6"}, {"idx": 13, "layer": "mg", "left": 31, "bottom": 80, "scale": 1.15, "opacity": 0.84, "stroke": "#ea580c", "fill": "#ffedd5"}, {"idx": 14, "layer": "mg", "left": 67, "bottom": 80, "scale": 1.12, "opacity": 0.82, "stroke": "#0d9488", "fill": "#ccfbf1"}, {"idx": 15, "layer": "fg", "left": 15, "bottom": 15, "scale": 1.38, "opacity": 0.96, "stroke": "#9333ea", "fill": "#f3e8ff"}, {"idx": 16, "layer": "fg", "left": 37, "bottom": 10, "scale": 1.45, "opacity": 0.98, "stroke": "#2563eb", "fill": "#dbeafe"}, {"idx": 17, "layer": "fg", "left": 51, "bottom": 22, "scale": 1.35, "opacity": 0.95, "stroke": "#0d9488", "fill": "#ccfbf1"}, {"idx": 18, "layer": "fg", "left": 74, "bottom": 12, "scale": 1.42, "opacity": 0.97, "stroke": "#ea580c", "fill": "#ffedd5"}, {"idx": 19, "layer": "fg", "left": 86, "bottom": 20, "scale": 1.36, "opacity": 0.95, "stroke": "#059669", "fill": "#d1fae5"}];

  // Helper: APA Author formatter
  function formatAuthorListApa(authorStr) {
    if (!authorStr) return "Unknown Author";
    const rawList = authorStr.split(/;| and |,/);
    const cleaned = rawList.map(a => a.trim()).filter(a => a.length > 1);
    if (cleaned.length === 0) return authorStr;
    if (cleaned.length === 1) return cleaned[0];
    if (cleaned.length === 2) return `${cleaned[0]} & ${cleaned[1]}`;
    return `${cleaned[0]} et al.`;
  }

  // Helper: Spline smoothing
  function pointsToSmoothPath(pts) {
    if (!pts || pts.length < 2) return "";
    let d = [`M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`];
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = i > 0 ? pts[i - 1] : pts[i];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = i < pts.length - 2 ? pts[i + 2] : p2;

      const cp1x = p1[0] + (p2[0] - p0[0]) / 6;
      const cp1y = p1[1] + (p2[1] - p0[1]) / 6;
      const cp2x = p2[0] - (p3[0] - p1[0]) / 6;
      const cp2y = p2[1] - (p3[1] - p1[1]) / 6;

      d.push(`C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`);
    }
    d.push("Z");
    return d.join(" ");
  }

  // Computes SVG Silhouette Geometry matching reference visual
  function computeSilhouetteGeometry(tokensObj, cx, totalH, maxTokens, svgW) {
    cx = cx || 55;
    totalH = totalH || 240;
    svgW = svgW || 110;
    maxTokens = maxTokens || 2200;

    const t1 = tokensObj ? (tokensObj["Abstract & Introduction"] || 0) : 600;
    const t2 = tokensObj ? (tokensObj["Methodology & Context"] || 0) : 500;
    const t3 = tokensObj ? (tokensObj["Results & Findings"] || 0) : 900;
    const t4 = tokensObj ? (tokensObj["Discussion & Conclusion"] || 0) : 650;

    const dotCy = 12;
    const dotR = 4.2;
    const yTop = 26;
    const yBase = totalH - 12;

    const bodyH = yBase - yTop;
    const secH = bodyH / 4;

    const y1 = yTop + secH * 0.5;
    const y2 = yTop + secH * 1.5;
    const y3 = yTop + secH * 2.5;
    const y4 = yTop + secH * 3.5;

    const maxSafeHalfW = cx - 10;
    const targetHalfW = cx * 0.82;
    const minW = Math.max(4, cx * 0.08);

    const w1 = Math.min(maxSafeHalfW, Math.max(minW, (t1 / maxTokens) * targetHalfW));
    const w2 = Math.min(maxSafeHalfW, Math.max(minW, (t2 / maxTokens) * targetHalfW));
    const w3 = Math.min(maxSafeHalfW, Math.max(minW, (t3 / maxTokens) * targetHalfW));
    const w4 = Math.min(maxSafeHalfW, Math.max(minW, (t4 / maxTokens) * targetHalfW));

    const rightPts = [
      [cx, yTop],
      [cx + w1 * 0.48, yTop + secH * 0.22],
      [cx + w1, y1],
      [cx + w2, y2],
      [cx + w3, y3],
      [cx + w4, y4],
      [cx + w4 * 0.40, yBase - secH * 0.25],
      [cx, yBase]
    ];

    const leftPts = rightPts.slice(1, -1).reverse().map(([x, y]) => [cx - (x - cx), y]);
    const allPts = rightPts.concat(leftPts).concat([[cx, yTop]]);
    const pathD = pointsToSmoothPath(allPts);

    return {
      pathD,
      cx,
      svgW,
      totalH,
      dotCy,
      dotR,
      yTop,
      yBase,
      secH
    };
  }

  // Build Crowd Stage
  function initSilhouetteCrowd() {
    const stage = document.getElementById("crowdStage");
    if (!stage) return;

    stage.innerHTML = "";
    const popover = document.getElementById("hudPopover");

    CROWD_CONFIGS.forEach((cfg, idx) => {
      const paper = OUTLIERS_DATA[cfg.idx] || OUTLIERS_DATA[idx % OUTLIERS_DATA.length];
      if (!paper) return;

      const svgW = 110;
      const svgH = 240;
      const cx = svgW / 2;
      const geom = computeSilhouetteGeometry(paper.section_tokens, cx, svgH, 2400, svgW);
      const clipId = `crowdClip-${idx}`;

      const figWrap = document.createElement("div");
      figWrap.className = `crowd-figure layer-${cfg.layer}`;
      figWrap.style.left = `${cfg.left}%`;
      figWrap.style.bottom = `${cfg.bottom}px`;
      figWrap.style.transform = `scale(${cfg.scale})`;
      figWrap.style.opacity = cfg.opacity;
      figWrap.style.zIndex = cfg.layer === "fg" ? 30 : (cfg.layer === "mg" ? 20 : 10);

      const shadowW = Math.round(80 * cfg.scale);
      const shadowH = Math.round(18 * cfg.scale);

      figWrap.innerHTML = `
        <div class="figure-shadow" style="width:${shadowW}px; height:${shadowH}px;"></div>
        <svg class="figure-svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
          <defs>
            <clipPath id="${clipId}">
              <path d="${geom.pathD}" />
            </clipPath>
          </defs>

          <!-- 4 Pastel Section Fills -->
          <g clip-path="url(#${clipId})">
            <rect x="0" y="0" width="${svgW}" height="${geom.yTop + geom.secH}" fill="#dbeafe" opacity="0.92" />
            <rect x="0" y="${geom.yTop + geom.secH}" width="${svgW}" height="${geom.secH}" fill="#ccfbf1" opacity="0.92" />
            <rect x="0" y="${geom.yTop + 2 * geom.secH}" width="${svgW}" height="${geom.secH}" fill="#ffedd5" opacity="0.92" />
            <rect x="0" y="${geom.yTop + 3 * geom.secH}" width="${svgW}" height="${svgH - (geom.yTop + 3 * geom.secH)}" fill="#f3e8ff" opacity="0.92" />
          </g>

          <!-- Outer Contour Stroke -->
          <path d="${geom.pathD}" fill="none" stroke="${cfg.stroke}" stroke-width="1.6" stroke-linejoin="round" />

          <!-- Floating Abstract Head Dot -->
          <circle cx="${cx}" cy="${geom.dotCy}" r="${geom.dotR}" fill="${cfg.stroke}" stroke="#ffffff" stroke-width="1.4" />

          <!-- Center Spine Dashed Axis -->
          <line x1="${cx}" y1="${geom.yTop}" x2="${cx}" y2="${geom.yBase}" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="2,2" opacity="0.9" />
        </svg>
      `;

      // Hover HUD interaction
      const searchUrl = `./viewer.html?keywords=${encodeURIComponent(paper.title)}`;

      // Render HUD content
      const showFigureHud = (e, isMobileTap = false) => {
        if (!popover) return;
        const authorApa = formatAuthorListApa(paper.authors);
        const isHigh = paper.outlier_type === "Very High";
        const badgeLabel = `${isHigh ? "Maxxed" : "Mini"} • ${paper.section}`;

        popover.innerHTML = `
          <div class="hud-header-row">
            <span class="hud-genre-badge" style="color:${cfg.stroke}; border-color:${cfg.stroke}55; background:${cfg.stroke}18;">${badgeLabel}</span>
            <span class="hud-year-badge">${paper.conference} ${paper.year} • ${paper.paper_type}</span>
            ${isMobileTap ? `<button class="hud-close-btn" id="hudCloseBtn" aria-label="Close">&times;</button>` : ""}
          </div>
          <div class="hud-title">${paper.title}</div>
          <div class="hud-authors">${authorApa} (${paper.year})</div>
          <div class="hud-outlier-box">
            <div class="hud-outlier-label">
              <span>${isHigh ? "📈 Max Length Outlier" : "📉 Min Length Outlier"}</span>
              <span style="font-family:var(--font-mono); font-size:0.72rem;">${paper.tokens.toLocaleString()} tk (${paper.pct_of_paper}%)</span>
            </div>
            <div class="hud-outlier-context">${paper.context}</div>
          </div>
          ${isMobileTap 
            ? `<a href="${searchUrl}" class="hud-mobile-action-link">Open in Review Viewer ↗</a>` 
            : `<div class="hud-action-hint">Click figure to explore paper in Review Viewer ↗</div>`
          }
        `;
        popover.classList.add("visible");

        if (isMobileTap) {
          const closeBtn = popover.querySelector("#hudCloseBtn");
          if (closeBtn) {
            closeBtn.addEventListener("click", (ev) => {
              ev.stopPropagation();
              popover.classList.remove("visible");
            });
          }
        } else {
          positionHud(e, popover);
        }
      };

      // Desktop Hover HUD interaction
      figWrap.addEventListener("mouseenter", (e) => {
        if (window.innerWidth <= 768) return;
        showFigureHud(e, false);
      });

      figWrap.addEventListener("mousemove", (e) => {
        if (window.innerWidth <= 768) return;
        if (popover && popover.classList.contains("visible")) {
          positionHud(e, popover);
        }
      });

      figWrap.addEventListener("mouseleave", () => {
        if (window.innerWidth <= 768) return;
        if (popover) popover.classList.remove("visible");
      });

      // Click / Tap Handler
      figWrap.addEventListener("click", (e) => {
        if (window.innerWidth <= 768) {
          e.stopPropagation();
          showFigureHud(e, true);
        } else {
          window.open(searchUrl, "_blank");
        }
      });

      stage.appendChild(figWrap);
    });

    // Close HUD on outside tap for mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 768 && popover && popover.classList.contains("visible")) {
        if (!popover.contains(e.target) && !e.target.closest(".crowd-figure")) {
          popover.classList.remove("visible");
        }
      }
    });
  }

  // HUD Positioning
  function positionHud(e, popover) {
    if (window.innerWidth <= 768) return;
    const w = 360;
    const h = 210;
    let x = e.clientX + 16;
    let y = e.clientY + 16;

    if (x + w > window.innerWidth - 20) {
      x = e.clientX - w - 16;
    }
    if (y + h > window.innerHeight - 20) {
      y = e.clientY - h - 16;
    }

    popover.style.left = `${Math.max(12, x)}px`;
    popover.style.top = `${Math.max(12, y)}px`;
  }

  // Toast Notification Helper
  function showToast(message) {
    let toast = document.getElementById("toastNotice");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toastNotice";
      toast.className = "toast-notice";
      document.body.appendChild(toast);
    }
    toast.innerHTML = message;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2600);
  }

  // Robust clipboard copy with fallback
  function copyTextToClipboard(text, successCb) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(() => {
        if (successCb) successCb();
      }).catch(() => {
        fallbackCopyText(text, successCb);
      });
    } else {
      fallbackCopyText(text, successCb);
    }
  }

  function fallbackCopyText(text, successCb) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand("copy");
      if (successCb) successCb();
    } catch (err) {
      console.error("Fallback copy failed:", err);
    }
    textArea.remove();
  }

  // Setup Clipboard Copy for Prompts & Citations
  function setupClipboardActions() {
    document.querySelectorAll(".btn-copy-prompt").forEach(btn => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-prompt-id");
        const promptEl = document.getElementById(targetId);
        if (!promptEl) return;
        
        const textToCopy = promptEl.textContent.trim();
        copyTextToClipboard(textToCopy, () => {
          const origText = btn.innerHTML;
          btn.innerHTML = "✓ Copied!";
          btn.classList.add("copied");
          showToast("📋 Prompt copied to clipboard!");
          setTimeout(() => {
            btn.innerHTML = origText;
            btn.classList.remove("copied");
          }, 2000);
        });
      });
    });

    const citeCopyBtn = document.getElementById("btnCopyCite");
    const headerCiteBtn = document.getElementById("headerCiteBtn");

    const apaText = "Jhunja, R. (2026). 10 Years ISLS Proceedings Research Repository & Agentic Review System (2016–2026) [Web platform and dataset commons]. International Society of the Learning Sciences. https://isls-repository.org";

    const handleCiteCopy = () => {
      copyTextToClipboard(apaText, () => {
        showToast("✓ Copied APA 7 Citation to clipboard!");
      });
    };

    if (citeCopyBtn) citeCopyBtn.addEventListener("click", handleCiteCopy);
    if (headerCiteBtn) headerCiteBtn.addEventListener("click", handleCiteCopy);

    const bibToggleBtn = document.getElementById("btnToggleBibtex");
    const bibBox = document.getElementById("bibtexBox");
    if (bibToggleBtn && bibBox) {
      bibToggleBtn.addEventListener("click", () => {
        const isOpen = bibBox.classList.toggle("open");
        bibToggleBtn.textContent = isOpen ? "Hide BibTeX" : "Show BibTeX";
      });
    }

    const setupPromptBtn = document.getElementById("btnCopySetupPrompt");
    const setupPromptEl = document.getElementById("setupPromptText");
    if (setupPromptBtn && setupPromptEl) {
      setupPromptBtn.addEventListener("click", () => {
        copyTextToClipboard(setupPromptEl.textContent.trim(), () => {
          showToast("✓ Copied 1-Click Setup Prompt to clipboard!");
          const origHtml = setupPromptBtn.innerHTML;
          setupPromptBtn.innerHTML = `<span>✓ Copied!</span>`;
          setTimeout(() => {
            setupPromptBtn.innerHTML = origHtml;
          }, 2000);
        });
      });
    }

    const gitCloneBtn = document.getElementById("btnCopyGitClone");
    if (gitCloneBtn) {
      gitCloneBtn.addEventListener("click", () => {
        const cmd = "git clone https://github.com/rohanjhunja/isls-repository-2026.git";
        copyTextToClipboard(cmd, () => {
          showToast("✓ Copied git clone command to clipboard!");
          const origHtml = gitCloneBtn.innerHTML;
          gitCloneBtn.innerHTML = `<span>✓ Copied!</span>`;
          setTimeout(() => {
            gitCloneBtn.innerHTML = origHtml;
          }, 2000);
        });
      });
    }
  }

  // Initialize Mermaid diagrams
  function initMermaid() {
    if (window.mermaid) {
      window.mermaid.initialize({
        startOnLoad: true,
        theme: "neutral",
        themeVariables: {
          fontFamily: "Inter, sans-serif",
          fontSize: "13px",
          primaryColor: "#eff6ff",
          primaryTextColor: "#0f172a",
          primaryBorderColor: "#93c5fd",
          lineColor: "#64748b",
          secondaryColor: "#f0fdfa",
          tertiaryColor: "#f8fafc",
          clusterBkg: "#ffffff",
          clusterBorder: "#e2e8f0"
        },
        flowchart: {
          curve: "basis",
          useMaxWidth: true,
          htmlLabels: true
        }
      });
    }
  }

  // Header appears only when scrolled past the hero section
  function setupHeaderScroll() {
    const header = document.getElementById("coverHeader");
    const hero = document.getElementById("heroSection") || document.querySelector(".hero-section");
    if (!header) return;

    const onScroll = () => {
      const threshold = hero ? (hero.offsetTop + hero.offsetHeight - 80) : 400;
      if (window.scrollY > threshold) {
        header.classList.add("header-visible");
      } else {
        header.classList.remove("header-visible");
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    const scrollBtn = document.querySelector(".btn-hero-scroll");
    if (scrollBtn) {
      scrollBtn.addEventListener("click", () => {
        setTimeout(() => {
          header.classList.add("header-visible");
        }, 350);
      });
    }
  }

  // Hero Section Visual Guide Popover Toggle
  function setupHeroInfoGuide() {
    const wrapper = document.getElementById("heroInfoWrapper");
    const btn = document.getElementById("heroInfoBtn");
    const closeBtn = document.getElementById("heroInfoCloseBtn");
    if (!wrapper || !btn) return;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      wrapper.classList.toggle("open");
    });

    if (closeBtn) {
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        wrapper.classList.remove("open");
      });
    }

    document.addEventListener("click", (e) => {
      if (!wrapper.contains(e.target)) {
        wrapper.classList.remove("open");
      }
    });
  }

  // Header Accordion on Mobile (Toggle Navigation Menu)
  function setupHeaderAccordion() {
    const toggleBtn = document.getElementById("headerAccordionToggle");
    const nav = document.getElementById("coverHeaderNav");
    if (!toggleBtn || !nav) return;

    toggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = nav.classList.toggle("is-open");
      toggleBtn.classList.toggle("is-open", isOpen);
      toggleBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    // Close on navigation link click
    nav.querySelectorAll("a, button").forEach((el) => {
      el.addEventListener("click", () => {
        nav.classList.remove("is-open");
        toggleBtn.classList.remove("is-open");
        toggleBtn.setAttribute("aria-expanded", "false");
      });
    });

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (!nav.contains(e.target) && !toggleBtn.contains(e.target)) {
        nav.classList.remove("is-open");
        toggleBtn.classList.remove("is-open");
        toggleBtn.setAttribute("aria-expanded", "false");
      }
    });

    // Close on window scroll
    window.addEventListener("scroll", () => {
      if (nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggleBtn.classList.remove("is-open");
        toggleBtn.setAttribute("aria-expanded", "false");
      }
    }, { passive: true });
  }

  // Advances Section 3D Flip Card Toggle (supports touch, tap and keyboard)
  function setupAdvancesFlipCards() {
    const cards = document.querySelectorAll(".advance-flip-card");
    cards.forEach((card) => {
      let touchStartX = 0;
      let touchStartY = 0;
      let isTouch = false;

      card.addEventListener("touchstart", (e) => {
        if (e.touches && e.touches.length === 1) {
          isTouch = true;
          touchStartX = e.touches[0].clientX;
          touchStartY = e.touches[0].clientY;
        }
      }, { passive: true });

      card.addEventListener("touchend", (e) => {
        if (!isTouch) return;
        if (e.changedTouches && e.changedTouches.length === 1) {
          const dx = e.changedTouches[0].clientX - touchStartX;
          const dy = e.changedTouches[0].clientY - touchStartY;
          // Only trigger flip if it was a clean tap (< 10px movement), not a vertical scroll
          if (Math.hypot(dx, dy) < 10) {
            e.preventDefault();
            card.classList.toggle("is-flipped");
          }
        }
        setTimeout(() => { isTouch = false; }, 300);
      });

      card.addEventListener("click", (e) => {
        // Prevent double toggle if touchend already fired
        if (isTouch) return;
        card.classList.toggle("is-flipped");
      });

      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          card.classList.toggle("is-flipped");
        }
      });
    });
  }

  // Technical Structure Diagram: Expand & Pan Modal (Touch pan, Pinch zoom, Zoom buttons)
  function setupDiagramModal() {
    const expandBtn = document.getElementById("btnExpandDiagram");
    const mainSvg = document.getElementById("mainPipelineSvg");
    const modal = document.getElementById("diagramModal");
    const backdrop = document.getElementById("diagramModalBackdrop");
    const closeBtn = document.getElementById("btnCloseDiagModal");
    const viewport = document.getElementById("diagramModalViewport");
    const canvas = document.getElementById("diagramModalCanvas");
    const btnZoomIn = document.getElementById("btnZoomIn");
    const btnZoomOut = document.getElementById("btnZoomOut");
    const btnZoomReset = document.getElementById("btnZoomReset");

    if (!expandBtn || !modal || !viewport || !canvas || !mainSvg) return;

    let scale = 1;
    let translateX = 0;
    let translateY = 0;
    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let initialPinchDistance = 0;
    let initialPinchScale = 1;

    function updateTransform() {
      canvas.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    function resetView() {
      const vpRect = viewport.getBoundingClientRect();
      const svgW = 1024;
      const svgH = 416;
      const fitScale = Math.min((vpRect.width - 32) / svgW, (vpRect.height - 32) / svgH);
      scale = Math.max(0.65, Math.min(fitScale, 1.25));
      translateX = (vpRect.width - svgW * scale) / 2;
      translateY = (vpRect.height - svgH * scale) / 2;
      updateTransform();
    }

    function openModal() {
      if (!canvas.hasChildNodes()) {
        const clone = mainSvg.cloneNode(true);
        clone.id = "clonedPipelineSvg";
        canvas.appendChild(clone);
      }
      modal.classList.add("is-active");
      modal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
      requestAnimationFrame(() => {
        resetView();
      });
    }

    function closeModal() {
      modal.classList.remove("is-active");
      modal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }

    expandBtn.addEventListener("click", openModal);

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (backdrop) backdrop.addEventListener("click", closeModal);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && modal.classList.contains("is-active")) {
        closeModal();
      }
    });

    // Zoom buttons
    if (btnZoomIn) {
      btnZoomIn.addEventListener("click", () => {
        scale = Math.min(scale * 1.3, 3.8);
        updateTransform();
      });
    }
    if (btnZoomOut) {
      btnZoomOut.addEventListener("click", () => {
        scale = Math.max(scale / 1.3, 0.35);
        updateTransform();
      });
    }
    if (btnZoomReset) {
      btnZoomReset.addEventListener("click", resetView);
    }

    // Pointer Drag Panning
    viewport.addEventListener("pointerdown", (e) => {
      isDragging = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      viewport.classList.add("is-dragging");
      viewport.setPointerCapture(e.pointerId);
    });

    viewport.addEventListener("pointermove", (e) => {
      if (!isDragging) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform();
    });

    const endDrag = (e) => {
      if (isDragging) {
        isDragging = false;
        viewport.classList.remove("is-dragging");
        try { viewport.releasePointerCapture(e.pointerId); } catch(err) {}
      }
    };

    viewport.addEventListener("pointerup", endDrag);
    viewport.addEventListener("pointercancel", endDrag);

    // Touch Pinch to Zoom
    viewport.addEventListener("touchstart", (e) => {
      if (e.touches.length === 2) {
        isDragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        initialPinchDistance = Math.hypot(dx, dy);
        initialPinchScale = scale;
      }
    }, { passive: true });

    viewport.addEventListener("touchmove", (e) => {
      if (e.touches.length === 2 && initialPinchDistance > 0) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const currentDistance = Math.hypot(dx, dy);
        const factor = currentDistance / initialPinchDistance;
        scale = Math.max(0.35, Math.min(initialPinchScale * factor, 4.0));
        updateTransform();
      }
    }, { passive: true });

    viewport.addEventListener("touchend", () => {
      initialPinchDistance = 0;
    }, { passive: true });

    // Wheel zoom
    viewport.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.88;
      scale = Math.max(0.35, Math.min(scale * zoomFactor, 4.0));
      updateTransform();
    }, { passive: false });
  }

  // Researcher Prompts 3-Card Row Accordion (Single Active Expanded)
  function setupUseCaseAccordion() {
    const cards = document.querySelectorAll(".use-case-card");
    cards.forEach((card) => {
      card.addEventListener("click", (e) => {
        // Prevent toggle if clicking inside a copy button or link
        if (e.target.closest(".btn-copy-prompt") || e.target.closest("a")) {
          return;
        }
        if (card.classList.contains("is-collapsed")) {
          cards.forEach((c) => {
            c.classList.remove("is-expanded");
            c.classList.add("is-collapsed");
            const btn = c.querySelector(".use-case-expand-btn");
            if (btn) btn.setAttribute("aria-expanded", "false");
          });
          card.classList.remove("is-collapsed");
          card.classList.add("is-expanded");
          const btn = card.querySelector(".use-case-expand-btn");
          if (btn) btn.setAttribute("aria-expanded", "true");
        }
      });
    });
  }

  function init() {
    initSilhouetteCrowd();
    setupClipboardActions();
    setupHeaderScroll();
    setupHeroInfoGuide();
    setupHeaderAccordion();
    setupAdvancesFlipCards();
    setupDiagramModal();
    setupUseCaseAccordion();
    initMermaid();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
