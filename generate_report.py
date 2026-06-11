import os
import sys
import subprocess
import time
import shutil
import re

def run_step(cmd, desc):
    print(f"\n==========================================")
    print(f"[*] [Pipeline Step] {desc}")
    print(f"Executing: {cmd}")
    print(f"==========================================")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True)
    duration = time.time() - start_time
    
    if result.returncode != 0:
        print(f"\n[Error] {desc} failed with exit code {result.returncode}! Pipeline aborted.")
        sys.exit(result.returncode)
    
    print(f"[+] Success: {desc} finished in {duration:.1f}s.")

def perform_compliance_check(username):
    print(f"\n==========================================")
    print(f"[*] PIPELINE COMPLIANCE VERIFICATION RUN FOR: {username}")
    print(f"==========================================")
    
    passed_rules = 0
    total_rules = 9
    
    # Define files and paths
    raw_path = os.path.join("data", "raw", "full_stats_api.json")
    processed_path = os.path.join("data", "stats_processed.json")
    report_path = os.path.join("output", "report.md")
    report_html_path = os.path.join("output", "report.html")
    
    charts_dir = os.path.join("output", "charts")
    charts = [
        "map_winrate_overview.png",
        "map_attack_vs_defence.png",
        "operator_quadrant.png",
        "attacker_kd.png",
        "defender_kd.png",
        "operator_winrate.png",
        "skill_radar.png",
        "map_ban_spectrum.png"
    ]
    
    # Rule 1: Verify data files exist
    print("[*] Rule 1: Verifying data files presence...")
    if os.path.exists(raw_path) and os.path.exists(processed_path):
        print(f"  [PASS] Found raw stats: {raw_path} ({os.path.getsize(raw_path)/1024:.1f} KB)")
        print(f"  [PASS] Found processed stats: {processed_path} ({os.path.getsize(processed_path)/1024:.1f} KB)")
        passed_rules += 1
    else:
        print("  [FAIL] Critical data files missing!")

    # Rule 2: Verify all 8 charts exist and are non-empty
    print("\n[*] Rule 2: Verifying presence and sizes of exactly 8 visual charts...")
    missing_charts = []
    charts_ok = True
    for c in charts:
        c_path = os.path.join(charts_dir, c)
        if os.path.exists(c_path) and os.path.getsize(c_path) > 0:
            print(f"  [PASS] {c} verified ({os.path.getsize(c_path)/1024:.1f} KB)")
        else:
            print(f"  [FAIL] {c} is missing or empty!")
            charts_ok = False
            missing_charts.append(c)
    if charts_ok:
        passed_rules += 1
    else:
        print(f"  [FAIL] The following charts failed validation: {missing_charts}")

    # Load report content for textual rules
    report_exists = os.path.exists(report_path)
    report_content = ""
    if report_exists:
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

    # Rule 3: Verify output report files exist
    print("\n[*] Rule 3: Verifying final reports presence...")
    if report_exists and os.path.exists(report_html_path):
        print(f"  [PASS] Found markdown report: {report_path} ({os.path.getsize(report_path)/1024:.1f} KB)")
        print(f"  [PASS] Found HTML report: {report_html_path} ({os.path.getsize(report_html_path)/1024:.1f} KB)")
        passed_rules += 1
    else:
        print("  [FAIL] Final reports are missing!")

    # Rule 4: Verify report contains all 8 sections
    print("\n[*] Rule 4: Checking for presence of exactly 8 coaching sections...")
    sections = [
        "SECTION 1: PERFORMANCE SNAPSHOT",
        "SECTION 2: TREND ANALYSIS",
        "SECTION 3: MAP MASTERY MATRIX",
        "SECTION 4: MAP DEEP DIVE",
        "SECTION 5: OPERATOR AUDIT",
        "SECTION 6: OPERATOR COACHING ENGINE",
        "SECTION 7: PRIORITY IMPROVEMENT MATRIX",
        "SECTION 8: BAN & VETO STRATEGY"
    ]
    sections_found = 0
    for sec in sections:
        if sec in report_content:
            sections_found += 1
            print(f"  [PASS] Found Section: {sec}")
        else:
            print(f"  [FAIL] Section not found: {sec}")
    if sections_found == 8:
        passed_rules += 1
    else:
        print(f"  [FAIL] Only found {sections_found}/8 required sections!")

    # Rule 5: Verify all 8 visual chart embeds are present in the markdown
    print("\n[*] Rule 5: Verifying all 8 visual chart references are embedded in markdown...")
    embeds = [
        "charts/skill_radar.png",
        "charts/map_winrate_overview.png",
        "charts/map_attack_vs_defence.png",
        "charts/operator_quadrant.png",
        "charts/operator_winrate.png",
        "charts/attacker_kd.png",
        "charts/defender_kd.png",
        "charts/map_ban_spectrum.png"
    ]
    embeds_found = 0
    for emb in embeds:
        if emb in report_content:
            embeds_found += 1
            print(f"  [PASS] Found embed link: {emb}")
        else:
            print(f"  [FAIL] Missing embed link: {emb}")
    if embeds_found == 8:
        passed_rules += 1
    else:
        print(f"  [FAIL] Only found {embeds_found}/8 required chart embeds!")

    # Rule 6: Absolute block list check (Ranked 2.0)
    print("\n[*] Rule 6: Verifying zero occurrences of blocklisted term 'Ranked 2.0'...")
    occurrences = report_content.lower().count("ranked 2.0")
    if occurrences == 0:
        print("  [PASS] Zero occurrences of 'Ranked 2.0' in the entire coaching report.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Found {occurrences} occurrences of 'Ranked 2.0'! Check compliance requirements.")

    # Rule 7: Rule out generic fluff - check that at least 50 numerical statistics are cited
    print("\n[*] Rule 7: Verifying statistical density (no generic fluff)...")
    numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', report_content)
    if len(numbers) >= 50:
        print(f"  [PASS] Statistical density verified. Cites at least {len(numbers)} numerical data points.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Statistical density too low ({len(numbers)} numbers). The report may contain generic fluff!")

    # Rule 8: Map Mastery Matrix map count check (must be exactly 19 competitive maps)
    print("\n[*] Rule 8: Checking competitive map count inside Section 3 matrix...")
    matrix_section = ""
    if "SECTION 3:" in report_content:
        parts = report_content.split("SECTION 3:")
        if len(parts) > 1:
            matrix_section = parts[1].split("SECTION 4:")[0]
            
    table_lines = [l for l in matrix_section.split("\n") if l.strip().startswith("|")]
    map_rows = 0
    for line in table_lines:
        if "Map" in line or "---" in line:
            continue
        map_rows += 1
    if map_rows == 19:
        print(f"  [PASS] Found exactly 19 competitive active Ranked maps in the mastery matrix.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Found {map_rows} maps in matrix instead of exactly 19 competitive maps!")

    # Rule 9: Priority Improvement Matrix row count check (must be exactly 5 rows)
    print("\n[*] Rule 9: Checking Priority Improvement Matrix row count...")
    matrix_section_7 = ""
    if "SECTION 7:" in report_content:
        parts = report_content.split("SECTION 7:")
        if len(parts) > 1:
            matrix_section_7 = parts[1].split("SECTION 8:")[0]
            
    table_lines_7 = [l for l in matrix_section_7.split("\n") if l.strip().startswith("|")]
    priority_rows = 0
    for line in table_lines_7:
        if "Focus Area" in line or "---" in line:
            continue
        priority_rows += 1
    if priority_rows == 5:
        print(f"  [PASS] Priority Improvement Matrix verified with exactly 5 strategic action items.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Priority matrix contains {priority_rows} action items instead of exactly 5!")

    # Summary
    print(f"\n==========================================")
    print(f"[*] COMPLIANCE SUMMARY REPORT FOR: {username}")
    print(f"==========================================")
    print(f"Total Rules Run: {total_rules}")
    print(f"Rules Passed:    {passed_rules}")
    print(f"Rules Failed:    {total_rules - passed_rules}")
    print(f"------------------------------------------")
    
    if passed_rules == total_rules:
        print(f"[SUCCESS] The pipeline outputs for {username} are 100% COMPLIANT and verified.")
        return True
    else:
        print(f"[WARNING] Pipeline outputs for {username} are NOT fully compliant. Review failures above.")
        return False

def copy_player_to_compliance_paths(username):
    print(f"\n[*] Copying generated outputs for {username} to global compliance paths...")
    
    # 1. Raw stats API JSON
    raw_player = os.path.join("data", "raw", f"{username}_full_stats_api.json")
    raw_player_fb = os.path.join("data", "raw", f"{username}_full_stats.json")
    raw_compliance = os.path.join("data", "raw", "full_stats_api.json")
    if os.path.exists(raw_player):
        shutil.copy(raw_player, raw_compliance)
    elif os.path.exists(raw_player_fb):
        shutil.copy(raw_player_fb, raw_compliance)
        
    # 2. Processed stats JSON
    proc_player = os.path.join("data", f"{username}_stats_processed.json")
    proc_compliance = os.path.join("data", "stats_processed.json")
    if os.path.exists(proc_player):
        shutil.copy(proc_player, proc_compliance)
        
    # 3. MD report
    md_player = os.path.join("output", f"{username}_report.md")
    md_compliance = os.path.join("output", "report.md")
    if os.path.exists(md_player):
        shutil.copy(md_player, md_compliance)
        
    # 4. HTML report
    html_player = os.path.join("output", f"{username}_report.html")
    html_compliance = os.path.join("output", "report.html")
    if os.path.exists(html_player):
        shutil.copy(html_player, html_compliance)
        
    # 5. Charts
    charts_player_dir = os.path.join("output", "charts", username)
    charts_compliance_dir = os.path.join("output", "charts")
    if os.path.exists(charts_player_dir):
        for f in os.listdir(charts_player_dir):
            if f.endswith(".png"):
                shutil.copy(os.path.join(charts_player_dir, f), os.path.join(charts_compliance_dir, f))
    print(f"[+] Copying completed for {username}.")

def run_single_player_pipeline(username, platform="ubi"):
    print(f"\n==========================================")
    print(f"[*] RUNNING PIPELINE FOR PLAYER: {username}")
    print(f"==========================================")
    
    # Step 1: Fetch fresh data from r6data API or fallback
    run_step(f"python r6data_fetch.py \"{username}\" \"{platform}\"", f"Fetching stats for {username} via API")
    if username == "WamaiDoingThis":
        run_step(f"python fetch_stats.py \"{username}\" \"{platform}\"", f"Fetching stats for {username} via Selenium Web Scraper")
    
    # Step 2: Stats calculations
    run_step(f"python stats.py \"{username}\"", f"Processing stats for {username}")
    
    # Step 3: Charts generation
    run_step(f"python charts.py \"{username}\"", f"Generating 8 premium charts for {username}")
    
    # Step 4: Report generation
    run_step(f"python report.py \"{username}\"", f"Compiling elite report and HTML dashboard for {username}")
    
    # Copy to compliance paths
    copy_player_to_compliance_paths(username)
    
    # Step 5: Verify compliance
    success = perform_compliance_check(username)
    return success

def main():
    print(r"""
    ___       _   _                             _ _           ___   ___  
   / _ \___ _| |_(_) __ _ _ __ __ ___   __(_) |_ _   _     / _ \ / _ \ 
  / /_)/ _ \__  | |/ _` | '__/ _` \ \ / / | __| | | | |   | | | | | | |
 / ___/  __// / | | (_| | | | (_| |\ V /| | |_| | |_| |   | |_| | |_| |
 \/    \___|\___|_|\__, |_|  \__,_| \_/ |_|\__|_|\__, |    \___/ \___/ 
                   |___/                         |___/                 
         Multi-Player Stack Tactical Coaching Orchestrator v3.0
    """)
    
    username_arg = "Amlenk"
    if len(sys.argv) > 1:
        username_arg = sys.argv[1].strip()
        
    scope_arg = None
    if len(sys.argv) > 2:
        scope_arg = sys.argv[2].strip().lower()
        if scope_arg in ["lifetime", "y11s1"]:
            os.environ["FORCE_SCOPE"] = scope_arg
            print(f"[+] Forcing pipeline scope to: {scope_arg}")
        
    total_start_time = time.time()
    
    if username_arg.lower() == "all":
        stack_players = ["Amlenk", "WamaiDoingThis", "Covetous_Demon"]
        print(f"\n[+] Detected 'all' command. Running pipeline for full 3-player stack: {stack_players}")
        print(f"------------------------------------------")
        
        results = {}
        for player in stack_players:
            # WamaiDoingThis platform is uplay, other players ubi
            plat = "uplay" if player == "WamaiDoingThis" else "ubi"
            success = run_single_player_pipeline(player, plat)
            results[player] = success
            
        print(f"\n==========================================")
        print(f"[*] FINAL STACK PIPELINE RUN SUMMARY")
        print(f"==========================================")
        all_passed = True
        for player, success in results.items():
            status_str = "PASSED (100% COMPLIANT)" if success else "FAILED"
            print(f"-> {player}: {status_str}")
            if not success:
                all_passed = False
                
        total_duration = time.time() - total_start_time
        print(f"\nTotal execution time: {total_duration:.1f}s")
        print(f"==========================================")
        
        if all_passed:
            print("[SUCCESS] All 3 players in the stack compiled and verified successfully!")
        else:
            print("[WARNING] One or more player pipeline runs did not pass compliance. Review details above.")
            sys.exit(1)
            
    else:
        # Single player run
        plat = "uplay" if username_arg == "WamaiDoingThis" else "ubi"
        success = run_single_player_pipeline(username_arg, plat)
        total_duration = time.time() - total_start_time
        print(f"\nTotal execution time: {total_duration:.1f}s")
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
