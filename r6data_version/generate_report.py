import os
import sys
import subprocess
import time

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
    print(f"[*] PIPELINE COMPLIANCE VERIFICATION RUN")
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

    # Rule 6: Absolute block list check (Ranked 3.0)
    print("\n[*] Rule 6: Verifying zero occurrences of blocklisted term 'Ranked 3.0'...")
    occurrences = report_content.lower().count("ranked 3.0")
    if occurrences == 0:
        print("  [PASS] Zero occurrences of 'Ranked 3.0' in the entire coaching report.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Found {occurrences} occurrences of 'Ranked 3.0'! Check compliance requirements.")

    # Rule 7: Rule out generic fluff - check that at least 50 numerical statistics are cited
    print("\n[*] Rule 7: Verifying statistical density (no generic fluff)...")
    import re
    numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', report_content)
    # Ignore dates, headers, etc. But a high count of numeric characters indicates high statistical density
    if len(numbers) >= 50:
        print(f"  [PASS] Statistical density verified. Cites at least {len(numbers)} numerical data points.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Statistical density too low ({len(numbers)} numbers). The report may contain generic fluff!")

    # Rule 8: Map Mastery Matrix map count check (must be exactly 17 competitive maps)
    print("\n[*] Rule 8: Checking competitive map count inside Section 3 matrix...")
    matrix_section = ""
    if "SECTION 3:" in report_content:
        parts = report_content.split("SECTION 3:")
        if len(parts) > 1:
            matrix_section = parts[1].split("SECTION 4:")[0]
            
    # Count rows in the table (marked by pipelines |) excluding header and alignment lines
    table_lines = [l for l in matrix_section.split("\n") if l.strip().startswith("|")]
    map_rows = 0
    for line in table_lines:
        # Avoid counting header and line dividers
        if "Map" in line or "---" in line:
            continue
        map_rows += 1
    if map_rows == 17:
        print(f"  [PASS] Found exactly 17 competitive active Ranked maps in the mastery matrix.")
        passed_rules += 1
    else:
        print(f"  [FAIL] Found {map_rows} maps in matrix instead of exactly 17 competitive maps!")

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
    print(f"[*] COMPLIANCE VERIFICATION SUMMARY REPORT")
    print(f"==========================================")
    print(f"Total Rules Run: {total_rules}")
    print(f"Rules Passed:    {passed_rules}")
    print(f"Rules Failed:    {total_rules - passed_rules}")
    print(f"------------------------------------------")
    
    if passed_rules == total_rules:
        print(f"[SUCCESS] The entire pipeline is 100% COMPLIANT and verified.")
        return True
    else:
        print(f"[WARNING] Pipeline is NOT fully compliant. Please review failures above.")
        return False

def main():
    print(r"""
    ___       _   _                             _ _           ___   ___  
   / _ \___ _| |_(_) __ _ _ __ __ ___   __(_) |_ _   _     / _ \ / _ \ 
  / /_)/ _ \__  | |/ _` | '__/ _` \ \ / / | __| | | | |   | | | | | | |
 / ___/  __// / | | (_| | | | (_| |\ V /| | |_| | |_| |   | |_| | |_| |
 \/    \___|\___|_|\__, |_|  \__,_| \_/ |_|\__|_|\__, |    \___/ \___/ 
                   |___/                         |___/                 
         r6data.eu REST API Tactical Coaching Report Orchestrator v3.0
    """)
    
    # Target values default from .env or config
    username = "Amlenk"
    platform = "ubi"
    
    # Try loading username from local .env if possible to default gracefully
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.split('=', 1)
                    if k.strip() == 'UBISOFT_USERNAME':
                        username = v.strip()
                    elif k.strip() == 'UBISOFT_PLATFORM':
                        platform = v.strip()
                        
    # Check command-line arguments
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
    if len(sys.argv) > 2:
        platform = sys.argv[2].strip()
        
    print(f"\n[+] Target Player:  `{username}`")
    print(f"[+] Platform:       `{platform.upper()}`")
    print(f"[+] Local Time:     {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"------------------------------------------")
    print("Initiating full end-to-end tactical analysis...")
    
    total_start_time = time.time()
    
    # Step 1: Fetch fresh data from r6data.eu API
    run_step(f"python fetch_stats.py \"{username}\" \"{platform}\"", "Fetching stats from r6data.eu API")
    
    # Step 2: Run stats calculations
    run_step("python stats.py", "Processing stats and calculating advanced derived metrics")
    
    # Step 3: Generate 8 premium visual charts
    run_step("python charts_generator.py", "Generating 8 premium visualization charts in dark mode STYLE")
    
    # Step 4: Compile 8-section tactical markdown and premium HTML reports
    run_step("python generate_report_api.py", "Compiling 8-section elite tactical coaching report and glassmorphism HTML dashboard")
    
    # Step 5: Automated pipeline compliance verification checklist
    verification_success = perform_compliance_check(username)
    
    total_duration = time.time() - total_start_time
    
    report_path = os.path.abspath(os.path.join("output", "report.md"))
    html_path = os.path.abspath(os.path.join("output", "report.html"))
    
    print(f"\n==========================================")
    print(f"[+] PIPELINE EXECUTION COMPLETED!")
    print(f"Total processing time: {total_duration:.1f}s")
    print(f"Verification status: {'PASSED (100% COMPLIANT)' if verification_success else 'FAILED'}")
    print(f"==========================================")
    print(f"Your custom tactical coaching reports have been generated at:")
    print(f"-> Markdown: {report_path}")
    print(f"-> HTML:     {html_path}")
    print(f"\nYou can open the HTML report directly in your browser to view a stunning glassmorphism dark-mode dashboard of your personalized coaching advice!")
    print(f"==========================================\n")
    
    if not verification_success:
        sys.exit(1)

if __name__ == "__main__":
    main()
