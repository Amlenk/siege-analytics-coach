"""
r6data_fetch.py — Primary data fetcher using r6data.com REST API.
Replaces the slow Selenium scraper for player stats, operator stats,
and seasonal rank data.
Uses Selenium for map data (tracker.gg maps page) since no API
endpoint provides per-map stats.
"""
import os
import json
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://api.r6data.com"

def load_env():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

def get_rank_name(rp):
    """Convert rank points to a human-readable rank name."""
    if rp is None:
        return "UNRANKED"
    rp = int(rp)
    if rp >= 5000:
        return "CHAMPION"
    
    tiers = ["COPPER", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND"]
    if rp < 1000:
        div = 5 - (rp // 100)
        div = max(1, min(5, div))
        return f"COPPER {div}"
    
    tier_idx = (rp - 1000) // 500
    if tier_idx >= len(tiers):
        tier_idx = len(tiers) - 1
    
    tier_name = tiers[tier_idx]
    tier_base = 1000 + tier_idx * 500
    div = 5 - ((rp - tier_base) // 100)
    div = max(1, min(5, div))
    return f"{tier_name} {div}"

class R6DataClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"api-key": api_key}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get(self, endpoint, params=None, retries=3):
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(retries):
            try:
                resp = self.session.get(url, params=params, timeout=30)
                if resp.status_code == 429:
                    wait = 2 ** attempt
                    print(f"  [Rate limited] Waiting {wait}s...")
                    time.sleep(wait)
                    continue
                if resp.status_code == 200:
                    return resp.json()
                else:
                    print(f"  [HTTP {resp.status_code}] {url} -> {resp.text[:200]}")
                    return None
            except requests.exceptions.Timeout:
                print(f"  [Timeout] Attempt {attempt+1}/{retries}: {url}")
                time.sleep(2)
            except Exception as e:
                print(f"  [Error] {e}")
                return None
        return None

    def get_account_info(self, username, platform="uplay"):
        """Get account info (profile + rank)."""
        print(f"  -> Fetching account info for {username}...")
        return self._get("/api/stats", params={
            "type": "accountInfo",
            "nameOnPlatform": username,
            "platformType": platform
        })

    def get_player_stats(self, username, platform="uplay"):
        """Get overall player stats (lifetime)."""
        print(f"  -> Fetching lifetime stats for {username}...")
        platform_family = "pc" if platform in ["uplay", "ubi", "steam"] else "console"
        return self._get("/api/stats", params={
            "type": "stats",
            "nameOnPlatform": username,
            "platformType": platform,
            "platform_families": platform_family
        })

    def get_operator_stats(self, username, platform="uplay", season_year=None, modes="ranked"):
        """Get operator stats, optionally filtered by season and mode."""
        params = {
            "type": "operatorStats",
            "nameOnPlatform": username,
            "platformType": platform,
            "modes": modes
        }
        if season_year:
            params["seasonYear"] = season_year
        label = f"operator stats ({season_year or 'latest'}, {modes})"
        print(f"  -> Fetching {label} for {username}...")
        return self._get("/api/stats", params=params)

    def get_seasonal_stats(self, username, platform="uplay"):
        """Get current season rank history."""
        print(f"  -> Fetching seasonal rank history for {username}...")
        return self._get("/api/stats", params={
            "type": "seasonalStats",
            "nameOnPlatform": username,
            "platformType": platform
        })

    def get_seasons_history(self, username, platform="uplay"):
        """Get all-seasons rank history."""
        print(f"  -> Fetching all-seasons history for {username}...")
        return self._get("/api/stats", params={
            "type": "seasonsStats",
            "nameOnPlatform": username,
            "platformType": platform
        })

    def get_is_banned(self, username, platform="uplay"):
        """Check if player is banned."""
        return self._get("/api/stats", params={
            "type": "isBanned",
            "nameOnPlatform": username,
            "platformType": platform
        })


def _create_driver():
    """Create a headless Chrome driver for scraping tracker.gg maps."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _scrape_page_text(url):
    """Load a page with Selenium and return the body text."""
    driver = None
    try:
        driver = _create_driver()
        driver.get(url)
        try:
            driver.execute_script("""
                var el = document.getElementById('ncmp__tool');
                if (el) { el.remove(); }
                var normalisers = document.getElementsByClassName('ncmp__normalise');
                for (var i=0; i < normalisers.length; i++) { normalisers[i].remove(); }
            """)
        except Exception:
            pass
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "v3-tabs__item"))
        )
        time.sleep(5)
        return driver.find_element(By.TAG_NAME, "body").text
    finally:
        if driver:
            driver.quit()


def _parse_maps_text(text):
    """Parse the tracker.gg maps table text into structured map data."""
    maps_list = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    header_idx = -1
    for idx in range(len(lines) - 5):
        if lines[idx] == "Map" and lines[idx+1] == "Matches" and lines[idx+2] == "Win %":
            header_idx = idx
            break

    if header_idx != -1:
        cols_count = 10
        data_start = header_idx + cols_count

        i = data_start
        while i <= len(lines) - cols_count:
            try:
                map_name = lines[i]
                matches = int(lines[i+1].replace(",", ""))
                win_rate = lines[i+2]
                wins = int(lines[i+3].replace(",", ""))
                losses = int(lines[i+4].replace(",", ""))
                kd_ratio = float(lines[i+5])
                atk_win_rate = lines[i+6]
                def_win_rate = lines[i+7]
                hs_pct = lines[i+8]
                esr = float(lines[i+9])

                if map_name.lower() == "yacht":
                    i += cols_count
                    continue

                if not map_name.replace(".", "").isdigit() and "%" in win_rate:
                    maps_list.append({
                        "name": map_name,
                        "matches": matches,
                        "win_rate": win_rate,
                        "wins": wins,
                        "losses": losses,
                        "kd_ratio": kd_ratio,
                        "attack_win_rate": atk_win_rate,
                        "defense_win_rate": def_win_rate,
                        "headshot_percentage": hs_pct,
                        "esr": esr
                    })
                    i += cols_count
                    continue
            except Exception:
                pass
            i += 1
    return maps_list


def scrape_maps_for_player(username, platform="ubi", season_id=41):
    """
    Scrape map stats from tracker.gg for a player.
    Returns (lifetime_ranked_maps, seasonal_ranked_maps) tuple.
    Both use gamemode=pvp_ranked to get ranked-only data.
    """
    tracker_platform = "ubi" if platform in ["uplay", "ubi", "uplayconnect", "pc", "uplay_pc"] else platform
    base_maps_url = f"https://r6.tracker.network/r6siege/profile/{tracker_platform}/{username}/maps"

    # Scrape Lifetime Ranked maps
    lifetime_url = f"{base_maps_url}?gamemode=pvp_ranked"
    print(f"  -> Scraping lifetime ranked maps: {lifetime_url}")
    try:
        lt_text = _scrape_page_text(lifetime_url)
        lifetime_maps = _parse_maps_text(lt_text)
        print(f"     Parsed {len(lifetime_maps)} lifetime ranked maps.")
    except Exception as e:
        print(f"     [Error] Lifetime maps scrape failed: {e}")
        lifetime_maps = []

    # Scrape Seasonal Ranked maps (Y11S1)
    seasonal_url = f"{base_maps_url}?season={season_id}&gamemode=pvp_ranked"
    print(f"  -> Scraping Y11S1 ranked maps: {seasonal_url}")
    try:
        s_text = _scrape_page_text(seasonal_url)
        seasonal_maps = _parse_maps_text(s_text)
        print(f"     Parsed {len(seasonal_maps)} Y11S1 ranked maps.")
    except Exception as e:
        print(f"     [Error] Seasonal maps scrape failed: {e}")
        seasonal_maps = []

    return lifetime_maps, seasonal_maps


def parse_operator_stats_response(raw_resp):
    """
    Parse the r6data operatorStats response into the internal format
    used by stats.py and report.py.
    """
    if not raw_resp:
        return []
    
    # The response can be a list of operator objects directly, or nested
    operators_raw = []
    if isinstance(raw_resp, list):
        operators_raw = raw_resp
    elif isinstance(raw_resp, dict):
        # Try common response shapes
        if "operators" in raw_resp:
            operators_raw = raw_resp["operators"]
        elif "data" in raw_resp:
            data = raw_resp["data"]
            if isinstance(data, list):
                operators_raw = data
            elif isinstance(data, dict) and "operators" in data:
                operators_raw = data["operators"]
    
    parsed = []
    for op in operators_raw:
        if not isinstance(op, dict):
            continue
        name = op.get("operator", op.get("name", ""))
        if not name:
            continue
        rounds_played = int(op.get("roundsPlayed", op.get("rounds_played", 0)))
        wins = int(op.get("wins", 0))
        losses = int(op.get("losses", 0))
        kills = int(op.get("kills", 0))
        deaths = int(op.get("deaths", 0))
        
        # Win rate
        if "winPercent" in op:
            wr_raw = float(op["winPercent"])
            win_rate_str = f"{wr_raw:.1f}%"
        elif wins + losses > 0:
            wr_raw = (wins / (wins + losses)) * 100
            win_rate_str = f"{wr_raw:.1f}%"
        else:
            win_rate_str = "0.0%"

        # K/D
        kd = round(kills / max(deaths, 1), 2)
        
        # Headshot
        hs_pct_raw = op.get("headshotPercent", op.get("headshot_percentage", 0.0))
        if isinstance(hs_pct_raw, str) and '%' in hs_pct_raw:
            hs_str = hs_pct_raw
        else:
            hs_str = f"{float(hs_pct_raw):.1f}%"

        if rounds_played > 0:
            parsed.append({
                "name": name,
                "matches": rounds_played,
                "win_rate": win_rate_str,
                "kd_ratio": kd,
                "kills": kills,
                "deaths": deaths,
                "wins": wins,
                "losses": losses,
                "headshot_percentage": hs_str,
                "side": op.get("side", "")
            })

    return parsed


def parse_account_stats_response(raw_resp, username, platform, ranked_rating="UNRANKED"):
    """
    Parse accountInfo + stats response into the internal summary format.
    Returns a dict compatible with full_stats.json entry format.
    """
    if not raw_resp:
        return None
    
    # accountInfo response structure varies — extract what we can
    # It may be a list (profile array) or dict
    profile = None
    if isinstance(raw_resp, list) and raw_resp:
        profile = raw_resp[0]
    elif isinstance(raw_resp, dict):
        profile = raw_resp
    
    if not profile:
        return None

    # Extract key fields with sensible defaults
    level = profile.get("level", profile.get("clearanceLevel", 0))
    
    # Stats are sometimes nested under "statistics" or flat
    stats = profile.get("statistics", profile.get("stats", profile))
    
    overall_kd = float(stats.get("kd", stats.get("kdRatio", 1.0)))
    win_rate_raw = stats.get("winPercent", stats.get("winRate", stats.get("win_rate", 50.0)))
    if isinstance(win_rate_raw, str) and '%' in win_rate_raw:
        win_rate_str = win_rate_raw
    else:
        win_rate_str = f"{float(win_rate_raw):.1f}%"
    
    hs_pct_raw = stats.get("headshotPct", stats.get("headshot_pct", 50.0))
    if isinstance(hs_pct_raw, str) and '%' in hs_pct_raw:
        hs_str = hs_pct_raw
    else:
        hs_str = f"{float(hs_pct_raw):.1f}%"
    
    matches = int(stats.get("matchesPlayed", stats.get("matches_played", 0)))
    kills = int(stats.get("kills", 0))
    deaths = int(stats.get("deaths", 0))
    wins = int(stats.get("matchesWon", stats.get("wins", 0)))
    losses = int(stats.get("matchesLost", stats.get("losses", 0)))
    
    return {
        "username": username,
        "platform": platform,
        "overall_kd": overall_kd,
        "win_rate": win_rate_str,
        "headshot_pct": hs_str,
        "ranked_rating": ranked_rating,
        "lifetime_overall": {
            "level": level,
            "matches": matches,
            "time_played": "N/A",
            "win_rate": win_rate_str,
            "kd_ratio": overall_kd,
            "headshot_percentage": hs_str,
            "wins": wins,
            "losses": losses,
            "kills": kills,
            "deaths": deaths
        }
    }


def main():
    import sys
    env = load_env()
    api_key = env.get('R6DATA_API_KEY', '')
    username = env.get('UBISOFT_USERNAME', 'Amlenk')
    platform = env.get('UBISOFT_PLATFORM', 'uplay')

    if not api_key:
        print("[Error] R6DATA_API_KEY not found in .env. Exiting.")
        return

    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    if len(sys.argv) > 2:
        platform = sys.argv[2].strip()

    # Normalise platform
    if platform in ['uplayconnect', 'pc', 'uplay_pc', 'ubi']:
        platform = 'uplay'

    print(f"\n{'='*50}")
    print(f"R6DATA API FETCH: {username} ({platform.upper()})")
    print(f"{'='*50}\n")

    client = R6DataClient(api_key)

    # --- Step 1: Account info ---
    account_raw = client.get_account_info(username, platform)
    
    # --- Step 2: Seasonal rank history (to get rank points) ---
    seasonal_raw = client.get_seasonal_stats(username, platform)
    
    # --- Step 3: Seasons rank history (to get accurate lifetime & seasonal stats) ---
    print(f"  -> Fetching seasons stats history...")
    seasons_history_raw = client.get_seasons_history(username, platform)
    
    # --- Step 4: Lifetime and Y11S1 Operator stats ---
    print(f"  -> Fetching lifetime operator stats...")
    ops_lifetime_raw = client.get_operator_stats(username, platform, season_year=None, modes="ranked")
    print(f"  -> Fetching Y11S1 seasonal operator stats...")
    ops_seasonal_raw = client.get_operator_stats(username, platform, season_year="Y11S1", modes="ranked")

    # ---- Parse rank points from seasonal stats ----
    ranked_rating = "UNRANKED"
    try:
        if seasonal_raw:
            if isinstance(seasonal_raw, dict):
                data = seasonal_raw.get("data", seasonal_raw)
                if isinstance(data, dict):
                    history = data.get("history", {})
                    if isinstance(history, dict):
                        history_entries = history.get("data", [])
                        if history_entries:
                            last_entry = history_entries[0]
                            if isinstance(last_entry, list) and len(last_entry) > 1:
                                rp_info = last_entry[1]
                                rp_val = int(rp_info.get("value", 0))
                                rank_name = rp_info.get("metadata", {}).get("rank", get_rank_name(rp_val))
                                ranked_rating = f"{rp_val:,} RP ({rank_name})"
        
        # Fallback to seasons_history_raw for current season 41 (Y11S1) if not parsed
        if ranked_rating == "UNRANKED" and seasons_history_raw:
            segments = []
            if isinstance(seasons_history_raw, dict):
                segments = seasons_history_raw.get("data", {}).get("segments", [])
            elif isinstance(seasons_history_raw, list):
                segments = seasons_history_raw
            
            for s in segments:
                attr = s.get("attributes", {})
                if attr.get("gamemode") == "pvp_ranked" and attr.get("season") == 41:
                    rp_val = int(s.get("stats", {}).get("rankPoints", {}).get("value", 0))
                    if rp_val > 0:
                        ranked_rating = f"{rp_val:,} RP ({get_rank_name(rp_val)})"
                        break
    except Exception as e:
        print(f"  [Warning] Could not parse ranked rating: {e}")

    # ---- Parse accurate lifetime and seasonal ranked stats from seasonsStats ----
    lifetime_kd = 1.0
    lifetime_wr_str = "50.0%"
    lifetime_hs_pct = "50.0%"
    lifetime_wins = 0
    lifetime_losses = 0
    lifetime_kills = 0
    lifetime_deaths = 0
    lifetime_matches = 0

    seasonal_kd = 1.0
    seasonal_wr_str = "50.0%"
    seasonal_hs_pct = "50.0%"
    seasonal_wins = 0
    seasonal_losses = 0
    seasonal_kills = 0
    seasonal_deaths = 0
    seasonal_matches = 0

    if seasons_history_raw:
        segments = []
        if isinstance(seasons_history_raw, dict):
            segments = seasons_history_raw.get("data", {}).get("segments", [])
        elif isinstance(seasons_history_raw, list):
            segments = seasons_history_raw

        lifetime_ranked_stats = {}
        seasonal_ranked_stats = {}

        for s in segments:
            attr = s.get("attributes", {})
            if attr.get("gamemode") == "pvp_ranked":
                # Lifetime ranked segment: season is None
                if attr.get("season") is None:
                    lifetime_ranked_stats = s.get("stats", {})
                # Seasonal ranked segment: season 41 or metadata shortName is Y11S1
                elif attr.get("season") == 41 or s.get("metadata", {}).get("shortName") == "Y11S1":
                    seasonal_ranked_stats = s.get("stats", {})

        # Fallback to highest season if Y11S1 not explicitly tagged
        if not seasonal_ranked_stats:
            ranked_seasons = [s for s in segments if s.get("attributes", {}).get("gamemode") == "pvp_ranked" and s.get("attributes", {}).get("season") is not None]
            if ranked_seasons:
                max_season_seg = max(ranked_seasons, key=lambda x: x.get("attributes", {}).get("season", 0))
                seasonal_ranked_stats = max_season_seg.get("stats", {})
                print(f"  [Fallback] Found highest ranked season: {max_season_seg.get('attributes', {}).get('season')} ({max_season_seg.get('metadata', {}).get('name')})")

        # Parse Lifetime stats
        if lifetime_ranked_stats:
            lifetime_kd = float(lifetime_ranked_stats.get("kdRatio", {}).get("value", 1.0))
            lifetime_hs_pct = lifetime_ranked_stats.get("headshotPct", {}).get("displayValue", "50.0%")
            lifetime_wins = int(lifetime_ranked_stats.get("matchesWon", {}).get("value", 0))
            lifetime_losses = int(lifetime_ranked_stats.get("matchesLost", {}).get("value", 0))
            lifetime_kills = int(lifetime_ranked_stats.get("kills", {}).get("value", 0))
            lifetime_deaths = int(lifetime_ranked_stats.get("deaths", {}).get("value", 0))
            lifetime_matches = int(lifetime_ranked_stats.get("matchesPlayed", {}).get("value", 0))
            # Calculate win rate programmatically
            lifetime_wr_str = f"{(lifetime_wins / max(lifetime_matches, 1)) * 100:.1f}%"
            print(f"  Parsed Lifetime Ranked Stats: matches={lifetime_matches}, kd={lifetime_kd}, win_rate={lifetime_wr_str}")

        # Parse Seasonal stats
        if seasonal_ranked_stats:
            seasonal_kd = float(seasonal_ranked_stats.get("kdRatio", {}).get("value", 1.0))
            seasonal_hs_pct = seasonal_ranked_stats.get("headshotPct", {}).get("displayValue", "50.0%")
            seasonal_wins = int(seasonal_ranked_stats.get("matchesWon", {}).get("value", 0))
            seasonal_losses = int(seasonal_ranked_stats.get("matchesLost", {}).get("value", 0))
            seasonal_kills = int(seasonal_ranked_stats.get("kills", {}).get("value", 0))
            seasonal_deaths = int(seasonal_ranked_stats.get("deaths", {}).get("value", 0))
            seasonal_matches = int(seasonal_ranked_stats.get("matchesPlayed", {}).get("value", 0))
            # Calculate win rate programmatically
            seasonal_wr_str = f"{(seasonal_wins / max(seasonal_matches, 1)) * 100:.1f}%"
            print(f"  Parsed Y11S1 Seasonal Ranked Stats: matches={seasonal_matches}, kd={seasonal_kd}, win_rate={seasonal_wr_str}")

    # ---- Parse operators stats ----
    ops_lifetime_parsed = []
    if ops_lifetime_raw:
        ops_lifetime_parsed = parse_operator_stats_response(ops_lifetime_raw)
        print(f"  Parsed {len(ops_lifetime_parsed)} lifetime operators.")
    
    if len(ops_lifetime_parsed) < 3:
        print("  [Fallback] Operator count too low, fetching unfiltered lifetime operators...")
        ops_all_raw = client.get_operator_stats(username, platform, season_year=None, modes="all")
        if ops_all_raw:
            ops_lifetime_parsed = parse_operator_stats_response(ops_all_raw)
            print(f"  Parsed {len(ops_lifetime_parsed)} lifetime operators (fallback).")

    ops_seasonal_parsed = []
    if ops_seasonal_raw:
        ops_seasonal_parsed = parse_operator_stats_response(ops_seasonal_raw)
        print(f"  Parsed {len(ops_seasonal_parsed)} seasonal operators.")
    
    if len(ops_seasonal_parsed) < 3:
        print("  [Fallback] Operator count too low, fetching unfiltered seasonal operators...")
        ops_seasonal_all_raw = client.get_operator_stats(username, platform, season_year="Y11S1", modes="all")
        if ops_seasonal_all_raw:
            ops_seasonal_parsed = parse_operator_stats_response(ops_seasonal_all_raw)
            print(f"  Parsed {len(ops_seasonal_parsed)} seasonal operators (fallback).")

    # Extract clearance level from account_raw
    level = 0
    if account_raw:
        acc_dict = account_raw if isinstance(account_raw, dict) else {}
        level = acc_dict.get("level", acc_dict.get("clearanceLevel", acc_dict.get("profile", {}).get("level", 0)))

    # ---- Scrape maps from tracker.gg (ranked-only, per scope) ----
    print(f"\n  Scraping map stats from tracker.gg for {username}...")
    lifetime_maps, seasonal_maps = scrape_maps_for_player(username, platform, season_id=41)

    # Save player-specific map files
    os.makedirs('data/raw', exist_ok=True)
    with open(f'data/raw/{username}_maps.json', 'w', encoding='utf-8') as f:
        json.dump(lifetime_maps, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_y11s1_maps.json', 'w', encoding='utf-8') as f:
        json.dump(seasonal_maps, f, indent=2, ensure_ascii=False)
    print(f"  Saved lifetime ranked maps -> data/raw/{username}_maps.json ({len(lifetime_maps)} maps)")
    print(f"  Saved Y11S1 ranked maps   -> data/raw/{username}_y11s1_maps.json ({len(seasonal_maps)} maps)")

    # ---- Build lifetime summary ----
    lifetime_entry = {
        "username": username,
        "platform": platform,
        "overall_kd": lifetime_kd,
        "win_rate": lifetime_wr_str,
        "headshot_pct": lifetime_hs_pct,
        "ranked_rating": ranked_rating,
        "lifetime_overall": {
            "level": level,
            "matches": lifetime_matches,
            "time_played": "N/A",
            "win_rate": lifetime_wr_str,
            "kd_ratio": lifetime_kd,
            "headshot_percentage": lifetime_hs_pct,
            "wins": lifetime_wins,
            "losses": lifetime_losses,
            "kills": lifetime_kills,
            "deaths": lifetime_deaths
        },
        "operators": ops_lifetime_parsed,
        "maps": lifetime_maps
    }

    # ---- Build y11s1 entry using seasonal stats and operators ----
    y11s1_entry = {
        "username": username,
        "platform": platform,
        "season": "Y11S1",
        "overall_kd": seasonal_kd,
        "win_rate": seasonal_wr_str,
        "headshot_pct": seasonal_hs_pct,
        "ranked_rating": ranked_rating,
        "lifetime_overall": {
            "level": level,
            "matches": seasonal_matches,
            "time_played": "N/A",
            "win_rate": seasonal_wr_str,
            "kd_ratio": seasonal_kd,
            "headshot_percentage": seasonal_hs_pct,
            "wins": seasonal_wins,
            "losses": seasonal_losses,
            "kills": seasonal_kills,
            "deaths": seasonal_deaths
        },
        "operators": ops_seasonal_parsed,
        "maps": seasonal_maps
    }

    # ---- Tag scopes ----
    lifetime_entry["scope"] = "lifetime"
    y11s1_entry["scope"] = "y11s1"

    # ---- Save raw outputs (both player-segregated and default fallback) ----
    os.makedirs('data/raw', exist_ok=True)
    
    with open('data/raw/r6data_account_raw.json', 'w', encoding='utf-8') as f:
        json.dump({"account": account_raw, "seasonal": seasonal_raw}, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_r6data_account_raw.json', 'w', encoding='utf-8') as f:
        json.dump({"account": account_raw, "seasonal": seasonal_raw}, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved raw account data to data/raw/{username}_r6data_account_raw.json")
    
    with open('data/raw/r6data_ops_raw.json', 'w', encoding='utf-8') as f:
        json.dump(ops_seasonal_raw, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_r6data_ops_raw.json', 'w', encoding='utf-8') as f:
        json.dump(ops_seasonal_raw, f, indent=2, ensure_ascii=False)
    print(f"  Saved raw operator data to data/raw/{username}_r6data_ops_raw.json")

    with open('data/raw/seasons_history.json', 'w', encoding='utf-8') as f:
        json.dump(seasons_history_raw, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_seasons_history.json', 'w', encoding='utf-8') as f:
        json.dump(seasons_history_raw, f, indent=2, ensure_ascii=False)
    print(f"  Saved raw seasons history to data/raw/{username}_seasons_history.json")

    full_stats = [lifetime_entry, y11s1_entry]
    with open('data/raw/full_stats.json', 'w', encoding='utf-8') as f:
        json.dump(full_stats, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_full_stats.json', 'w', encoding='utf-8') as f:
        json.dump(full_stats, f, indent=2, ensure_ascii=False)
    print(f"  Saved merged stats to data/raw/{username}_full_stats.json")

    # Save standardized dict formats for api compliance
    full_stats_api = {
        "lifetime": lifetime_entry,
        "y11s1": y11s1_entry
    }
    with open('data/raw/full_stats_api.json', 'w', encoding='utf-8') as f:
        json.dump(full_stats_api, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_full_stats_api.json', 'w', encoding='utf-8') as f:
        json.dump(full_stats_api, f, indent=2, ensure_ascii=False)
    print(f"  Saved standardized API stats to data/raw/{username}_full_stats_api.json")

    with open('data/raw/stats.json', 'w', encoding='utf-8') as f:
        json.dump(lifetime_entry, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_stats.json', 'w', encoding='utf-8') as f:
        json.dump(lifetime_entry, f, indent=2, ensure_ascii=False)
    print(f"  Saved lifetime stats to data/raw/{username}_stats.json")

    with open('data/raw/y11s1_stats.json', 'w', encoding='utf-8') as f:
        json.dump(y11s1_entry, f, indent=2, ensure_ascii=False)
    with open(f'data/raw/{username}_y11s1_stats.json', 'w', encoding='utf-8') as f:
        json.dump(y11s1_entry, f, indent=2, ensure_ascii=False)
    print(f"  Saved Y11S1 stats to data/raw/{username}_y11s1_stats.json")

    print(f"\n{'='*50}")
    print(f"R6DATA FETCH SUMMARY: {username}")
    print(f"  Ranked Rating:  {ranked_rating}")
    print(f"  Lifetime K/D:   {lifetime_entry['overall_kd']}")
    print(f"  Lifetime WR:    {lifetime_entry['win_rate']}")
    print(f"  Seasonal K/D:   {y11s1_entry['overall_kd']}")
    print(f"  Seasonal WR:    {y11s1_entry['win_rate']}")
    print(f"  Operators:      {len(ops_seasonal_parsed)} (seasonal), {len(ops_lifetime_parsed)} (lifetime)")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
