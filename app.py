"""
app.py — FastAPI backend for the Siege Coaching Portal.

Endpoints:
  GET  /                          → HTML dashboard showing all stack members
  GET  /api/players               → List known stack members with report status
  GET  /api/coach?username=X      → Run full pipeline for a player (fresh fetch + report)
  GET  /api/report/{username}     → Serve the cached HTML report
  GET  /api/stack                 → AI-powered team stack analysis
  GET  /api/status                → Health check
"""
import os
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("[Error] FastAPI not installed. Run: pip install fastapi uvicorn[standard]")
    sys.exit(1)

# ─── Config ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"

def load_env():
    env_vars = {}
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

ENV = load_env()

STACK_MEMBERS = [
    {"username": m.strip(), "platform": "uplay" if m.strip() == "WamaiDoingThis" else "ubi"}
    for m in ENV.get("STACK_MEMBERS", "Amlenk,WamaiDoingThis,Covetous_Demon").split(",")
    if m.strip()
]

INDIVIDUAL_PLAYERS = [
    {"username": m.strip(), "platform": "uplay" if m.strip() == "WamaiDoingThis" else "ubi"}
    for m in ENV.get("INDIVIDUAL_PLAYERS", "FearlessCoppeR").split(",")
    if m.strip()
]

ALL_PLAYERS = STACK_MEMBERS + INDIVIDUAL_PLAYERS

DISPLAY_NAMES = {
    "amlenk": "Amlenk",
    "wamaidoingthis": "WamaiDoingThis (yeetingyeti)",
    "covetous_demon": "Covetous_Demon",
    "fearlesscopper": "FearlessCoppeR",
}


# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Siege Coaching Portal API",
    description="AI-powered Rainbow Six Siege tactical coaching for your stack.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def run_pipeline(username: str, platform: str = "uplay") -> dict:
    """
    Execute the full analysis pipeline for a player.
    Returns a dict with status and any errors.
    """
    steps = [
        (f'python r6data_fetch.py "{username}" "{platform}"', "Fetching stats via R6Data API"),
        (f'python stats.py "{username}"', "Processing stats"),
        (f'python charts.py "{username}"', "Generating lifetime charts"),
        (f'python generate_charts_y11s1.py "{username}"', "Generating Y11S1 charts"),
        (f'python report.py "{username}"', "Generating coaching report"),
    ]
    
    results = []
    for cmd, desc in steps:
        start = time.time()
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=str(BASE_DIR)
        )
        duration = round(time.time() - start, 1)
        step_result = {
            "step": desc,
            "command": cmd,
            "duration_s": duration,
            "success": result.returncode == 0,
            "stdout": result.stdout[-1000:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else ""
        }
        results.append(step_result)
        if result.returncode != 0:
            return {"success": False, "steps": results, "failed_at": desc}
    
    return {"success": True, "steps": results}


def get_player_report_status(username: str) -> dict:
    """Check if a player has generated reports."""
    md_path = OUTPUT_DIR / f"{username}_report.md"
    html_path = OUTPUT_DIR / f"{username}_report.html"
    
    md_exists = md_path.exists()
    html_exists = html_path.exists()
    
    last_updated = None
    if html_exists:
        last_updated = time.strftime(
            "%Y-%m-%d %H:%M UTC",
            time.gmtime(html_path.stat().st_mtime)
        )
    
    # Try to read summary stats from processed file
    summary = {}
    processed_path = DATA_DIR / f"{username}_stats_processed.json"
    if not processed_path.exists():
        processed_path = DATA_DIR / "stats_processed.json"
        
    if processed_path.exists():
        try:
            with open(processed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            lifetime = data.get("lifetime", {})
            s_life = lifetime.get("summary", {})
            
            y11 = data.get("y11s1", {})
            s_y11 = y11.get("summary", {})
            
            if s_life.get("username", "").lower() == username.lower() or s_y11.get("username", "").lower() == username.lower():
                summary = {
                    "kd": s_life.get("kd", "—"),
                    "win_rate": s_life.get("win_rate", "—"),
                    "ranked_rating": s_life.get("ranked_rating", "—"),
                    "y11_kd": s_y11.get("kd", "—"),
                    "y11_win_rate": s_y11.get("win_rate", "—"),
                    "y11_rating": s_y11.get("ranked_rating", "—"),
                }
        except Exception:
            pass
    
    display = DISPLAY_NAMES.get(username.lower(), username)
    
    return {
        "username": username,
        "display_name": display,
        "has_report": html_exists,
        "has_markdown": md_exists,
        "last_updated": last_updated,
        "stats": summary
    }


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/api/status")
def health_check():
    return {
        "status": "online",
        "version": "2.0.0",
        "stack_members": [m["username"] for m in STACK_MEMBERS],
        "individual_players": [m["username"] for m in INDIVIDUAL_PLAYERS],
        "gemini_configured": bool(ENV.get("GEMINI_API_KEY")),
        "r6data_configured": bool(ENV.get("R6DATA_API_KEY"))
    }


@app.get("/api/players")
def list_players():
    """List all players and their report status."""
    return [get_player_report_status(m["username"]) for m in ALL_PLAYERS]


@app.get("/api/coach")
def run_coach(
    username: str = Query(..., description="Ubisoft username"),
    platform: str = Query("uplay", description="Platform: uplay, psn, xbl")
):
    """
    Run the full coaching pipeline for a player.
    Fetches fresh data, processes stats, generates charts and report.
    """
    # Normalise platform
    if platform in ['ubi', 'uplayconnect', 'pc']:
        platform = 'uplay'
    
    print(f"\n[API] Running pipeline for {username} ({platform})...")
    pipeline_result = run_pipeline(username, platform)
    
    report_md = ""
    html_path = OUTPUT_DIR / f"{username}_report.html"
    md_path = OUTPUT_DIR / f"{username}_report.md"
    
    if pipeline_result["success"]:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/api/report/{username}")
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed at: {pipeline_result.get('failed_at', 'unknown step')}. Stderr: {pipeline_result.get('steps', [])[-1].get('stderr', '')}"
        )


@app.get("/api/report/{username}", response_class=HTMLResponse)
def get_report(username: str):
    """Serve the cached HTML coaching report for a player."""
    # Case-insensitive search
    for member in ALL_PLAYERS:
        if member["username"].lower() == username.lower():
            username = member["username"]
            break
    
    html_path = OUTPUT_DIR / f"{username}_report.html"
    
    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No report found for '{username}'. Run /api/coach?username={username} first."
        )
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get("/api/stack")
def stack_analysis():
    """
    Generate an AI-powered team stack analysis comparing all stack members.
    Uses cached processed stats — does not re-fetch.
    """
    from ai_coach import get_ai_stack_analysis
    
    # Collect all available stack member stats
    stack_stats = []
    for member in STACK_MEMBERS:
        username = member["username"]
        processed_path = DATA_DIR / f"{username}_stats_processed.json"
        if not processed_path.exists():
            # Try default path as fallback
            processed_path = DATA_DIR / "stats_processed.json"
            
        if processed_path.exists():
            try:
                with open(processed_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                y11 = data.get("y11s1", {})
                if y11.get("summary", {}).get("username", "").lower() == username.lower():
                    stack_stats.append(y11)
            except Exception as e:
                print(f"Error reading stats for {username}: {e}")
    
    if not stack_stats:
        raise HTTPException(
            status_code=404, 
            detail="No stack member stats available. Run the analysis pipeline for at least one player first."
        )
    
    api_key = ENV.get("GEMINI_API_KEY", "")
    analysis = get_ai_stack_analysis(stack_stats, api_key=api_key)
    
    if not analysis:
        raise HTTPException(status_code=500, detail="AI stack analysis failed.")
    
    return {"analysis_markdown": analysis}


@app.get("/sensitivity", response_class=HTMLResponse)
def sensitivity_dashboard():
    """Serve the premium interactive sensitivity and ADS scaling dashboard."""
    html_path = BASE_DIR / "sensitivity_dashboard.html"
    if not html_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Sensitivity dashboard template file not found."
        )
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HTMLResponse(content=content)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Serve the premium coaching portal dashboard."""
    stack_players = [get_player_report_status(m["username"]) for m in STACK_MEMBERS]
    individual_players = [get_player_report_status(m["username"]) for m in INDIVIDUAL_PLAYERS]
    
    def make_player_cards(players_list):
        cards_html = ""
        for p in players_list:
            status_badge = (
                '<span class="badge badge-ready">✓ Report Ready</span>'
                if p["has_report"] else
                '<span class="badge badge-pending">⏳ No Report</span>'
            )
            stats_html = ""
            if p["stats"]:
                stats_html = f"""
                <!-- Tab Switcher -->
                <div class="card-tabs" style="display: flex; gap: 4px; background: rgba(0,0,0,0.25); padding: 3px; border-radius: 10px; margin-bottom: 12px; border: 1px solid var(--border);">
                    <button class="tab-btn active" onclick="switchCardTab(this, 'overall')" style="flex: 1; background: var(--bg-card); border: 1px solid rgba(74, 144, 226, 0.15); color: var(--primary); box-shadow: 0 2px 6px rgba(0,0,0,0.3); padding: 6px 12px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; cursor: pointer; transition: all 0.2s;">Overall</button>
                    <button class="tab-btn" onclick="switchCardTab(this, 'y11s1')" style="flex: 1; background: transparent; border: none; color: var(--text-secondary); padding: 6px 12px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; cursor: pointer; transition: all 0.2s;">Y11S1 Season</button>
                </div>
                
                <!-- Overall Stats Group -->
                <div class="stats-overall stats-group" style="display: grid; gap: 8px;">
                    <div class="stat-row">
                        <span class="stat-label">Ranked Overall K/D</span>
                        <span class="stat-value">{p['stats'].get('kd', '—')}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Overall Win Rate</span>
                        <span class="stat-value">{p['stats'].get('win_rate', '—')}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Overall Rank</span>
                        <span class="stat-value rank-value" style="color: var(--accent); font-weight: 800; font-size: 0.8rem;">{p['stats'].get('ranked_rating', '—')}</span>
                    </div>
                </div>
                
                <!-- Y11S1 Stats Group -->
                <div class="stats-y11s1 stats-group" style="display: none; gap: 8px;">
                    <div class="stat-row">
                        <span class="stat-label">Y11S1 Season K/D</span>
                        <span class="stat-value" style="color: var(--accent-purple);">{p['stats'].get('y11_kd', '—')}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Season Win Rate</span>
                        <span class="stat-value" style="color: var(--accent-purple);">{p['stats'].get('y11_win_rate', '—')}</span>
                    </div>
                    <div class="stat-row">
                        <span class="stat-label">Season Rank</span>
                        <span class="stat-value rank-value" style="color: var(--accent-purple); font-weight: 800; font-size: 0.8rem;">{p['stats'].get('y11_rating', '—')}</span>
                    </div>
                </div>
                """
            
            report_btn = ""
            if p["has_report"]:
                report_btn = f'<a href="/api/report/{p["username"]}" class="btn btn-primary" target="_blank">View Report</a>'
            
            run_btn = f'<a href="/api/coach?username={p["username"]}" class="btn btn-secondary" target="_blank">Run Analysis</a>'
            last_updated = f'<div class="last-updated">Last updated: {p["last_updated"]}</div>' if p["last_updated"] else ""
            
            cards_html += f"""
            <div class="player-card">
                <div class="card-header">
                    <div class="player-avatar">{"".join([w[0].upper() for w in p['display_name'].split()[:2]])}</div>
                    <div class="player-info">
                        <h3 class="player-name">{p['display_name']}</h3>
                        <span class="player-username">@{p['username']}</span>
                    </div>
                    {status_badge}
                </div>
                <div class="stats-grid">{stats_html}</div>
                {last_updated}
                <div class="card-actions">
                    {report_btn}
                    {run_btn}
                </div>
            </div>"""
        return cards_html
        
    stack_player_cards = make_player_cards(stack_players)
    individual_player_cards = make_player_cards(individual_players)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Siege Coaching Portal | Stack Dashboard</title>
    <meta name="description" content="AI-powered Rainbow Six Siege tactical coaching portal for your competitive stack.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0b0f;
            --bg-secondary: #12141a;
            --bg-card: #1a1d26;
            --bg-card-hover: #1f2330;
            --border: #2a2d3a;
            --border-glow: #4a90e2;
            --primary: #4a90e2;
            --primary-dark: #3578c8;
            --accent: #f59e0b;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-purple: #8b5cf6;
            --text-primary: #f0f2ff;
            --text-secondary: #8892b0;
            --text-muted: #5a6480;
            --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-hero: linear-gradient(135deg, #0a0b0f 0%, #1a1d3a 50%, #0d1117 100%);
            --shadow-glow: 0 0 40px rgba(74, 144, 226, 0.15);
            --radius: 16px;
            --radius-sm: 8px;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* ── Hero ── */
        .hero {{
            background: var(--gradient-hero);
            border-bottom: 1px solid var(--border);
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        .hero::before {{
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at 50% 0%, rgba(74, 144, 226, 0.12) 0%, transparent 70%);
            pointer-events: none;
        }}
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(74, 144, 226, 0.1);
            border: 1px solid rgba(74, 144, 226, 0.3);
            border-radius: 999px;
            padding: 6px 16px;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--primary);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }}
        .hero-badge::before {{
            content: '';
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(0.8); }}
        }}
        .hero h1 {{
            font-family: 'Orbitron', monospace;
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 900;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 0%, #a0b4e0 50%, #4a90e2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.75rem;
        }}
        .hero-subtitle {{
            color: var(--text-secondary);
            font-size: 1.05rem;
            font-weight: 400;
            max-width: 480px;
            margin: 0 auto 2rem;
            line-height: 1.6;
        }}
        .hero-actions {{
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}

        /* ── Layout ── */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        .section {{
            padding: 3rem 0;
        }}
        .section-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 2rem;
        }}
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-primary);
        }}
        .section-line {{
            flex: 1;
            height: 1px;
            background: var(--border);
        }}

        /* ── Cards Grid ── */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
        }}
        .player-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }}
        .player-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--primary), var(--accent-purple));
            opacity: 0;
            transition: opacity 0.25s;
        }}
        .player-card:hover {{
            background: var(--bg-card-hover);
            border-color: rgba(74, 144, 226, 0.4);
            transform: translateY(-3px);
            box-shadow: var(--shadow-glow);
        }}
        .player-card:hover::before {{ opacity: 1; }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.25rem;
        }}
        .player-avatar {{
            width: 52px; height: 52px;
            border-radius: 12px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent-purple) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Orbitron', monospace;
            font-weight: 900;
            font-size: 1.1rem;
            color: white;
            flex-shrink: 0;
        }}
        .player-info {{ flex: 1; min-width: 0; }}
        .player-name {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .player-username {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 400;
        }}

        /* ── Badge ── */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            white-space: nowrap;
        }}
        .badge-ready {{
            background: rgba(16, 185, 129, 0.12);
            color: var(--accent-green);
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}
        .badge-pending {{
            background: rgba(245, 158, 11, 0.1);
            color: var(--accent);
            border: 1px solid rgba(245, 158, 11, 0.25);
        }}

        /* ── Stats ── */
        .stats-grid {{
            display: grid;
            gap: 8px;
            margin-bottom: 1rem;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: var(--bg-secondary);
            border-radius: var(--radius-sm);
            border: 1px solid var(--border);
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            font-weight: 500;
        }}
        .stat-value {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--primary);
            font-variant-numeric: tabular-nums;
        }}
        .rank-value {{ color: var(--accent); font-size: 0.8rem; }}

        /* ── Last Updated ── */
        .last-updated {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            text-align: right;
        }}

        /* ── Buttons ── */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 0.875rem;
            font-weight: 600;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        }}
        .btn-primary:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(74, 144, 226, 0.45);
        }}
        .btn-secondary {{
            background: rgba(255,255,255,0.05);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }}
        .btn-secondary:hover {{
            background: rgba(255,255,255,0.08);
            color: var(--text-primary);
            border-color: var(--border-glow);
        }}
        .btn-accent {{
            background: linear-gradient(135deg, var(--accent) 0%, #d97706 100%);
            color: #000;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }}
        .btn-accent:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.45);
        }}
        .card-actions {{
            display: flex;
            gap: 10px;
        }}
        .card-actions .btn {{ flex: 1; }}

        /* ── API Info ── */
        .api-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 1rem;
        }}
        .api-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 1.25rem;
            text-decoration: none;
            display: block;
            transition: all 0.2s ease;
        }}
        .api-card:hover {{
            border-color: rgba(74, 144, 226, 0.4);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .api-method {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
            background: rgba(74, 144, 226, 0.15);
            color: var(--primary);
            margin-bottom: 6px;
            font-family: monospace;
        }}
        .api-path {{
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-primary);
            display: block;
            margin-bottom: 4px;
        }}
        .api-desc {{
            font-size: 0.78rem;
            color: var(--text-secondary);
        }}

        /* ── Footer ── */
        .footer {{
            border-top: 1px solid var(--border);
            padding: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.8rem;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}

        /* ── Status indicator ── */
        .status-bar {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 10px 2rem;
            display: flex;
            align-items: center;
            gap: 1.5rem;
            font-size: 0.78rem;
            color: var(--text-muted);
            overflow-x: auto;
        }}
        .status-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}
        .dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
        }}
        .dot-green {{ background: var(--accent-green); box-shadow: 0 0 6px var(--accent-green); }}
        .dot-red {{ background: var(--accent-red); }}
    </style>
</head>
<body>
    <div class="status-bar">
        <div class="status-item">
            <div class="dot dot-green"></div>
            <span>API Online</span>
        </div>
        <div class="status-item">
            <div class="dot {'dot-green' if ENV.get('R6DATA_API_KEY') else 'dot-red'}"></div>
            <span>R6Data {"Connected" if ENV.get('R6DATA_API_KEY') else "Not configured"}</span>
        </div>
        <div class="status-item">
            <div class="dot {'dot-green' if ENV.get('GEMINI_API_KEY') else 'dot-red'}"></div>
            <span>Gemini AI {"Connected" if ENV.get('GEMINI_API_KEY') else "Not configured"}</span>
        </div>
        <div class="status-item" style="margin-left: auto;">
            <span>Stack: {' · '.join(m['username'] for m in STACK_MEMBERS)}</span>
        </div>
    </div>

    <div class="hero">
        <div class="hero-badge">🎯 Rainbow Six Siege — Y11S1</div>
        <h1>SIEGE COACHING<br>PORTAL</h1>
        <p class="hero-subtitle">AI-powered tactical analysis for your competitive stack. Real data, real coaching.</p>
        <div class="hero-actions">
            <a href="/sensitivity" class="btn btn-primary">🎯 Sensitivity Scaler</a>
            <a href="/api/stack" class="btn btn-accent" target="_blank">🤝 Stack Analysis</a>
            <a href="/docs" class="btn btn-secondary" target="_blank">📖 API Docs</a>
        </div>
    </div>

    <div class="container">
        <div class="section">
            <div class="section-header">
                <span class="section-title">Active Trio Stack (Y11S1 Scope)</span>
                <div class="section-line"></div>
                <span style="font-size:0.8rem;color:var(--text-muted)">{len(stack_players)} players</span>
            </div>
            <div class="cards-grid">
                {stack_player_cards}
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <span class="section-title">Individual Audits (Lifetime Scope)</span>
                <div class="section-line"></div>
                <span style="font-size:0.8rem;color:var(--text-muted)">{len(individual_players)} player</span>
            </div>
            <div class="cards-grid">
                {individual_player_cards}
            </div>
        </div>

        <div class="section">
            <div class="section-header">
                <span class="section-title">API Endpoints</span>
                <div class="section-line"></div>
            </div>
            <div class="api-grid">
                <a class="api-card" href="/api/players" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/api/players</span>
                    <p class="api-desc">List all stack members with report status and stats</p>
                </a>
                <a class="api-card" href="/api/coach?username=Amlenk" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/api/coach?username=Amlenk</span>
                    <p class="api-desc">Run pipeline for a player (Example: Amlenk)</p>
                </a>
                <a class="api-card" href="/api/report/Amlenk" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/api/report/{{username}}</span>
                    <p class="api-desc">Serve cached HTML report (Example: Amlenk)</p>
                </a>
                <a class="api-card" href="/api/stack" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/api/stack</span>
                    <p class="api-desc">AI-powered team stack analysis and role assignments</p>
                </a>
                <a class="api-card" href="/sensitivity" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/sensitivity</span>
                    <p class="api-desc">Interactive Sensitivity & ADS Focal-Scaling Dashboard</p>
                </a>
                <a class="api-card" href="/api/status" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/api/status</span>
                    <p class="api-desc">Health check and configuration status</p>
                </a>
                <a class="api-card" href="/docs" target="_blank">
                    <span class="api-method">GET</span>
                    <span class="api-path">/docs</span>
                    <p class="api-desc">FastAPI Swagger Interactive Documentation</p>
                </a>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Siege Coaching Portal v2.0 &nbsp;·&nbsp; Powered by <a href="https://r6data.com" target="_blank">R6Data API</a> &amp; <a href="https://deepmind.google/technologies/gemini/" target="_blank">Gemini AI</a></p>
    </div>

    <script>
        function switchCardTab(btn, tabType) {{
            const card = btn.closest('.player-card');
            
            // Toggle active button style
            card.querySelectorAll('.tab-btn').forEach(b => {{
                b.classList.remove('active');
                b.style.background = 'transparent';
                b.style.color = 'var(--text-secondary)';
                b.style.boxShadow = 'none';
                b.style.border = 'none';
            }});
            
            btn.classList.add('active');
            btn.style.background = 'var(--bg-card)';
            btn.style.color = 'var(--primary)';
            btn.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
            btn.style.border = '1px solid rgba(74, 144, 226, 0.15)';
            
            // Toggle visible stats group
            if (tabType === 'overall') {{
                card.querySelector('.stats-overall').style.display = 'grid';
                card.querySelector('.stats-y11s1').style.display = 'none';
            }} else {{
                card.querySelector('.stats-overall').style.display = 'none';
                card.querySelector('.stats-y11s1').style.display = 'grid';
            }}
        }}
    </script>
</body>
</html>"""
    return HTMLResponse(content=html)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    members_str = " · ".join(m["username"] for m in STACK_MEMBERS)
    print(rf"""
   _____ ___ ___  ____ _____    ____  ___  ____  _____ _   _  ____
  / ___||_ _| __|/ ___| ____|  |  _ \/ _ \|  _ \|_   _| | | |/ ___|
  \___ \ | || |_ | |  |  _|    | |_) | | | | |_) | | | | |_| | |
   ___) || ||  _|| |__| |___   |  __/| |_| |  _ <  | | |  _  | |___
  |____/|___|_|   \____|_____|  |_|    \___/|_| \_\ |_| |_| |_|\____|

        Siege Coaching Portal API v2.0
        Stack: {members_str}
    """)
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
