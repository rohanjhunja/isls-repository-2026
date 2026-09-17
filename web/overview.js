// ISLS 10-Year Research Observatory (2016–2026) Overview Script
(function() {
  'use strict';

  // Global State
  let metaData = null;
  let currentDimension = 'conceptualisation';
  let currentHierarchyLevel = 2; // 1 = Family, 2 = Granular Label
  let currentCentrality = 1;
  let currentMode = 'relative'; // 'count', 'relative' (100% full height), or 'conference'
  let selectedLabels = new Set();

  // Chart Instances
  const charts = {
    trends: null,
    density: null,
    network: null,
    citations: null
  };

  // Distinct Categorical Color Palette (high perceptual contrast across color wheel)
  const DISTINCT_PALETTE = [
    '#2563eb', // 0: Vivid Royal Blue
    '#16a34a', // 1: Fresh Emerald Green
    '#ea580c', // 2: Bright Tangerine Orange
    '#9333ea', // 3: Rich Royal Purple
    '#dc2626', // 4: Crimson Red
    '#d97706', // 5: Golden Amber
    '#0d9488', // 6: Deep Teal
    '#db2777', // 7: Rose Pink
    '#4f46e5', // 8: Indigo
    '#65a30d', // 9: Lime Olive
    '#0284c7', // 10: Sky Blue
    '#c026d3', // 11: Fuchsia
    '#b45309', // 12: Warm Bronze
    '#059669', // 13: Jade
    '#7c2d12', // 14: Russet Brown
    '#334155'  // 15: Slate
  ];

  // Specific high-contrast distinct colors for Broad Theoretical Families
  const BROAD_FAMILY_COLORS = {
    'Collaborative & Dialogic': '#2563eb',      // Royal Blue
    'Cognitive & Constructivist': '#16a34a',    // Fresh Emerald Green
    'Design & Participatory': '#ea580c',        // Bright Orange
    'Critical, Equity & Culture': '#9333ea',    // Vivid Purple
    'Sociocultural & Historical': '#dc2626',    // Crimson Red
    'Embodied & Sensorimotor': '#d97706',       // Golden Amber
    // TPACK single-family fallbacks if Level 1 is clicked
    'Technology Knowledge (TK)': '#2563eb',
    'Pedagogical Knowledge (PK)': '#16a34a',
    'Content Knowledge (CK)': '#ea580c',
    'Setting': '#9333ea',
    'Subject': '#d97706'
  };

  function getLabelColor(labelName, idx = 0) {
    if (BROAD_FAMILY_COLORS[labelName]) {
      return BROAD_FAMILY_COLORS[labelName];
    }
    return DISTINCT_PALETTE[idx % DISTINCT_PALETTE.length];
  }

  // Strict APA 7th Author Formatting Helpers
  function formatAuthorApa(name) {
    if (!name) return '';
    name = name.replace(/[,;.]+$/, '').trim();
    if (!name) return '';
    if (name.includes(',')) {
      const parts = name.split(',');
      const last = parts[0].trim();
      const firstTokens = parts[1].trim().split(/\s+/).filter(t => t);
      const initials = firstTokens.map(t => {
        const clean = t.replace(/[^a-zA-Z]/g, '');
        return clean ? clean[0].toUpperCase() + '.' : '';
      }).filter(Boolean);
      return initials.length > 0 ? `${last}, ${initials.join(' ')}` : last;
    }
    const tokens = name.split(/\s+/).filter(Boolean);
    if (tokens.length === 1) return tokens[0];
    const last = tokens[tokens.length - 1];
    const firstTokens = tokens.slice(0, -1);
    const initials = firstTokens.map(t => {
      const clean = t.replace(/[^a-zA-Z]/g, '');
      return clean ? clean[0].toUpperCase() + '.' : '';
    }).filter(Boolean);
    return initials.length > 0 ? `${last}, ${initials.join(' ')}` : last;
  }

  function formatAuthorListApa(authorsStr) {
    if (!authorsStr) return '';
    if (authorsStr.includes('&') && authorsStr.includes('.')) return authorsStr;
    const delimiter = authorsStr.includes(';') ? ';' : ',';
    const names = authorsStr.split(delimiter).map(s => s.trim()).filter(Boolean);
    const apaNames = names.map(n => formatAuthorApa(n)).filter(Boolean);
    if (apaNames.length === 0) return authorsStr;
    if (apaNames.length === 1) return apaNames[0];
    if (apaNames.length === 2) return `${apaNames[0]} & ${apaNames[1]}`;
    return `${apaNames.slice(0, -1).join(', ')}, & ${apaNames[apaNames.length - 1]}`;
  }

  // DOM Elements
  const dimensionSelect = document.getElementById('dimensionSelect');
  const floatingActiveDimPill = document.getElementById('floatingActiveDimPill');
  const btnLevel1 = document.getElementById('btnLevel1');
  const btnLevel2 = document.getElementById('btnLevel2');
  const labelsList = document.getElementById('labelsList');
  const labelSearchInput = document.getElementById('labelSearchInput');
  const btnSelectAll = document.getElementById('btnSelectAll');
  const btnClearAll = document.getElementById('btnClearAll');
  const btnSelectTop = document.getElementById('btnSelectTop');
  const centralityGroup = document.getElementById('centralityGroup');

  // Drawer / Floating Menu Elements
  const btnOpenControls = document.getElementById('btnOpenControls');
  const filterDrawer = document.getElementById('filterDrawer');
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  const btnCloseFilter = document.getElementById('btnCloseFilter');

  // Trends Toolbar Controls
  let currentTimeGranularity = 'biannual'; // 'biannual' (default) or 'yearwise'
  const btnTimeBiannual = document.getElementById('btnTimeBiannual');
  const btnTimeYearwise = document.getElementById('btnTimeYearwise');
  const btnToggleCount = document.getElementById('btnToggleCount');
  const btnToggleRelative = document.getElementById('btnToggleRelative');
  const btnToggleConference = document.getElementById('btnToggleConference');
  const trendsChartHeaderTitle = document.getElementById('trendsChartHeaderTitle');

  // Network Controls
  const networkMinWeight = document.getElementById('networkMinWeight');
  const btnResetNetwork = document.getElementById('btnResetNetwork');

  // Knowledge Lineage State & Elements
  let currentLineageFilter = 'all'; // 'all', 'citations', 'collaborations'
  let lineageRawData = null;
  const btnLineageAll = document.getElementById('btnLineageAll');
  const btnLineageCites = document.getElementById('btnLineageCites');
  const btnLineageCollabs = document.getElementById('btnLineageCollabs');
  const seminalWorksTableBody = document.getElementById('seminalWorksTableBody');

  // Paper Inspector Elements
  const paperInspector = document.getElementById('paperInspector');
  const inspectorBackdrop = document.getElementById('inspectorBackdrop');
  const inspectorTitle = document.getElementById('inspectorTitle');
  const inspectorContent = document.getElementById('inspectorContent');
  const btnCloseInspector = document.getElementById('btnCloseInspector');

  // Initialize
  async function init() {
    try {
      let res;
      try {
        res = await fetch('/api/overview/meta');
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch('data/overview_static/meta.json');
      }
      metaData = await res.json();

      // Populate metric counters in hero
      if (document.getElementById('cntPapers')) {
        document.getElementById('cntPapers').textContent = metaData.total_papers.toLocaleString();
      }
      if (document.getElementById('cntAuthors')) {
        document.getElementById('cntAuthors').textContent = metaData.total_authors.toLocaleString();
      }
      if (document.getElementById('cntLabels')) {
        document.getElementById('cntLabels').textContent = metaData.total_labels.toLocaleString();
      }
      if (document.getElementById('cntCollabs')) {
        document.getElementById('cntCollabs').textContent = metaData.total_collaborations.toLocaleString();
      }
      if (document.getElementById('cntCitations')) {
        document.getElementById('cntCitations').textContent = metaData.total_citations.toLocaleString();
      }

      // Default label selection (Top 6)
      selectTopLabels(6);

      // Render filter list in drawer
      renderLabelsList();
      updateFloatingPill();

      // Bind all UI event listeners
      bindEvents();
      updateTrendsHeaderTitle();

      // Load all 4 story charts simultaneously
      loadAllCharts();

      // Load Beautiful Papers section
      await initBeautifulPapers();

      // Global window resize listener
      window.addEventListener('resize', () => {
        Object.values(charts).forEach(c => {
          if (c) c.resize();
        });
      });

    } catch (err) {
      console.error('Failed to load overview metadata:', err);
    }
  }

  function getActiveDimObj() {
    if (!metaData || !metaData.dimensions) return null;
    return metaData.dimensions.find(d => d.id === currentDimension);
  }

  function updateFloatingPill() {
    if (!floatingActiveDimPill) return;
    const dimObj = getActiveDimObj();
    if (dimObj) {
      const nameMap = {
        'conceptualisation': 'Theories',
        'tpack_tk': 'TK (Tech)',
        'tpack_pk': 'PK (Pedagogy)',
        'tpack_ck': 'CK (Content)',
        'setting': 'Settings',
        'subject': 'Subjects'
      };
      floatingActiveDimPill.textContent = nameMap[currentDimension] || dimObj.name;
    }
  }

  function selectTopLabels(n = 6) {
    selectedLabels.clear();
    const dimObj = getActiveDimObj();
    if (!dimObj) return;

    if (currentHierarchyLevel === 1) {
      // Level 1: Broad Families
      dimObj.families.forEach(f => selectedLabels.add(f.family));
    } else {
      // Level 2: Granular Labels
      let allLabels = [];
      dimObj.families.forEach(f => {
        f.labels.forEach(l => allLabels.push(l));
      });
      allLabels.sort((a, b) => b.count - a.count);
      allLabels.slice(0, n).forEach(l => selectedLabels.add(l.name));
    }
  }

  function renderLabelsList(filterText = '') {
    if (!labelsList) return;
    labelsList.innerHTML = '';
    const dimObj = getActiveDimObj();
    if (!dimObj) return;

    if (currentHierarchyLevel === 1) {
      // Render families
      dimObj.families.forEach((fam, fIdx) => {
        if (filterText && !fam.family.toLowerCase().includes(filterText.toLowerCase())) return;

        const famTotal = fam.labels.reduce((acc, l) => acc + l.count, 0);
        const isSelected = selectedLabels.has(fam.family);
        const color = getLabelColor(fam.family, fIdx);

        const item = document.createElement('div');
        item.className = 'label-item-pill' + (isSelected ? ' selected' : '');
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
            <input type="checkbox" ${isSelected ? 'checked' : ''} style="pointer-events:none; accent-color: ${color};">
            <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background-color:${color}; flex-shrink:0;"></span>
            <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${fam.family}"><strong>${fam.family}</strong></span>
          </div>
          <span style="font-size:0.75rem; color:var(--text-muted); font-weight:600; padding:1px 6px; background:#f1f5f9; border-radius:10px;">${famTotal}</span>
        `;

        item.addEventListener('click', () => {
          if (selectedLabels.has(fam.family)) {
            selectedLabels.delete(fam.family);
          } else {
            selectedLabels.add(fam.family);
          }
          renderLabelsList(labelSearchInput ? labelSearchInput.value : '');
          loadTrendsChart();
          loadDensityChart();
        });

        labelsList.appendChild(item);
      });

    } else {
      // Render granular labels
      let globalLIdx = 0;
      dimObj.families.forEach(fam => {
        fam.labels.forEach(lbl => {
          const lIdx = globalLIdx++;
          if (filterText && !lbl.name.toLowerCase().includes(filterText.toLowerCase())) return;

          const isSelected = selectedLabels.has(lbl.name);
          const color = getLabelColor(lbl.name, lIdx);
          const item = document.createElement('div');
          item.className = 'label-item-pill' + (isSelected ? ' selected' : '');
          item.innerHTML = `
            <div style="display:flex; align-items:center; gap:8px; overflow:hidden;">
              <input type="checkbox" ${isSelected ? 'checked' : ''} style="pointer-events:none; accent-color: ${color};">
              <span style="display:inline-block; width:9px; height:9px; border-radius:50%; background-color:${color}; flex-shrink:0;"></span>
              <span style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${fam.family}: ${lbl.name}">${lbl.name}</span>
            </div>
            <span style="font-size:0.75rem; color:var(--text-muted); font-weight:600; padding:1px 6px; background:#f1f5f9; border-radius:10px;">${lbl.count}</span>
          `;

          item.addEventListener('click', () => {
            if (selectedLabels.has(lbl.name)) {
              selectedLabels.delete(lbl.name);
            } else {
              selectedLabels.add(lbl.name);
            }
            renderLabelsList(labelSearchInput ? labelSearchInput.value : '');
            loadTrendsChart();
            loadDensityChart();
          });

          labelsList.appendChild(item);
        });
      });
    }
  }

  function initChartInstance(chartKey) {
    const containerId = 'chart' + chartKey.charAt(0).toUpperCase() + chartKey.slice(1);
    const container = document.getElementById(containerId);
    if (!container) return null;

    if (!charts[chartKey]) {
      // Initialize ECharts with light-theme defaults
      charts[chartKey] = echarts.init(container, null, { renderer: 'canvas' });

      // Attach click handlers
      if (chartKey === 'trends') {
        charts.trends.on('click', function(params) {
          if (params.seriesName && params.name) {
            openPaperInspector(currentDimension, params.seriesName, params.name);
          }
        });
      } else if (chartKey === 'density') {
        charts.density.on('click', function(params) {
          if (params.data && params.data[3]) {
            openPaperInspector(currentDimension, params.data[3], null);
          }
        });
      } else if (chartKey === 'network') {
        charts.network.on('click', function(params) {
          if (params.dataType === 'node') {
            openPaperInspector(null, null, null, params.data.name);
          }
        });
      } else if (chartKey === 'citations') {
        charts.citations.on('click', function(params) {
          if (params.dataType === 'node' && params.data) {
            openPaperInspector(null, null, null, params.data.name);
          }
        });
      }
    }

    return charts[chartKey];
  }

  function loadAllCharts() {
    loadTrendsChart();
    loadDensityChart();
    loadNetworkChart();
    loadCitationsChart();
  }

  function updateTrendsHeaderTitle() {
    if (!trendsChartHeaderTitle) return;
    const isBiannual = (currentTimeGranularity === 'biannual');
    if (currentMode === 'count') {
      trendsChartHeaderTitle.textContent = isBiannual
        ? 'Bi-annual Paper Publication Volume Over Time'
        : 'Annual Paper Publication Volume Over Time';
    } else if (currentMode === 'conference') {
      trendsChartHeaderTitle.textContent = isBiannual
        ? 'Conference Penetration (% of All Proceedings Papers Each 2-Year Cycle)'
        : 'Conference Penetration (% of All Proceedings Papers Each Year)';
    } else {
      trendsChartHeaderTitle.textContent = isBiannual
        ? '100% Proportional Share of Mindshare Over Time (2-Year Cycles)'
        : '100% Proportional Share of Mindshare Over Time (Selected Categories)';
    }
  }

  function bindEvents() {
    // Header Mobile Accordion Toggle
    const headerToggle = document.getElementById('overviewHeaderToggle');
    const headerLinks = document.getElementById('overviewHeaderLinks');
    if (headerToggle && headerLinks) {
      headerToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = headerLinks.classList.toggle('is-open');
        headerToggle.classList.toggle('is-open', isOpen);
        headerToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });

      headerLinks.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
          headerLinks.classList.remove('is-open');
          headerToggle.classList.remove('is-open');
          headerToggle.setAttribute('aria-expanded', 'false');
        });
      });

      document.addEventListener('click', (e) => {
        if (!headerLinks.contains(e.target) && !headerToggle.contains(e.target)) {
          headerLinks.classList.remove('is-open');
          headerToggle.classList.remove('is-open');
          headerToggle.setAttribute('aria-expanded', 'false');
        }
      });
    }

    // Floating Drawer Open / Close
    if (btnOpenControls) {
      btnOpenControls.addEventListener('click', openFilterDrawer);
    }
    if (btnCloseFilter) {
      btnCloseFilter.addEventListener('click', closeFilterDrawer);
    }
    if (drawerBackdrop) {
      drawerBackdrop.addEventListener('click', closeFilterDrawer);
    }

    // Paper Inspector Close
    if (btnCloseInspector) {
      btnCloseInspector.addEventListener('click', closePaperInspector);
    }
    if (inspectorBackdrop) {
      inspectorBackdrop.addEventListener('click', closePaperInspector);
    }

    // Dimension Select
    if (dimensionSelect) {
      dimensionSelect.addEventListener('change', (e) => {
        currentDimension = e.target.value;
        updateFloatingPill();
        selectTopLabels(6);
        renderLabelsList();
        loadTrendsChart();
        loadDensityChart();
      });
    }

    // Level 1 / Level 2 Buttons
    if (btnLevel1) {
      btnLevel1.addEventListener('click', () => {
        currentHierarchyLevel = 1;
        btnLevel1.classList.add('active');
        btnLevel2.classList.remove('active');
        selectTopLabels(6);
        renderLabelsList();
        loadTrendsChart();
      });
    }

    if (btnLevel2) {
      btnLevel2.addEventListener('click', () => {
        currentHierarchyLevel = 2;
        btnLevel2.classList.add('active');
        btnLevel1.classList.remove('active');
        selectTopLabels(6);
        renderLabelsList();
        loadTrendsChart();
      });
    }

    // Centrality Threshold Buttons
    if (centralityGroup) {
      centralityGroup.querySelectorAll('.btn-pill-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
          centralityGroup.querySelectorAll('.btn-pill-toggle').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentCentrality = parseInt(btn.dataset.val, 10);
          loadTrendsChart();
        });
      });
    }

    // Label Search
    if (labelSearchInput) {
      labelSearchInput.addEventListener('input', (e) => {
        renderLabelsList(e.target.value);
      });
    }

    // Quick Label Selection Buttons
    if (btnSelectAll) {
      btnSelectAll.addEventListener('click', () => {
        const dimObj = getActiveDimObj();
        if (!dimObj) return;
        if (currentHierarchyLevel === 1) {
          dimObj.families.forEach(f => selectedLabels.add(f.family));
        } else {
          dimObj.families.forEach(f => f.labels.forEach(l => selectedLabels.add(l.name)));
        }
        renderLabelsList(labelSearchInput ? labelSearchInput.value : '');
        loadTrendsChart();
        loadDensityChart();
      });
    }

    if (btnClearAll) {
      btnClearAll.addEventListener('click', () => {
        selectedLabels.clear();
        renderLabelsList(labelSearchInput ? labelSearchInput.value : '');
        loadTrendsChart();
        loadDensityChart();
      });
    }

    if (btnSelectTop) {
      btnSelectTop.addEventListener('click', () => {
        selectTopLabels(6);
        renderLabelsList(labelSearchInput ? labelSearchInput.value : '');
        loadTrendsChart();
        loadDensityChart();
      });
    }

    // Trends Time Granularity Toggles (Bi-annual vs Year-wise)
    if (btnTimeBiannual) {
      btnTimeBiannual.addEventListener('click', () => {
        if (currentTimeGranularity === 'biannual') return;
        currentTimeGranularity = 'biannual';
        btnTimeBiannual.classList.add('active');
        if (btnTimeYearwise) btnTimeYearwise.classList.remove('active');
        updateTrendsHeaderTitle();
        loadTrendsChart();
      });
    }

    if (btnTimeYearwise) {
      btnTimeYearwise.addEventListener('click', () => {
        if (currentTimeGranularity === 'yearwise') return;
        currentTimeGranularity = 'yearwise';
        btnTimeYearwise.classList.add('active');
        if (btnTimeBiannual) btnTimeBiannual.classList.remove('active');
        updateTrendsHeaderTitle();
        loadTrendsChart();
      });
    }

    // Trends Mode Toggles
    if (btnToggleCount) {
      btnToggleCount.addEventListener('click', () => {
        currentMode = 'count';
        btnToggleCount.classList.add('active');
        btnToggleRelative.classList.remove('active');
        btnToggleConference.classList.remove('active');
        updateTrendsHeaderTitle();
        loadTrendsChart();
      });
    }

    if (btnToggleRelative) {
      btnToggleRelative.addEventListener('click', () => {
        currentMode = 'relative';
        btnToggleRelative.classList.add('active');
        btnToggleCount.classList.remove('active');
        btnToggleConference.classList.remove('active');
        updateTrendsHeaderTitle();
        loadTrendsChart();
      });
    }

    if (btnToggleConference) {
      btnToggleConference.addEventListener('click', () => {
        currentMode = 'conference';
        btnToggleConference.classList.add('active');
        btnToggleCount.classList.remove('active');
        btnToggleRelative.classList.remove('active');
        updateTrendsHeaderTitle();
        loadTrendsChart();
      });
    }

    // Network Min Weight
    if (networkMinWeight) {
      networkMinWeight.addEventListener('change', () => {
        loadNetworkChart();
      });
    }

    // Network Reset View Button
    if (btnResetNetwork) {
      btnResetNetwork.addEventListener('click', () => {
        const isMobile = window.innerWidth <= 768;
        networkCurrentZoom = isMobile ? 0.46 : 0.62;
        clearTimeout(networkRoamTimer);
        loadNetworkChart();
      });
    }

    // Knowledge Lineage Filter Toggles
    if (btnLineageAll) {
      btnLineageAll.addEventListener('click', () => {
        currentLineageFilter = 'all';
        btnLineageAll.classList.add('active');
        if (btnLineageCites) btnLineageCites.classList.remove('active');
        if (btnLineageCollabs) btnLineageCollabs.classList.remove('active');
        renderLineageGraph();
      });
    }

    if (btnLineageCites) {
      btnLineageCites.addEventListener('click', () => {
        currentLineageFilter = 'citations';
        btnLineageCites.classList.add('active');
        if (btnLineageAll) btnLineageAll.classList.remove('active');
        if (btnLineageCollabs) btnLineageCollabs.classList.remove('active');
        renderLineageGraph();
      });
    }

    if (btnLineageCollabs) {
      btnLineageCollabs.addEventListener('click', () => {
        currentLineageFilter = 'collaborations';
        btnLineageCollabs.classList.add('active');
        if (btnLineageAll) btnLineageAll.classList.remove('active');
        if (btnLineageCites) btnLineageCites.classList.remove('active');
        renderLineageGraph();
      });
    }
  }

  function openFilterDrawer() {
    if (filterDrawer) filterDrawer.classList.add('open');
    if (drawerBackdrop) {
      drawerBackdrop.classList.add('open');
      drawerBackdrop.style.display = 'block';
    }
  }

  function closeFilterDrawer() {
    if (filterDrawer) filterDrawer.classList.remove('open');
    if (drawerBackdrop) {
      drawerBackdrop.classList.remove('open');
      drawerBackdrop.style.display = 'none';
    }
  }

  // --- SECTION 1: Thematic Shifts & 10-Year Trends ---
  async function loadTrendsChart() {
    const chart = initChartInstance('trends');
    if (!chart) return;

    chart.showLoading({
      text: 'Loading trend data...',
      color: '#2563eb',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      textColor: '#0f172a'
    });

    const labelsArr = Array.from(selectedLabels);
    const labelsParam = labelsArr.join(',');
    const url = `/api/overview/trends?dimension=${currentDimension}&labels=${encodeURIComponent(labelsParam)}&level=${currentHierarchyLevel}&min_centrality=${currentCentrality}`;

    try {
      let res;
      try {
        res = await fetch(url);
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch(`data/overview_static/trends_${currentDimension}.json`).catch(() => fetch('data/overview_static/trends.json'));
      }
      const data = await res.json();
      chart.hideLoading();

      const isBiannual = (currentTimeGranularity === 'biannual');

      // Map calendar year to index in data.years
      const yearIdxMap = {};
      data.years.forEach((y, i) => { yearIdxMap[y] = i; });

      // Determine active time buckets
      const timeBuckets = isBiannual ? [
        { label: '2016–2017', years: [2016, 2017] },
        { label: '2018–2019', years: [2018, 2019] },
        { label: '2020–2021', years: [2020, 2021] },
        { label: '2022–2023', years: [2022, 2023] },
        { label: '2024–2025', years: [2024, 2025] },
        { label: '2026',       years: [2026] }
      ] : data.years.map(y => ({ label: String(y), years: [y] }));

      const numBuckets = timeBuckets.length;

      // Compute total conference proceedings papers in each bucket
      const bucketConfTotals = timeBuckets.map(b => {
        return b.years.reduce((acc, y) => {
          const idx = yearIdxMap[y];
          return acc + (idx !== undefined ? (data.yearly_paper_totals[idx] || 0) : 0);
        }, 0);
      });

      // Compute raw counts per series per bucket
      const seriesBucketCounts = data.series.map(s => {
        return timeBuckets.map(b => {
          return b.years.reduce((acc, y) => {
            const idx = yearIdxMap[y];
            return acc + (idx !== undefined ? (s.counts[idx] || 0) : 0);
          }, 0);
        });
      });

      // Compute bucket sums across selected categories (for 100% proportional share normalization)
      const selectedBucketSums = new Array(numBuckets).fill(0);
      seriesBucketCounts.forEach(counts => {
        counts.forEach((cnt, idx) => {
          selectedBucketSums[idx] += cnt;
        });
      });

      const seriesList = data.series.map((s, sIdx) => {
        const rawBucketCounts = seriesBucketCounts[sIdx];
        const confBucketPercentages = rawBucketCounts.map((cnt, idx) => {
          const confTotal = bucketConfTotals[idx];
          return confTotal > 0 ? parseFloat(((cnt / confTotal) * 100).toFixed(2)) : 0;
        });

        let values;
        if (currentMode === 'relative') {
          // 100% Proportional Share Mode: Normalizes each bucket across selected categories to sum to 100%
          values = rawBucketCounts.map((cnt, idx) => {
            const sumForBucket = selectedBucketSums[idx];
            return sumForBucket > 0 ? parseFloat(((cnt / sumForBucket) * 100).toFixed(1)) : 0;
          });
        } else if (currentMode === 'conference') {
          // % of Total Conference Proceedings
          values = confBucketPercentages;
        } else {
          // Raw Publication Counts
          values = rawBucketCounts;
        }

        const isStacked = (currentMode === 'relative');
        const color = getLabelColor(s.label, sIdx);

        return {
          name: s.label,
          type: 'line',
          stack: isStacked ? 'Total' : null, // Stacks exactly to 100% in relative mode
          smooth: false, // Sharp trend chart instead of smoothed spline curve
          showSymbol: true,
          symbolSize: 8,
          itemStyle: { color: color },
          lineStyle: { width: 2.5 },
          areaStyle: {
            color: color,
            opacity: isStacked ? 0.65 : 0.12
          },
          emphasis: {
            focus: 'series',
            scale: true,
            lineStyle: { width: 3.5 }
          },
          rawCounts: rawBucketCounts,
          confPercentages: confBucketPercentages,
          data: values
        };
      });

      // Responsive headroom for legend so it never obscures y-axis label or top data points
      const isMobile = window.innerWidth <= 768;
      const seriesCount = seriesList.length;
      let gridTop = 64;
      if (seriesCount > 8) {
        gridTop = isMobile ? 85 : 110;
      } else if (seriesCount > 5) {
        gridTop = isMobile ? 75 : 95;
      } else if (seriesCount > 2) {
        gridTop = isMobile ? 65 : 75;
      }

      const option = {
        backgroundColor: 'transparent',
        color: seriesList.map(s => s.itemStyle.color),
        tooltip: {
          trigger: 'item', // Specific to the hovered line/area/data point
          backgroundColor: '#ffffff',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: [12, 16],
          textStyle: {
            color: '#0f172a',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            fontSize: 12
          },
          extraCssText: 'box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.12), 0 4px 6px -2px rgba(0, 0, 0, 0.05); border-radius: 8px;',
          formatter: function(params) {
            if (!params || !params.seriesName) return '';
            const seriesObj = seriesList.find(s => s.name === params.seriesName);
            const countVal = seriesObj ? seriesObj.rawCounts[params.dataIndex] : 0;
            const confPct = seriesObj ? seriesObj.confPercentages[params.dataIndex] : 0;
            const periodStr = params.name;
            const colorDot = `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${params.color};margin-right:6px;"></span>`;

            let mainValDisplay = '';
            if (currentMode === 'relative') {
              mainValDisplay = `<div style="font-size:1.15rem; font-weight:800; color:#0f172a; margin: 4px 0;">${params.value}% <span style="font-size:0.75rem; font-weight:500; color:#64748b;">of selected mindshare</span></div>`;
            } else if (currentMode === 'conference') {
              mainValDisplay = `<div style="font-size:1.15rem; font-weight:800; color:#0f172a; margin: 4px 0;">${params.value}% <span style="font-size:0.75rem; font-weight:500; color:#64748b;">of all conference papers</span></div>`;
            } else {
              mainValDisplay = `<div style="font-size:1.15rem; font-weight:800; color:#0f172a; margin: 4px 0;">${params.value} <span style="font-size:0.75rem; font-weight:500; color:#64748b;">published papers</span></div>`;
            }

            const periodHeading = (currentTimeGranularity === 'biannual')
              ? `Bi-annual Cycle: ${periodStr}`
              : `Year ${periodStr}`;

            return `
              <div style="font-size:0.78rem; font-weight:600; color:#64748b; margin-bottom:2px;">${periodHeading}</div>
              <div style="font-size:0.95rem; font-weight:700; color:#0f172a; display:flex; align-items:center;">
                ${colorDot} ${params.seriesName}
              </div>
              ${mainValDisplay}
              <div style="font-size:0.78rem; color:#475569; border-top:1px solid #f1f5f9; padding-top:6px; margin-top:4px;">
                📊 <strong>${countVal}</strong> papers (${confPct}% of conf)
              </div>
              <div style="font-size:0.72rem; color:#94a3b8; margin-top:4px;">
                💡 Click point to inspect papers in drawer
              </div>
            `;
          }
        },
        legend: {
          type: 'scroll', // Paginated scroll prevents legend from spilling or colliding with chart
          orient: 'horizontal',
          top: 6,
          left: 'center',
          itemGap: 14,
          itemWidth: 12,
          itemHeight: 12,
          padding: [4, 16, 8, 16],
          textStyle: {
            color: '#334155',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12,
            fontWeight: 500
          },
          pageIconColor: '#2563eb',
          pageIconInactiveColor: '#cbd5e1',
          pageTextStyle: {
            color: '#64748b',
            fontSize: 11
          }
        },
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: 0,
            zoomOnMouseWheel: false,
            moveOnMouseMove: true,
            moveOnTouch: true,
            preventDefaultMouseMove: false
          }
        ],
        grid: {
          left: isMobile ? '12px' : '2%',
          right: isMobile ? '16px' : '3%',
          bottom: '5%',
          top: gridTop,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: timeBuckets.map(b => b.label),
          axisLine: { lineStyle: { color: '#cbd5e1' } },
          axisLabel: {
            color: '#64748b',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12
          }
        },
        yAxis: {
          type: 'value',
          name: currentMode === 'relative'
            ? (currentTimeGranularity === 'biannual' ? '100% Proportional Share (2-Year Cycles %)' : '100% Proportional Share of Selection (%)')
            : (currentMode === 'conference'
                ? (currentTimeGranularity === 'biannual' ? '% of Total Conference Papers (2-Year Cycle)' : '% of Total Conference Papers')
                : (currentTimeGranularity === 'biannual' ? 'Published Papers per 2-Year Cycle (Count)' : 'Published Papers (Count)')),
          nameLocation: 'end',
          nameGap: 18,
          nameTextStyle: {
            color: '#475569',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 11,
            padding: [0, 0, 6, 0]
          },
          max: (currentMode === 'relative') ? 100 : null,
          min: 0,
          splitLine: { lineStyle: { color: '#f1f5f9' } },
          axisLine: { lineStyle: { color: '#cbd5e1' } },
          axisLabel: {
            color: '#64748b',
            fontFamily: 'Inter, sans-serif',
            fontSize: 11,
            formatter: (currentMode === 'count') ? '{value}' : '{value}%'
          }
        },
        series: seriesList
      };

      chart.setOption(option, true);
      chart.resize();

    } catch (err) {
      chart.hideLoading();
      console.error('Error loading trends chart:', err);
    }
  }

  // --- SECTION 2: Callon 2x2 Research Density Matrix ---
  async function loadDensityChart() {
    const chart = initChartInstance('density');
    if (!chart) return;

    chart.showLoading({
      text: 'Loading density matrix...',
      color: '#2563eb',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      textColor: '#0f172a'
    });

    const url = `/api/overview/density?dimension=${currentDimension}`;

    try {
      let res;
      try {
        res = await fetch(url);
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch(`data/overview_static/density_${currentDimension}.json`).catch(() => fetch('data/overview_static/density.json'));
      }
      const data = await res.json();
      chart.hideLoading();

      // Filter out Computer-Supported Collaborative Learning since the conference is centered on it
      const rawPoints = data.points || [];
      const filteredPoints = rawPoints.filter(pt => {
        const lbl = (pt.label || '').toLowerCase();
        return !lbl.includes('computer-support') && !lbl.includes('cscl');
      });

      // Recalculate medians for filtered points
      let medianCentrality = data.median_centrality;
      let medianDensity = data.median_density;
      if (filteredPoints.length > 0) {
        const counts = filteredPoints.map(p => p.density).sort((a, b) => a - b);
        const centralities = filteredPoints.map(p => p.centrality).sort((a, b) => a - b);
        medianDensity = counts[Math.floor(counts.length / 2)];
        medianCentrality = centralities[Math.floor(centralities.length / 2)];
      }

      const scatterData = filteredPoints.map(pt => [
        pt.centrality,
        pt.density,
        pt.quadrant_num,
        pt.label,
        pt.quadrant,
        pt.family
      ]);

      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          backgroundColor: '#ffffff',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: [12, 16],
          textStyle: {
            color: '#0f172a',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12
          },
          extraCssText: 'box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1); border-radius: 8px;',
          formatter: function(params) {
            const d = params.data;
            let quadBadge = '';
            if (d[2] === 1) quadBadge = '<span style="color:#166534; background:#dcfce7; padding:2px 8px; border-radius:4px; font-weight:600;">Motor Theme</span>';
            else if (d[2] === 2) quadBadge = '<span style="color:#6b21a8; background:#f3e8ff; padding:2px 8px; border-radius:4px; font-weight:600;">Niche Theme</span>';
            else if (d[2] === 3) quadBadge = '<span style="color:#1e40af; background:#dbeafe; padding:2px 8px; border-radius:4px; font-weight:600;">Basic & Transversal</span>';
            else quadBadge = '<span style="color:#92400e; background:#fef3c7; padding:2px 8px; border-radius:4px; font-weight:600;">Emerging / Declining</span>';

            return `
              <div style="font-weight:700; font-size:0.95rem; margin-bottom:2px; color:#0f172a;">${d[3]}</div>
              <div style="font-size:0.75rem; color:#64748b; margin-bottom:6px;">Family: <strong>${d[5] || 'Core'}</strong></div>
              <div style="margin-bottom:8px;">${quadBadge}</div>
              <table style="width:100%; border-collapse:collapse; font-size:0.8rem; color:#334155;">
                <tr><td style="padding:2px 6px 2px 0;">External Centrality:</td><td style="font-weight:600; text-align:right;">${d[0].toLocaleString()} co-occurrences</td></tr>
                <tr><td style="padding:2px 6px 2px 0;">Internal Density:</td><td style="font-weight:600; text-align:right;">${d[1].toLocaleString()} papers</td></tr>
              </table>
              <div style="font-size:0.72rem; color:#94a3b8; margin-top:8px; border-top:1px solid #f1f5f9; padding-top:4px;">💡 Click bubble to inspect papers</div>
            `;
          }
        },
        grid: {
          left: '4%',
          right: '5%',
          bottom: '8%',
          top: '8%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          scale: true,
          min: function(value) {
            return Math.max(10, Math.floor(value.min - 3));
          },
          max: function(value) {
            return Math.ceil(value.max + 2);
          },
          name: 'Cross-Topic Centrality (External Connectivity / Interdisciplinarity) ➔',
          nameLocation: 'middle',
          nameGap: 32,
          nameTextStyle: {
            color: '#475569',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 12
          },
          splitLine: { lineStyle: { color: '#f1f5f9' } },
          axisLine: { lineStyle: { color: '#cbd5e1' } },
          axisLabel: {
            color: '#64748b',
            fontFamily: 'Inter, sans-serif',
            fontSize: 11
          }
        },
        yAxis: {
          type: 'value',
          scale: true,
          min: function(value) {
            return Math.max(0, Math.floor(value.min * 0.7));
          },
          max: function(value) {
            return Math.ceil(value.max * 1.06);
          },
          name: 'Internal Research Density (Publication Volume / Cohesion) ➔',
          nameLocation: 'middle',
          nameGap: 45,
          nameTextStyle: {
            color: '#475569',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 12
          },
          splitLine: { lineStyle: { color: '#f1f5f9' } },
          axisLine: { lineStyle: { color: '#cbd5e1' } },
          axisLabel: {
            color: '#64748b',
            fontFamily: 'Inter, sans-serif',
            fontSize: 11
          }
        },
        series: [
          {
            type: 'scatter',
            symbolSize: function(val) {
              return Math.min(26, Math.max(10, Math.sqrt(val[1]) * 1.2));
            },
            data: scatterData,
            label: {
              show: true,
              formatter: function(params) {
                return params.data[3];
              },
              position: 'top',
              distance: 5,
              color: '#0f172a',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 600,
              fontSize: 10.5,
              textBorderColor: '#ffffff',
              textBorderWidth: 2
            },
            labelLayout: {
              hideOverlap: true,
              moveOverlap: 'shiftY'
            },
            itemStyle: {
              color: function(params) {
                const q = params.data[2];
                if (q === 1) return '#059669'; // Motor: Emerald Green
                if (q === 2) return '#7c3aed'; // Niche: Purple
                if (q === 3) return '#2563eb'; // Basic: Blue
                return '#d97706'; // Emerging: Amber
              },
              opacity: 0.85,
              borderColor: '#ffffff',
              borderWidth: 1.5,
              shadowBlur: 6,
              shadowColor: 'rgba(0, 0, 0, 0.10)'
            },
            markLine: {
              silent: true,
              lineStyle: {
                color: '#94a3b8',
                type: 'dashed',
                width: 1.5
              },
              data: [
                {
                  xAxis: medianCentrality,
                  label: {
                    formatter: 'Median Centrality (' + medianCentrality + ')',
                    color: '#64748b',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10
                  }
                },
                {
                  yAxis: medianDensity,
                  label: {
                    formatter: 'Median Density (' + medianDensity + ')',
                    color: '#64748b',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 10
                  }
                }
              ]
            }
          }
        ]
      };

      chart.setOption(option, true);
      chart.resize();

    } catch (err) {
      chart.hideLoading();
      console.error('Error loading density chart:', err);
    }
  }

  // --- SECTION 3: Author Collaboration Network ---
  let networkCurrentZoom = 0.62;
  let networkRoamTimer = null;
  let networkIsUpdating = false;

  async function loadNetworkChart() {
    const chart = initChartInstance('network');
    if (!chart) return;

    chart.showLoading({
      text: 'Simulating collaboration network...',
      color: '#2563eb',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      textColor: '#0f172a'
    });

    const minW = networkMinWeight ? networkMinWeight.value : 2;
    const url = `/api/overview/network?min_weight=${minW}&limit=110`;

    try {
      let res;
      try {
        res = await fetch(url);
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch('data/overview_static/network.json');
      }
      const data = await res.json();
      chart.hideLoading();

      const isMobile = window.innerWidth <= 768;
      const defaultNetworkZoom = isMobile ? 0.46 : 0.62;

      // Reset zoom tracking
      networkCurrentZoom = defaultNetworkZoom;

      // Deep copy nodes for dynamic scaling reference
      const originalNodes = data.nodes.map(n => ({ ...n }));

      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          backgroundColor: '#ffffff',
          borderColor: '#e2e8f0',
          borderWidth: 1,
          padding: [10, 14],
          textStyle: {
            color: '#0f172a',
            fontFamily: 'Inter, sans-serif',
            fontSize: 12
          },
          extraCssText: 'box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1); border-radius: 8px;',
          formatter: function(params) {
            if (params.dataType === 'node') {
              const d = params.data;
              const yr = d.first_year ? d.first_year : 'Unknown';
              const yrLabel = yr === 2016 ? '2016 (Founding Cohort)' : (yr === 2026 ? '2026 (Newest Cohort)' : `${yr} Cohort`);
              const colorDot = `<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${d.color || '#2563eb'}; margin-right:6px; vertical-align:middle;"></span>`;
              return `
                <div style="font-weight:700; font-size:0.95rem; margin-bottom:5px; color:#0f172a; display:flex; align-items:center;">
                  ${colorDot}${d.name}
                </div>
                <div style="font-size:0.82rem; color:#334155; margin-bottom:3px;">
                  First Published: <strong>${yrLabel}</strong>
                </div>
                <div style="font-size:0.8rem; color:#475569;">
                  Total Collaborations: <strong>${d.value}</strong>
                </div>
                <div style="font-size:0.72rem; color:#94a3b8; margin-top:6px;">💡 Click author to view papers</div>
              `;
            } else if (params.dataType === 'edge') {
              return `
                <div style="font-size:0.85rem; font-weight:600; color:#0f172a;">${params.data.source} ⟷ ${params.data.target}</div>
                <div style="font-size:0.8rem; color:#475569; margin-top:2px;">Co-authored Papers: <strong>${params.data.value}</strong></div>
              `;
            }
          }
        },
        series: [
          {
            type: 'graph',
            layout: 'force',
            data: data.nodes,
            links: data.links,
            roam: true,
            zoom: defaultNetworkZoom,
            center: ['50%', '50%'],
            label: {
              show: true,
              position: 'right',
              color: '#1e293b',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 500,
              fontSize: 11,
              textBorderColor: '#ffffff',
              textBorderWidth: 2
            },
            itemStyle: {
              borderColor: '#ffffff',
              borderWidth: 1.5,
              shadowBlur: 3,
              shadowColor: 'rgba(0, 0, 0, 0.15)'
            },
            lineStyle: {
              color: 'rgba(148, 163, 184, 0.45)',
              curveness: 0.1,
              width: 1.6
            },
            emphasis: {
              focus: 'adjacency',
              lineStyle: {
                width: 3.5,
                color: '#2563eb'
              }
            },
            force: {
              repulsion: 220,
              edgeLength: 65,
              gravity: 0.14,
              friction: 0.6
            }
          }
        ]
      };

      chart.setOption(option, true);
      chart.resize();

      // Dynamic zoom listener: scales dots and adjusts labels to prevent obscuring
      chart.off('graphRoam');
      chart.on('graphRoam', function(params) {
        if (params.zoom != null && !networkIsUpdating) {
          networkCurrentZoom *= params.zoom;
          networkCurrentZoom = Math.max(0.25, Math.min(4.5, networkCurrentZoom));

          clearTimeout(networkRoamTimer);
          networkRoamTimer = setTimeout(() => {
            applyNetworkDynamicScaling(chart, originalNodes, networkCurrentZoom);
          }, 50);
        }
      });

    } catch (err) {
      chart.hideLoading();
      console.error('Error loading author network:', err);
    }
  }

  function applyNetworkDynamicScaling(chart, originalNodes, zoom) {
    try {
      const seriesModel = chart.getModel() ? chart.getModel().getSeriesByIndex(0) : null;
      const nodeData = seriesModel ? seriesModel.getData() : null;
      if (!nodeData) return;

      networkIsUpdating = true;
      const isMobile = window.innerWidth <= 768;
      const baseZoom = isMobile ? 0.46 : 0.62;
      const dampingFactor = Math.pow(zoom / baseZoom, -0.40);

      const updatedNodes = originalNodes.map((node, idx) => {
        const layout = nodeData.getItemLayout(idx);
        const x = (layout && layout[0] != null) ? layout[0] : node.x;
        const y = (layout && layout[1] != null) ? layout[1] : node.y;
        const dynSize = Math.max(3, Math.min(18, Math.round(node.baseSize * dampingFactor)));

        return {
          ...node,
          x: x,
          y: y,
          fixed: (x != null && y != null),
          symbolSize: dynSize,
          label: {
            show: zoom >= 0.70 || node.value >= 35
          }
        };
      });

      chart.setOption({
        series: [{
          data: updatedNodes,
          force: {
            layoutAnimation: false
          }
        }]
      });
    } catch (err) {
      console.warn('Network scaling update error:', err);
    } finally {
      setTimeout(() => { networkIsUpdating = false; }, 40);
    }
  }

  // --- SECTION 4: Citation Knowledge Flows & Lineage Timeline ---
  async function loadCitationsChart() {
    const chart = initChartInstance('citations');
    if (!chart) return;

    chart.showLoading({
      text: 'Mapping knowledge lineage & collaboration timeline...',
      color: '#2563eb',
      maskColor: 'rgba(255, 255, 255, 0.8)',
      textColor: '#0f172a'
    });

    const url = `/api/overview/citations?limit=60`;

    try {
      let res;
      try {
        res = await fetch(url);
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch('data/overview_static/citations.json');
      }
      lineageRawData = await res.json();
      chart.hideLoading();

      renderLineageGraph();
      renderSeminalWorksTable();

    } catch (err) {
      chart.hideLoading();
      console.error('Error loading citations chart:', err);
    }
  }

  function renderLineageGraph() {
    if (!charts.citations || !lineageRawData) return;

    let filteredLinks = lineageRawData.links || [];
    if (currentLineageFilter === 'citations') {
      filteredLinks = filteredLinks.filter(l => l.type === 'citation');
    } else if (currentLineageFilter === 'collaborations') {
      filteredLinks = filteredLinks.filter(l => l.type === 'collaboration');
    }

    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: '#ffffff',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: {
          color: '#0f172a',
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          fontSize: 12
        },
        extraCssText: 'box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.12); border-radius: 8px;',
        formatter: function(params) {
          if (params.dataType === 'node') {
            const d = params.data;
            return `
              <div style="font-weight:700; font-size:1rem; color:#0f172a; margin-bottom:4px;">${d.name}</div>
              <div style="font-size:0.78rem; color:#64748b; margin-bottom:6px;">
                Era: <strong>${d.eraName}</strong> • Domain: <span style="color:${d.color}; font-weight:600;">${d.family}</span>
              </div>
              <table style="width:100%; border-collapse:collapse; font-size:0.8rem; color:#334155; margin-bottom:6px;">
                <tr><td style="padding:2px 6px 2px 0;">Citations in Proceedings:</td><td style="font-weight:700; text-align:right;">${d.citationsCount}</td></tr>
                <tr><td style="padding:2px 6px 2px 0;">Total Collaborations:</td><td style="font-weight:700; text-align:right;">${d.collabCount}</td></tr>
              </table>
              <div style="font-size:0.72rem; color:#94a3b8; border-top:1px solid #f1f5f9; padding-top:4px;">
                💡 Click scholar to view their papers in drawer
              </div>
            `;
          } else if (params.dataType === 'edge') {
            const d = params.data;
            const isCite = (d.type === 'citation');
            const badge = isCite
              ? `<span style="background:#ffedd5; color:#c2410c; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.74rem;">➔ Knowledge Transmission (Citation)</span>`
              : `<span style="background:#eff6ff; color:#1d4ed8; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.74rem;">⟷ Team Science (Co-Authorship)</span>`;
            return `
              <div style="margin-bottom:6px;">${badge}</div>
              <div style="font-size:0.92rem; font-weight:700; color:#0f172a;">
                ${d.source} ${isCite ? '➔' : '⟷'} ${d.target}
              </div>
              <div style="font-size:0.82rem; color:#475569; margin-top:4px;">
                ${d.desc}
              </div>
            `;
          }
        }
      },
      series: [
        {
          type: 'graph',
          layout: 'none',
          coordinateSystem: null,
          roam: true,
          scaleLimit: { min: 0.6, max: 2.5 },
          data: lineageRawData.nodes,
          links: filteredLinks,
          label: {
            show: true,
            position: 'bottom',
            color: '#1e293b',
            fontFamily: 'Inter, sans-serif',
            fontWeight: 600,
            fontSize: 11,
            textBorderColor: '#ffffff',
            textBorderWidth: 2
          },
          emphasis: {
            focus: 'adjacency',
            lineStyle: { width: 4 }
          }
        }
      ]
    };

    charts.citations.setOption(option, true);
    charts.citations.resize();
  }

  function renderSeminalWorksTable() {
    if (!seminalWorksTableBody || !lineageRawData || !lineageRawData.top_cited_papers) return;

    seminalWorksTableBody.innerHTML = '';
    lineageRawData.top_cited_papers.forEach(p => {
      const tr = document.createElement('tr');
      const authorLastName = p.apa_authors ? p.apa_authors.split(',')[0].trim() : '';
      tr.innerHTML = `
        <td style="color: var(--text-primary);">
          <strong>${p.apa_citation}</strong>
        </td>
        <td>
          <span style="font-size:0.74rem; background:#f1f5f9; color:#334155; padding:2px 8px; border-radius:4px; font-weight:500;">
            🏷️ ${p.primary_theme}
          </span>
        </td>
        <td style="text-align: center; font-weight: 600;">${p.year}</td>
        <td style="text-align: center;">
          <span style="font-size:0.82rem; font-weight:700; color:var(--primary); background:var(--primary-subtle); padding:2px 8px; border-radius:10px;">
            ${p.cite_count}
          </span>
        </td>
        <td style="text-align: center;">
          <button class="btn-inspect-sm" data-year="${p.year}" data-author="${authorLastName}" title="Inspect paper">
            Inspect ↗
          </button>
        </td>
      `;

      const btn = tr.querySelector('.btn-inspect-sm');
      if (btn) {
        btn.addEventListener('click', () => {
          openPaperInspector(null, null, p.year, authorLastName);
        });
      }

      seminalWorksTableBody.appendChild(tr);
    });
  }

  // --- Slide-out Paper Inspector Drawer ---
  async function openPaperInspector(dimension, label, year, authorName) {
    if (!paperInspector || !inspectorContent) return;

    const apaAuthor = authorName ? formatAuthorApa(authorName) : '';

    if (label) {
      inspectorTitle.textContent = `${label} ${year ? '(' + year + ')' : ''}`;
    } else if (authorName) {
      inspectorTitle.textContent = `Papers by ${apaAuthor}`;
    } else {
      inspectorTitle.textContent = 'Papers';
    }

    inspectorContent.innerHTML = '<div style="text-align:center; padding: 30px; color:#64748b;">Loading papers...</div>';
    paperInspector.classList.add('open');
    if (inspectorBackdrop) {
      inspectorBackdrop.classList.add('open');
      inspectorBackdrop.style.display = 'block';
    }

    let url = `/api/overview/papers?limit=30&min_centrality=${currentCentrality}`;
    if (dimension) url += `&dimension=${dimension}`;
    if (label) url += `&label=${encodeURIComponent(label)}`;
    if (year) url += `&year=${year}`;
    if (authorName) url += `&author=${encodeURIComponent(authorName)}`;

    try {
      let res;
      try {
        res = await fetch(url);
        if (!res.ok) throw new Error('API 404');
      } catch (e) {
        res = await fetch('data/overview_static/papers.json');
      }
      const papers = await res.json();

      if (!papers || papers.length === 0) {
        inspectorContent.innerHTML = '<div style="color:#64748b; text-align:center; padding: 30px;">No matching papers found.</div>';
        return;
      }

      inspectorContent.innerHTML = '';
      papers.forEach(p => {
        const card = document.createElement('div');
        card.className = 'paper-detail-card';

        const cScoreBadge = p.centrality_score 
          ? `<span class="badge-claim-score">Claim Centrality: ${p.centrality_score}/5</span>` 
          : '';

        const urlLink = p.handle_url 
          ? `<a href="${p.handle_url}" target="_blank" style="color:var(--primary); text-decoration:none; font-size:0.78rem; font-weight:600; display:inline-flex; align-items:center; gap:4px;">📄 Open Full Paper ↗</a>` 
          : '';

        const authorsDisplay = p.authors ? formatAuthorListApa(p.authors) : 'Unknown Authors';

        card.innerHTML = `
          <div class="paper-detail-title">${p.title}</div>
          <div class="paper-detail-meta">
            <span>📅 <strong>${p.year}</strong> (${p.conference})</span>
            <span>✍️ ${authorsDisplay}</span>
            ${cScoreBadge}
          </div>
          <div class="paper-detail-abstract">${p.abstract || 'No abstract text available for this publication.'}</div>
          <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:2px;">
            ${p.label_value && p.label_value !== 'Unlabeled' ? `<span style="font-size:0.74rem; background:#f1f5f9; color:#334155; padding:2px 8px; border-radius:4px; font-weight:500;">🏷️ ${p.label_value}</span>` : ''}
            ${apaAuthor ? `<span style="font-size:0.74rem; background:#fdf2f8; color:#9d174d; padding:2px 8px; border-radius:4px; font-weight:500;">👤 ${apaAuthor}</span>` : ''}
            <span style="font-size:0.74rem; background:#eff6ff; color:#1d4ed8; padding:2px 8px; border-radius:4px; font-weight:500;">⚡ ${p.method}</span>
            ${urlLink}
          </div>
          <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 4px;">
            📝 <em>${p.notes || 'Heuristic 0-cost title/abstract extraction.'}</em>
          </div>
        `;
        inspectorContent.appendChild(card);
      });

    } catch (err) {
      inspectorContent.innerHTML = '<div style="color:#e11d48; padding: 25px; text-align:center;">Failed to load papers. Please try again.</div>';
      console.error('Failed to load papers for inspector:', err);
    }
  }

  function closePaperInspector() {
    if (paperInspector) paperInspector.classList.remove('open');
    if (inspectorBackdrop) {
      inspectorBackdrop.classList.remove('open');
      inspectorBackdrop.style.display = 'none';
    }
  }

  // --- Beautiful Papers Module: Year-by-Year Comparison & Absolute Token Silhouettes ---
  let bpData = null;
  let bpActiveGrouping = 'recent';      // 'recent' (2023–2026) | 'eras' (5 Cohort Eras) | 'all' (2016–2026)
  let bpActiveOutlierGenre = 'all';     // 'all' | 'full' | 'short' | 'other'
  let bpActiveOutlierType = 'All';      // 'All' | 'Very High' | 'Very Low'
  let bpActiveLineupCols = new Set(['full', 'short']); // 'full', 'short', 'other'

  const BP_CORE_SECTIONS = [
    {
      name: 'Abstract & Introduction',
      order: 1,
      shortLabel: 'Intro',
      role: 'Theoretical Framing',
      color: '#2563eb',
      gradStart: '#3b82f6',
      gradEnd: '#1d4ed8',
      light: '#eff6ff',
      border: '#bfdbfe',
      desc: 'Front-matter distillation, theoretical framing, problem statement, and literature grounding.'
    },
    {
      name: 'Methodology & Context',
      order: 2,
      shortLabel: 'Method',
      role: 'Inquiry Protocol',
      color: '#0d9488',
      gradStart: '#14b8a6',
      gradEnd: '#0f766e',
      light: '#f0fdfa',
      border: '#99f6e4',
      desc: 'Inquiry design, participant demographics, study contexts, and analytical protocols.'
    },
    {
      name: 'Results & Findings',
      order: 3,
      shortLabel: 'Results',
      role: 'Evidence & Analysis',
      color: '#ea580c',
      gradStart: '#f97316',
      gradEnd: '#c2410c',
      light: '#fff7ed',
      border: '#fed7aa',
      desc: 'Empirical evidence, qualitative interaction transcripts, and statistical models.'
    },
    {
      name: 'Discussion & Conclusion',
      order: 4,
      shortLabel: 'Discuss',
      role: 'Synthesis & Horizon',
      color: '#9333ea',
      gradStart: '#a855f7',
      gradEnd: '#7e22ce',
      light: '#faf5ff',
      border: '#e9d5ff',
      desc: 'Theoretical synthesis, design/pedagogical implications, and limitations.'
    }
  ];

  function pointsToSmoothPath(pts) {
    if (!pts || pts.length < 2) return '';
    let d = [`M ${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`];
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = i > 0 ? pts[i - 1] : pts[i];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = (i + 2 < pts.length) ? pts[i + 2] : p2;

      const cp1x = p1[0] + (p2[0] - p0[0]) / 5.5;
      const cp1y = p1[1] + (p2[1] - p0[1]) / 5.5;
      const cp2x = p2[0] - (p3[0] - p1[0]) / 5.5;
      const cp2y = p2[1] - (p3[1] - p1[1]) / 5.5;
      d.push(`C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`);
    }
    d.push('Z');
    return d.join(' ');
  }

  function computeSmoothViolinGeometry(secTokens, cx, totalH, maxTokens, svgW) {
    cx = cx || 55;
    totalH = totalH || 250;
    svgW = svgW || (cx * 2);
    maxTokens = maxTokens || 2200;

    const t1 = secTokens ? (secTokens['Abstract & Introduction'] || 0) : 0;
    const t2 = secTokens ? (secTokens['Methodology & Context'] || 0) : 0;
    const t3 = secTokens ? (secTokens['Results & Findings'] || 0) : 0;
    const t4 = secTokens ? (secTokens['Discussion & Conclusion'] || 0) : 0;

    const isLineup = totalH >= 200;
    const dotCy = isLineup ? 11 : 9;
    const dotR = isLineup ? 4.5 : 3.2;
    const yTop = isLineup ? 24 : 18;
    const yBase = totalH - (isLineup ? 12 : 10);

    const bodyH = yBase - yTop;
    const secH = bodyH / 4;

    const y1 = yTop + secH * 0.5;
    const y2 = yTop + secH * 1.5;
    const y3 = yTop + secH * 2.5;
    const y4 = yTop + secH * 3.5;

    // Guaranteed bounding constraints so the violin never extends beyond boundaries
    const maxSafeHalfW = cx - 8;
    const targetHalfW = cx * 0.78;
    const minW = Math.max(3.5, cx * 0.07);

    // Absolute token scaling (strictly proportional to tokens)
    const w1 = Math.min(maxSafeHalfW, Math.max(minW, (t1 / maxTokens) * targetHalfW));
    const w2 = Math.min(maxSafeHalfW, Math.max(minW, (t2 / maxTokens) * targetHalfW));
    const w3 = Math.min(maxSafeHalfW, Math.max(minW, (t3 / maxTokens) * targetHalfW));
    const w4 = Math.min(maxSafeHalfW, Math.max(minW, (t4 / maxTokens) * targetHalfW));

    // Smooth spline points with gentle apex shoulders and base taper, without neck cinching
    const rightPts = [
      [cx, yTop],
      [cx + w1 * 0.45, yTop + secH * 0.22],
      [cx + w1, y1],
      [cx + w2, y2],
      [cx + w3, y3],
      [cx + w4, y4],
      [cx + w4 * 0.45, yBase - secH * 0.22],
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
      secH,
      y1, y2, y3, y4,
      w1, w2, w3, w4,
      calipers: [
        { order: 1, name: 'Abstract & Introduction', y: y1, w: w1 * 2, tokens: Math.round(t1) },
        { order: 2, name: 'Methodology & Context', y: y2, w: w2 * 2, tokens: Math.round(t2) },
        { order: 3, name: 'Results & Findings', y: y3, w: w3 * 2, tokens: Math.round(t3) },
        { order: 4, name: 'Discussion & Conclusion', y: y4, w: w4 * 2, tokens: Math.round(t4) }
      ]
    };
  }

  async function initBeautifulPapers() {
    try {
      let res = await fetch('/api/overview/beautiful-papers?t=' + Date.now());
      if (!res.ok) {
        res = await fetch('beautiful_papers.json?t=' + Date.now());
      }
      bpData = await res.json();

      bpActiveOutlierGenre = 'all';
      bpActiveOutlierType = 'All';

      renderOutlierThumbnails();

    } catch (err) {
      console.error('Failed to load Beautiful Papers data:', err);
    }
  }

  function renderYearComparisonStage() {
    const stage = document.getElementById('bpYearComparisonStage');
    if (!stage || !bpData || !bpData.by_type) return;

    stage.innerHTML = '';

    let itemsToRender = [];
    if (bpActiveGrouping === 'eras') {
      stage.setAttribute('data-cols', '5');
      itemsToRender = bpData.summary?.cohort_buckets || [
        { id: '2016-2018', label: '2016–2018' },
        { id: '2019-2020', label: '2019–2020' },
        { id: '2021-2022', label: '2021–2022' },
        { id: '2023-2024', label: '2023–2024' },
        { id: '2025-2026', label: '2025–2026' }
      ];
    } else if (bpActiveGrouping === 'all') {
      stage.setAttribute('data-cols', '11');
      const years = bpData.summary?.years_covered || [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];
      itemsToRender = years.map(y => ({ id: String(y), label: String(y) }));
    } else {
      // Default: 'recent' Year-by-Year (2023–2026)
      stage.setAttribute('data-cols', '4');
      itemsToRender = [
        { id: '2023', label: '2023' },
        { id: '2024', label: '2024' },
        { id: '2025', label: '2025' },
        { id: '2026', label: '2026' }
      ];
    }

    const colConfigs = [
      { key: 'full', label: '📄 Full', color: '#2563eb', dotColor: '#3b82f6' },
      { key: 'short', label: '📑 Short', color: '#0d9488', dotColor: '#14b8a6' },
      { key: 'other', label: '🏛️ Other', color: '#7c3aed', dotColor: '#8b5cf6' }
    ];

    const activeConfigs = colConfigs.filter(c => bpActiveLineupCols.has(c.key));
    const numCols = Math.max(1, activeConfigs.length);

    itemsToRender.forEach(item => {
      const bId = item.id;
      const card = document.createElement('div');
      card.className = 'bp-lineup-card';

      // Gather distributions and totals for each active column
      const colData = {};
      activeConfigs.forEach(c => {
        const dist = bpData.by_type[c.key]?.[bId] || {};
        const count = (bpActiveGrouping === 'eras')
          ? (bpData.summary?.papers_by_bucket?.[c.key]?.[bId] || 0)
          : (bpData.summary?.papers_by_year?.[c.key]?.[bId] || 0);

        const tokens = {};
        let total = 0;
        BP_CORE_SECTIONS.forEach(sec => {
          const val = Math.round(dist[sec.name]?.median || 0);
          tokens[sec.name] = val;
          total += val;
        });
        colData[c.key] = { dist, count, tokens, total };
      });

      // Header subtitle
      const subLines = activeConfigs.map(c => {
        const d = colData[c.key];
        const cleanLabel = c.label.replace(/^[^\w\s]+/, '').trim();
        return `<strong>${cleanLabel}:</strong> ${d.count} papers (${d.total.toLocaleString()} tk)`;
      }).join('<br>');

      // Calculate SVG parameters based on column count
      const svgW = numCols === 1 ? 130 : (numCols === 2 ? 95 : 70);
      const svgH = 230;
      const cx = svgW / 2;
      const absoluteMax = 2200;

      // Geometries for active columns
      const geoms = {};
      activeConfigs.forEach(c => {
        geoms[c.key] = computeSmoothViolinGeometry(colData[c.key].tokens, cx, svgH, absoluteMax, svgW);
      });

      // Columns markup
      const colsHtml = activeConfigs.map(c => {
        const d = colData[c.key];
        const g = geoms[c.key];
        const clipId = `clip-${c.key}-${bId}`;

        return `
          <div class="bp-lineup-col-box" id="bpLineupCol-${c.key}-${bId}">
            <div class="bp-lineup-col-header">
              <span class="bp-lineup-col-label" style="color:${c.color};">${c.label}</span>
              <span class="bp-lineup-col-badge">${d.total.toLocaleString()} tk</span>
            </div>
            <svg class="bp-lineup-svg" viewBox="0 0 ${svgW} ${svgH}">
              <defs>
                <clipPath id="${clipId}">
                  <path d="${g.pathD}" />
                </clipPath>
              </defs>

              <g clip-path="url(#${clipId})">
                <rect id="figZone-${c.key}-${bId}-1" x="0" y="0" width="${svgW}" height="${g.yTop + g.secH}" fill="#2563eb" opacity="0.9" />
                <rect id="figZone-${c.key}-${bId}-2" x="0" y="${g.yTop + g.secH}" width="${svgW}" height="${g.secH}" fill="#0d9488" opacity="0.9" />
                <rect id="figZone-${c.key}-${bId}-3" x="0" y="${g.yTop + 2 * g.secH}" width="${svgW}" height="${g.secH}" fill="#ea580c" opacity="0.9" />
                <rect id="figZone-${c.key}-${bId}-4" x="0" y="${g.yTop + 3 * g.secH}" width="${svgW}" height="${svgH - (g.yTop + 3 * g.secH)}" fill="#9333ea" opacity="0.9" />
              </g>

              <path d="${g.pathD}" fill="none" stroke="#0f172a" stroke-width="1.6" stroke-linejoin="round" />
              <circle cx="${cx}" cy="${g.dotCy}" r="${g.dotR}" fill="${c.dotColor}" stroke="#ffffff" stroke-width="1.4" />
              <line x1="${cx}" y1="${g.yTop}" x2="${cx}" y2="${g.yBase}" stroke="#ffffff" stroke-width="1.2" stroke-dasharray="2,2"/>
            </svg>
          </div>
        `;
      }).join('');

      // Section stat rows
      const statsHtml = BP_CORE_SECTIONS.map(sec => {
        const valComps = activeConfigs.map(c => `<strong>${colData[c.key].tokens[sec.name].toLocaleString()}</strong>`).join(' vs ');
        return `
          <div class="bp-lineup-stat-row" id="statRow-${bId}-${sec.order}">
            <span style="color:${sec.color}; font-weight:700;">${sec.order}. ${sec.shortLabel}:</span>
            <span>${valComps} tk</span>
          </div>
        `;
      }).join('');

      card.innerHTML = `
        <div class="bp-lineup-year-header">
          <div class="bp-lineup-year-title">${item.label || bId}</div>
          <div class="bp-lineup-year-sub">${subLines}</div>
        </div>

        <div class="bp-lineup-dual-wrap" style="grid-template-columns: repeat(${numCols}, 1fr);">
          ${colsHtml}
        </div>

        <div class="bp-lineup-stats">
          ${statsHtml}
        </div>
      `;

      // Hover highlighting for sections
      BP_CORE_SECTIONS.forEach(sec => {
        const row = card.querySelector(`#statRow-${bId}-${sec.order}`);
        if (row) {
          row.style.cursor = 'pointer';
          row.addEventListener('mouseenter', () => {
            activeConfigs.forEach(c => {
              const zone = card.querySelector(`#figZone-${c.key}-${bId}-${sec.order}`);
              if (zone) zone.style.filter = 'brightness(1.25)';
            });
            row.style.background = '#f1f5f9';
          });
          row.addEventListener('mouseleave', () => {
            activeConfigs.forEach(c => {
              const zone = card.querySelector(`#figZone-${c.key}-${bId}-${sec.order}`);
              if (zone) zone.style.filter = 'none';
            });
            row.style.background = 'transparent';
          });
        }
      });

      stage.appendChild(card);
    });
  }

  // Floating Tooltip for Outliers
  function showBpTooltip(e, o, sec) {
    let tip = document.getElementById('bpTooltip');
    if (!tip) {
      tip = document.createElement('div');
      tip.id = 'bpTooltip';
      tip.className = 'bp-tooltip-popover';
      document.body.appendChild(tip);
    }

    const isHigh = o.outlier_type === 'Very High';
    const icon = isHigh ? '📈 Max Length Outlier' : '📉 Min Length Outlier';
    const totalCore = o.total_tokens || 1;

    const secLines = BP_CORE_SECTIONS.map(s => {
      const tok = o.section_tokens ? (o.section_tokens[s.name] || 0) : 0;
      const pct = ((tok / totalCore) * 100).toFixed(1);
      const isOutlierSec = s.name === sec.name;
      return `<div style="display:flex; justify-content:space-between; gap:14px; margin-top:2px; ${isOutlierSec ? 'font-weight:800; color:#60a5fa;' : 'color:#cbd5e1;'}">
        <span>${s.order}. ${s.shortLabel}:</span>
        <span style="font-family:monospace;">${tok.toLocaleString()} tk (${pct}%)</span>
      </div>`;
    }).join('');

    tip.innerHTML = `
      <div style="font-weight:800; color:#ffffff; margin-bottom:4px; font-size:0.78rem; border-bottom:1px solid #334155; padding-bottom:4px;">
        ${icon} • ${sec.name}
      </div>
      <div style="font-size:0.70rem; color:#94a3b8; margin-bottom:6px;">
        ${o.paper_type} • ${o.conference} ${o.year} • Total: ${totalCore.toLocaleString()} tk
      </div>
      <div style="font-size:0.72rem;">
        ${secLines}
      </div>
      <div style="margin-top:6px; padding-top:4px; border-top:1px solid #334155; font-size:0.68rem; color:#38bdf8; text-align:right;">
        Click card to open paper & abstract in sidebar →
      </div>
    `;

    tip.classList.add('visible');
    positionBpTooltip(e, tip);
  }

  function positionBpTooltip(e, tip) {
    const tipW = 280;
    const tipH = 170;
    let x = e.clientX + 14;
    let y = e.clientY + 14;

    if (x + tipW > window.innerWidth) {
      x = e.clientX - tipW - 14;
    }
    if (y + tipH > window.innerHeight) {
      y = e.clientY - tipH - 14;
    }

    tip.style.left = `${Math.max(10, x)}px`;
    tip.style.top = `${Math.max(10, y)}px`;
  }

  function hideBpTooltip() {
    const tip = document.getElementById('bpTooltip');
    if (tip) {
      tip.classList.remove('visible');
    }
  }

  // Open Outlier Paper and Abstract in Right Sidebar
  function openOutlierInSidebar(o, sec) {
    if (!paperInspector || !inspectorContent) return;

    if (inspectorTitle) {
      inspectorTitle.textContent = `${o.paper_type}: ${o.conference} ${o.year}`;
    }

    const authorsDisplay = o.authors ? formatAuthorListApa(o.authors) : 'Unknown Authors';
    const isHigh = o.outlier_type === 'Very High';
    const outlierTitle = isHigh ? '📈 Max Length Outlier' : '📉 Min Length Outlier';

    inspectorContent.innerHTML = `
      <div class="paper-detail-card" style="padding: 16px; border: none; box-shadow: none;">
        <div style="font-size: 1.15rem; font-weight: 800; color: var(--text-primary); line-height: 1.35; margin-bottom: 8px;">
          ${o.title}
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom: 12px; font-size: 0.78rem;">
          <span style="font-weight:700; color:#1d4ed8; background:#eff6ff; padding:2px 8px; border-radius:4px; border:1px solid #bfdbfe;">
            ${o.paper_type}
          </span>
          <span style="color:var(--text-muted);">
            📅 <strong>${o.year}</strong> (${o.conference})
          </span>
        </div>

        <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 16px; font-style: italic;">
          ✍️ ${authorsDisplay}
        </div>

        <!-- Outlier Focus Banner -->
        <div style="background:#f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid ${sec.color}; border-radius: 6px; padding: 10px 14px; margin-bottom: 18px;">
          <div style="font-size: 0.82rem; font-weight: 800; color: ${sec.color}; display: flex; align-items: center; justify-content: space-between;">
            <span>${outlierTitle}: ${sec.name}</span>
            <span style="font-family: monospace; font-size: 0.84rem;">${o.tokens.toLocaleString()} tk (${o.pct_of_paper}%)</span>
          </div>
          <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 4px; line-height: 1.4;">
            ${o.context}
          </div>
        </div>

        <!-- Section Proportions Breakdown -->
        <div style="margin-bottom: 20px;">
          <div style="font-size: 0.82rem; font-weight: 800; color: var(--text-primary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.4px;">
            📊 Section Token Breakdown
          </div>
          <div style="display:flex; flex-direction:column; gap: 6px; background:#f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0;">
            ${BP_CORE_SECTIONS.map(s => {
              const tok = o.section_tokens ? (o.section_tokens[s.name] || 0) : 0;
              const pct = o.total_tokens > 0 ? ((tok / o.total_tokens) * 100).toFixed(1) : 0;
              const isTarget = s.name === sec.name;
              return `
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.78rem; ${isTarget ? 'font-weight:800;' : ''}">
                  <span style="color:${s.color}; display:flex; align-items:center; gap:6px;">
                    <span style="width:8px; height:8px; border-radius:50%; background:${s.color}; display:inline-block;"></span>
                    ${s.name}:
                  </span>
                  <span style="font-family:monospace; color:${isTarget ? s.color : 'var(--text-primary)'};">
                    ${tok.toLocaleString()} tk (${pct}%)
                  </span>
                </div>
              `;
            }).join('')}
            <div style="border-top:1px solid #e2e8f0; padding-top:6px; margin-top:2px; display:flex; justify-content:space-between; font-size:0.78rem; font-weight:800;">
              <span>Total Substantive Core:</span>
              <span style="font-family:monospace;">${o.total_tokens.toLocaleString()} tk</span>
            </div>
          </div>
        </div>

        <!-- Abstract Block -->
        <div>
          <div style="font-size: 0.82rem; font-weight: 800; color: var(--text-primary); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.4px; display:flex; align-items:center; gap:6px;">
            <span>📖 Abstract</span>
          </div>
          <div style="font-size: 0.86rem; line-height: 1.6; color: #334155; background: #ffffff; padding: 14px; border-radius: 8px; border: 1px solid #cbd5e1; white-space: pre-line; box-shadow: var(--shadow-sm);">
            ${o.abstract || 'No abstract text available for this publication.'}
          </div>
        </div>

        <!-- Action Link -->
        <div style="margin-top: 20px; text-align: right;">
          <a href="./viewer.html?keywords=${encodeURIComponent(o.title)}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; font-size:0.80rem; font-weight:700; color:var(--primary); text-decoration:none; padding:8px 14px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px;">
            🔍 Open in Literature Review Viewer ↗
          </a>
        </div>
      </div>
    `;

    paperInspector.classList.add('open');
    if (inspectorBackdrop) {
      inspectorBackdrop.classList.add('open');
      inspectorBackdrop.style.display = 'block';
    }
  }

  function renderOutlierThumbnails() {
    if (!bpData || !bpData.outliers_by_type) return;
    const grid = document.getElementById('bpThumbnailsGrid');
    if (!grid) return;

    grid.innerHTML = '';
    let cardIdx = 0;

    // Strict sorting: Section > Max/Min > Full/Short
    const secOrder = BP_CORE_SECTIONS;
    const typeOrder = ['Very High', 'Very Low']; // Max first, then Min

    // Determine genres to inspect
    let genresToInspect = [];
    if (bpActiveOutlierGenre === 'all') {
      genresToInspect = ['full', 'short']; // Default: empirical scholarship only (symposia excluded)
    } else if (bpActiveOutlierGenre === 'full') {
      genresToInspect = ['full'];
    } else if (bpActiveOutlierGenre === 'short') {
      genresToInspect = ['short'];
    } else if (bpActiveOutlierGenre === 'other') {
      genresToInspect = ['other'];
    }

    const sortedItems = [];
    secOrder.forEach(sec => {
      typeOrder.forEach(tType => {
        genresToInspect.forEach(grp => {
          if (bpActiveOutlierType !== 'All' && bpActiveOutlierType !== tType) return;

          const list = bpData.outliers_by_type[grp]?.[sec.name] || [];
          const match = list.find(o => o.outlier_type === tType);
          if (match) {
            sortedItems.push({ o: match, sec });
          }
        });
      });
    });

    sortedItems.forEach(({ o, sec }) => {
      cardIdx++;

      const svgW = 120;
      const svgH = 160;
      const cx = svgW / 2;

      // Absolute token scaling with clamping ensuring x in [8, 112]
      const geom = computeSmoothViolinGeometry(o.section_tokens, cx, svgH, 2500, svgW);
      const clipId = `thumbClip-${cardIdx}`;

      // Highlight outlier section with opacity 1.0, others muted at 0.28
      const op1 = sec.order === 1 ? '1.0' : '0.28';
      const op2 = sec.order === 2 ? '1.0' : '0.28';
      const op3 = sec.order === 3 ? '1.0' : '0.28';
      const op4 = sec.order === 4 ? '1.0' : '0.28';

      const card = document.createElement('div');
      card.className = 'bp-thumbnail-card';
      card.style.setProperty('--card-theme', sec.color);
      card.onclick = () => openOutlierInSidebar(o, sec);

      // Tooltip listeners for examining section % breakdown
      card.addEventListener('mouseenter', (e) => showBpTooltip(e, o, sec));
      card.addEventListener('mousemove', (e) => {
        const tip = document.getElementById('bpTooltip');
        if (tip) positionBpTooltip(e, tip);
      });
      card.addEventListener('mouseleave', hideBpTooltip);

      const apaAuthor = o.authors ? formatAuthorListApa(o.authors) : 'Unknown Author';

      card.innerHTML = `
        <!-- Pure Violin Graphic: Primary visual element with zero distracting overlays -->
        <div class="bp-thumb-figure-box">
          <svg class="bp-thumb-svg" viewBox="0 0 ${svgW} ${svgH}">
            <defs>
              <clipPath id="${clipId}">
                <path d="${geom.pathD}" />
              </clipPath>
            </defs>

            <!-- Clipped 4 sections with outlier highlighted (covers 100% of width) -->
            <g clip-path="url(#${clipId})">
              <rect x="0" y="0" width="${svgW}" height="${geom.yTop + geom.secH}" fill="#2563eb" opacity="${op1}"/>
              <rect x="0" y="${geom.yTop + geom.secH}" width="${svgW}" height="${geom.secH}" fill="#0d9488" opacity="${op2}"/>
              <rect x="0" y="${geom.yTop + 2 * geom.secH}" width="${svgW}" height="${geom.secH}" fill="#ea580c" opacity="${op3}"/>
              <rect x="0" y="${geom.yTop + 3 * geom.secH}" width="${svgW}" height="${svgH - (geom.yTop + 3 * geom.secH)}" fill="#9333ea" opacity="${op4}"/>
            </g>

            <!-- Silhouette outer boundary stroke -->
            <path d="${geom.pathD}" fill="none" stroke="${sec.color}" stroke-width="1.8"/>

            <!-- Decorative Floating Abstract Head Dot -->
            <circle cx="${cx}" cy="${geom.dotCy}" r="${geom.dotR}" fill="${sec.color}" stroke="#ffffff" stroke-width="1.2" />

            <!-- Central spine axis -->
            <line x1="${cx}" y1="${geom.yTop}" x2="${cx}" y2="${geom.yBase}" stroke="#ffffff" stroke-width="1" stroke-dasharray="2,2"/>
          </svg>
        </div>

        <!-- Clean Data: Title, Author and Year only -->
        <div class="bp-thumb-content">
          <div class="bp-thumb-title" title="${o.title}">${o.title}</div>
          <div class="bp-thumb-authors-year">${apaAuthor} (${o.year})</div>
        </div>
      `;

      grid.appendChild(card);
    });
  }

  // Export globally for inline triggers
  window.openPaperInspector = openPaperInspector;

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
