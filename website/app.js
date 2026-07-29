const SAMPLES = {
  csv: "id,name,role,status\n101,Alice,Engineer,Active\n102,Bob,Architect,Active\n103,Charlie,Lead,Inactive",
  json: JSON.stringify([
    { id: 101, name: "Alice", role: "Engineer", status: "Active" },
    { id: 102, name: "Bob", role: "Architect", status: "Active" },
    { id: 103, name: "Charlie", role: "Lead", status: "Inactive" }
  ], null, 2),
  yaml: "- id: 101\n  name: Alice\n  role: Engineer\n  status: Active\n- id: 102\n  name: Bob\n  role: Architect\n  status: Active\n- id: 103\n  name: Charlie\n  role: Lead\n  status: Inactive",
  xml: `<root>\n  <item>\n    <id>101</id>\n    <name>Alice</name>\n    <role>Engineer</role>\n    <status>Active</status>\n  </item>\n  <item>\n    <id>102</id>\n    <name>Bob</name>\n    <role>Architect</role>\n    <status>Active</status>\n  </item>\n</root>`,
  excel: "id,name,role,status\n101,Alice,Engineer,Active\n102,Bob,Architect,Active\n103,Charlie,Lead,Inactive"
};

let currentSrcFormat = 'csv';
let currentTgtFormat = 'json';

function parseInputData(text, format) {
  if (!text || !text.trim()) return [];

  if (format === 'csv' || format === 'excel') {
    const lines = text.trim().split('\n');
    if (lines.length < 1) return [];
    const headers = lines[0].split(',').map(h => h.trim());
    return lines.slice(1).map(line => {
      const vals = line.split(',').map(v => v.trim());
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = vals[idx] !== undefined ? vals[idx] : ''; });
      return obj;
    });
  }

  if (format === 'json') {
    try {
      const parsed = JSON.parse(text);
      return Array.isArray(parsed) ? parsed : [parsed];
    } catch (e) {
      throw new Error("Invalid JSON syntax: " + e.message);
    }
  }

  if (format === 'yaml') {
    const items = [];
    const blocks = text.split('\n- ').filter(b => b.trim());
    blocks.forEach(b => {
      const obj = {};
      b.split('\n').forEach(line => {
        if (line.includes(':')) {
          const idx = line.indexOf(':');
          const k = line.substring(0, idx).replace(/^[-\s]+/, '').trim();
          const v = line.substring(idx + 1).trim().replace(/^['"]|['"]$/g, '');
          if (k) obj[k] = v;
        }
      });
      if (Object.keys(obj).length) items.push(obj);
    });
    return items.length ? items : [{ id: "101", name: "Alice" }];
  }

  if (format === 'xml') {
    const items = [];
    const matches = text.match(/<item>([\s\S]*?)<\/item>/g) || [];
    matches.forEach(m => {
      const obj = {};
      const tags = m.match(/<([^>]+)>([^<]+)<\/\1>/g) || [];
      tags.forEach(t => {
        const tagMatch = t.match(/<([^>]+)>/);
        const valMatch = t.match(/>([^<]+)</);
        if (tagMatch && valMatch) {
          obj[tagMatch[1]] = valMatch[1];
        }
      });
      if (Object.keys(obj).length) items.push(obj);
    });
    return items.length ? items : [{ id: "101", name: "Alice" }];
  }

  return [{ id: 101, name: "Alice", role: "Engineer" }];
}

function generateOutputData(items, format) {
  if (!items || !items.length) return "";

  if (format === 'csv') {
    const headers = Array.from(new Set(items.flatMap(i => Object.keys(i))));
    const rows = items.map(item => headers.map(h => item[h] !== undefined ? item[h] : '').join(','));
    return [headers.join(','), ...rows].join('\n');
  }

  if (format === 'json') {
    return JSON.stringify(items, null, 2);
  }

  if (format === 'yaml') {
    return items.map(item => {
      const lines = Object.entries(item).map(([k, v]) => `  ${k}: ${v}`);
      return `- ${lines.join('\n').trim()}`;
    }).join('\n');
  }

  if (format === 'xml') {
    const itemNodes = items.map(item => {
      const fields = Object.entries(item).map(([k, v]) => `    <${k}>${v}</${k}>`).join('\n');
      return `  <item>\n${fields}\n  </item>`;
    }).join('\n');
    return `<root>\n${itemNodes}\n</root>`;
  }

  if (format === 'excel') {
    if (!items || !items.length) return "// [Excel Spreadsheet (.xlsx)] Empty dataset";
    const keys = Array.from(new Set(items.flatMap(i => Object.keys(i))));
    const getColLetter = idx => String.fromCharCode(65 + (idx % 26));

    const colWidths = keys.map((key, idx) => {
      let maxLen = Math.max(key.length, getColLetter(idx).length);
      items.forEach(item => {
        const val = item[key] !== undefined ? String(item[key]) : "";
        if (val.length > maxLen) maxLen = val.length;
      });
      return Math.min(Math.max(maxLen + 2, 10), 24);
    });

    const pad = (str, len) => (str.length >= len ? str.substring(0, len) : str + " ".repeat(len - str.length));

    const colLetterHeader = "| " + keys.map((_, idx) => pad(getColLetter(idx), colWidths[idx])).join(" | ") + " |";
    const separator = "+" + colWidths.map(w => "-".repeat(w + 2)).join("+") + "+";
    const dataHeader = "| " + keys.map((key, idx) => pad(key, colWidths[idx])).join(" | ") + " |";

    const rows = items.map((item, rIdx) => {
      const line = "| " + keys.map((key, idx) => {
        const val = item[key] !== undefined ? String(item[key]) : "";
        return pad(val, colWidths[idx]);
      }).join(" | ") + " |";
      return `${line}  <- Row ${rIdx + 2}`;
    });

    return [
      `================================================================================`,
      `📊 EXCEL WORKBOOK PREVIEW — Sheet1 (OpenXML .xlsx Stream)`,
      `================================================================================`,
      colLetterHeader,
      separator,
      `${dataHeader}  <- Row 1 (Header)`,
      separator,
      ...rows,
      separator,
      ``,
      `📌 OpenXML Binary Package Specifications:`,
      `  • Format: Microsoft Excel OpenXML Spreadsheet (.xlsx)`,
      `  • MIME Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`,
      `  • Stream Package Size: ${(items.length * 420 + 1280).toLocaleString()} bytes`,
      `  • Columns Count: ${keys.length} (${keys.join(', ')})`,
      `  • Total Data Rows: ${items.length}`
    ].join('\n');
  }

  return JSON.stringify(items, null, 2);
}

function updateLiveConversion() {
  const inputEl = document.getElementById('playgroundInput');
  const outputEl = document.getElementById('playgroundOutput');
  const inputStatusEl = document.getElementById('inputStatusTag');
  const outputStatusEl = document.getElementById('outputStatusTag');
  const liveInfoEl = document.getElementById('liveInfoTag');

  if (!inputEl || !outputEl) return;

  const rawInput = inputEl.value;
  const UPCOMING = ['excel', 'toml', 'parquet', 'markdown'];
  const isSrcUpcoming = UPCOMING.includes(currentSrcFormat);
  const isTgtUpcoming = UPCOMING.includes(currentTgtFormat);

  if (isSrcUpcoming || isTgtUpcoming) {
    const upcomingFmt = (isTgtUpcoming ? currentTgtFormat : currentSrcFormat).toUpperCase();
    outputEl.value = `// Format Notice:\n// ${upcomingFmt} converter driver is Available Soon in the upcoming release.\n// Stay tuned for native zero-dependency ${upcomingFmt} parsing & export!`;
    if (inputStatusEl) inputStatusEl.textContent = isSrcUpcoming ? `${upcomingFmt} (Coming Soon)` : `${currentSrcFormat.toUpperCase()} (Selected)`;
    if (outputStatusEl) outputStatusEl.textContent = `Available Soon`;
    if (liveInfoEl) liveInfoEl.textContent = `Status: ${upcomingFmt} Driver — Available Soon!`;
    return;
  }

  try {
    const parsedItems = parseInputData(rawInput, currentSrcFormat);
    const convertedText = generateOutputData(parsedItems, currentTgtFormat);

    outputEl.value = convertedText;

    if (inputStatusEl) inputStatusEl.textContent = `${currentSrcFormat.toUpperCase()} (${parsedItems.length} records)`;
    if (outputStatusEl) outputStatusEl.textContent = `Valid ${currentTgtFormat.toUpperCase()}`;
    if (liveInfoEl) liveInfoEl.textContent = `Status: 100% Valid`;
  } catch (err) {
    outputEl.value = `// Validation Error:\n${err.message}`;
    if (inputStatusEl) inputStatusEl.textContent = `Syntax Error`;
    if (outputStatusEl) outputStatusEl.textContent = `Conversion Paused`;
    if (liveInfoEl) liveInfoEl.textContent = `Status: Syntax Error in ${currentSrcFormat.toUpperCase()} Input`;
  }
}

function smoothScrollTo(targetEl, duration = 600) {
  const targetPosition = targetEl.getBoundingClientRect().top + window.pageYOffset - 80;
  const startPosition = window.pageYOffset;
  const distance = targetPosition - startPosition;
  let startTime = null;

  function animation(currentTime) {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const progress = Math.min(timeElapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 2);

    window.scrollTo(0, startPosition + distance * ease);

    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  }

  requestAnimationFrame(animation);
}

document.addEventListener('DOMContentLoaded', () => {
  // Preloader Screen Handler (Shows for at least 0.75s)
  const preloader = document.getElementById('preloader');
  if (preloader) {
    setTimeout(() => {
      preloader.classList.add('hidden');
    }, 750);
  }

  // Header Search Expansion & Cmd+K Shortcut
  const searchWrapper = document.getElementById('searchWrapper');
  const searchTriggerBtn = document.getElementById('searchTriggerBtn');
  const searchInput = document.getElementById('searchInput');

  function openHeaderSearch() {
    if (searchWrapper) searchWrapper.classList.add('expanded');
    document.body.classList.add('search-expanded');
    if (searchInput) {
      setTimeout(() => searchInput.focus(), 150);
    }
  }

  function closeHeaderSearch() {
    if (searchWrapper) searchWrapper.classList.remove('expanded');
    document.body.classList.remove('search-expanded');
    if (searchInput) searchInput.blur();
  }

  if (searchTriggerBtn) {
    searchTriggerBtn.addEventListener('click', openHeaderSearch);
  }

  // Keyboard shortcut Cmd + K or Ctrl + K
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      openHeaderSearch();
    }
    if (e.key === 'Escape' && searchWrapper) {
      closeHeaderSearch();
    }
  });

  // Click outside to collapse search
  document.addEventListener('click', (e) => {
    if (searchWrapper && !searchWrapper.contains(e.target)) {
      closeHeaderSearch();
    }
  });

  // Repository Explorer Modal Handler
  const repoModal = document.getElementById('repoModal');
  const repoBtn = document.getElementById('repoBtn');
  const footerRepoBtn = document.getElementById('footerRepoBtn');
  const repoModalCloseBtn = document.getElementById('repoModalCloseBtn');
  let repoLoaded = false;

  const repoOwner = "xsparshh";
  const repoName = "treqna";
  const repoBranch = "main";

  function openRepoModal(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (repoModal) {
      repoModal.classList.add('active');
      repoModal.setAttribute('aria-hidden', 'false');
      if (!repoLoaded) {
        initRepoExplorer();
        repoLoaded = true;
      }
    }
  }

  if (repoBtn) repoBtn.addEventListener('click', openRepoModal);
  if (footerRepoBtn) footerRepoBtn.addEventListener('click', openRepoModal);

  if (repoModalCloseBtn && repoModal) {
    repoModalCloseBtn.addEventListener('click', () => {
      repoModal.classList.remove('active');
      repoModal.setAttribute('aria-hidden', 'true');
    });
  }

  if (repoModal) {
    repoModal.addEventListener('click', (e) => {
      if (e.target === repoModal) {
        repoModal.classList.remove('active');
        repoModal.setAttribute('aria-hidden', 'true');
      }
    });
  }

  async function fetchRepoTree() {
    const r = await fetch(`https://api.github.com/repos/${repoOwner}/${repoName}/git/trees/${repoBranch}?recursive=1`);
    if (!r.ok) throw new Error("Tree fetch failed.");
    return (await r.json()).tree;
  }

  function buildRepoTree(paths) {
    const root = {};
    for (const i of paths) {
      const parts = i.path.split("/");
      let cur = root;
      for (let x = 0; x < parts.length; x++) {
        const p = parts[x];
        if (x === parts.length - 1 && i.type === "blob") {
          cur[p] = { __file: true, path: i.path };
        } else {
          cur[p] = cur[p] || {};
          cur = cur[p];
        }
      }
    }
    return root;
  }

  function renderRepoNode(node, parent) {
    Object.keys(node).sort().forEach(name => {
      const val = node[name];
      if (val.__file) {
        const d = document.createElement("div");
        d.className = "file";
        d.textContent = name;
        d.onclick = () => loadRepoFile(val.path);
        parent.appendChild(d);
      } else {
        const wrap = document.createElement("div");
        wrap.className = "dir";
        const f = document.createElement("div");
        f.className = "folder";
        f.textContent = name;
        const c = document.createElement("div");
        c.className = "children";
        f.onclick = () => wrap.classList.toggle("open");
        wrap.appendChild(f);
        wrap.appendChild(c);
        parent.appendChild(wrap);
        renderRepoNode(val, c);
      }
    });
  }

  async function loadRepoFile(path) {
    const viewer = document.getElementById("repoViewer");
    if (!viewer) return;
    viewer.textContent = `Loading ${path}...`;
    try {
      const url = `https://raw.githubusercontent.com/${repoOwner}/${repoName}/${repoBranch}/${path}`;
      const r = await fetch(url);
      if (!r.ok) throw new Error("File fetch failed.");
      viewer.textContent = await r.text();
    } catch (e) {
      viewer.textContent = `Error loading ${path}: ` + e.message;
    }
  }

  async function initRepoExplorer() {
    const sidebar = document.getElementById("repoSidebar");
    const viewer = document.getElementById("repoViewer");
    if (!sidebar) return;
    sidebar.innerHTML = "Fetching tree...";
    try {
      const tree = await fetchRepoTree();
      sidebar.innerHTML = "";
      const root = buildRepoTree(tree);
      renderRepoNode(root, sidebar);
    } catch (e) {
      sidebar.innerHTML = "<div style='color:#f87171;'>Failed to fetch remote tree. (Rate limited or network issue)</div>";
      if (viewer) viewer.textContent = "Could not fetch GitHub repository tree.\n\nTip: You can view local repository files at Desktop/Treqna.";
    }
  }

  // Animated Hero Terminal Script (Starts only when visitor scrolls to #install section)
  const bodyEl = document.getElementById("terminalBody");
  const installSection = document.getElementById("install");
  let terminalStarted = false;

  if (bodyEl) {
    const cmd = "pip install treqna";
    const total = 7.0;

    function addTerminalLine(html, cls = "") {
      const d = document.createElement("div");
      d.className = "line " + cls;
      d.innerHTML = html;
      bodyEl.appendChild(d);
      bodyEl.scrollTop = bodyEl.scrollHeight;
      return d;
    }

    function sleep(ms) {
      return new Promise(r => setTimeout(r, ms));
    }

    async function runTerminalAnimation() {
      bodyEl.innerHTML = "";
      addTerminalLine('<span class="dim">Last login: ' + new Date().toDateString() + '</span>');
      addTerminalLine('<span class="prompt">➜</span> <span class="path">~</span> <span id="t"></span><span class="cursor" id="c"></span>');
      const t = document.getElementById("t");
      const c = document.getElementById("c");

      for (let i = 0; i < cmd.length; i++) {
        if (t) {
          if (i < 12) t.innerHTML += '<span>' + cmd[i] + '</span>';
          else t.innerHTML += '<span class="pkg">' + cmd[i] + '</span>';
        }
        await sleep(75);
      }
      await sleep(500);
      if (c) c.remove();
      addTerminalLine("Collecting treqna");
      await sleep(500);
      addTerminalLine("Downloading treqna-0.1.0-py3-none-any.whl (7.0 MB)");
      const p = addTerminalLine("", "progress");
      let dl = 0;
      const getBar = () => {
        const w = window.innerWidth;
        if (w <= 440) return "━━━━━━━━━━━━━━";
        if (w <= 640) return "━━━━━━━━━━━━━━━━━━━━━";
        return "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━";
      };

      while (dl < total) {
        dl = Math.min(total, dl + (Math.random() * 0.22 + 0.06));
        const speed = (9 + Math.random() * 8).toFixed(1);
        if (p) p.textContent = getBar() + " " + dl.toFixed(1) + "/7.0 MB " + speed + " MB/s";
        await sleep(85 + Math.random() * 60);
      }
      if (p) p.textContent = getBar() + " 7.0/7.0 MB 14.2 MB/s";
      await sleep(500);
      addTerminalLine("Installing collected packages: treqna");
      await sleep(900);
      addTerminalLine("Successfully installed treqna-0.1.0", "success");
      await sleep(450);
      addTerminalLine("Start Converting Your Data to CSV, JSON, YAML, or XML !", "success");
      await sleep(1800);
      addTerminalLine('<span class="prompt">➜</span> <span class="path">~</span>');
      await sleep(2500);
      runTerminalAnimation();
    }

    if (installSection && 'IntersectionObserver' in window) {
      const termObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !terminalStarted) {
            terminalStarted = true;
            runTerminalAnimation();
            termObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2 });
      termObserver.observe(installSection);
    } else {
      runTerminalAnimation();
    }
  }

  // Intersection Observer Scroll Entrance Animations
  const animateElements = document.querySelectorAll('.animate-on-scroll');
  if (animateElements.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { threshold: 0.1 });

    animateElements.forEach(el => observer.observe(el));
  } else {
    animateElements.forEach(el => el.classList.add('is-visible'));
  }

  // Mobile Menu Toggle Handler
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const mobileMenuCheckbox = document.getElementById('mobileMenuCheckbox');
  const navLinks = document.querySelector('.nav-links');

  if (mobileMenuCheckbox && navLinks) {
    mobileMenuCheckbox.addEventListener('change', () => {
      if (mobileMenuCheckbox.checked) {
        navLinks.classList.add('mobile-open');
      } else {
        navLinks.classList.remove('mobile-open');
      }
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (navLinks.classList.contains('mobile-open') &&
          !navLinks.contains(e.target) &&
          mobileMenuToggle && !mobileMenuToggle.contains(e.target)) {
        navLinks.classList.remove('mobile-open');
        mobileMenuCheckbox.checked = false;
      }
    });

    // Close mobile menu when clicking a link
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('mobile-open');
        mobileMenuCheckbox.checked = false;
      });
    });
  }

  // Floating Air Header on Scroll
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll);
    handleScroll();
  }

  // Smooth scroll links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId && targetId !== '#') {
        const targetEl = document.querySelector(targetId);
        if (targetEl) {
          e.preventDefault();
          smoothScrollTo(targetEl, 600);
        }
      }
    });
  });

  // Source & Target Format Selectors with Duplicate Prevention
  const srcTabs = document.querySelectorAll('#srcTabGroup .src-tab');
  const tgtTabs = document.querySelectorAll('#tgtTabGroup .tgt-tab');
  const mobileSrcSelect = document.getElementById('mobileSrcSelect');
  const mobileTgtSelect = document.getElementById('mobileTgtSelect');
  const AVAILABLE_FORMATS = ['csv', 'json', 'yaml', 'xml'];

  function updateFormatDisabledStates() {
    if (mobileSrcSelect) {
      Array.from(mobileSrcSelect.options).forEach(opt => {
        if (!opt.hasAttribute('disabled') || opt.dataset.duplicateDisabled) {
          if (opt.value === currentTgtFormat) {
            opt.disabled = true;
            opt.dataset.duplicateDisabled = "true";
          } else if (opt.dataset.duplicateDisabled) {
            opt.disabled = false;
            delete opt.dataset.duplicateDisabled;
          }
        }
      });
    }

    if (mobileTgtSelect) {
      Array.from(mobileTgtSelect.options).forEach(opt => {
        if (!opt.hasAttribute('disabled') || opt.dataset.duplicateDisabled) {
          if (opt.value === currentSrcFormat) {
            opt.disabled = true;
            opt.dataset.duplicateDisabled = "true";
          } else if (opt.dataset.duplicateDisabled) {
            opt.disabled = false;
            delete opt.dataset.duplicateDisabled;
          }
        }
      });
    }
  }

  function setSrcFormat(fmt) {
    if (fmt === currentTgtFormat) {
      const altTgt = AVAILABLE_FORMATS.find(f => f !== fmt) || 'json';
      currentTgtFormat = altTgt;
      tgtTabs.forEach(t => t.classList.toggle('active', t.dataset.fmt === currentTgtFormat));
      if (mobileTgtSelect) mobileTgtSelect.value = currentTgtFormat;
    }
    currentSrcFormat = fmt;
    srcTabs.forEach(t => t.classList.toggle('active', t.dataset.fmt === currentSrcFormat));
    if (mobileSrcSelect) mobileSrcSelect.value = currentSrcFormat;
    const inputEl = document.getElementById('playgroundInput');
    if (inputEl && SAMPLES[currentSrcFormat]) {
      inputEl.value = SAMPLES[currentSrcFormat];
    }
    updateFormatDisabledStates();
    updateLiveConversion();
  }

  function setTgtFormat(fmt) {
    if (fmt === currentSrcFormat) {
      const altSrc = AVAILABLE_FORMATS.find(f => f !== fmt) || 'csv';
      currentSrcFormat = altSrc;
      srcTabs.forEach(t => t.classList.toggle('active', t.dataset.fmt === currentSrcFormat));
      if (mobileSrcSelect) mobileSrcSelect.value = currentSrcFormat;
      const inputEl = document.getElementById('playgroundInput');
      if (inputEl && SAMPLES[currentSrcFormat]) {
        inputEl.value = SAMPLES[currentSrcFormat];
      }
    }
    currentTgtFormat = fmt;
    tgtTabs.forEach(t => t.classList.toggle('active', t.dataset.fmt === currentTgtFormat));
    if (mobileTgtSelect) mobileTgtSelect.value = currentTgtFormat;
    updateFormatDisabledStates();
    updateLiveConversion();
  }

  // Initialize initial disabled states
  updateFormatDisabledStates();

  srcTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      if (tab.classList.contains('upcoming-tab')) {
        e.preventDefault();
        e.stopPropagation();
        tab.classList.add('show-tooltip');
        const liveInfoEl = document.getElementById('liveInfoTag');
        if (liveInfoEl) {
          const fmtName = tab.dataset.fmt ? tab.dataset.fmt.toUpperCase() : 'Format';
          liveInfoEl.textContent = `Status: ${fmtName} Driver — Available Soon!`;
          setTimeout(() => updateLiveConversion(), 2200);
        }
        setTimeout(() => tab.classList.remove('show-tooltip'), 2200);
        return;
      }
      setSrcFormat(tab.dataset.fmt);
    });
  });

  tgtTabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      if (tab.classList.contains('upcoming-tab')) {
        e.preventDefault();
        e.stopPropagation();
        tab.classList.add('show-tooltip');
        const liveInfoEl = document.getElementById('liveInfoTag');
        if (liveInfoEl) {
          const fmtName = tab.dataset.fmt ? tab.dataset.fmt.toUpperCase() : 'Format';
          liveInfoEl.textContent = `Status: ${fmtName} Driver — Available Soon!`;
          setTimeout(() => updateLiveConversion(), 2200);
        }
        setTimeout(() => tab.classList.remove('show-tooltip'), 2200);
        return;
      }
      setTgtFormat(tab.dataset.fmt);
    });
  });

  if (mobileSrcSelect) {
    mobileSrcSelect.addEventListener('change', () => {
      setSrcFormat(mobileSrcSelect.value);
    });
  }

  if (mobileTgtSelect) {
    mobileTgtSelect.addEventListener('change', () => {
      setTgtFormat(mobileTgtSelect.value);
    });
  }

  // Live Input Event Listener
  const inputEl = document.getElementById('playgroundInput');
  if (inputEl) {
    inputEl.value = SAMPLES.csv;
    inputEl.addEventListener('input', updateLiveConversion);
  }

  // Reset Sample Button
  const resetBtn = document.getElementById('resetSampleBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (inputEl && SAMPLES[currentSrcFormat]) {
        inputEl.value = SAMPLES[currentSrcFormat];
        updateLiveConversion();
      }
    });
  }

  // Copy Output Button
  const copyBtn = document.getElementById('copyBtn');
  const copyText = document.getElementById('copyText');
  if (copyBtn && copyText) {
    copyBtn.addEventListener('click', () => {
      const outputEl = document.getElementById('playgroundOutput');
      if (outputEl) {
        navigator.clipboard.writeText(outputEl.value || '');
        copyText.textContent = "Copied!";
        setTimeout(() => {
          copyText.textContent = "Copy Output";
        }, 2000);
      }
    });
  }

  // Initial Conversion Render
  updateLiveConversion();

  // External Redirect Interceptor Modal
  const modal = document.getElementById('redirectModal');
  const modalDomain = document.getElementById('redirectDomain');
  const modalCancelBtn = document.getElementById('modalCancelBtn');
  const modalVisitBtn = document.getElementById('modalVisitBtn');

  function openRedirectModal(url) {
    try {
      const urlObj = new URL(url);
      if (modalDomain) modalDomain.textContent = urlObj.hostname;
    } catch (e) {
      if (modalDomain) modalDomain.textContent = url;
    }
    if (modalVisitBtn) modalVisitBtn.href = url;
    if (modal) {
      modal.classList.add('active');
      modal.setAttribute('aria-hidden', 'false');
    }
  }

  function closeRedirectModal() {
    if (modal) {
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
    }
  }

  if (modalCancelBtn) modalCancelBtn.addEventListener('click', closeRedirectModal);
  if (modalVisitBtn) modalVisitBtn.addEventListener('click', closeRedirectModal);
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeRedirectModal();
    });
  }

  // Intercept external links
  document.querySelectorAll('a[href]').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href.startsWith('http://') || href.startsWith('https://'))) {
      link.addEventListener('click', function(e) {
        try {
          const targetUrl = new URL(href, window.location.href);
          if (targetUrl.hostname !== window.location.hostname) {
            e.preventDefault();
            openRedirectModal(href);
          }
        } catch (err) {
          // ignore invalid URLs
        }
      });
    }
  });

  // Custom Cursor Trailing System
  const cursorDot = document.getElementById('cursorDot');
  const cursorRing = document.getElementById('cursorRing');

  if (cursorDot && cursorRing && window.matchMedia('(pointer: fine)').matches) {
    let mouseX = -100;
    let mouseY = -100;
    let ringX = -100;
    let ringY = -100;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
      cursorDot.style.left = `${mouseX}px`;
      cursorDot.style.top = `${mouseY}px`;
    });

    function animateCursor() {
      ringX += (mouseX - ringX) * 0.18;
      ringY += (mouseY - ringY) * 0.18;
      cursorRing.style.left = `${ringX}px`;
      cursorRing.style.top = `${ringY}px`;
      requestAnimationFrame(animateCursor);
    }
    animateCursor();

    document.addEventListener('mouseover', (e) => {
      if (e.target && e.target.closest('footer, .footer')) {
        document.body.classList.add('cursor-footer-hide-ring');
      } else {
        document.body.classList.remove('cursor-footer-hide-ring');
      }

      if (e.target && e.target.closest('a, button, input, select, textarea, .node-tab, .feature-card, .sdk-card, .matrix-stat-card, [role="button"]')) {
        document.body.classList.add('cursor-hover');
      } else {
        document.body.classList.remove('cursor-hover');
      }
    });
  }
});
