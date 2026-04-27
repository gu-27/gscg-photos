#!/usr/bin/env python3
"""
GSCG Photo Gallery Builder
Run this script after dropping photos into docs/photos/portland/ or docs/photos/seattle/
It scans both folders and regenerates docs/index.html automatically.

Usage:
    python3 scripts/build.py
"""

import os
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
PHOTOS_DIR = DOCS / "photos"
OUTPUT = DOCS / "index.html"

IMG_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".JPG", ".JPEG", ".PNG"}

TRIPS = {
    "portland": {
        "label": "Portland",
        "subtitle": "Nike Campus Visit",
        "color": "#C8102E",
        "emoji": "🌹",
    },
    "seattle": {
        "label": "Seattle",
        "subtitle": "Seattle Trip",
        "color": "#004687",
        "emoji": "⚓",
    },
}

def get_photos(city):
    folder = PHOTOS_DIR / city
    if not folder.exists():
        return []
    files = sorted(
        f.name for f in folder.iterdir()
        if f.suffix in IMG_EXTENSIONS
    )
    return files

def build():
    data = {}
    for city, meta in TRIPS.items():
        photos = get_photos(city)
        data[city] = {**meta, "photos": photos}
        print(f"  {meta['label']}: {len(photos)} photo(s)")

    photos_json = json.dumps(data, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSCG Trip Photos — Portland &amp; Seattle</title>
  <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,700;1,400&family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --navy: #041E42;
      --red:  #C8102E;
      --accent: #e8edf5;
      --border: #dde3ec;
      --muted: #6b7a8d;
      --white: #ffffff;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Outfit', sans-serif; background: var(--accent); color: var(--navy); }}

    /* ── HEADER ── */
    header {{
      background: var(--navy); color: white;
      padding: 3rem 2rem 2.5rem; text-align: center;
    }}
    .header-eyebrow {{
      font-size: .65rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase;
      color: rgba(255,255,255,.45); margin-bottom: .75rem;
    }}
    header h1 {{
      font-family: 'Libre Baskerville', serif;
      font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 700;
      margin-bottom: .5rem;
    }}
    header p {{ font-size: .95rem; color: rgba(255,255,255,.55); }}

    /* ── TABS ── */
    .tabs {{
      display: flex; justify-content: center; gap: 0;
      background: var(--navy); padding-bottom: 0;
      border-bottom: 1px solid rgba(255,255,255,.1);
    }}
    .tab-btn {{
      padding: .85rem 2.5rem; border: none; background: transparent;
      font-family: 'Outfit', sans-serif; font-size: .875rem; font-weight: 600;
      color: rgba(255,255,255,.45); cursor: pointer;
      border-bottom: 3px solid transparent; transition: all .2s;
    }}
    .tab-btn:hover {{ color: rgba(255,255,255,.8); }}
    .tab-btn.active {{ color: white; border-bottom-color: var(--red); }}

    /* ── CITY PANEL ── */
    .city-panel {{ display: none; padding: 2rem; max-width: 1300px; margin: 0 auto; }}
    .city-panel.active {{ display: block; }}

    .city-header {{
      display: flex; align-items: center; justify-content: space-between;
      flex-wrap: wrap; gap: 1rem; margin-bottom: 1.75rem;
    }}
    .city-title {{
      display: flex; align-items: center; gap: .75rem;
    }}
    .city-emoji {{ font-size: 1.75rem; }}
    .city-name {{ font-size: 1.4rem; font-weight: 800; color: var(--navy); }}
    .city-sub  {{ font-size: .82rem; color: var(--muted); margin-top: .1rem; }}
    .photo-count {{
      font-size: .78rem; font-weight: 600; color: var(--muted);
      background: white; border: 1px solid var(--border);
      padding: .4rem .9rem; border-radius: 999px;
    }}

    /* ── PHOTO GRID ── */
    .photo-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem;
    }}
    .photo-card {{
      background: white; border-radius: 12px; overflow: hidden;
      border: 1px solid var(--border);
      box-shadow: 0 2px 8px rgba(4,30,66,.06);
      transition: transform .2s, box-shadow .2s;
      cursor: pointer;
    }}
    .photo-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(4,30,66,.12);
    }}
    .photo-card img {{
      width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block;
    }}
    .photo-card-footer {{
      padding: .65rem .85rem;
      display: flex; align-items: center; justify-content: space-between;
    }}
    .photo-name {{ font-size: .72rem; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px; }}
    .dl-btn {{
      display: flex; align-items: center; gap: .35rem;
      font-size: .72rem; font-weight: 700; color: var(--red);
      text-decoration: none; padding: .3rem .65rem;
      border: 1px solid rgba(200,16,46,.25); border-radius: 6px;
      transition: background .15s; white-space: nowrap; flex-shrink: 0;
    }}
    .dl-btn:hover {{ background: rgba(200,16,46,.06); }}

    /* ── EMPTY STATE ── */
    .empty-state {{
      text-align: center; padding: 5rem 2rem;
      background: white; border-radius: 16px; border: 1px solid var(--border);
    }}
    .empty-state .icon {{ font-size: 3rem; margin-bottom: 1rem; }}
    .empty-state h3 {{ font-size: 1.1rem; font-weight: 700; color: var(--navy); margin-bottom: .5rem; }}
    .empty-state p  {{ font-size: .875rem; color: var(--muted); line-height: 1.7; }}
    .empty-state code {{
      display: inline-block; margin-top: .75rem;
      background: var(--accent); border: 1px solid var(--border);
      border-radius: 6px; padding: .35rem .75rem;
      font-size: .82rem; color: var(--navy);
    }}

    /* ── LIGHTBOX ── */
    #lightbox {{
      display: none; position: fixed; inset: 0; z-index: 1000;
      background: rgba(4,30,66,.96); backdrop-filter: blur(6px);
      align-items: center; justify-content: center; flex-direction: column;
    }}
    #lightbox.open {{ display: flex; }}
    #lightbox img {{
      max-width: 92vw; max-height: 80vh;
      border-radius: 8px; object-fit: contain;
      box-shadow: 0 24px 64px rgba(0,0,0,.5);
    }}
    .lb-controls {{
      display: flex; align-items: center; gap: 1rem; margin-top: 1.25rem; flex-wrap: wrap; justify-content: center;
    }}
    .lb-btn {{
      display: flex; align-items: center; gap: .5rem;
      padding: .6rem 1.25rem; border-radius: 8px; border: 1px solid rgba(255,255,255,.2);
      background: rgba(255,255,255,.08); color: white;
      font-family: 'Outfit', sans-serif; font-size: .85rem; font-weight: 600;
      cursor: pointer; text-decoration: none; transition: background .15s;
    }}
    .lb-btn:hover {{ background: rgba(255,255,255,.16); }}
    .lb-btn.primary {{ background: var(--red); border-color: var(--red); }}
    .lb-btn.primary:hover {{ background: #a50d25; }}
    .lb-counter {{ font-size: .78rem; color: rgba(255,255,255,.45); }}
    .lb-close {{
      position: absolute; top: 1.25rem; right: 1.5rem;
      background: none; border: none; color: rgba(255,255,255,.5);
      font-size: 1.75rem; cursor: pointer; line-height: 1; padding: .25rem;
      transition: color .15s;
    }}
    .lb-close:hover {{ color: white; }}

    /* ── FOOTER ── */
    footer {{
      background: var(--navy); color: rgba(255,255,255,.35);
      text-align: center; padding: 1.75rem; font-size: .75rem; margin-top: 3rem;
    }}
    footer strong {{ color: rgba(255,255,255,.6); }}

    @media (max-width: 600px) {{
      .city-panel {{ padding: 1.25rem; }}
      .photo-grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: .75rem; }}
      .tab-btn {{ padding: .75rem 1.25rem; font-size: .8rem; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-eyebrow">Gonzaga Sports Consulting Group</div>
  <h1>GSCG Trip Photos</h1>
  <p>Browse and download photos from our professional visits</p>
</header>

<div class="tabs" id="tabs">
  <button class="tab-btn active" onclick="switchTab('portland')" id="tab-portland">🌹 Portland</button>
  <button class="tab-btn" onclick="switchTab('seattle')" id="tab-seattle">⚓ Seattle</button>
</div>

<!-- City Panels (injected by JS) -->
<div id="panels"></div>

<!-- ── LIGHTBOX ── -->
<div id="lightbox" onclick="closeLightbox(event)">
  <button class="lb-close" onclick="closeLightbox()">&times;</button>
  <img id="lb-img" src="" alt="">
  <div class="lb-controls">
    <button class="lb-btn" onclick="lbNav(-1)">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
      Prev
    </button>
    <span class="lb-counter" id="lb-counter"></span>
    <button class="lb-btn" onclick="lbNav(1)">
      Next
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
    </button>
    <a id="lb-dl" href="" download class="lb-btn primary">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download
    </a>
  </div>
</div>

<footer>
  <strong>Gonzaga Sports Consulting Group</strong> &nbsp;&middot;&nbsp; GSCG Trip Photos &nbsp;&middot;&nbsp; 2026
</footer>

<script>
const PHOTOS = {photos_json};

let activeCity = 'portland';
let lbPhotos = [];
let lbIdx = 0;

// Build panels
const panelsEl = document.getElementById('panels');
Object.entries(PHOTOS).forEach(([city, data]) => {{
  const panel = document.createElement('div');
  panel.className = 'city-panel' + (city === 'portland' ? ' active' : '');
  panel.id = 'panel-' + city;

  if (data.photos.length === 0) {{
    panel.innerHTML = `
      <div class="city-header">
        <div class="city-title">
          <span class="city-emoji">${{data.emoji}}</span>
          <div>
            <div class="city-name">${{data.label}}</div>
            <div class="city-sub">${{data.subtitle}}</div>
          </div>
        </div>
        <span class="photo-count">0 photos</span>
      </div>
      <div class="empty-state">
        <div class="icon">📸</div>
        <h3>No photos yet</h3>
        <p>Drop your photos into the folder below, then run the build script to update the gallery.</p>
        <code>docs/photos/${{city}}/</code>
      </div>`;
  }} else {{
    const grid = data.photos.map((file, i) => `
      <div class="photo-card" onclick="openLightbox('${{city}}', ${{i}})">
        <img src="photos/${{city}}/${{file}}" alt="${{file}}" loading="lazy">
        <div class="photo-card-footer">
          <span class="photo-name">${{file}}</span>
          <a class="dl-btn" href="photos/${{city}}/${{file}}" download onclick="event.stopPropagation()">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            Save
          </a>
        </div>
      </div>`).join('');

    panel.innerHTML = `
      <div class="city-header">
        <div class="city-title">
          <span class="city-emoji">${{data.emoji}}</span>
          <div>
            <div class="city-name">${{data.label}}</div>
            <div class="city-sub">${{data.subtitle}}</div>
          </div>
        </div>
        <span class="photo-count">${{data.photos.length}} photo${{data.photos.length !== 1 ? 's' : ''}}</span>
      </div>
      <div class="photo-grid">${{grid}}</div>`;
  }}

  panelsEl.appendChild(panel);
}});

function switchTab(city) {{
  activeCity = city;
  document.querySelectorAll('.city-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + city).classList.add('active');
  document.getElementById('tab-' + city).classList.add('active');
}}

// Lightbox
function openLightbox(city, idx) {{
  lbPhotos = PHOTOS[city].photos.map(f => ({{ src: `photos/${{city}}/${{f}}`, name: f }}));
  lbIdx = idx;
  showLbPhoto();
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}}

function showLbPhoto() {{
  const p = lbPhotos[lbIdx];
  document.getElementById('lb-img').src = p.src;
  document.getElementById('lb-dl').href = p.src;
  document.getElementById('lb-dl').download = p.name;
  document.getElementById('lb-counter').textContent = `${{lbIdx + 1}} / ${{lbPhotos.length}}`;
}}

function lbNav(dir) {{
  lbIdx = (lbIdx + dir + lbPhotos.length) % lbPhotos.length;
  showLbPhoto();
}}

function closeLightbox(e) {{
  if (!e || e.target === document.getElementById('lightbox') || e.target.classList.contains('lb-close')) {{
    document.getElementById('lightbox').classList.remove('open');
    document.body.style.overflow = '';
  }}
}}

document.addEventListener('keydown', e => {{
  const lb = document.getElementById('lightbox');
  if (!lb.classList.contains('open')) return;
  if (e.key === 'ArrowRight') lbNav(1);
  if (e.key === 'ArrowLeft')  lbNav(-1);
  if (e.key === 'Escape')     closeLightbox();
}});
</script>
</body>
</html>"""

    OUTPUT.write_text(html)
    print(f"\n✓ Gallery built → {OUTPUT}")
    print("  Push to GitHub to publish.")

if __name__ == "__main__":
    print("Scanning photos...")
    build()
