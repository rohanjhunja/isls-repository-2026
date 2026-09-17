let reviewsList = [];
let activeReviewId = null;
let isDipstickMode = true;
let activeReviewMeta = {};
let allPapers = [];
let filteredPapers = [];
let preloadedTitles = [];
let activePaper = null;
let isResizingColumn = false;
let isResizingOverlay = false;
let currentSortBy = 'relevance'; // 'relevance' or 'year'
let isScopeExpanded = false;

// Helper to render SVG Line Icons from sprite sheet
function getIcon(name, extraClass = '') {
  const cls = extraClass ? `icon ${extraClass}` : 'icon';
  return `<svg class="${cls}"><use href="icons/icons.svg#icon-${name}"/></svg>`;
}

// Global Column Multi-Select Filter Selections
let columnFilterSelections = {}; // { colKey: Set of selected string values }

// Default Column Definitions Mapping
const DEFAULT_COLUMN_DEFINITIONS = {
  "title": { "label": "Paper Title", "width": 280, "minWidth": 220 },
  "year": { "label": "Year", "width": 80, "minWidth": 70, "isShort": true },
  "conference": { "label": "Conference", "width": 100, "minWidth": 85, "isShort": true },
  "paper_type": { "label": "Paper Type", "width": 125, "minWidth": 95, "isShort": true },
  "authors": { "label": "Authors", "width": 200, "minWidth": 160 },
  "abstract": { "label": "Abstract", "width": 380, "minWidth": 280 },
  "relevance": { "label": "Relevance", "width": 100, "minWidth": 80, "isShort": true },
  "databases_searched": { "label": "Databases Searched", "width": 160, "minWidth": 140 },
  "summary": { "label": "~50-Word Summary", "width": 320, "minWidth": 250 },
  "keywords": { "label": "Keywords", "width": 200, "minWidth": 160 }
};

function formatConferenceAcronym(conf) {
  const s = String(conf || '').toUpperCase();
  if (s.includes('CSCL')) return 'CSCL';
  if (s.includes('ICLS')) return 'ICLS';
  return 'ISLS';
}

function getEffectivePaperType(paper) {
  if (!paper) return 'Paper';
  if (paper.is_practise_paper || paper.is_practice_paper) {
    return 'Practise Paper';
  }
  return paper.paper_type || 'Paper';
}

const DIPSTICK_COLUMNS = ["title", "year", "conference", "paper_type", "authors", "abstract"];

const STANDARD_PROPERTIES = new Set([
  "paper_id", "title", "authors", "year", "conference", "paper_type", "is_practise_paper", "abstract",
  "summary", "keywords", "databases_searched"
]);

// DOM Elements
const sidebarNav = document.getElementById('sidebarNav');
const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
const mobileSidebarToggleBtn = document.getElementById('mobileSidebarToggleBtn');
const sidebarBackdrop = document.getElementById('sidebarBackdrop');
const reviewsListEl = document.getElementById('reviewsList');
const dipstickNavItem = document.getElementById('dipstickNavItem');

const searchInput = document.getElementById('searchInput');
const searchClearBtn = document.getElementById('searchClearBtn');
const saveAsReviewBtn = document.getElementById('saveAsReviewBtn');
const controlActionsToggle = document.getElementById('controlActionsToggle');
const controlActions = document.getElementById('controlActions');
const dipstickControls = document.getElementById('dipstickControls');
const multiSelectToggleBtn = document.getElementById('multiSelectToggleBtn');
const multiSelectPopover = document.getElementById('multiSelectPopover');
const expandScopeBtn = document.getElementById('expandScopeBtn');

function updateClearBtnVisibility() {
  if (!searchClearBtn) return;
  if (searchInput && searchInput.value.trim()) {
    searchClearBtn.classList.remove('hidden');
  } else {
    searchClearBtn.classList.add('hidden');
  }
}

function closeMobileSidebar() {
  if (sidebarNav) sidebarNav.classList.remove('open');
  if (sidebarBackdrop) sidebarBackdrop.classList.remove('active');
}

const rowModeToggle = document.getElementById('rowModeToggle');
const rowModeLabel = document.getElementById('rowModeLabel');
const tableExportContainer = document.getElementById('tableExportContainer');
const copyTableBtn = document.getElementById('copyTableBtn');
const tableExportPopover = document.getElementById('tableExportPopover');
const copyTableItem = document.getElementById('copyTableItem');
const downloadCsvItem = document.getElementById('downloadCsvItem');
const dataTable = document.getElementById('dataTable');
const tableHeaderRow = document.getElementById('tableHeaderRow');
const tableBody = document.getElementById('tableBody');
const paperCountBadge = document.getElementById('paperCountBadge');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');

const detailsOverlay = document.getElementById('detailsOverlay');
const overlayBackdrop = document.getElementById('overlayBackdrop');
const closeOverlayBtn = document.getElementById('closeOverlayBtn');
const overlayResizer = document.getElementById('overlayResizer');
const resetColumnsBtn = document.getElementById('resetColumnsBtn');

function setExportControlsVisibility(visible) {
  const el = tableExportContainer || copyTableBtn;
  if (!el) return;
  if (visible) {
    el.classList.remove('hidden');
  } else {
    el.classList.add('hidden');
    if (tableExportPopover) tableExportPopover.classList.remove('active');
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  setupMultiSelectPopover();
  setupTableExportDropdown();
  setupOverlayResizing();
  window.addEventListener('popstate', parseUrlQueryParams);
  await preloadTitleIndex();
  parseUrlQueryParams();
  await fetchReviewsList();
});

// Preload Lightweight Title Index for Instant (<3ms) Client-Side Search
async function preloadTitleIndex() {
  try {
    const res = await fetch('/api/titles');
    if (res.ok) {
      preloadedTitles = await res.json();
      allPapers = [...preloadedTitles];
      if (isDipstickMode) {
        applyFilters();
      }
    }
  } catch (err) {
    console.error('Failed to preload titles index:', err);
  }
}

// Parse URL Query Params (e.g. ?review=systematic_review_lit_review or ?keywords=Generative+AI or ?q=play)
function parseUrlQueryParams() {
  const urlParams = new URLSearchParams(window.location.search);
  let reviewId = urlParams.get('review') || urlParams.get('review_id') || urlParams.get('id');

  if (!reviewId) {
    const pathMatch = window.location.pathname.match(/^\/(?:review|reviews)\/([^\/]+)$/);
    if (pathMatch) {
      reviewId = decodeURIComponent(pathMatch[1]);
    }
  }

  if (!reviewId && window.location.hash) {
    const hash = window.location.hash.substring(1);
    if (hash.startsWith('review=')) {
      reviewId = decodeURIComponent(hash.substring(7));
    } else if (hash && !hash.includes('=')) {
      reviewId = decodeURIComponent(hash);
    }
  }

  const kwParam = urlParams.get('keywords') || urlParams.get('q') || urlParams.get('query') || urlParams.get('search');

  if (reviewId) {
    loadReview(reviewId, false);
  } else if (kwParam) {
    if (searchInput) {
      searchInput.value = kwParam;
    }
    openDipstickMode(false);
  } else {
    openDipstickMode(false);
  }
}

// Open Dipstick Initial Mode (No Saved Review Selected in Navigation)
function openDipstickMode(updateUrl = true) {
  closeMobileSidebar();
  isDipstickMode = true;
  isScopeExpanded = false;
  activeReviewId = null;
  columnFilterSelections = {};
  activeReviewMeta = {
    selected_columns: DIPSTICK_COLUMNS,
    visible_columns: DIPSTICK_COLUMNS
  };

  if (updateUrl && window.location.search) {
    window.history.pushState({ mode: 'dipstick' }, '', window.location.pathname);
  }

  renderSidebarReviews();

  if (saveAsReviewBtn) saveAsReviewBtn.classList.add('hidden');
  if (dipstickControls) dipstickControls.classList.add('hidden');
  setExportControlsVisibility(false);

  if (searchInput) {
    searchInput.placeholder = 'Search titles, authors, concepts (e.g. Generative AI AND Scaffolding, CSCL OR ICLS)...';
    updateClearBtnVisibility();
  }

  allPapers = [...preloadedTitles];
  filteredPapers = [...allPapers];
  configureHeaders(DIPSTICK_COLUMNS);
  applyFilters();
}

let isHostedMode = false;

// Fetch List of Saved Reviews
async function fetchReviewsList() {
  try {
    const res = await fetch('/api/reviews');
    if (!res.ok) throw new Error('API 404');
    reviewsList = await res.json();
    renderSidebarReviews();
  } catch (err) {
    console.warn('Backend /api/reviews unavailable, falling back to static sample reviews:', err);
    isHostedMode = true;
    try {
      const sampleRes = await fetch('data/sample_reviews/manifest.json');
      const manifest = await sampleRes.json();
      reviewsList = manifest.map(m => ({
        id: m.id,
        name: m.name,
        description: m.description,
        paper_count: m.paper_count,
        is_sample: true
      }));
      renderSidebarReviews();
      if (!activeReviewId && reviewsList.length > 0) {
        loadReview(reviewsList[0].id);
      }
    } catch (sampleErr) {
      console.error('Failed to load sample reviews:', sampleErr);
      reviewsListEl.innerHTML = `<div style="padding:15px; color:#64748b; font-size:12px;">Failed to load reviews.</div>`;
    }
  }
}

// Global Context Dropdown Menu Management
let activeContextMenu = null;

function closeContextMenu() {
  if (activeContextMenu) {
    activeContextMenu.remove();
    activeContextMenu = null;
  }
  document.querySelectorAll('.btn-dots.active').forEach(b => b.classList.remove('active'));
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.item-dropdown-menu')) {
    closeContextMenu();
  }
});
document.addEventListener('scroll', closeContextMenu, true);
window.addEventListener('resize', closeContextMenu);

function openContextMenu(e, targetType, targetData, triggerBtn = null) {
  if (e) {
    e.preventDefault();
    e.stopPropagation();
  }
  closeContextMenu();

  if (triggerBtn) {
    triggerBtn.classList.add('active');
  }

  const menu = document.createElement('div');
  menu.className = 'item-dropdown-menu';

  let itemsHtml = '';

  if (targetType === 'review') {
    itemsHtml = `
      <div class="dropdown-item" data-action="copy-text">
        ${getIcon('copy')} Copy Text
      </div>
      <div class="dropdown-item" data-action="copy-cite">
        ${getIcon('quote')} Copy Citation
      </div>
      <div class="dropdown-item" data-action="copy-ref">
        ${getIcon('file-text')} Copy Reference
      </div>
      <div class="dropdown-divider"></div>
      <div class="dropdown-item danger" data-action="delete">
        ${getIcon('trash')} Delete Review
      </div>
    `;
  } else if (targetType === 'column') {
    const { colKey, label } = targetData;
    const isStandard = STANDARD_PROPERTIES.has(colKey);
    itemsHtml = `
      <div class="dropdown-item" data-action="sort-asc">
        ${getIcon('chevron-up')} Sort Ascending (A-Z / Low-High)
      </div>
      <div class="dropdown-item" data-action="sort-desc">
        ${getIcon('chevron-down')} Sort Descending (Z-A / High-Low)
      </div>
      <div class="dropdown-item" data-action="reverse-order">
        ${getIcon('repeat')} Reverse Order
      </div>
      <div class="dropdown-divider"></div>
      <div class="dropdown-item" data-action="copy-text">
        ${getIcon('copy')} Copy Text
      </div>
      <div class="dropdown-item" data-action="copy-cite">
        ${getIcon('quote')} Copy Citation
      </div>
      <div class="dropdown-item" data-action="copy-ref">
        ${getIcon('file-text')} Copy Reference
      </div>
      <div class="dropdown-divider"></div>
      ${isStandard ? 
        `<div class="dropdown-item disabled" title="Standard properties cannot be deleted.">${getIcon('trash')} Delete Column (Standard)</div>` :
        `<div class="dropdown-item danger" data-action="delete">${getIcon('trash')} Delete Column</div>`
      }
    `;
  } else if (targetType === 'title') {
    itemsHtml = `
      <div class="dropdown-item" data-action="copy-row">
        ${getIcon('copy')} Copy Row
      </div>
      <div class="dropdown-item" data-action="copy-text">
        ${getIcon('copy')} Copy Text
      </div>
      <div class="dropdown-item" data-action="copy-cite">
        ${getIcon('quote')} Copy Citation
      </div>
      <div class="dropdown-item" data-action="copy-ref">
        ${getIcon('file-text')} Copy Reference
      </div>
      <div class="dropdown-divider"></div>
      <div class="dropdown-item danger" data-action="delete">
        ${getIcon('trash')} Delete Paper
      </div>
    `;
  }

  menu.innerHTML = itemsHtml;
  document.body.appendChild(menu);
  activeContextMenu = menu;

  let x = e ? e.clientX : 0;
  let y = e ? e.clientY : 0;

  if (triggerBtn) {
    const rect = triggerBtn.getBoundingClientRect();
    x = rect.right - 175;
    y = rect.bottom + 4;
  }

  const menuWidth = 180;
  const menuHeight = 165;

  if (x + menuWidth > window.innerWidth - 10) {
    x = window.innerWidth - menuWidth - 10;
  }
  if (x < 10) x = 10;

  if (y + menuHeight > window.innerHeight - 10) {
    y = y - menuHeight - (triggerBtn ? 30 : 0);
  }
  if (y < 10) y = 10;

  menu.style.left = `${x}px`;
  menu.style.top = `${y}px`;

  menu.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', (evt) => {
      evt.stopPropagation();
      const action = item.dataset.action;
      if (!action || item.classList.contains('disabled')) return;

      closeContextMenu();

      if (targetType === 'review') {
        const r = targetData;
        if (action === 'copy-text') {
          copyToClipboard(`Review: ${r.name}\n${r.description || ''}`, 'Review Text');
        } else if (action === 'copy-cite') {
          copyToClipboard(`Review: ${r.name}`, 'Review Citation');
        } else if (action === 'copy-ref') {
          copyToClipboard(r.id, 'Review Reference');
        } else if (action === 'delete') {
          deleteReview(r.id, r.name);
        }
      } else if (targetType === 'column') {
        const { colKey, label } = targetData;
        if (action === 'sort-asc') {
          sortPapersByColumn(colKey, 'asc');
        } else if (action === 'sort-desc') {
          sortPapersByColumn(colKey, 'desc');
        } else if (action === 'reverse-order') {
          sortPapersByColumn(colKey, 'reverse');
        } else if (action === 'copy-text') {
          copyToClipboard(label, 'Column Header');
        } else if (action === 'copy-cite') {
          copyToClipboard(`${label} (${colKey})`, 'Column Citation');
        } else if (action === 'copy-ref') {
          copyToClipboard(colKey, 'Column Reference');
        } else if (action === 'delete') {
          deleteColumn(colKey, label);
        }
      } else if (targetType === 'title') {
        const paper = targetData;
        if (action === 'copy-row') {
          copyPaperRowToClipboard(paper);
        } else if (action === 'copy-text') {
          copyToClipboard(`${paper.title || 'Untitled'}\n\nAbstract:\n${paper.abstract || ''}`, 'Paper Text');
        } else if (action === 'copy-cite') {
          const authors = paper.authors || 'Unknown';
          const year = paper.year || 'n.d.';
          const title = paper.title || 'Untitled';
          const conf = paper.conference || 'ISLS';
          copyToClipboard(`${authors} (${year}). ${title}. ${conf}.`, 'APA Citation');
        } else if (action === 'copy-ref') {
          copyToClipboard(paper.id, 'Paper Reference');
        } else if (action === 'delete') {
          deletePaper(paper.id, paper.title);
        }
      }
    });
  });
}

function getPaperCellValue(paper, colKey) {
  if (!paper) return '';
  const val = paper[colKey];
  if (Array.isArray(val)) {
    return val.join(', ');
  }
  if (val === undefined || val === null) {
    return '';
  }
  if (typeof val === 'object') {
    return JSON.stringify(val);
  }
  return String(val);
}

function cleanTsvCell(str) {
  if (!str) return '';
  const s = String(str);
  if (s.includes('\t') || s.includes('\n') || s.includes('\r') || s.includes('"')) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function copyTableToClipboard() {
  if (!filteredPapers || filteredPapers.length === 0) {
    showStatus('No table data to copy.');
    setTimeout(hideStatus, 2000);
    return;
  }

  const selectedColumns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;
  const columnDefs = Object.assign({}, DEFAULT_COLUMN_DEFINITIONS, activeReviewMeta.column_definitions || {});

  const headers = selectedColumns.map(colKey => (columnDefs[colKey] && columnDefs[colKey].label) ? columnDefs[colKey].label : colKey);

  // Build TSV (Plain Text)
  const tsvHeader = headers.map(cleanTsvCell).join('\t');
  const tsvRows = filteredPapers.map(paper => {
    return selectedColumns.map(col => cleanTsvCell(getPaperCellValue(paper, col))).join('\t');
  });
  const tsvContent = [tsvHeader, ...tsvRows].join('\n');

  // Build HTML Table
  let htmlContent = '<table border="1"><thead><tr>';
  headers.forEach(h => {
    htmlContent += `<th>${escapeHtml(h)}</th>`;
  });
  htmlContent += '</tr></thead><tbody>';
  filteredPapers.forEach(paper => {
    htmlContent += '<tr>';
    selectedColumns.forEach(col => {
      htmlContent += `<td>${escapeHtml(getPaperCellValue(paper, col))}</td>`;
    });
    htmlContent += '</tr>';
  });
  htmlContent += '</tbody></table>';

  copyTableDataToClipboard(tsvContent, htmlContent, `table (${filteredPapers.length} rows)`);
}

function copyPaperRowToClipboard(paper) {
  if (!paper) return;

  const selectedColumns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;
  const columnDefs = Object.assign({}, DEFAULT_COLUMN_DEFINITIONS, activeReviewMeta.column_definitions || {});

  const headers = selectedColumns.map(colKey => (columnDefs[colKey] && columnDefs[colKey].label) ? columnDefs[colKey].label : colKey);

  // Build TSV (Plain Text)
  const tsvRow = selectedColumns.map(col => cleanTsvCell(getPaperCellValue(paper, col))).join('\t');

  // Build HTML Table
  let htmlContent = '<table border="1"><thead><tr>';
  headers.forEach(h => {
    htmlContent += `<th>${escapeHtml(h)}</th>`;
  });
  htmlContent += '</tr></thead><tbody><tr>';
  selectedColumns.forEach(col => {
    htmlContent += `<td>${escapeHtml(getPaperCellValue(paper, col))}</td>`;
  });
  htmlContent += '</tr></tbody></table>';

  copyTableDataToClipboard(tsvRow, htmlContent, `row "${paper.title || paper.id}"`);
}

function copyTableDataToClipboard(tsvContent, htmlContent, label) {
  if (navigator.clipboard && window.ClipboardItem) {
    const blobText = new Blob([tsvContent], { type: 'text/plain' });
    const blobHtml = new Blob([htmlContent], { type: 'text/html' });
    const item = new ClipboardItem({
      'text/plain': blobText,
      'text/html': blobHtml
    });
    navigator.clipboard.write([item]).then(() => {
      showStatus(`${getIcon('check-circle')} Copied ${label} to clipboard!`);
      setTimeout(hideStatus, 2500);
    }).catch(err => {
      console.warn('ClipboardItem failed, fallback to writeText:', err);
      copyToClipboard(tsvContent, label);
    });
  } else {
    copyToClipboard(tsvContent, label);
  }
}

function copyToClipboard(text, label) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showStatus(`${getIcon('check-circle')} Copied ${label} to clipboard!`);
      setTimeout(hideStatus, 2500);
    }).catch(() => {
      fallbackCopy(text, label);
    });
  } else {
    fallbackCopy(text, label);
  }
}

function fallbackCopy(text, label) {
  const ta = document.createElement('textarea');
  ta.value = text;
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  showStatus(`${getIcon('check-circle')} Copied ${label} to clipboard!`);
  setTimeout(hideStatus, 2500);
}

function cleanCsvCell(str) {
  if (str === null || str === undefined) return '';
  const s = String(str);
  if (s.includes(',') || s.includes('\n') || s.includes('\r') || s.includes('"')) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

function generateTableCsv() {
  if (!filteredPapers || filteredPapers.length === 0) {
    return null;
  }

  const selectedColumns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;
  const columnDefs = Object.assign({}, DEFAULT_COLUMN_DEFINITIONS, activeReviewMeta.column_definitions || {});

  const headers = selectedColumns.map(colKey => (columnDefs[colKey] && columnDefs[colKey].label) ? columnDefs[colKey].label : colKey);

  const csvHeader = headers.map(cleanCsvCell).join(',');
  const csvRows = filteredPapers.map(paper => {
    return selectedColumns.map(col => cleanCsvCell(getPaperCellValue(paper, col))).join(',');
  });

  return [csvHeader, ...csvRows].join('\r\n');
}

function downloadTableAsCsv() {
  if (!filteredPapers || filteredPapers.length === 0) {
    showStatus('No table data to download.');
    setTimeout(hideStatus, 2000);
    return;
  }

  const csvContent = generateTableCsv();
  if (!csvContent) return;

  let filename = 'isls_papers.csv';
  if (activeReviewMeta && activeReviewMeta.name) {
    filename = `${activeReviewMeta.name.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}.csv`;
  } else if (searchInput && searchInput.value.trim()) {
    filename = `dipstick_${searchInput.value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_')}.csv`;
  }

  // Prepend \uFEFF UTF-8 BOM so Microsoft Excel correctly displays non-ASCII characters
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showStatus(`${getIcon('check-circle')} Downloaded ${filename} (${filteredPapers.length} rows)!`);
  setTimeout(hideStatus, 2500);
}

function setupTableExportDropdown() {
  if (!copyTableBtn || !tableExportPopover) return;

  copyTableBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    // Close other popovers if active
    if (multiSelectPopover) multiSelectPopover.classList.remove('active');
    document.querySelectorAll('.col-filter-popover').forEach(p => p.classList.remove('active'));

    tableExportPopover.classList.toggle('active');
  });

  if (copyTableItem) {
    copyTableItem.addEventListener('click', (e) => {
      e.stopPropagation();
      tableExportPopover.classList.remove('active');
      copyTableToClipboard();
    });
  }

  if (downloadCsvItem) {
    downloadCsvItem.addEventListener('click', (e) => {
      e.stopPropagation();
      tableExportPopover.classList.remove('active');
      downloadTableAsCsv();
    });
  }

  document.addEventListener('click', (e) => {
    if (!tableExportPopover.contains(e.target) && e.target !== copyTableBtn && !copyTableBtn.contains(e.target)) {
      tableExportPopover.classList.remove('active');
    }
  });
}


async function deleteReview(reviewId, reviewName) {
  const rev = reviewsList.find(r => r.id === reviewId);
  if (rev && rev.is_sample) {
    alert(`"${reviewName || reviewId}" is a curated sample template and cannot be deleted.`);
    return;
  }
  if (!confirm(`Are you sure you want to delete review "${reviewName || reviewId}"?`)) return;

  showStatus(`Deleting review '${reviewName}'...`);
  try {
    let res = await fetch(`/api/reviews/${encodeURIComponent(reviewId)}`, { method: 'DELETE' });
    if (!res.ok) {
      res = await fetch(`/api/reviews/${encodeURIComponent(reviewId)}/delete`, { method: 'POST' });
    }
    if (!res.ok) throw new Error('Failed to delete review');

    reviewsList = reviewsList.filter(r => r.id !== reviewId);
    renderSidebarReviews();

    if (activeReviewId === reviewId) {
      openDipstickMode();
    }
    showStatus(`${getIcon('check-circle')} Deleted review '${reviewName || reviewId}'`);
    setTimeout(hideStatus, 2500);
  } catch (err) {
    console.error('Delete review error:', err);
    showStatus(`Failed to delete review.`);
    setTimeout(hideStatus, 3000);
  }
}

async function deletePaper(paperId, paperTitle) {
  if (!confirm(`Are you sure you want to delete paper "${paperTitle || paperId}" from this review?`)) return;

  if (activeReviewId && !isDipstickMode) {
    showStatus(`Removing paper from review...`);
    try {
      let res = await fetch(`/api/reviews/${encodeURIComponent(activeReviewId)}/papers/${encodeURIComponent(paperId)}`, { method: 'DELETE' });
      if (!res.ok) {
        res = await fetch(`/api/reviews/${encodeURIComponent(activeReviewId)}/papers/${encodeURIComponent(paperId)}/delete`, { method: 'POST' });
      }
      if (!res.ok) throw new Error('Failed to delete paper from review');
    } catch (err) {
      console.error('Delete paper error:', err);
    }
  }

  allPapers = allPapers.filter(p => p.id !== paperId);
  filteredPapers = filteredPapers.filter(p => p.id !== paperId);
  renderTable();
  showStatus(`${getIcon('check-circle')} Paper removed`);
  setTimeout(hideStatus, 2500);
}

async function deleteColumn(colKey, colLabel) {
  if (STANDARD_PROPERTIES.has(colKey)) {
    alert(`Standard property '${colLabel}' cannot be deleted.`);
    return;
  }

  if (!confirm(`Are you sure you want to delete column "${colLabel || colKey}" from this review?`)) return;

  if (activeReviewId && !isDipstickMode) {
    showStatus(`Deleting column '${colLabel}'...`);
    try {
      let res = await fetch(`/api/reviews/${encodeURIComponent(activeReviewId)}/columns/${encodeURIComponent(colKey)}`, { method: 'DELETE' });
      if (!res.ok) {
        res = await fetch(`/api/reviews/${encodeURIComponent(activeReviewId)}/columns/${encodeURIComponent(colKey)}/delete`, { method: 'POST' });
      }
      if (!res.ok) throw new Error('Failed to delete column');
    } catch (err) {
      console.error('Delete column error:', err);
    }
  }

  if (activeReviewMeta.selected_columns) {
    activeReviewMeta.selected_columns = activeReviewMeta.selected_columns.filter(c => c !== colKey);
  }
  if (activeReviewMeta.visible_columns) {
    activeReviewMeta.visible_columns = activeReviewMeta.visible_columns.filter(c => c !== colKey);
  }

  const updatedColumns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS.filter(c => c !== colKey);
  configureHeaders(updatedColumns);
  applyFilters();
  showStatus(`${getIcon('check-circle')} Deleted column '${colLabel}'`);
  setTimeout(hideStatus, 2500);
}

// Render Left Sidebar Navigation Items
function renderSidebarReviews() {
  const userReviews = reviewsList.filter(r => !r.is_sample);
  const sampleReviews = reviewsList.filter(r => r.is_sample);

  function getReviewItemHtml(r) {
    const isActive = (r.id === activeReviewId && !isDipstickMode) ? 'active' : '';
    const tooltip = `${escapeHtml(r.name)} (${r.paper_count} papers)`;
    const sampleBadge = r.is_sample ? '<span class="badge-sample">Sample</span>' : '';
    return `
      <div class="review-item ${isActive}" data-id="${r.id}" title="${tooltip}">
        <span class="review-item-icon">${getIcon('file-text')}</span>
        <div class="review-item-content-group">
          <div class="review-item-header">
            <span class="review-item-title">${escapeHtml(r.name)} ${sampleBadge}</span>
          </div>
          <div class="review-item-desc">${escapeHtml(r.description || 'Saved literature review dataset')}</div>
        </div>
        <div class="review-item-aside">
          <span class="review-item-count">${r.paper_count}</span>
          <button class="btn-dots review-dots-btn" title="Review options" data-id="${r.id}">
            ${getIcon('more-vertical')}
          </button>
        </div>
      </div>
    `;
  }

  let html = '';

  // 1. My Saved Reviews Section
  html += `
    <div class="sidebar-section-title" style="display:flex; justify-content:space-between; align-items:center; padding: 10px 14px 4px;">
      <span>My Saved Reviews</span>
      <span style="font-size:10px; background:#e2e8f0; color:#475569; padding:1px 6px; border-radius:10px;">${userReviews.length}</span>
    </div>
  `;

  if (userReviews.length === 0) {
    html += `
      <div style="padding: 10px 12px; font-size: 11px; color: #94a3b8; line-height: 1.4; border-radius: 6px; background: rgba(241, 245, 249, 0.6); margin: 4px 6px 8px 6px; border: 1px dashed #cbd5e1;">
        No local reviews saved yet. Use the <strong>Search</strong> above or type <code>import &lt;file&gt;</code> in agent chat.
      </div>
    `;
  } else {
    userReviews.forEach(r => {
      html += getReviewItemHtml(r);
    });
  }

  // 2. Curated System Samples Section
  if (sampleReviews.length > 0) {
    html += `
      <div class="sidebar-section-title" style="display:flex; justify-content:space-between; align-items:center; padding: 12px 14px 4px; margin-top: 6px; border-top: 1px solid #f1f5f9;">
        <span>Curated Samples</span>
        <span style="font-size:10px; background:#e2e8f0; color:#475569; padding:1px 6px; border-radius:10px;">${sampleReviews.length}</span>
      </div>
    `;
    sampleReviews.forEach(r => {
      html += getReviewItemHtml(r);
    });
  }

  reviewsListEl.innerHTML = html;

  if (dipstickNavItem) {
    if (isDipstickMode) {
      dipstickNavItem.style.background = '#e0e7ff';
      dipstickNavItem.style.borderColor = '#818cf8';
    } else {
      dipstickNavItem.style.background = 'var(--accent-light)';
      dipstickNavItem.style.borderColor = '#c7d2fe';
    }
  }

  document.querySelectorAll('.review-item').forEach(item => {
    const revId = item.dataset.id;
    const revData = reviewsList.find(r => r.id === revId);

    item.addEventListener('click', (e) => {
      if (e.target.closest('.btn-dots')) return;
      loadReview(revId);
    });

    item.addEventListener('contextmenu', (e) => {
      if (revData) openContextMenu(e, 'review', revData);
    });

    const dotsBtn = item.querySelector('.review-dots-btn');
    if (dotsBtn && revData) {
      dotsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openContextMenu(e, 'review', revData, dotsBtn);
      });
    }
  });
}

// Load Selected Saved Review Data
async function loadReview(reviewId, updateUrl = true) {
  closeMobileSidebar();
  isDipstickMode = false;
  activeReviewId = reviewId;
  renderSidebarReviews();

  if (updateUrl) {
    const targetUrl = `${window.location.pathname}?review=${encodeURIComponent(reviewId)}`;
    if (window.location.search !== `?review=${encodeURIComponent(reviewId)}`) {
      window.history.pushState({ reviewId }, '', targetUrl);
    }
  }

  if (saveAsReviewBtn) saveAsReviewBtn.classList.add('hidden');
  if (dipstickControls) dipstickControls.classList.add('hidden');
  setExportControlsVisibility(true);

  if (searchInput) {
    searchInput.value = '';
    searchInput.placeholder = 'Filter papers in this review (supports AND, OR, comma, quotes)...';
    updateClearBtnVisibility();
  }

  tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 40px; color: var(--text-muted);">Loading review papers...</td></tr>`;

  try {
    let data;
    try {
      const res = await fetch(`/api/reviews/${reviewId}`);
      if (!res.ok) throw new Error(`Review '${reviewId}' not found on backend`);
      data = await res.json();
    } catch (apiErr) {
      const sampleRes = await fetch(`data/sample_reviews/${reviewId}.json`);
      if (!sampleRes.ok) throw new Error(`Sample review '${reviewId}' not found`);
      data = await sampleRes.json();
    }

    activeReviewMeta = data.meta || data || {};

    allPapers = data.papers || [];
    filteredPapers = [...allPapers];

    let columns = activeReviewMeta.selected_columns;
    if (!columns || columns.length === 0) {
      const colSet = new Set(DIPSTICK_COLUMNS);
      allPapers.forEach(p => {
        Object.keys(p).forEach(k => {
          if (!['_mtime', 'raw_paper_json', 'sections', 'full_text', 'search_text', 'id'].includes(k)) {
            colSet.add(k);
          }
        });
      });
      columns = Array.from(colSet);
    }

    configureHeaders(columns);
    applyFilters();
  } catch (err) {
    console.error('Failed to load review data:', err);
    tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 40px; color: red;">Failed to load review '${escapeHtml(reviewId)}'.</td></tr>`;
  }
}

function formatColumnLabel(colKey) {
  if (DEFAULT_COLUMN_DEFINITIONS[colKey] && DEFAULT_COLUMN_DEFINITIONS[colKey].label) {
    return DEFAULT_COLUMN_DEFINITIONS[colKey].label;
  }
  return colKey
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
    .replace(/\bChat\b/i, 'CHAT / Activity Theory')
    .replace(/\bLlm\b/i, 'LLM')
    .replace(/\bRq\b/i, 'Research Questions');
}

// Configure Dynamic Table Headers with Column Multi-Select Filter Dropdowns & Sorting
function configureHeaders(selectedColumns) {
  const columnDefs = Object.assign({}, DEFAULT_COLUMN_DEFINITIONS, activeReviewMeta.column_definitions || {});

  let headerHtml = '';
  selectedColumns.forEach(colKey => {
    const rawDef = columnDefs[colKey];
    const label = rawDef && rawDef.label ? rawDef.label : formatColumnLabel(colKey);
    const def = { label, width: (rawDef && rawDef.width) || 240 };
    const isShort = def.isShort || ['year', 'conference', 'paper_type', 'id', 'paper_id', 'page', 'count', 'relevance'].includes(colKey.toLowerCase());
    const minW = def.minWidth || (isShort ? 70 : 160);
    const isFiltered = columnFilterSelections[colKey] && columnFilterSelections[colKey].size > 0;
    const isSorted = (currentSortColumn === colKey);
    const sortIcon = isSorted ? (currentSortDirection === 'asc' ? ' ▲' : ' ▼') : '';

    headerHtml += `
      <th style="width: ${def.width}px; min-width: ${minW}px;" data-col="${colKey}" data-min-width="${minW}" class="${isShort ? 'col-short' : ''}">
        <div class="th-content">
          <span class="th-label" style="cursor: pointer;" title="Click to sort by ${escapeHtml(def.label)}">
            <span class="th-label-text">${escapeHtml(def.label)}</span>
            <small class="th-sort-icon">${sortIcon}</small>
          </span>
          <div class="col-filter-wrapper">
            <button class="col-filter-btn ${isFiltered ? 'active' : ''}" data-col="${colKey}" title="Filter ${escapeHtml(def.label)}">
              <span>${isFiltered ? getIcon('filter') : getIcon('chevron-down', 'icon-sm')}</span>
            </button>
            <div class="col-filter-popover" id="filterPopover_${colKey}"></div>
          </div>
          <button class="btn-dots col-dots-btn" title="Column options" data-col="${colKey}" data-label="${escapeHtml(def.label)}">
            ${getIcon('more-vertical')}
          </button>
        </div>
        <div class="col-resizer"></div>
      </th>
    `;
  });

  tableHeaderRow.innerHTML = headerHtml;
  setupColumnHeaderFilters();
  setupColumnResizing();

  document.querySelectorAll('#tableHeaderRow th').forEach(th => {
    const colKey = th.dataset.col;
    const rawDef = columnDefs[colKey];
    const label = rawDef && rawDef.label ? rawDef.label : formatColumnLabel(colKey);
    const colData = { colKey, label };

    const thLabel = th.querySelector('.th-label');
    if (thLabel) {
      thLabel.addEventListener('click', () => {
        sortPapersByColumn(colKey);
      });
    }

    const thContent = th.querySelector('.th-content');
    if (thContent) {
      thContent.addEventListener('contextmenu', (e) => {
        openContextMenu(e, 'column', colData);
      });
    }

    const dotsBtn = th.querySelector('.col-dots-btn');
    if (dotsBtn) {
      dotsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openContextMenu(e, 'column', colData, dotsBtn);
      });
    }
  });
}

// Setup Column Header Multi-Select Filter Popovers
function setupColumnHeaderFilters() {
  document.querySelectorAll('.col-filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const colKey = btn.dataset.col;
      const popover = document.getElementById(`filterPopover_${colKey}`);
      if (!popover) return;

      // Close all other filter popovers first
      document.querySelectorAll('.col-filter-popover').forEach(p => {
        if (p !== popover) p.classList.remove('active');
      });

      const isActive = popover.classList.contains('active');
      if (!isActive) {
        if (tableExportPopover) tableExportPopover.classList.remove('active');
        populateColumnFilterPopover(colKey, popover);
        popover.classList.add('active');
        const rect = popover.getBoundingClientRect();
        if (rect.right > window.innerWidth - 12) {
          popover.style.left = 'auto';
          popover.style.right = '0';
        } else {
          popover.style.left = '0';
          popover.style.right = 'auto';
        }
      } else {
        popover.classList.remove('active');
      }
    });
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.col-filter-wrapper')) {
      document.querySelectorAll('.col-filter-popover').forEach(p => p.classList.remove('active'));
    }
  });
}

// Populate Column Filter Popover Content Dynamically
function populateColumnFilterPopover(colKey, popoverEl) {
  const corpus = (preloadedTitles.length > 0 ? preloadedTitles : allPapers);

  // Compute unique values & counts for this column
  const valCounts = {};
  corpus.forEach(paper => {
    let val = paper[colKey];
    if (colKey === 'paper_type') {
      val = getEffectivePaperType(paper);
    }
    if (Array.isArray(val)) {
      val.forEach(v => {
        const s = String(v).trim();
        if (s) valCounts[s] = (valCounts[s] || 0) + 1;
      });
    } else if (val !== undefined && val !== null) {
      const s = String(val).trim();
      if (s) valCounts[s] = (valCounts[s] || 0) + 1;
    }
  });

  let sortedVals = Object.keys(valCounts);
  if (colKey === 'year') {
    sortedVals.sort((a, b) => b.localeCompare(a));
  } else if (colKey === 'conference') {
    const order = { 'ISLS': 1, 'CSCL': 2, 'ICLS': 3 };
    sortedVals.sort((a, b) => (order[a] || 99) - (order[b] || 99));
  } else if (colKey === 'paper_type') {
    const order = { 'Full Paper': 1, 'Short Paper': 2, 'Practise Paper': 3, 'Poster': 4, 'Poster / Short Note': 5, 'Symposium': 6, 'Paper': 7 };
    sortedVals.sort((a, b) => (order[a] || 99) - (order[b] || 99));
  } else {
    sortedVals.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  }

  const selectedSet = columnFilterSelections[colKey] || new Set();

  let html = `
    <input type="text" class="col-filter-search" placeholder="Filter values..." data-col="${colKey}">
    <div class="col-filter-actions">
      <span class="col-filter-select-all" data-col="${colKey}">Select All</span>
      <span class="col-filter-clear" data-col="${colKey}">Clear</span>
    </div>
    <div class="col-filter-list">
  `;

  if (sortedVals.length === 0) {
    html += `<div style="font-size:12px; color: var(--text-muted); padding:4px;">No unique values</div>`;
  } else {
    sortedVals.forEach(val => {
      const checked = selectedSet.has(val) ? 'checked' : '';
      html += `
        <label class="col-filter-option" data-val="${escapeHtml(val.toLowerCase())}">
          <input type="checkbox" value="${escapeHtml(val)}" ${checked}>
          <span>${escapeHtml(val)}</span>
          <span class="val-count">(${valCounts[val]})</span>
        </label>
      `;
    });
  }

  html += `</div>`;
  popoverEl.innerHTML = html;

  // Event Listeners inside Popover
  const checkboxes = popoverEl.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      updateColumnFilterSelection(colKey, popoverEl);
    });
  });

  const searchInputEl = popoverEl.querySelector('.col-filter-search');
  if (searchInputEl) {
    searchInputEl.addEventListener('input', () => {
      const q = searchInputEl.value.toLowerCase().trim();
      popoverEl.querySelectorAll('.col-filter-option').forEach(opt => {
        const textVal = opt.dataset.val || '';
        opt.style.display = textVal.includes(q) ? 'flex' : 'none';
      });
    });
  }

  const selectAllBtn = popoverEl.querySelector('.col-filter-select-all');
  if (selectAllBtn) {
    selectAllBtn.addEventListener('click', () => {
      popoverEl.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        if (cb.closest('.col-filter-option').style.display !== 'none') {
          cb.checked = true;
        }
      });
      updateColumnFilterSelection(colKey, popoverEl);
    });
  }

  const clearBtn = popoverEl.querySelector('.col-filter-clear');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      popoverEl.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
      updateColumnFilterSelection(colKey, popoverEl);
    });
  }
}

// Update Column Filter Selection State & Re-trigger Filtering
function updateColumnFilterSelection(colKey, popoverEl) {
  const selected = new Set();
  popoverEl.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
    selected.add(cb.value);
  });

  if (selected.size > 0) {
    columnFilterSelections[colKey] = selected;
  } else {
    delete columnFilterSelections[colKey];
  }

  // Update button active state
  const btn = document.querySelector(`.col-filter-btn[data-col="${colKey}"]`);
  if (btn) {
    if (selected.size > 0) {
      btn.classList.add('active');
      btn.querySelector('span').innerHTML = getIcon('filter');
    } else {
      btn.classList.remove('active');
      btn.querySelector('span').innerHTML = getIcon('chevron-down', 'icon-sm');
    }
  }

  applyFilters();
}

// Render Data Rows into Table Body
function renderTable() {
  const selectedColumns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;

  if (paperCountBadge) {
    paperCountBadge.textContent = `${filteredPapers.length} Papers`;
  }

  if (!filteredPapers || filteredPapers.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="${selectedColumns.length}" style="text-align:center; padding: 40px; color: var(--text-muted);">No matching papers found.</td></tr>`;
    return;
  }

  let html = '';
  filteredPapers.forEach((paper, rowIdx) => {
    html += `<tr data-id="${paper.id}" class="${rowIdx % 2 === 0 ? 'row-even' : 'row-odd'}">`;

    selectedColumns.forEach(colKey => {
      html += `<td>`;
      if (colKey === 'title') {
        html += `
          <div class="cell-title-wrapper">
            <div class="cell-title">${escapeHtml(paper.title || 'Untitled')}</div>
            <button class="btn-dots title-dots-btn" title="Paper options" data-id="${paper.id}">
              ${getIcon('more-vertical')}
            </button>
          </div>
        `;
      } else if (colKey === 'authors') {
        html += `<div class="cell-authors">${escapeHtml(paper.authors || 'Unknown')}</div>`;
      } else if (colKey === 'year') {
        html += `<span class="badge badge-secondary">${escapeHtml(paper.year || '-')}</span>`;
      } else if (colKey === 'conference') {
        html += `<span class="badge badge-primary">${escapeHtml(formatConferenceAcronym(paper.conference))}</span>`;
      } else if (colKey === 'paper_type') {
        const displayType = getEffectivePaperType(paper);
        const isPractise = (paper.is_practise_paper || paper.is_practice_paper);
        const badgeClass = isPractise ? 'badge-warning' : 'badge-secondary';
        html += `<span class="badge ${badgeClass}">${escapeHtml(displayType)}</span>`;
      } else if (colKey === 'relevance') {
        html += `<span class="badge badge-success" style="background: rgba(16, 185, 129, 0.15); color: #10b981; font-weight: 600; padding: 3px 8px; border-radius: 4px;">${escapeHtml(paper.relevance || '1.00')}</span>`;
      } else if (colKey === 'abstract') {
        html += `<div class="cell-abstract">${renderMarkdown(paper.abstract)}</div>`;
      } else if (colKey === 'summary') {
        html += `<div class="cell-summary">${renderMarkdown(paper.summary)}</div>`;
      } else if (colKey === 'keywords') {
        const kws = paper.keywords || [];
        html += `<div>${kws.map(k => `<span class="kw-tag">${escapeHtml(k)}</span>`).join('')}</div>`;
      } else {
        const val = paper[colKey];
        if (typeof val === 'string') {
          html += `<div>${renderMarkdown(val)}</div>`;
        } else {
          html += `<div>${escapeHtml(typeof val === 'object' ? JSON.stringify(val) : String(val || '-'))}</div>`;
        }
      }
      html += `</td>`;
    });

    html += `</tr>`;
  });

  tableBody.innerHTML = html;

  document.querySelectorAll('#tableBody tr').forEach(tr => {
    const paperId = tr.dataset.id;
    const paper = filteredPapers.find(p => p.id === paperId);
    if (!paper) return;

    const titleWrapper = tr.querySelector('.cell-title-wrapper');
    if (titleWrapper) {
      titleWrapper.addEventListener('contextmenu', (e) => {
        openContextMenu(e, 'title', paper);
      });

      const dotsBtn = titleWrapper.querySelector('.title-dots-btn');
      if (dotsBtn) {
        dotsBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          openContextMenu(e, 'title', paper, dotsBtn);
        });
      }
    }
  });
}

let currentSortColumn = null;
let currentSortDirection = 'asc';

function sortPapersByColumn(colKey, direction) {
  if (direction === 'reverse') {
    filteredPapers.reverse();
    currentSortDirection = (currentSortDirection === 'asc' ? 'desc' : 'asc');
    renderTable();
    return;
  }

  if (!direction) {
    if (currentSortColumn === colKey) {
      direction = (currentSortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      direction = 'asc';
    }
  }

  currentSortColumn = colKey;
  currentSortDirection = direction;

  filteredPapers.sort((a, b) => {
    let valA = a[colKey];
    let valB = b[colKey];

    if (colKey === 'paper_type') {
      valA = getEffectivePaperType(a);
      valB = getEffectivePaperType(b);
    }

    if (Array.isArray(valA)) valA = valA.join(', ');
    if (Array.isArray(valB)) valB = valB.join(', ');

    if (valA === undefined || valA === null) valA = '';
    if (valB === undefined || valB === null) valB = '';

    const numA = parseFloat(valA);
    const numB = parseFloat(valB);
    const isNumeric = !isNaN(numA) && !isNaN(numB) && String(numA) === String(valA).trim() && String(numB) === String(valB).trim();

    if (isNumeric) {
      return direction === 'asc' ? numA - numB : numB - numA;
    } else {
      const strA = String(valA).toLowerCase();
      const strB = String(valB).toLowerCase();
      return direction === 'asc'
        ? strA.localeCompare(strB, undefined, { numeric: true, sensitivity: 'base' })
        : strB.localeCompare(strA, undefined, { numeric: true, sensitivity: 'base' });
    }
  });

  const selectedCols = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;
  configureHeaders(selectedCols);
  renderTable();
}

// --- Boolean & Multi-Keyword Query Engine ---
let searchDebounceTimer = null;
const SEARCH_DEBOUNCE_DELAY_MS = 280;
const termRegexCache = new Map();

function getTermRegex(term) {
  if (!term) return null;
  const isQuoted = (term.startsWith('"') && term.endsWith('"')) || (term.startsWith("'") && term.endsWith("'"));
  const clean = isQuoted ? term.slice(1, -1).trim() : term.trim();
  if (!clean) return null;
  
  let re = termRegexCache.get(clean.toLowerCase());
  if (!re) {
    const escaped = clean.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Strict boundary check: preceding char cannot be alphanumeric or underscore,
    // following char cannot be alphanumeric or underscore.
    // Strictly guarantees that AND and OR NEVER clash with substrings in words
    // (e.g. "understand", "demand", "collaborative", "exploration", "mentor", "world", etc.)
    // or acronyms (e.g. "NAND", "CORD", "STAND", "XOR", "TOR", etc.)
    const pattern = `(?:^|[^a-zA-Z0-9_])${escaped}(?=$|[^a-zA-Z0-9_])`;
    re = new RegExp(pattern, 'i');
    termRegexCache.set(clean.toLowerCase(), re);
  }
  return re;
}

function testTermMatch(text, term) {
  if (!text || !term) return false;
  const re = getTermRegex(term);
  if (!re) return true;
  return re.test(text);
}

function tokenizeQuery(query) {
  const rawTokens = [];
  let i = 0;
  const q = query.trim();
  while (i < q.length) {
    if (/\s/.test(q[i])) { i++; continue; }
    
    // Explicit quotes: always treated as literal TERM, never an operator
    if (q[i] === '"' || q[i] === "'") {
      const quoteChar = q[i];
      let j = i + 1;
      let val = '';
      while (j < q.length && q[j] !== quoteChar) {
        if (q[j] === '\\' && j + 1 < q.length) { val += q[j + 1]; j += 2; }
        else { val += q[j]; j++; }
      }
      rawTokens.push({ type: 'TERM', value: val.trim(), quoted: true });
      i = j + 1;
      continue;
    }
    
    // Comma acts as OR clause separator
    if (q[i] === ',') {
      rawTokens.push({ type: 'COMMA', value: ',' });
      i++;
      continue;
    }
    if (q[i] === '(') { rawTokens.push({ type: 'LPAREN', value: '(' }); i++; continue; }
    if (q[i] === ')') { rawTokens.push({ type: 'RPAREN', value: ')' }); i++; continue; }

    // Read full word bounded by whitespace, comma, or parens
    let j = i;
    while (j < q.length && !/[\s,()]/.test(q[j])) j++;
    const word = q.slice(i, j);
    const upper = word.toUpperCase();
    
    // An operator MUST be an exact standalone word: AND, OR, NOT, &&, ||, !
    // Any acronym like NAND, XOR, NOR, CORD, STAND, LAND, BRAND, etc. is NOT an operator!
    if (upper === 'AND' || upper === '&&') {
      rawTokens.push({ type: 'AND', value: word });
      i = j;
      continue;
    } else if (upper === 'OR' || upper === '||') {
      rawTokens.push({ type: 'OR', value: word });
      i = j;
      continue;
    } else if (upper === 'NOT' || upper === '!') {
      rawTokens.push({ type: 'NOT', value: word });
      i = j;
      continue;
    }

    // Accumulate words into multi-word phrases until an operator, delimiter, or quote is encountered
    let termStr = word;
    let k = j;
    while (k < q.length) {
      let m = k;
      while (m < q.length && /\s/.test(q[m])) m++;
      if (m >= q.length) { k = m; break; }
      if (q[m] === ',' || q[m] === '(' || q[m] === ')' || q[m] === '"' || q[m] === "'") break;
      
      let n = m;
      while (n < q.length && !/[\s,()]/.test(q[n])) n++;
      const nextWord = q.slice(m, n).toUpperCase();
      if (nextWord === 'AND' || nextWord === '&&' || nextWord === 'OR' || nextWord === '||' || nextWord === 'NOT' || nextWord === '!') {
        break;
      }
      termStr += q.slice(k, n);
      k = n;
    }
    i = k;
    if (termStr.trim()) {
      rawTokens.push({ type: 'TERM', value: termStr.trim() });
    }
  }

  // Second pass: distinguish operators from standalone acronyms/terms
  // If AND or OR has no left operand or no right operand, it cannot be an infix operator,
  // so treat it as a search TERM (e.g. searching the acronym "OR" or "AND")
  const tokens = [];
  for (let idx = 0; idx < rawTokens.length; idx++) {
    const t = rawTokens[idx];
    if (t.type === 'AND' || t.type === 'OR') {
      const prev = idx > 0 ? rawTokens[idx - 1] : null;
      const next = idx < rawTokens.length - 1 ? rawTokens[idx + 1] : null;
      const hasPrevOperand = prev && (prev.type === 'TERM' || prev.type === 'RPAREN');
      const hasNextOperand = next && (next.type === 'TERM' || next.type === 'LPAREN' || next.type === 'NOT');

      if (!hasPrevOperand && !hasNextOperand) {
        // Standalone acronym e.g. "OR" or "AND"
        tokens.push({ type: 'TERM', value: t.value });
      } else if (!hasPrevOperand && hasNextOperand) {
        // At start of expression or after comma e.g. "Operations Research, OR"
        tokens.push({ type: 'TERM', value: t.value });
      } else if (hasPrevOperand && !hasNextOperand) {
        // Trailing operator while user is typing e.g. "generative ai AND"
        tokens.push(t);
      } else {
        tokens.push(t);
      }
    } else if (t.type === 'COMMA') {
      tokens.push({ type: 'OR', value: ',' });
    } else {
      tokens.push(t);
    }
  }
  return tokens;
}

function parseQuery(query) {
  if (!query || !query.trim()) return null;
  const tokens = tokenizeQuery(query);
  if (tokens.length === 0) return null;

  let pos = 0;
  function peek() { return tokens[pos]; }
  function consume() { return tokens[pos++]; }

  function parseOr() {
    let left = parseAnd();
    while (pos < tokens.length && peek().type === 'OR') {
      consume(); // eat OR or ,
      const right = parseAnd();
      if (right) {
        left = { type: 'OR', left, right };
      }
    }
    return left;
  }

  function parseAnd() {
    let left = parseNot();
    while (pos < tokens.length && peek().type === 'AND') {
      consume(); // eat AND
      const right = parseNot();
      if (right) {
        left = { type: 'AND', left, right };
      }
    }
    return left;
  }

  function parseNot() {
    if (pos < tokens.length && peek().type === 'NOT') {
      consume();
      const expr = parseNot();
      return expr ? { type: 'NOT', expr } : null;
    }
    return parsePrimary();
  }

  function parsePrimary() {
    if (pos >= tokens.length) return null;
    const t = peek();
    if (t.type === 'LPAREN') {
      consume();
      const expr = parseOr();
      if (pos < tokens.length && peek().type === 'RPAREN') {
        consume();
      }
      return expr;
    }
    if (t.type === 'TERM') {
      consume();
      return { type: 'TERM', value: t.value };
    }
    // Skip unexpected operator gracefully while typing
    consume();
    return null;
  }

  try {
    return parseOr();
  } catch (err) {
    console.warn('Query parse fallback:', err);
    return { type: 'TERM', value: query.trim() };
  }
}

function evaluateAst(ast, checkTermFn) {
  if (!ast) return true;
  if (ast.type === 'TERM') return checkTermFn(ast.value);
  if (ast.type === 'AND') return evaluateAst(ast.left, checkTermFn) && evaluateAst(ast.right, checkTermFn);
  if (ast.type === 'OR') return evaluateAst(ast.left, checkTermFn) || evaluateAst(ast.right, checkTermFn);
  if (ast.type === 'NOT') return !evaluateAst(ast.expr, checkTermFn);
  return true;
}

function collectPositiveTerms(ast) {
  if (!ast) return [];
  if (ast.type === 'TERM') return [ast.value];
  if (ast.type === 'AND' || ast.type === 'OR') {
    return [...collectPositiveTerms(ast.left), ...collectPositiveTerms(ast.right)];
  }
  return [];
}

// Apply Filters (Combines Search Input + Column Multi-Select Header Filters)
function applyFilters() {
  const query = (searchInput ? searchInput.value : '').trim();
  const corpus = isDipstickMode ? (preloadedTitles.length > 0 ? preloadedTitles : allPapers) : allPapers;
  const ast = query ? parseQuery(query) : null;
  const positiveTerms = ast ? collectPositiveTerms(ast) : [];

  filteredPapers = corpus.filter(paper => {
    // 1. Top Search Bar Filter Check
    if (ast) {
      if (isDipstickMode) {
        const titleText = paper.title || '';
        const abstractText = paper.abstract || '';
        const authorsText = paper.authors || '';
        const confText = `${paper.conference || ''} ${paper.year || ''}`;
        const combinedText = `${titleText} ${abstractText} ${authorsText} ${confText}`;

        const isMatch = evaluateAst(ast, (term) => testTermMatch(combinedText, term));
        if (!isMatch) return false;

        // Calculate relevance score (0.50 - 1.00) based on title & term hits
        if (positiveTerms.length > 0) {
          let titleHits = 0;
          let matchCount = 0;
          positiveTerms.forEach(term => {
            if (testTermMatch(titleText, term)) titleHits++;
            if (testTermMatch(combinedText, term)) matchCount++;
          });
          const relScore = Math.min(1.00, 0.50 + (titleHits * 0.30) + ((matchCount / Math.max(1, positiveTerms.length)) * 0.20));
          paper.relevance = relScore.toFixed(2);
        }
      } else {
        // Saved Review Mode: evaluate AST across paper fields and column values
        const titleText = paper.title || '';
        const authorsText = paper.authors || '';
        const summaryText = paper.summary || '';
        const abstractText = paper.abstract || '';
        const kwText = (paper.keywords || []).join(' ');
        
        let colText = '';
        if (activeReviewMeta && activeReviewMeta.selected_columns) {
          colText = activeReviewMeta.selected_columns
            .map(col => String(paper[col] || ''))
            .join(' ');
        }
        const fullPaperText = `${titleText} ${authorsText} ${summaryText} ${abstractText} ${kwText} ${colText}`;

        const isMatch = evaluateAst(ast, (term) => testTermMatch(fullPaperText, term));
        if (!isMatch) return false;
      }
    }

    // 2. Column Header Multi-Select Filters Check
    for (const colKey in columnFilterSelections) {
      const selectedSet = columnFilterSelections[colKey];
      if (!selectedSet || selectedSet.size === 0) continue;

      let val = paper[colKey];
      if (colKey === 'paper_type') {
        val = getEffectivePaperType(paper);
      }
      if (Array.isArray(val)) {
        if (!val.some(v => selectedSet.has(String(v)))) return false;
      } else if (val !== undefined && val !== null) {
        if (!selectedSet.has(String(val))) return false;
      } else {
        return false;
      }
    }

    return true;
  });

  if (currentSortBy === 'year') {
    filteredPapers.sort((a, b) => {
      const yA = parseInt(a.year) || 0;
      const yB = parseInt(b.year) || 0;
      return yB - yA;
    });
  }

  renderTable();
}

// Multi-Select Scope Dropdown Popover Logic
function setupMultiSelectPopover() {
  if (!multiSelectToggleBtn || !multiSelectPopover) return;

  multiSelectToggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (tableExportPopover) tableExportPopover.classList.remove('active');
    multiSelectPopover.classList.toggle('active');
  });

  document.addEventListener('click', (e) => {
    if (!multiSelectPopover.contains(e.target) && e.target !== multiSelectToggleBtn) {
      multiSelectPopover.classList.remove('active');
    }
  });

  const checkboxes = multiSelectPopover.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(cb => {
    cb.addEventListener('change', updateMultiSelectButtonText);
  });
  updateMultiSelectButtonText();
}

function updateMultiSelectButtonText() {
  const checkboxes = multiSelectPopover.querySelectorAll('input[type="checkbox"]:checked');
  const selectedValues = Array.from(checkboxes).map(c => c.value);
  if (multiSelectToggleBtn) {
    if (selectedValues.length === 0) {
      multiSelectToggleBtn.innerHTML = `${getIcon('globe')} Select Scope ${getIcon('chevron-down', 'icon-sm')}`;
    } else if (selectedValues.length === 1) {
      multiSelectToggleBtn.innerHTML = `${getIcon('globe')} Scope (${selectedValues[0]}) ${getIcon('chevron-down', 'icon-sm')}`;
    } else {
      multiSelectToggleBtn.innerHTML = `${getIcon('globe')} Scope (${selectedValues.length} selected) ${getIcon('chevron-down', 'icon-sm')}`;
    }
  }
}

// Save Current Search Results as a Literature Review (Format: '<Review Protocol> - <keyword(s)>')
async function saveCurrentReview() {
  const keywords = searchInput ? searchInput.value.trim() : '';
  if (!keywords) {
    alert('Please enter keywords in the Search Bar before saving a review.');
    return;
  }

  const ast = parseQuery(keywords);
  const positiveTerms = ast ? collectPositiveTerms(ast) : [];
  const cleanKeywords = positiveTerms.length > 0
    ? positiveTerms.join(', ')
    : keywords.split(',').map(s => s.trim()).filter(Boolean).join(', ');

  const activeProtocol = isScopeExpanded ? 'Expanded Scope' : 'Dipstick Review';
  const defaultReviewName = `${activeProtocol} - ${cleanKeywords}`;

  const promptMsg = 'Enter a name for this Literature Review:\n(Format: <Review Protocol> - <keyword(s)>, e.g. Dipstick Review, Expanded Scope, or Agentic Review)';
  const userInput = prompt(promptMsg, defaultReviewName);
  if (!userInput) return;

  // Enforce/Normalize naming: '<Review Protocol> - <keyword(s)>'
  let reviewName = userInput.trim();
  const validProtocols = ['Dipstick Review', 'Expanded Scope', 'Agentic Review'];
  const hasValidPrefix = validProtocols.some(p => reviewName.startsWith(p + ' - '));

  if (!hasValidPrefix) {
    reviewName = `${activeProtocol} - ${reviewName}`;
  }

  let selectedProtocol = activeProtocol;
  for (const p of validProtocols) {
    if (reviewName.startsWith(p + ' - ')) {
      selectedProtocol = p;
      break;
    }
  }

  showStatus(`Saving review '${reviewName}'...`);
  const matchedPids = filteredPapers.map(p => p.id).join(',');

  try {
    const res = await fetch(`/api/reviews/save?name=${encodeURIComponent(reviewName)}&keywords=${encodeURIComponent(keywords)}&protocol=${encodeURIComponent(selectedProtocol)}&paper_ids=${encodeURIComponent(matchedPids)}`);
    const manifest = await res.json();
    hideStatus();
    await fetchReviewsList();
    loadReview(manifest.id);
  } catch (err) {
    console.error('Failed to save review:', err);
    showStatus('Error saving review.');
    setTimeout(hideStatus, 3000);
  }
}

// Expand Scope into Selected Sections (Abstract, Methodology, Findings, Full Text)
function expandScopeSection() {
  const keywords = searchInput ? searchInput.value.trim() : '';
  const checkboxes = multiSelectPopover ? multiSelectPopover.querySelectorAll('input[type="checkbox"]:checked') : [];
  const selectedSections = Array.from(checkboxes).map(c => c.value).join(',');

  if (!keywords) {
    alert('Please enter keywords in the Search Bar first.');
    return;
  }

  if (!selectedSections) {
    alert('Please select at least one section checkbox from the Scope dropdown.');
    return;
  }

  if (multiSelectPopover) multiSelectPopover.classList.remove('active');

  isScopeExpanded = true;

  const ast = parseQuery(keywords);
  const positiveTerms = ast ? collectPositiveTerms(ast) : [];
  const expandKwParam = positiveTerms.length > 0 ? positiveTerms.join(',') : keywords;

  showStatus(`Expanding scope to sections '${selectedSections}' (ISLS -> CSCL -> ICLS order)...`);

  const eventSource = new EventSource(`/api/dipstick/expand?keywords=${encodeURIComponent(expandKwParam)}&section=${encodeURIComponent(selectedSections)}`);

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.event === 'section_match') {
        showStatus(`Section '${data.section}' checked '${data.keyword}': ${data.match_count} matches.`);

        if (data.matched_papers) {
          data.matched_papers.forEach(mp => {
            if (!filteredPapers.some(fp => fp.id === mp.id)) {
              filteredPapers.push(mp);
            }
          });
          renderTable();
        }
      } else if (data.event === 'expand_complete') {
        showStatus(`${getIcon('check-circle')} Expansion Complete for '${selectedSections}'! Total matches: ${filteredPapers.length}`);
        setTimeout(hideStatus, 4000);
        eventSource.close();
      }
    } catch (err) {
      console.error('Expansion SSE Error:', err);
    }
  };

  eventSource.onerror = () => {
    hideStatus();
    eventSource.close();
  };
}

// Helper: Show/Hide Status Indicator
function showStatus(msg) {
  if (statusIndicator && statusText) {
    statusText.innerHTML = msg;
    statusIndicator.style.display = 'flex';
  }
}

function hideStatus() {
  if (statusIndicator) {
    statusIndicator.style.display = 'none';
  }
}

function showHostedModal(title, desc) {
  const modal = document.getElementById('hostedFeatureModal');
  if (!modal) return;
  if (title) {
    const tEl = document.getElementById('hostedModalTitle');
    if (tEl) tEl.textContent = title;
  }
  if (desc) {
    const dEl = document.getElementById('hostedModalDesc');
    if (dEl) dEl.textContent = desc;
  }
  modal.classList.add('open');
}

function hideHostedModal() {
  const modal = document.getElementById('hostedFeatureModal');
  if (modal) modal.classList.remove('open');
}

// Setup Global Event Listeners
function setupEventListeners() {
  const closeBtn = document.getElementById('closeHostedModal');
  const dismissBtn = document.getElementById('btnDismissHostedModal');
  if (closeBtn) closeBtn.addEventListener('click', hideHostedModal);
  if (dismissBtn) dismissBtn.addEventListener('click', hideHostedModal);
  const modal = document.getElementById('hostedFeatureModal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) hideHostedModal();
    });
  }

  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener('click', () => {
      sidebarNav.classList.toggle('collapsed');
    });
  }

  if (mobileSidebarToggleBtn) {
    mobileSidebarToggleBtn.addEventListener('click', () => {
      const isOpen = sidebarNav && sidebarNav.classList.toggle('open');
      if (sidebarBackdrop) {
        sidebarBackdrop.classList.toggle('active', !!isOpen);
      }
    });
  }

  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeMobileSidebar);
  }

  if (controlActionsToggle && controlActions) {
    controlActionsToggle.addEventListener('click', () => {
      const isOpen = controlActions.classList.toggle('is-open');
      controlActionsToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      controlActionsToggle.classList.toggle('active', isOpen);
    });
  }

  if (dipstickNavItem) {
    dipstickNavItem.addEventListener('click', () => {
      if (isHostedMode || preloadedTitles.length === 0) {
        showHostedModal(
          'Full Corpus Search (5,402 Papers)',
          'Full corpus title sweeps, boolean keywords, and real-time dipstick reviews require the local agentic runtime with SQLite FTS5 database.'
        );
        return;
      }
      openDipstickMode();
    });
  }

  function executeSearch() {
    isScopeExpanded = false;
    applyFilters();
    if (isDipstickMode) {
      const val = searchInput ? searchInput.value.trim() : '';
      const sortToggleGroup = document.getElementById('sortToggleGroup');
      if (val) {
        if (saveAsReviewBtn) saveAsReviewBtn.classList.remove('hidden');
        if (dipstickControls) dipstickControls.classList.remove('hidden');
        if (sortToggleGroup) sortToggleGroup.classList.remove('hidden');
        setExportControlsVisibility(true);
      } else {
        if (saveAsReviewBtn) saveAsReviewBtn.classList.add('hidden');
        if (dipstickControls) dipstickControls.classList.add('hidden');
        if (sortToggleGroup) sortToggleGroup.classList.add('hidden');
        setExportControlsVisibility(false);
      }
      const newUrl = val ? `${window.location.pathname}?keywords=${encodeURIComponent(val)}` : window.location.pathname;
      if (window.location.search !== (val ? `?keywords=${encodeURIComponent(val)}` : '')) {
        window.history.replaceState({ mode: 'dipstick' }, '', newUrl);
      }
    }
  }

  if (searchInput) {
    // 1. Debounced typing: wait for a pause before executing search to avoid input latency
    searchInput.addEventListener('input', () => {
      updateClearBtnVisibility();
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        executeSearch();
      }, SEARCH_DEBOUNCE_DELAY_MS);
    });

    // 2. Immediate execution on Enter, reset on Escape
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
        executeSearch();
      } else if (e.key === 'Escape') {
        if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
        searchInput.value = '';
        updateClearBtnVisibility();
        executeSearch();
      }
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', () => {
      if (searchInput) {
        searchInput.value = '';
        searchInput.focus();
      }
      updateClearBtnVisibility();
      if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
      executeSearch();
    });
  }

  if (saveAsReviewBtn) {
    saveAsReviewBtn.addEventListener('click', () => {
      if (isHostedMode || preloadedTitles.length === 0) {
        showHostedModal(
          'Save Custom Review to Local Workspace',
          'Saving custom literature reviews to persistent datasets requires the local Python server or agent workspace.'
        );
        return;
      }
      saveCurrentReview();
    });
  }
  if (expandScopeBtn) {
    expandScopeBtn.addEventListener('click', () => {
      if (isHostedMode || preloadedTitles.length === 0) {
        showHostedModal(
          'Iterative Scope Expansion',
          'Deep section scanning across Abstract, Methodology, and Findings requires the local full-text corpus and SQLite FTS5 database.'
        );
        return;
      }
      expandScopeSection();
    });
  }

  if (rowModeToggle) {
    // Auto-wrap is enabled by default
    rowModeToggle.checked = true;
    if (dataTable) {
      dataTable.classList.remove('mode-compact');
      dataTable.classList.add('mode-autowrap');
    }
    if (rowModeLabel) rowModeLabel.innerHTML = `${getIcon('wrap-text')} Auto Wrap`;

    rowModeToggle.addEventListener('change', () => {
      if (rowModeToggle.checked) {
        dataTable.classList.remove('mode-compact');
        dataTable.classList.add('mode-autowrap');
        if (rowModeLabel) rowModeLabel.innerHTML = `${getIcon('wrap-text')} Auto Wrap`;
      } else {
        dataTable.classList.remove('mode-autowrap');
        dataTable.classList.add('mode-compact');
        if (rowModeLabel) rowModeLabel.innerHTML = `${getIcon('compact')} Compact`;
      }
    });
  }

  if (tableBody) {
    tableBody.addEventListener('click', (e) => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim().length > 0) return;
      if (isResizingColumn) return;
      if (e.target.closest('.col-filter-wrapper')) return;
      if (e.target.closest('.btn-dots') || e.target.closest('.item-dropdown-menu')) return;

      const row = e.target.closest('tr');
      if (row && row.dataset.id) {
        openOverlay(row.dataset.id);
      }
    });
  }

  if (closeOverlayBtn) closeOverlayBtn.addEventListener('click', closeOverlay);
  if (overlayBackdrop) overlayBackdrop.addEventListener('click', closeOverlay);

  // Overlay Width Toggle
  const toggleOverlayWidthBtn = document.getElementById('toggleOverlayWidthBtn');
  if (toggleOverlayWidthBtn) {
    toggleOverlayWidthBtn.addEventListener('click', () => {
      detailsOverlay.classList.toggle('expanded');
    });
  }

  // View Full Text CTA Button on Summary Tab
  const ovTriggerReadBtn = document.getElementById('ovTriggerReadBtn');
  if (ovTriggerReadBtn) {
    ovTriggerReadBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const pid = (activePaper && activePaper.id) ? activePaper.id : (detailsOverlay.dataset.currentId || '');
      if (pid) {
        loadFullPaper(pid);
      }
    });
  }

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      const targetPane = document.getElementById(tabId);
      if (targetPane) targetPane.classList.add('active');

      // Auto-load full paper if user switches directly to the Full Text Reader tab
      if (tabId === 'tabSections') {
        const pid = (activePaper && activePaper.id) ? activePaper.id : (detailsOverlay.dataset.currentId || '');
        if (pid && !paperFullTextCache.has(pid)) {
          loadFullPaper(pid);
        }
      }
    });
  });

  if (resetColumnsBtn) {
    resetColumnsBtn.addEventListener('click', () => {
      columnFilterSelections = {};
      if (searchInput) searchInput.value = '';
      if (window.location.search) {
        window.history.replaceState({ mode: 'dipstick' }, '', window.location.pathname);
      }

      const columns = activeReviewMeta.selected_columns || DIPSTICK_COLUMNS;
      configureHeaders(columns);
      applyFilters();
    });
  }
}

// Paper Reader & Overlay State
const paperFullTextCache = new Map();
let currentReaderFontSize = 15;
let isReaderSerif = false;
let isReaderCardsMode = false;

// Open Side Panel Overlay (Instant 0ms - Local Data First, On-Demand Full Text)
function openOverlay(paperId) {
  try {
    detailsOverlay.dataset.currentId = paperId;
    const paperData = allPapers.find(p => p.id === paperId) ||
                      preloadedTitles.find(p => p.id === paperId) ||
                      { id: paperId, title: 'Paper Details', authors: 'Unknown', year: '-', conference: 'ISLS', abstract: 'Abstract text not available.' };

    activePaper = paperData;

    document.getElementById('ovTitle').textContent = activePaper.title || 'Untitled';
    document.getElementById('ovAuthors').textContent = activePaper.authors || 'Unknown';
    document.getElementById('ovYear').textContent = activePaper.year || '-';
    document.getElementById('ovConf').textContent = activePaper.conference || 'ISLS';

    document.getElementById('ovSummaryText').innerHTML = renderMarkdown(activePaper.summary || 'No summary available.');

    document.getElementById('ovDatabasesList').innerHTML = (activePaper.databases_searched || ['Not specified'])
      .map(d => `<span class="match-tag" style="font-size:12px; padding:4px 10px; background:#e0f2fe; color:#0369a1;">${escapeHtml(d)}</span>`).join('');

    document.getElementById('ovKeywordsList').innerHTML = (activePaper.keywords || [])
      .map(k => `<span class="kw-tag" style="font-size:12px; padding:4px 10px;">${escapeHtml(k)}</span>`).join('');

    document.getElementById('ovAbstractText').textContent = activePaper.abstract || 'No abstract text available.';
    document.getElementById('ovRawJson').textContent = JSON.stringify(activePaper.raw_paper_json || activePaper, null, 2);

    // Update Full Text CTA description in Summary tab
    const ctaDesc = document.getElementById('ovFullTextCtaDesc');
    if (ctaDesc) {
      ctaDesc.textContent = `Read complete paper with empirical findings, methodology, and references.`;
    }

    // Check if full paper is already cached in memory
    if (paperFullTextCache.has(paperId)) {
      renderFullPaperReader(paperFullTextCache.get(paperId));
    } else {
      // If user is already on the Full Text Reader tab, fetch and render immediately
      const fullTextTabBtn = document.getElementById('tabFullTextBtn');
      if (fullTextTabBtn && fullTextTabBtn.classList.contains('active')) {
        loadFullPaper(paperId);
      } else {
        renderReaderLaunchCard(activePaper);
      }
    }

    document.querySelectorAll('.data-table tbody tr').forEach(r => r.classList.remove('selected'));
    const selectedRow = document.querySelector(`tr[data-id="${paperId}"]`);
    if (selectedRow) selectedRow.classList.add('selected');

    detailsOverlay.classList.add('active');
    overlayBackdrop.classList.add('active');
  } catch (err) {
    console.error('Error opening paper details:', err);
  }
}

// On-Demand Full Paper Fetch with Loading Spinner
async function loadFullPaper(paperId) {
  const container = document.getElementById('ovSectionsContainer');
  if (!container) return;

  // Switch to Full Text Reader tab
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  const fullTextTabBtn = document.getElementById('tabFullTextBtn');
  if (fullTextTabBtn) fullTextTabBtn.classList.add('active');
  const sectionsTab = document.getElementById('tabSections');
  if (sectionsTab) sectionsTab.classList.add('active');

  // Check memory cache first
  if (paperFullTextCache.has(paperId)) {
    renderFullPaperReader(paperFullTextCache.get(paperId));
    return;
  }

  // Display Animated Loading Spinner
  container.innerHTML = `
    <div class="reader-loading">
      <span class="spin">${getIcon('zap', 'icon-lg')}</span>
      <p>Retrieving complete formatted paper from repository...</p>
      <span style="font-size:12px; color: var(--text-muted);">Pulling structured sections, page bounds, and references</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/paper/${encodeURIComponent(paperId)}`);
    if (res.ok) {
      const data = await res.json();
      paperFullTextCache.set(paperId, data);
      renderFullPaperReader(data);
    } else {
      container.innerHTML = `
        <div class="reader-launch-card">
          <div class="reader-launch-icon" style="background:#fee2e2; color:#b91c1c;">${getIcon('x', 'icon-lg')}</div>
          <h3 class="reader-launch-title">Full Paper Text Unavailable</h3>
          <p class="reader-launch-subtitle">Full digitized text is not present in local storage for this paper. The abstract and bibliographic details remain available.</p>
          <button class="btn btn-outline" onclick="window.loadFullPaper('${escapeHtml(paperId)}')">${getIcon('refresh-cw')} Retry Retrieval</button>
        </div>
      `;
    }
  } catch (err) {
    console.error('Error loading full paper:', err);
    container.innerHTML = `
      <div class="reader-launch-card">
        <div class="reader-launch-icon" style="background:#fee2e2; color:#b91c1c;">${getIcon('x', 'icon-lg')}</div>
        <h3 class="reader-launch-title">Failed to Load Paper</h3>
        <p class="reader-launch-subtitle">${escapeHtml(err.message || 'Connection error while fetching paper text.')}</p>
        <button class="btn btn-outline" onclick="window.loadFullPaper('${escapeHtml(paperId)}')">${getIcon('refresh-cw')} Retry Retrieval</button>
      </div>
    `;
  }
}
window.loadFullPaper = loadFullPaper;

// Render Unloaded Launch State (Zero Bloat)
function renderReaderLaunchCard(paper) {
  const container = document.getElementById('ovSectionsContainer');
  if (!container) return;

  const pid = paper.id || '';
  const title = paper.title || 'Untitled';
  const authors = paper.authors || 'Unknown';
  const yr = paper.year || '';
  const conf = paper.conference || 'ISLS';

  container.innerHTML = `
    <div class="reader-launch-card">
      <div class="reader-launch-icon">${getIcon('book', 'icon-lg')}</div>
      <h3 class="reader-launch-title">${escapeHtml(title)}</h3>
      <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 6px;">${escapeHtml(authors)}</p>
      <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 20px;">${escapeHtml(conf)} ${escapeHtml(yr)}</p>
      <p class="reader-launch-subtitle">Full paper content (all empirical sections, methodology, findings, and references) will be loaded on demand.</p>
      <button class="btn btn-primary btn-lg" id="readerLaunchBtn" style="padding: 10px 24px; font-size: 14px;" onclick="window.loadFullPaper('${escapeHtml(pid)}')">
        ${getIcon('book')} View Full Text
      </button>
    </div>
  `;

  const launchBtn = document.getElementById('readerLaunchBtn');
  if (launchBtn) {
    launchBtn.addEventListener('click', () => loadFullPaper(pid));
  }
}

// In-Text Academic Citation Highlighter e.g. (Adkins, 2020), (Toprani et al., 2021; Borge & Mercier, 2018), Stahl (2006)
function formatCitationsAndEscape(rawText) {
  if (!rawText) return '';
  const parenCitationRegex = /\(((?:(?:see|e\.g\.|cf\.|i\.e\.)\s+)?(?:[A-Z][a-zA-Z\u00C0-\u024F\s\.,&\'\-–—]+?(?:\s+et\s+al\.)?,?\s*(?:19|20)\d{2}[a-z]?(?:,\s*p{1,2}\.?\s*\d+(?:-\d+)?)?)(?:;\s*(?:[A-Z][a-zA-Z\u00C0-\u024F\s\.,&\'\-–—]+?(?:\s+et\s+al\.)?,?\s*(?:19|20)\d{2}[a-z]?(?:,\s*p{1,2}\.?\s*\d+(?:-\d+)?)?))*\s*)\)/g;
  const narrativeCitationRegex = /\b([A-Z][a-zA-Z\u00C0-\u024F]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z\u00C0-\u024F]+|\s+et\s+al\.)?)\s+\(((?:19|20)\d{2}[a-z]?)\)/g;

  const citations = [];

  let tokenized = rawText.replace(parenCitationRegex, (match, citationBody) => {
    if (/^\d+$/.test(citationBody.trim())) return match;
    const token = `___CIT_${citations.length}___`;
    const cleanBody = citationBody.trim();
    citations.push(`<span class="reader-citation" title="Citation: ${escapeHtml(cleanBody)}">(${escapeHtml(cleanBody)})</span>`);
    return token;
  });

  tokenized = tokenized.replace(narrativeCitationRegex, (match, authors, yr) => {
    const token = `___CIT_${citations.length}___`;
    const fullText = `${authors.trim()} (${yr.trim()})`;
    citations.push(`<span class="reader-citation" title="Citation: ${escapeHtml(fullText)}">${escapeHtml(authors.trim())} (${escapeHtml(yr.trim())})</span>`);
    return token;
  });

  let escaped = escapeHtml(tokenized);
  for (let i = 0; i < citations.length; i++) {
    escaped = escaped.replace(`___CIT_${i}___`, citations[i]);
  }
  return escaped;
}

// Scholarly Article Formatter (Paragraph Reflow, List Grouping, Citation Highlighting)
function formatArticleContent(str, sectionHeading = '') {
  if (!str) return '';

  // 1. Repair font-extraction ligature artifacts, hyphen spaces, and punctuation spacing
  let prepped = str
    .replace(/\s+([,;:\.\)])/g, '$1')
    .replace(/([\(\[])\s+/g, '$1')
    .replace(/(\b\w+)\s+-\s*(\w+\b)/g, '$1-$2')
    .replace(/(\b\w+)-\s+(\w+\b)/g, '$1-$2')
    .replace(/(\b[A-Za-z]+)\s+([a-z]{2,}\b)/g, (match, w1, w2) => {
      const combined = (w1 + w2).toLowerCase();
      const knownGlitchWords = {
        'attending': 'attending', 'approaches': 'approaches', 'approach': 'approach',
        'technology': 'technology', 'technologies': 'technologies', 'technologically': 'technologically',
        'record': 'record', 'records': 'records', 'individual': 'individual', 'individually': 'individually',
        'collaborative': 'collaborative', 'collaborating': 'collaborating', 'collaboration': 'collaboration',
        'learning': 'learning', 'interactions': 'interactions', 'environment': 'environment',
        'environments': 'environments', 'analysis': 'analysis', 'qualitative': 'qualitative',
        'quantitative': 'quantitative', 'participants': 'participants', 'understanding': 'understanding',
        'investments': 'investments', 'foundations': 'foundations', 'exploration': 'exploration',
        'explorations': 'explorations', 'ecological': 'ecological', 'transformative': 'transformative',
        'pedagogical': 'pedagogical', 'pedagogically': 'pedagogically', 'student': 'student',
        'students': 'students', 'digital': 'digital', 'digitally': 'digitally', 'lived': 'lived',
        'define': 'define', 'defined': 'defined', 'multidimensionality': 'multidimensionality',
        'interactional': 'interactional', 'deductive': 'deductive', 'throughout': 'throughout',
        'educational': 'educational', 'education': 'education'
      };
      if (knownGlitchWords[combined]) {
        return (w1[0] === w1[0].toUpperCase() ? combined.charAt(0).toUpperCase() + combined.slice(1) : combined);
      }
      return match;
    });

  const rawLines = prepped.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  const blocks = [];
  let currentLines = [];

  const flushParagraph = () => {
    if (currentLines.length > 0) {
      blocks.push({ type: 'paragraph', text: currentLines.join(' ') });
      currentLines = [];
    }
  };

  const isRefSection = /references|bibliography|works cited|literature cited|endnotes/i.test(sectionHeading || '');

  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i];

    // Remove exact running footers (never drop substantive body text)
    if (/^(?:CSCL|ICLS|ISLS)\s+\d{4}\s+Proceedings\s+\d+(\s+©\s+ISLS)?$/i.test(line)) {
      continue;
    }

    // Markdown subheaders
    if (line.startsWith('### ') || line.startsWith('#### ') || line.startsWith('## ')) {
      flushParagraph();
      blocks.push({ type: 'heading', text: line.replace(/^#+\s*/, '') });
      continue;
    }

    // Blockquotes
    if (line.startsWith('&gt;') || line.startsWith('>')) {
      flushParagraph();
      blocks.push({ type: 'quote', text: line.replace(/^(&gt;|>)\s*/, '') });
      continue;
    }

    // List items (bullet or numbered)
    const bulletMatch = line.match(/^([-*•–—]|\(?\d+[\.\)]|\(?[a-z]\))\s+(.*)$/);
    if (bulletMatch) {
      flushParagraph();
      const isOrdered = /^\(?\d+[\.\)]/.test(line);
      blocks.push({
        type: isOrdered ? 'ordered-item' : 'list-item',
        marker: bulletMatch[1],
        text: bulletMatch[2]
      });
      continue;
    }

    // Figure captions
    if (/^Figure\s+\d+[\.:]/i.test(line)) {
      flushParagraph();
      blocks.push({ type: 'caption', text: line });
      continue;
    }

    // Reference bibliography items (strictly inside References section)
    if (isRefSection && /^[A-Z][^\(\)\n\r]{2,80}\s*\([12][0-9]{3}[a-z]?\)[\.\s]/.test(line) && line.length > 30) {
      flushParagraph();
      blocks.push({ type: 'reference', text: line });
      continue;
    }

    // Accumulate lines with smart reflow
    if (currentLines.length > 0) {
      const prevLine = currentLines[currentLines.length - 1];

      // Join hyphenated words split across lines
      if (prevLine.endsWith('-') && !prevLine.endsWith(' -')) {
        currentLines[currentLines.length - 1] = prevLine.slice(0, -1) + line;
        continue;
      }

      // Never break inside citations, unclosed parentheses, or trailing connectors
      const prevClean = prevLine.trim();
      const currClean = line.trim();
      const hasUnclosedParen = (prevClean.split('(').length - 1) > (prevClean.split(')').length - 1);
      const hasUnclosedBracket = (prevClean.split('[').length - 1) > (prevClean.split(']').length - 1);
      const endsWithConnector = /[&;,—–\/\-]$/.test(prevClean) || /^(?:et al\.|e\.g\.|i\.e\.)$/i.test(prevClean);
      const lastWord = (prevClean.split(/\s+/).pop() || '').toLowerCase().replace(/[^a-z]/g, '');
      const endsWithPreposition = ['and', 'or', 'the', 'a', 'an', 'of', 'to', 'in', 'for', 'with', 'by', 'from', 'on', 'at', 'as', 'that', 'which', 'between', 'into', 'through'].includes(lastWord);
      const startsWithContinuation = /^[)\]\},;:]/.test(currClean) || /^[a-z]/.test(currClean) || /^(?:[12][0-9]{3}[a-z]?\s*[\)\],]|(?:[A-Z][a-zA-Z\s\.,&]+,\s*)?[12][0-9]{3}[a-z]?\s*\))/.test(currClean);

      if (hasUnclosedParen || hasUnclosedBracket || endsWithConnector || endsWithPreposition || startsWithContinuation) {
        currentLines.push(line);
        continue;
      }

      // Check if previous line ended a complete sentence AND this line starts a new thematic paragraph
      const endsWithTerminal = /[.!?:]$/.test(prevLine);
      const isShortPrev = prevLine.length < 55;
      const isNewSentenceStarter = /^[A-Z]/.test(line) && (
        isShortPrev ||
        line.startsWith('Abstract:') ||
        line.startsWith('Keywords:') ||
        line.startsWith('The study ') ||
        line.startsWith('In this paper') ||
        line.startsWith('Our findings') ||
        line.startsWith('Using Interaction') ||
        line.startsWith('In L5 ') ||
        line.startsWith('When students ') ||
        line.startsWith('As students ') ||
        line.startsWith('As we are ') ||
        line.startsWith('Policymakers ') ||
        line.startsWith('To address ') ||
        line.startsWith('In conclusion')
      );

      if (endsWithTerminal && isNewSentenceStarter) {
        flushParagraph();
        currentLines = [line];
        continue;
      }

      currentLines.push(line);
    } else {
      currentLines.push(line);
    }
  }
  flushParagraph();

  // Render HTML blocks
  let html = '';
  let inList = false;
  let inOrderedList = false;

  for (let i = 0; i < blocks.length; i++) {
    const b = blocks[i];

    if (b.type === 'list-item') {
      if (!inList) {
        if (inOrderedList) { html += '</ol>'; inOrderedList = false; }
        html += '<ul class="reader-list">';
        inList = true;
      }
      let itemText = formatCitationsAndEscape(b.text);
      html += `<li>${itemText}</li>`;
      continue;
    } else if (inList) {
      html += '</ul>';
      inList = false;
    }

    if (b.type === 'ordered-item') {
      if (!inOrderedList) {
        if (inList) { html += '</ul>'; inList = false; }
        html += '<ol class="reader-olist">';
        inOrderedList = true;
      }
      let itemText = formatCitationsAndEscape(b.text);
      html += `<li>${itemText}</li>`;
      continue;
    } else if (inOrderedList) {
      html += '</ol>';
      inOrderedList = false;
    }

    if (b.type === 'heading') {
      html += `<h4 class="reader-h3">${escapeHtml(b.text)}</h4>`;
    } else if (b.type === 'quote') {
      let qText = formatCitationsAndEscape(b.text);
      html += `<blockquote class="reader-quote">${qText}</blockquote>`;
    } else if (b.type === 'caption') {
      html += `<div style="font-size: 12.5px; color: var(--text-muted); font-style: italic; margin: 8px 0 16px 0; border-left: 2px solid #cbd5e1; padding-left: 10px;">${escapeHtml(b.text)}</div>`;
    } else if (b.type === 'reference') {
      let refText = escapeHtml(b.text);
      html += `<div class="reader-reference-item">${refText}</div>`;
    } else if (b.type === 'paragraph') {
      let pText = formatCitationsAndEscape(b.text);
      pText = pText
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_([^_]+)_/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
      html += `<p class="reader-p">${pText}</p>`;
    }
  }

  if (inList) html += '</ul>';
  if (inOrderedList) html += '</ol>';

  return html;
}

// Render Formatted Complete Paper Reader
function renderFullPaperReader(paperData) {
  const container = document.getElementById('ovSectionsContainer');
  if (!container) return;

  const sections = paperData.sections || [];
  const totalWords = paperData.total_words || sections.reduce((acc, sec) => acc + (sec.text ? sec.text.trim().split(/\s+/).filter(Boolean).length : 0), 0);
  const estMins = paperData.estimated_reading_minutes || Math.max(1, Math.round(totalWords / 220));
  const pid = paperData.id || '';
  const pdfUrl = paperData.source_url && paperData.source_url.startsWith('http') ? paperData.source_url : (paperData.pdf_url || '');

  let html = `
    <!-- Sticky Reader Toolbar & Navigation -->
    <div class="reader-sticky-header">
      <div class="reader-toolbar">
        <div class="reader-stats-group">
          <span>${getIcon('book')} <strong>${sections.length}</strong> Sections</span>
          <span>&bull;</span>
          <span><strong>${totalWords.toLocaleString()}</strong> Words</span>
          <span>&bull;</span>
          <span>~<strong>${estMins}</strong> min read</span>
        </div>
        <div class="reader-tools-group">
          <button class="btn-reader-tool" id="readerFontDecBtn" title="Decrease font size">A-</button>
          <button class="btn-reader-tool" id="readerFontIncBtn" title="Increase font size">A+</button>
          <button class="btn-reader-tool ${isReaderSerif ? 'active' : ''}" id="readerSerifToggleBtn" title="Toggle Serif / Sans Font">Serif</button>
          <button class="btn-reader-tool ${isReaderCardsMode ? 'active' : ''}" id="readerModeToggleBtn" title="Toggle Continuous / Cards">${isReaderCardsMode ? 'Cards' : 'Flow'}</button>
          <button class="btn-reader-tool" id="readerCopyBtn" title="Copy article text">${getIcon('copy')} Copy</button>
          ${pdfUrl ? `<a href="${pdfUrl}" target="_blank" rel="noopener noreferrer" class="btn-reader-tool" title="Open Original PDF">${getIcon('file-text')} PDF</a>` : ''}
        </div>
      </div>
      <!-- Sticky Section Navigation Pills -->
      <div class="reader-pills-bar">
        ${sections.map((sec, idx) => {
          const hName = sec.original_heading || sec.heading || `Section ${idx+1}`;
          return `<button class="reader-pill" onclick="jumpToSection('${idx}')">${escapeHtml(hName)}</button>`;
        }).join('')}
      </div>
    </div>

    <!-- Article Content -->
    <div class="reader-article reader-font-${currentReaderFontSize} ${isReaderSerif ? 'reader-serif' : ''}" id="readerArticleFlow">
  `;

  sections.forEach((sec, idx) => {
    const heading = sec.original_heading || sec.heading || `Section ${idx+1}`;
    const pageText = (sec.pdf_start_page || sec.pdf_end_page)
      ? `Pages ${sec.pdf_start_page || 'N/A'} - ${sec.pdf_end_page || 'N/A'}`
      : (sec.pages ? `Pages ${sec.pages.pdf_start || 'N/A'} - ${sec.pages.pdf_end || 'N/A'}` : '');

    const isRef = heading.toLowerCase().includes('reference') || heading.toLowerCase().includes('bibliography');

    if (isReaderCardsMode) {
      html += `
        <div class="section-block" id="reader-sec-${idx}">
          <div class="section-block-header">
            <span class="section-title">${getIcon('pin')} ${escapeHtml(heading)}</span>
            ${pageText ? `<span class="section-page badge badge-secondary">${escapeHtml(pageText)}</span>` : ''}
          </div>
          <div class="section-content ${isRef ? 'reader-references' : ''}">
            ${formatArticleContent(sec.text, heading)}
          </div>
        </div>
      `;
    } else {
      html += `
        <section id="reader-sec-${idx}" style="margin-bottom: 28px; scroll-margin-top: 110px;">
          <h3 style="font-size: 16px; font-weight: 700; color: var(--accent-primary); margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
            <span>${escapeHtml(heading)}</span>
            ${pageText ? `<span style="font-size: 11.5px; font-weight: 500; color: var(--text-muted);">${escapeHtml(pageText)}</span>` : ''}
          </h3>
          <div class="reader-content-body ${isRef ? 'reader-references' : ''}">
            ${formatArticleContent(sec.text, heading)}
          </div>
        </section>
      `;
    }
  });

  html += `</div>`;
  container.innerHTML = html;

  // Bind Reader Toolbar Controls
  const decBtn = document.getElementById('readerFontDecBtn');
  const incBtn = document.getElementById('readerFontIncBtn');
  const serifBtn = document.getElementById('readerSerifToggleBtn');
  const modeBtn = document.getElementById('readerModeToggleBtn');
  const copyBtn = document.getElementById('readerCopyBtn');
  const articleEl = document.getElementById('readerArticleFlow');

  if (decBtn) {
    decBtn.addEventListener('click', () => {
      const sizes = [13, 14, 15, 16, 18];
      const curIdx = sizes.indexOf(currentReaderFontSize);
      if (curIdx > 0) {
        currentReaderFontSize = sizes[curIdx - 1];
        if (articleEl) {
          articleEl.className = `reader-article reader-font-${currentReaderFontSize} ${isReaderSerif ? 'reader-serif' : ''}`;
        }
      }
    });
  }

  if (incBtn) {
    incBtn.addEventListener('click', () => {
      const sizes = [13, 14, 15, 16, 18];
      const curIdx = sizes.indexOf(currentReaderFontSize);
      if (curIdx < sizes.length - 1) {
        currentReaderFontSize = sizes[curIdx + 1];
        if (articleEl) {
          articleEl.className = `reader-article reader-font-${currentReaderFontSize} ${isReaderSerif ? 'reader-serif' : ''}`;
        }
      }
    });
  }

  if (serifBtn) {
    serifBtn.addEventListener('click', () => {
      isReaderSerif = !isReaderSerif;
      serifBtn.classList.toggle('active', isReaderSerif);
      if (articleEl) {
        articleEl.classList.toggle('reader-serif', isReaderSerif);
      }
    });
  }

  if (modeBtn) {
    modeBtn.addEventListener('click', () => {
      isReaderCardsMode = !isReaderCardsMode;
      renderFullPaperReader(paperData);
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const allText = sections.map(s => `## ${s.original_heading || s.heading}\n\n${s.text}`).join('\n\n');
      navigator.clipboard.writeText(allText).then(() => {
        const origHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = `${getIcon('check-circle')} Copied!`;
        setTimeout(() => { copyBtn.innerHTML = origHtml; }, 2000);
      });
    });
  }
}

// Section Jump Navigation
window.jumpToSection = function(idx) {
  const el = document.getElementById(`reader-sec-${idx}`);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

function closeOverlay() {
  detailsOverlay.classList.remove('active');
  overlayBackdrop.classList.remove('active');
  document.querySelectorAll('.data-table tbody tr').forEach(r => r.classList.remove('selected'));
}

function setupColumnResizing() {
  document.querySelectorAll('.col-resizer').forEach(resizer => {
    resizer.addEventListener('mousedown', (e) => {
      e.preventDefault();
      isResizingColumn = true;

      const th = resizer.closest('th');
      const startX = e.pageX;
      const startWidth = th.offsetWidth;

      resizer.classList.add('resizing');
      document.body.style.cursor = 'col-resize';

      const onMouseMove = (moveEvent) => {
        const delta = moveEvent.pageX - startX;
        const minW = parseInt(th.dataset.minWidth, 10) || 60;
        const newWidth = Math.max(minW, startWidth + delta);
        th.style.width = `${newWidth}px`;
      };

      const onMouseUp = () => {
        resizer.classList.remove('resizing');
        document.body.style.cursor = '';
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        setTimeout(() => { isResizingColumn = false; }, 100);
      };

      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    });
  });
}

function setupOverlayResizing() {
  let startX = 0;
  let startWidth = 0;

  if (!overlayResizer) return;
  overlayResizer.addEventListener('mousedown', (e) => {
    e.preventDefault();
    isResizingOverlay = true;

    startX = e.clientX;
    startWidth = detailsOverlay.offsetWidth;

    overlayResizer.classList.add('resizing');
    document.body.style.cursor = 'ew-resize';

    const onMouseMove = (moveEvent) => {
      const delta = startX - moveEvent.clientX;
      const newWidth = Math.min(window.innerWidth, Math.max(350, startWidth + delta));
      detailsOverlay.style.width = `${newWidth}px`;
    };

    const onMouseUp = () => {
      overlayResizer.classList.remove('resizing');
      document.body.style.cursor = '';
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      setTimeout(() => { isResizingOverlay = false; }, 100);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderMarkdown(str) {
  if (!str) return '-';
  let html = escapeHtml(str);
  // Bold: **text** or __text__
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
  // Italic: *text* or _text_
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.*?)_/g, '<em>$1</em>');
  // Code: `code`
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Convert newlines to breaks
  html = html.replace(/\r\n|\r|\n/g, '<br>');
  return html;
}
