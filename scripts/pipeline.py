"""
Sphagnum pipeline
"""
import pandas as pd
import folium
from folium.plugins import HeatMap
import argparse
import os
import json

# ── Chemins ────────────────────────────────────────────────────────────────────
INPUT   = "data/occurrence.txt"
CLEAN   = "data/occurrence_clean.csv"
OUT_EU  = "outputs/heatmap_europe.html"
OUT_FR  = "outputs/heatmap_france.html"
OUT_ST  = "outputs/stats.html"
SAMPLE  = 100_000
# ───────────────────────────────────────────────────────────────────────────────

COLS = [
    "decimalLatitude", "decimalLongitude",
    "species", "family", "eventDate",
    "countryCode", "occurrenceID",
    "iucnRedListCategory", "order",
]


# 1. Suivi du Chargement


def load(path: str, sample: int) -> pd.DataFrame:
    print(f"\n[1/4] Chargement de {path} ({sample:,} lignes max)…")

    chunks, loaded = [], 0
    for chunk in pd.read_csv(
        path, sep="\t",
        usecols=lambda c: c in COLS,
        dtype=str, on_bad_lines="skip",
        chunksize=50_000, low_memory=False
    ):
        chunks.append(chunk)
        loaded += len(chunk)
        print(f"    {loaded:,} lignes lues…", end="\r")
        if loaded >= sample:
            break

    print()
    df = pd.concat(chunks, ignore_index=True)
    print(f"    ✓ {len(df):,} lignes chargées")
    return df


# 2. Nettoyage du GBIF Sphagnum EU


def clean(df: pd.DataFrame) -> pd.DataFrame:
    print("\n[2/4] Nettoyage…")
    avant = len(df)

    # Conversion en numérique remplace les valeurs nul par NaN
    df["decimalLatitude"]  = pd.to_numeric(df["decimalLatitude"],  errors="coerce")
    df["decimalLongitude"] = pd.to_numeric(df["decimalLongitude"], errors="coerce")

    # Supprime les NaN
    df = df.dropna(subset=["decimalLatitude", "decimalLongitude"])

    # Valide des plages géographiques correctes
    df = df[
        df["decimalLatitude"].between(-90, 90) &
        df["decimalLongitude"].between(-180, 180)
    ]

    # Supprime les artefacts (0, 0)
    df = df[~((df["decimalLatitude"] == 0) & (df["decimalLongitude"] == 0))]

    print(f"    Supprimées  : {avant - len(df):,} lignes")
    print(f"    ✓ Restantes : {len(df):,} lignes")
    print(f"    ✓ Espèces   : {df['species'].nunique():,}")

    # Sauvegarde du fichier nettoyé
    df.to_csv(CLEAN, index=False)
    print(f"    ✓ Sauvegardé → {CLEAN}")
    return df


# 3. Carte de chaleur (Heatmap)


GRADIENT = {
    0.2: "#0d47a1",
    0.4: "#1565c0",
    0.55: "#00bcd4",
    0.7: "#4caf50",
    0.85: "#ffeb3b",
    1.0: "#f44336",
}


def make_heatmap(df: pd.DataFrame, output: str, center: list, zoom: int, title: str):
    """Génère une carte heatmap via Folium et la sauvegarde en HTML."""
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB dark_matter", prefer_canvas=True)

    heat_data = df[["decimalLatitude", "decimalLongitude"]].values.tolist()
    HeatMap(heat_data, radius=12, blur=10, min_opacity=0.2, gradient=GRADIENT).add_to(m)

    n_obs     = len(df)
    n_species = df["species"].nunique() if "species" in df.columns else "n/a"

    # Titre flottant
    m.get_root().html.add_child(folium.Element(f"""
    <div style="position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;
        background:rgba(10,10,20,0.82);color:#f0f0f0;padding:10px 22px;border-radius:8px;
        font-family:'Segoe UI',sans-serif;font-size:14px;pointer-events:none;
        border:1px solid rgba(255,255,255,0.12);">
        🌿 <b>{title}</b> &nbsp;·&nbsp;
        <span style="color:#4fc3f7">{n_obs:,} occurrences</span> &nbsp;·&nbsp;
        <span style="color:#a5d6a7">{n_species:,} espèces</span>
    </div>"""))

    # Légende
    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:30px;right:20px;z-index:9999;
        background:rgba(10,10,20,0.82);color:#ccc;padding:10px 14px;border-radius:8px;
        font-family:'Segoe UI',sans-serif;font-size:12px;border:1px solid rgba(255,255,255,0.1);">
        <div style="margin-bottom:6px;font-weight:600;color:#f0f0f0">Densité</div>
        <div style="width:120px;height:10px;border-radius:5px;
            background:linear-gradient(to right,#0d47a1,#00bcd4,#4caf50,#ffeb3b,#f44336)"></div>
        <div style="display:flex;justify-content:space-between;width:120px;margin-top:3px;font-size:11px">
            <span>faible</span><span>forte</span>
        </div>
    </div>"""))

    m.save(output)
    print(f"      ✓ Sauvegardé → {output}")


def make_heatmaps(df: pd.DataFrame):
    print("\n[3/4] Génération des heatmaps…")

    # Europe
    make_heatmap(df, OUT_EU,
                 center=[54, 15], zoom=4,
                 title="Biodiversité GBIF — Europe")

    # France uniquement
    df_fr = df[df["countryCode"] == "FR"]
    print(f"      France : {len(df_fr):,} occurrences")
    if len(df_fr) == 0:
        print(" ⚠️  Aucune occurrence FR trouvée — vérifier la colonne countryCode")
    else:
        make_heatmap(df_fr, OUT_FR,
                     center=[46.5, 2.5], zoom=6,
                     title="Biodiversité GBIF — France")


# 4. Tableaux statistiques en HTML


def make_stats(df: pd.DataFrame, output: str = OUT_ST):
    print("\n[4/4] Génération des statistiques…")

    # ── Calcul des tableaux ──
    top_species = (
        df.groupby("species").size()
        .reset_index(name="occurrences")
        .sort_values("occurrences", ascending=False)
        .head(200)
    )

    by_country = (
        df.groupby("countryCode").size()
        .reset_index(name="occurrences")
        .sort_values("occurrences", ascending=False)
    )

    by_order = (
        df.groupby("order").size()
        .reset_index(name="occurrences")
        .sort_values("occurrences", ascending=False)
        .head(50)
    )

    species_x_country = (
        df.groupby(["countryCode", "species"]).size()
        .reset_index(name="occurrences")
        .sort_values("occurrences", ascending=False)
        .head(300)
    )

    def df_to_json(d):
        return json.dumps(d.fillna("—").values.tolist())


    # Génération du HTML


    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Statistiques Biodiversité GBIF</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

  :root {{
    --bg: #0a0d12;
    --surface: #111520;
    --border: #1e2535;
    --accent: #4fc3f7;
    --green: #69db7c;
    --text: #e2e8f0;
    --muted: #64748b;
    --row-hover: #161c2b;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'IBM Plex Sans', sans-serif; min-height: 100vh; }}

  header {{ padding: 2.5rem 2rem 1.5rem; border-bottom: 1px solid var(--border); }}
  header h1 {{ font-size: 1.4rem; font-weight: 600; color: #fff; letter-spacing: -0.02em; }}
  header p {{ font-size: 0.85rem; color: var(--muted); margin-top: 4px; }}
  .stats-bar {{ display: flex; gap: 2rem; margin-top: 1.2rem; flex-wrap: wrap; }}
  .stat {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-val {{ font-family: 'IBM Plex Mono', monospace; font-size: 1.3rem; color: var(--accent); font-weight: 500; }}
  .stat-label {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }}

  nav {{ display: flex; gap: 0; border-bottom: 1px solid var(--border); padding: 0 2rem; overflow-x: auto; }}
  .tab {{ padding: 0.85rem 1.2rem; font-size: 0.82rem; font-weight: 500; cursor: pointer;
          color: var(--muted); border-bottom: 2px solid transparent; white-space: nowrap;
          transition: color 0.15s, border-color 0.15s; }}
  .tab:hover {{ color: var(--text); }}
  .tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  .panel {{ display: none; padding: 1.5rem 2rem; }}
  .panel.active {{ display: block; }}

  .toolbar {{ display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: center; flex-wrap: wrap; }}
  .search-box {{ flex: 1; min-width: 200px; max-width: 360px; }}
  .search-box input {{
    width: 100%; padding: 0.5rem 0.9rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 6px; color: var(--text); font-size: 0.82rem;
    font-family: 'IBM Plex Sans', sans-serif; outline: none;
    transition: border-color 0.15s;
  }}
  .search-box input:focus {{ border-color: var(--accent); }}
  .search-box input::placeholder {{ color: var(--muted); }}
  .count-label {{ font-size: 0.78rem; color: var(--muted); font-family: 'IBM Plex Mono', monospace; }}

  .table-wrap {{ overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
  thead th {{
    padding: 0.65rem 1rem; text-align: left;
    background: var(--surface); color: var(--muted);
    font-size: 0.72rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em;
    border-bottom: 1px solid var(--border); cursor: pointer; user-select: none;
    white-space: nowrap;
  }}
  thead th:hover {{ color: var(--text); }}
  thead th.sorted-asc::after {{ content: ' ↑'; color: var(--accent); }}
  thead th.sorted-desc::after {{ content: ' ↓'; color: var(--accent); }}
  tbody tr {{ border-bottom: 1px solid var(--border); transition: background 0.1s; }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--row-hover); }}
  tbody td {{ padding: 0.6rem 1rem; color: var(--text); }}
  tbody td:last-child {{ font-family: 'IBM Plex Mono', monospace; color: var(--accent); text-align: right; }}

  .bar-cell {{ display: flex; align-items: center; gap: 8px; }}
  .bar {{ height: 6px; border-radius: 3px; background: var(--accent); opacity: 0.6; min-width: 2px; }}
  .bar.green {{ background: var(--green); }}

  .pagination {{ display: flex; gap: 0.4rem; margin-top: 1rem; align-items: center; flex-wrap: wrap; }}
  .page-btn {{ padding: 0.35rem 0.7rem; border-radius: 5px; border: 1px solid var(--border);
               background: var(--surface); color: var(--muted); font-size: 0.78rem; cursor: pointer; }}
  .page-btn:hover, .page-btn.active {{ border-color: var(--accent); color: var(--accent); }}
  .page-info {{ font-size: 0.78rem; color: var(--muted); margin-left: 0.5rem; font-family: 'IBM Plex Mono', monospace; }}
</style>
</head>
<body>

<header>
  <h1>🌿 Statistiques Biodiversité GBIF</h1>
  <p>Données issues du fichier occurrence.txt — {len(df):,} occurrences analysées</p>
  <div class="stats-bar">
    <div class="stat"><span class="stat-val">{len(df):,}</span><span class="stat-label">Occurrences</span></div>
    <div class="stat"><span class="stat-val">{df['species'].nunique():,}</span><span class="stat-label">Espèces</span></div>
    <div class="stat"><span class="stat-val">{df['countryCode'].nunique():,}</span><span class="stat-label">Pays</span></div>
    <div class="stat"><span class="stat-val">{df['order'].nunique():,}</span><span class="stat-label">Ordres</span></div>
  </div>
</header>

<nav>
  <div class="tab active" onclick="switchTab('species')">Par espèce</div>
  <div class="tab" onclick="switchTab('country')">Par pays</div>
  <div class="tab" onclick="switchTab('order')">Par ordre</div>
  <div class="tab" onclick="switchTab('species_country')">Espèce × Pays</div>
</nav>

<!-- TAB 1 : Par espèce -->
<div class="panel active" id="panel-species">
  <div class="toolbar">
    <div class="search-box"><input type="text" placeholder="Rechercher une espèce…" oninput="filterTable('species',this.value)"></div>
    <span class="count-label" id="count-species">{len(top_species)} espèces</span>
  </div>
  <div class="table-wrap">
    <table id="table-species">
      <thead><tr>
        <th onclick="sortTable('species',0)">#</th>
        <th onclick="sortTable('species',1)">Espèce</th>
        <th onclick="sortTable('species',2)">Occurrences</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="pagination" id="pag-species"></div>
</div>

<!-- TAB 2 : Par pays -->
<div class="panel" id="panel-country">
  <div class="toolbar">
    <div class="search-box"><input type="text" placeholder="Rechercher un pays…" oninput="filterTable('country',this.value)"></div>
    <span class="count-label" id="count-country">{len(by_country)} pays</span>
  </div>
  <div class="table-wrap">
    <table id="table-country">
      <thead><tr>
        <th onclick="sortTable('country',0)">#</th>
        <th onclick="sortTable('country',1)">Pays (code ISO)</th>
        <th onclick="sortTable('country',2)">Occurrences</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="pagination" id="pag-country"></div>
</div>

<!-- TAB 3 : Par ordre -->
<div class="panel" id="panel-order">
  <div class="toolbar">
    <div class="search-box"><input type="text" placeholder="Rechercher un ordre…" oninput="filterTable('order',this.value)"></div>
    <span class="count-label" id="count-order">{len(by_order)} ordres</span>
  </div>
  <div class="table-wrap">
    <table id="table-order">
      <thead><tr>
        <th onclick="sortTable('order',0)">#</th>
        <th onclick="sortTable('order',1)">Ordre</th>
        <th onclick="sortTable('order',2)">Occurrences</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="pagination" id="pag-order"></div>
</div>

<!-- TAB 4 : Espèce × Pays -->
<div class="panel" id="panel-species_country">
  <div class="toolbar">
    <div class="search-box"><input type="text" placeholder="Rechercher espèce ou pays…" oninput="filterTable('species_country',this.value)"></div>
    <span class="count-label" id="count-species_country">{len(species_x_country)} combinaisons</span>
  </div>
  <div class="table-wrap">
    <table id="table-species_country">
      <thead><tr>
        <th onclick="sortTable('species_country',0)">#</th>
        <th onclick="sortTable('species_country',1)">Pays</th>
        <th onclick="sortTable('species_country',2)">Espèce</th>
        <th onclick="sortTable('species_country',3)">Occurrences</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="pagination" id="pag-species_country"></div>
</div>

<script>
const RAW = {{
  species:         {df_to_json(top_species)},
  country:         {df_to_json(by_country)},
  order:           {df_to_json(by_order)},
  species_country: {df_to_json(species_x_country)}
}};

const state = {{}};
['species','country','order','species_country'].forEach(k => {{
  state[k] = {{ data: RAW[k], filtered: RAW[k], page: 0, perPage: 25, sortCol: -1, sortDir: 1 }};
}});

function switchTab(id) {{
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', ['species','country','order','species_country'][i]===id));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-'+id).classList.add('active');
  renderTable(id);
}}

function filterTable(id, q) {{
  const s = state[id];
  s.filtered = q ? RAW[id].filter(r => r.some(v => String(v).toLowerCase().includes(q.toLowerCase()))) : RAW[id];
  s.page = 0;
  document.getElementById('count-'+id).textContent = s.filtered.length + ' résultats';
  renderTable(id);
}}

function sortTable(id, col) {{
  const s = state[id];
  s.sortDir = (s.sortCol === col) ? -s.sortDir : -1;
  s.sortCol = col;
  s.filtered = [...s.filtered].sort((a,b) => {{
    const av = isNaN(a[col]) ? a[col] : +a[col];
    const bv = isNaN(b[col]) ? b[col] : +b[col];
    return av < bv ? s.sortDir : av > bv ? -s.sortDir : 0;
  }});
  s.page = 0;
  renderTable(id);
}}

function renderTable(id) {{
  const s = state[id];
  const tbl = document.querySelector('#table-'+id+' tbody');
  const start = s.page * s.perPage;
  const rows  = s.filtered.slice(start, start + s.perPage);
  const maxVal = Math.max(...s.filtered.map(r => +r[r.length-1]||0));

  tbl.innerHTML = rows.map((r, i) => {{
    const rank = start + i + 1;
    const val  = +r[r.length-1] || 0;
    const pct  = Math.round(val / maxVal * 120);
    const cells = r.slice(0, r.length-1).map(v => `<td>${{v}}</td>`).join('');
    return `<tr>
      <td style="color:var(--muted);font-family:'IBM Plex Mono',monospace;font-size:0.75rem">${{rank}}</td>
      ${{cells}}
      <td>
        <div class="bar-cell">
          <div class="bar" style="width:${{pct}}px"></div>
          ${{val.toLocaleString('fr-FR')}}
        </div>
      </td>
    </tr>`;
  }}).join('');

  // Pagination
  const total = Math.ceil(s.filtered.length / s.perPage);
  const pag = document.getElementById('pag-'+id);
  let btns = '';
  const p = s.page;
  const pages = [...new Set([0, p-1, p, p+1, total-1])].filter(x => x>=0 && x<total).sort((a,b)=>a-b);
  pages.forEach((pg, idx) => {{
    if (idx > 0 && pg - pages[idx-1] > 1) btns += '<span style="color:var(--muted);padding:0 4px">…</span>';
    btns += `<button class="page-btn ${{pg===p?'active':''}}" onclick="goPage('${{id}}',${{pg}})">${{pg+1}}</button>`;
  }});
  pag.innerHTML = btns + `<span class="page-info">${{start+1}}–${{Math.min(start+s.perPage, s.filtered.length)}} / ${{s.filtered.length}}</span>`;

  // Tri header
  document.querySelectorAll('#table-'+id+' thead th').forEach((th,i) => {{
    th.classList.remove('sorted-asc','sorted-desc');
    if (i === s.sortCol) th.classList.add(s.sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
  }});
}}

function goPage(id, pg) {{
  state[id].page = pg;
  renderTable(id);
}}

// Init
renderTable('species');
</script>
</body>
</html>"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"      ✓ Sauvegardé → {output}")


# MAIN


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=SAMPLE)
    args = parser.parse_args()

    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    if not os.path.exists(INPUT):
        raise FileNotFoundError(f"❌ Fichier introuvable : {INPUT}")

    df = load(INPUT, args.sample)
    df = clean(df)
    make_heatmaps(df)
    make_stats(df)

    print("\n✅ Pipeline terminé !")
    print(f"   Heatmap Europe  → {OUT_EU}")
    print(f"   Heatmap France  → {OUT_FR}")
    print(f"   Statistiques    → {OUT_ST}")
    print("\nOuvrir les fichiers .html dans Chrome ou Firefox.")


if __name__ == "__main__":
    main()