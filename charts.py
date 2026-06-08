import os
import json
import sys
import numpy as np

# Set matplotlib backend to headless to prevent display environment errors
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Custom PREMIUM dark theme styling constants
STYLE = {
    "bg_color": "#0d1117",
    "surface_color": "#161b22",
    "border_color": "#30363d",
    "text_primary": "#e6edf3",
    "text_muted": "#8b949e"
}

# Robust sets of Attackers and Defenders matching data strings
ATTACKERS = {
    'Thatcher', 'Hibana', 'Maverick', 'Deimos', 'Blackbeard', 'Glaz', 'Jackal', 
    'Sledge', 'Grim', 'Ram', 'Sens', 'Striker', 'Rauora', 'Lion', 'Brava', 
    'Fuze', 'Blitz', 'Twitch', 'Osa', 'Thermite', 'Solid Snake', 'Ash', 
    'Dokkaebi', 'Gridlock', 'Ying', 'Capitão', 'Capito', 'Nøkk', 'Nkk', 
    'Zofia', 'Zero', 'Kali', 'IQ', 'Buck', 'Iana', 'Amaru', 'Montagne', 
    'Flores', 'Nomad', 'Ace'
}

DEFENDERS = {
    'Smoke', 'Pulse', 'Melusi', 'Tubarão', 'Tubaro', 'Clash', 'Goyo', 
    'Thunderbird', 'Lesion', 'Castle', 'Thorn', 'Mozzie', 'Solis', 'Skopés', 
    'Skops', 'Skopos', 'Sentry', 'Vigil', 'Jäger', 'Jger', 'Mute', 'Fenrir', 
    'Alibi', 'Oryx', 'Doc', 'Maestro', 'Kapkan', 'Rook', 'Valkyrie', 'Azami', 
    'Aruni', 'Tachanka', 'Bandit', 'Frost', 'Echo', 'Warden', 'Denari', 'Caveira',
    'Mira'
}

def is_attacker(name):
    name_clean = name.strip()
    if name_clean in ATTACKERS:
        return True
    if name_clean in DEFENDERS:
        return False
    # Fallback substring detection for resilient classification
    attacker_substrings = [
        "sledge", "thatcher", "ash", "thermite", "twitch", "montagne", "glaz", 
        "fuze", "blitz", "iq", "buck", "blackbeard", "capit", "hibana", "jackal", 
        "ying", "zofia", "dokkaebi", "finka", "lion", "maverick", "nomad", 
        "gridlock", "n", "amaru", "kali", "iana", "ace", "zero", "flores", 
        "osa", "sens", "grim", "brava", "ram", "rauora", "deimos", "striker", "snake"
    ]
    name_lower = name_clean.lower()
    for sub in attacker_substrings:
        if sub in name_lower:
            return True
    return False

def apply_premium_style(fig, ax):
    """Applies the custom dark style to standard matplotlib axes."""
    fig.patch.set_facecolor(STYLE["bg_color"])
    ax.set_facecolor(STYLE["surface_color"])
    
    # Grid lines
    ax.grid(color=STYLE["border_color"], linestyle='--', linewidth=0.5, zorder=0)
    
    # Spine/Border settings
    for spine in ax.spines.values():
        spine.set_color(STYLE["border_color"])
        spine.set_linewidth(1.0)
        
    # Text and labels
    ax.xaxis.label.set_color(STYLE["text_primary"])
    ax.yaxis.label.set_color(STYLE["text_primary"])
    if ax.title:
        ax.title.set_color(STYLE["text_primary"])
    ax.tick_params(colors=STYLE["text_muted"], which='both')
    
    # Ensure Segoe UI or standard sans-serif is loaded
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['text.color'] = STYLE["text_primary"]
    plt.rcParams['axes.labelcolor'] = STYLE["text_primary"]
    plt.rcParams['xtick.color'] = STYLE["text_muted"]
    plt.rcParams['ytick.color'] = STYLE["text_muted"]

# 1. map_winrate_overview.png
def generate_map_winrate_overview(maps, username, output_paths):
    maps_sorted = sorted(maps, key=lambda x: x['win_pct'], reverse=True)
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    apply_premium_style(fig, ax)
    
    names = [m['name'] for m in maps_sorted]
    win_pcts = [m['win_pct'] for m in maps_sorted]
    
    # Muted red (<50%), amber (50-55%), emerald green (>=55%)
    colors = []
    for win in win_pcts:
        if win < 50.0:
            colors.append('#f43f5e')  # Muted rose red
        elif win < 55.0:
            colors.append('#fbbf24')  # Amber
        else:
            colors.append('#10b981')  # Emerald green
            
    y_pos = range(len(names))
    bars = ax.barh(y_pos, win_pcts, color=colors, height=0.6, edgecolor=STYLE["border_color"], linewidth=0.8, zorder=3)
    
    # Add vertical lines at thresholds
    ax.axvline(50.0, color='#ffa500', linestyle='--', linewidth=1.2, alpha=0.4, zorder=2)
    ax.axvline(55.0, color='#10b981', linestyle='--', linewidth=1.2, alpha=0.4, zorder=2)
    
    # Text labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=STYLE["text_primary"], fontsize=9, fontweight='bold')
                
    ax.set_title(f"Active Ranked Map Win Rates — {username} Overview", fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Win Percentage (%)", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9, fontweight='semibold', color=STYLE["text_muted"])
    
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 2. map_attack_vs_defence.png
def generate_map_attack_vs_defence(maps, username, output_paths):
    maps_sorted = sorted(maps, key=lambda x: x['win_pct'], reverse=True)
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    apply_premium_style(fig, ax)
    
    names = [m['name'] for m in maps_sorted]
    attack_pcts = [m['attack_win_pct'] for m in maps_sorted]
    defence_pcts = [m['defence_win_pct'] for m in maps_sorted]
    
    y_pos = np.arange(len(names))
    height = 0.3
    
    # Orange for Attack, Blue for Defense
    rects_att = ax.barh(y_pos - height/2, attack_pcts, height, label='Attack Win %', color='#f97316', edgecolor=STYLE["border_color"], linewidth=0.5, zorder=3)
    rects_def = ax.barh(y_pos + height/2, defence_pcts, height, label='Defense Win %', color='#3b82f6', edgecolor=STYLE["border_color"], linewidth=0.5, zorder=3)
    
    ax.axvline(50.0, color=STYLE["text_primary"], linestyle='--', linewidth=1.0, alpha=0.3, zorder=2)
    
    # Text labels
    for rect in rects_att:
        width = rect.get_width()
        ax.text(width + 0.5, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color='#f97316', fontsize=7, fontweight='semibold')
                
    for rect in rects_def:
        width = rect.get_width()
        ax.text(width + 0.5, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color='#3b82f6', fontsize=7, fontweight='semibold')
                
    ax.set_title(f"Active Ranked Maps: Attack vs Defense Win% — {username}", fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Win Percentage (%)", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9, fontweight='semibold', color=STYLE["text_muted"])
    
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    
    ax.legend(facecolor=STYLE["surface_color"], edgecolor=STYLE["border_color"], loc='lower right', labelcolor=STYLE["text_primary"], fontsize=9)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 3. operator_quadrant.png
def generate_operator_quadrant(operators, username, output_paths):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    apply_premium_style(fig, ax)
    
    kds = [op['kd_float'] for op in operators]
    win_rates = [op['win_rate_float'] * 100.0 for op in operators]
    rounds = [op['rounds_played'] for op in operators]
    names = [op['name'] for op in operators]
    
    if not kds:
        # Resiliency in case player has no operators
        kds = [1.0]
        win_rates = [50.0]
        rounds = [1]
        names = ["None"]
        
    # Scale bubble sizes based on rounds played
    max_r = max(rounds) if rounds else 1
    sizes = [max(40, (r / max_r) * 700) for r in rounds]
    
    # Color coordinates by their respective quadrant
    colors = []
    for kd, wr in zip(kds, win_rates):
        if kd >= 1.0 and wr >= 50.0:
            colors.append('#10b981')  # Carry / Star (green)
        elif kd < 1.0 and wr >= 50.0:
            colors.append('#3b82f6')  # Support / Anchor (blue)
        elif kd >= 1.0 and wr < 50.0:
            colors.append('#f97316')  # Impact Fragger (orange)
        else:
            colors.append('#ef4444')  # Underperforming (red)
            
    scatter = ax.scatter(kds, win_rates, s=sizes, c=colors, alpha=0.7, edgecolors=STYLE["border_color"], linewidths=1.0, zorder=3)
    
    # Quadrant lines at baseline
    ax.axvline(1.0, color='#8b949e', linestyle='--', linewidth=1.2, alpha=0.6, zorder=2)
    ax.axhline(50.0, color='#8b949e', linestyle='--', linewidth=1.2, alpha=0.6, zorder=2)
    
    # Set limit padding dynamically
    ax.set_xlim(max(0.1, min(kds) - 0.15), max(kds) + 0.15)
    ax.set_ylim(max(0.0, min(win_rates) - 5), min(100.0, max(win_rates) + 5))
    
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    
    # Add stylish quadrant tag overlays in corners
    ax.text(xmax - 0.05, ymax - 3, "CARRY / STAR", color='#10b981', fontsize=9, fontweight='bold', ha='right', va='top', bbox=dict(facecolor=STYLE["surface_color"], alpha=0.9, edgecolor='#10b981', boxstyle='round,pad=0.3'))
    ax.text(xmin + 0.05, ymax - 3, "SUPPORT / ANCHOR", color='#3b82f6', fontsize=9, fontweight='bold', ha='left', va='top', bbox=dict(facecolor=STYLE["surface_color"], alpha=0.9, edgecolor='#3b82f6', boxstyle='round,pad=0.3'))
    ax.text(xmax - 0.05, ymin + 3, "IMPACT FRAGGER", color='#f97316', fontsize=9, fontweight='bold', ha='right', va='bottom', bbox=dict(facecolor=STYLE["surface_color"], alpha=0.9, edgecolor='#f97316', boxstyle='round,pad=0.3'))
    ax.text(xmin + 0.05, ymin + 3, "UNDERPERFORMING", color='#ef4444', fontsize=9, fontweight='bold', ha='left', va='bottom', bbox=dict(facecolor=STYLE["surface_color"], alpha=0.9, edgecolor='#ef4444', boxstyle='round,pad=0.3'))
    
    # Annotate key operators
    target_ops = {'Azami', 'Ace', 'Lesion', 'Thorn', 'Mute', 'Ash', 'Bandit', 'Nomad', 'Gridlock'}
    sorted_by_rounds = sorted(operators, key=lambda x: x['rounds_played'], reverse=True)
    top_rounds_names = {op['name'] for op in sorted_by_rounds[:8]}
    
    for i, name in enumerate(names):
        if name in target_ops or name in top_rounds_names:
            ax.annotate(name, (kds[i], win_rates[i]), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center', 
                        fontsize=8, 
                        fontweight='bold',
                        color=STYLE["text_primary"],
                        bbox=dict(boxstyle="round,pad=0.2", fc=STYLE["bg_color"], ec=STYLE["border_color"], alpha=0.85, lw=0.5))
            
    ax.set_title(f"Operator Performance Quadrants — {username}", fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("K/D Ratio", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_ylabel("Win Rate (%)", fontsize=10, fontweight='bold', labelpad=10)
    
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
        
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 4 & 5. Attacker / Defender K/D Bar charts
def generate_role_kd_chart(operators, role_name, username, output_paths):
    role_ops = []
    # Try with lower round threshold if no operators meet 20 rounds threshold to ensure charts are always created!
    for threshold in [20, 10, 5, 0]:
        role_ops = []
        for op in operators:
            if op['rounds_played'] >= threshold:
                is_att = is_attacker(op['name'])
                if (role_name == "Attacker" and is_att) or (role_name == "Defender" and not is_att):
                    role_ops.append(op)
        if len(role_ops) >= 2:
            break
            
    role_ops_sorted = sorted(role_ops, key=lambda x: x['kd_float'], reverse=True)[:15] # limit to top 15
    
    if not role_ops_sorted:
        # Create a dummy chart to prevent missing file error
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        ax.text(0.5, 0.5, f"No {role_name} operator stats found.", color=STYLE["text_muted"], ha='center', va='center')
        ax.set_title(f"{role_name} Individual K/D — {username}", fontsize=14, fontweight='bold')
    else:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        
        names = [op['name'] for op in role_ops_sorted]
        kds = [op['kd_float'] for op in role_ops_sorted]
        rounds = [op['rounds_played'] for op in role_ops_sorted]
        
        colors = ['#10b981' if kd >= 1.0 else '#f43f5e' for kd in kds]
        
        y_pos = range(len(names))
        bars = ax.barh(y_pos, kds, color=colors, height=0.6, edgecolor=STYLE["border_color"], linewidth=0.8, zorder=3)
        
        ax.axvline(1.0, color='#ffa500', linestyle='--', linewidth=1.2, alpha=0.5, zorder=2)
        
        for bar, r in zip(bars, rounds):
            width = bar.get_width()
            ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f"{width:.2f} ({r}r)",
                    va='center', ha='left', color=STYLE["text_primary"], fontsize=8, fontweight='semibold')
                    
        ax.set_title(f"{role_name} Individual K/D — {username} (Rounds Sorted)", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("K/D Ratio", fontsize=10, fontweight='bold', labelpad=10)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9, fontweight='semibold', color=STYLE["text_muted"])
        
        ax.set_xlim(0, max(kds) + 0.2 if kds else 1.5)
        ax.invert_yaxis()
        
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 6. operator_winrate.png
def generate_operator_winrate_chart(operators, username, output_paths):
    ops_filtered = []
    for threshold in [20, 10, 5, 0]:
        ops_filtered = [op for op in operators if op['rounds_played'] >= threshold]
        if len(ops_filtered) >= 2:
            break
            
    ops_sorted = sorted(ops_filtered, key=lambda x: x['win_rate_float'], reverse=True)[:15] # Limit to top 15
    
    if not ops_sorted:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        ax.text(0.5, 0.5, "No operator stats found.", color=STYLE["text_muted"], ha='center', va='center')
        ax.set_title(f"Operator Win Rates — {username}", fontsize=14, fontweight='bold')
    else:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        
        names = [op['name'] for op in ops_sorted]
        win_rates = [op['win_rate_float'] * 100.0 for op in ops_sorted]
        rounds = [op['rounds_played'] for op in ops_sorted]
        
        colors = ['#10b981' if wr >= 50.0 else '#f43f5e' for wr in win_rates]
        
        y_pos = range(len(names))
        bars = ax.barh(y_pos, win_rates, color=colors, height=0.6, edgecolor=STYLE["border_color"], linewidth=0.8, zorder=3)
        
        ax.axvline(50.0, color='#ffa500', linestyle='--', linewidth=1.2, alpha=0.5, zorder=2)
        
        for bar, r in zip(bars, rounds):
            width = bar.get_width()
            ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{width:.1f}% ({r}r)",
                    va='center', ha='left', color=STYLE["text_primary"], fontsize=8, fontweight='semibold')
                    
        ax.set_title(f"Operator Win Rates — {username} (Top Performing)", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Win Rate Percentage (%)", fontsize=10, fontweight='bold', labelpad=10)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9, fontweight='semibold', color=STYLE["text_muted"])
        
        ax.set_xlim(0, 100)
        ax.invert_yaxis()
        
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 7. skill_radar.png
def generate_skill_radar(summary, operators, maps, username, output_paths):
    kd = float(summary.get('kd', 1.0))
    win_rate_str = summary.get('win_rate', '50.0%')
    try:
        win_rate_float = float(win_rate_str.replace('%', '').strip()) / 100.0
    except Exception:
        win_rate_float = 0.50
        
    # Axes calculations
    avg_esr = sum(m.get('esr', 0.50) for m in maps) / max(len(maps), 1)
    num_maps_above_50 = sum(1 for m in maps if m.get('win_rate_float', 0.0) >= 0.50)
    num_ops_above_10 = sum(1 for o in operators if o.get('rounds_played', 0) >= 10)
    
    # 0-100 Normalization formulas relative to Diamond Baseline (which is fixed at 70)
    fragging_score = min(100.0, max(10.0, 50.0 + (kd - 1.0) * 80.0))
    win_rate_score = min(100.0, max(10.0, 50.0 + (win_rate_float - 0.50) * 450.0))
    esr_score = min(100.0, max(10.0, 70.0 + (avg_esr - 0.55) * 100.0))
    breadth_score = min(100.0, max(10.0, 70.0 + (num_maps_above_50 - 10) * 5.0))
    versatility_score = min(100.0, max(10.0, 70.0 + (num_ops_above_10 - 8) * 5.0))
    
    labels = ['Fragging', 'Team Win Rate', 'Survival / Entry', 'Map Breadth', 'Versatility']
    num_vars = len(labels)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the radar loop
    
    player_values = [fragging_score, win_rate_score, esr_score, breadth_score, versatility_score]
    player_values += player_values[:1]
    
    diamond_values = [70, 70, 70, 70, 70]
    diamond_values += diamond_values[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), dpi=300)
    
    fig.patch.set_facecolor(STYLE["bg_color"])
    ax.set_facecolor(STYLE["surface_color"])
    
    # Style polar grid lines and boundary spines
    ax.spines['polar'].set_color(STYLE["border_color"])
    ax.spines['polar'].set_linewidth(1.0)
    ax.grid(color=STYLE["border_color"], linestyle='--', linewidth=0.8)
    
    # Plot Diamond baseline
    ax.plot(angles, diamond_values, color='#8b949e', linewidth=1.5, linestyle='--', label='Diamond Baseline (70)', zorder=2)
    ax.fill(angles, diamond_values, color='#8b949e', alpha=0.1, zorder=2)
    
    season_year = summary.get('season', 'Y11S2')
    # Plot Player profile
    ax.plot(angles, player_values, color='#10b981', linewidth=2.5, linestyle='-', label=f"{username} ({season_year})", zorder=3)
    ax.fill(angles, player_values, color='#10b981', alpha=0.25, zorder=3)
    
    # Axes configuration
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color=STYLE["text_primary"], fontsize=10, fontweight='bold')
    
    # Y-axis ticks and labels
    ax.set_rlabel_position(30)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color=STYLE["text_muted"], size=8)
    ax.set_ylim(0, 100)
    
    ax.set_title(f"Tactical Performance Profile vs. Diamond Baseline — {username}", fontsize=13, fontweight='bold', pad=25, color=STYLE["text_primary"])
    ax.legend(facecolor=STYLE["surface_color"], edgecolor=STYLE["border_color"], loc='upper right', bbox_to_anchor=(1.15, 1.1), labelcolor=STYLE["text_primary"], fontsize=9)
    
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

# 8. map_ban_spectrum.png
def generate_map_ban_spectrum(maps, username, output_paths):
    # Sort maps ascending: from worst (lowest Win%) to best
    maps_sorted = sorted(maps, key=lambda x: x['win_pct'], reverse=False)
    
    if not maps_sorted:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        ax.text(0.5, 0.5, "No map stats found.", color=STYLE["text_muted"], ha='center', va='center')
        ax.set_title(f"Map Ban Spectrum & Veto Guide — {username}", fontsize=14, fontweight='bold')
    else:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        apply_premium_style(fig, ax)
        
        names = [m['name'] for m in maps_sorted]
        win_pcts = [m['win_pct'] for m in maps_sorted]
        
        # Determine the spectrum bands across the maps
        colors = []
        actions = []
        num_maps = len(names)
        
        for i in range(num_maps):
            # Proportional distribution for resilient dynamic sizing of any map list length
            pct = i / max(1, num_maps - 1)
            if pct <= 0.20:
                colors.append('#ef4444')  # MUST BAN
                actions.append("MUST BAN")
            elif pct <= 0.45:
                colors.append('#f97316')  # SITUATIONAL BAN
                actions.append("SITUATIONAL BAN")
            elif pct <= 0.65:
                colors.append('#eab308')  # NEUTRAL
                actions.append("NEUTRAL / PRACTICE")
            elif pct <= 0.85:
                colors.append('#22c55e')  # PROTECT
                actions.append("PROTECT")
            else:
                colors.append('#047857')  # STRONG COMFORT
                actions.append("STRONG COMFORT")
                
        y_pos = range(num_maps)
        bars = ax.barh(y_pos, win_pcts, color=colors, height=0.6, edgecolor=STYLE["border_color"], linewidth=0.8, zorder=3)
        
        # Draw soft background spans to visually group the bands
        # Since we might have maps, draw them at float boundaries
        for i in range(num_maps):
            ax.axhspan(i - 0.5, i + 0.5, color=colors[i], alpha=0.03, zorder=1)
            
        # Add textual band labels next to each map bar
        for bar, action in zip(bars, actions):
            width = bar.get_width()
            ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, f"{action} — {width:.1f}%",
                    va='center', ha='left', color=STYLE["text_primary"], fontsize=8, fontweight='bold')
                    
        ax.set_title(f"Tactical Map Ban Spectrum & Veto Guide — {username}", fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel("Win Percentage (%)", fontsize=10, fontweight='bold', labelpad=10)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9, fontweight='semibold', color=STYLE["text_muted"])
        
        ax.set_xlim(0, 100)
        ax.invert_yaxis()  # Invert so worst maps (Must Ban) sit right at the top
        
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_visible(False)
        ax.tick_params(left=False, bottom=False)
        
    plt.tight_layout()
    for path in output_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, facecolor=STYLE["bg_color"], bbox_inches='tight')
    plt.close()

def main():
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1].strip()
        
    if username:
        data_path = os.path.join('data', f'{username}_stats_processed.json')
    else:
        data_path = os.path.join('data', 'stats_processed.json')
        
    print(f"[*] [Charts Generator] Loading processed statistics from: {data_path}")
    
    if not os.path.exists(data_path):
        fallback = os.path.join('data', 'stats_processed.json')
        if os.path.exists(fallback):
            print(f"[*] [Charts Generator] Specific processed stats not found, falling back to: {fallback}")
            data_path = fallback
        else:
            print(f"[!] Error: processed statistics file {data_path} does not exist!")
            sys.exit(1)
            
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Check both scopes, prefer 'y11s1' then 'lifetime', unless overridden by FORCE_SCOPE env var
    scope_env = os.environ.get("FORCE_SCOPE", "").lower().strip()
    if scope_env in ['y11s1', 'lifetime'] and scope_env in data:
        y11s1 = data[scope_env]
    else:
        y11s1 = data.get('y11s1', data.get('lifetime', {}))
    # Resiliency fallback
    if not y11s1:
        for scope_name, scope_content in data.items():
            if isinstance(scope_content, dict) and 'operators' in scope_content:
                y11s1 = scope_content
                break
                
    if not y11s1:
        print("[!] Error: No valid statistical scope with operators/maps found!")
        sys.exit(1)
        
    # Resolve username
    if not username:
        for scope_name in ["y11s1", "lifetime"]:
            if scope_name in data and "summary" in data[scope_name]:
                username = data[scope_name]["summary"].get("username", "")
                if username:
                    break
        if not username:
            username = "Unknown"

    if username.lower() == "fearlesscopper":
        print("[*] [Charts Generator] Forcing scope to 'lifetime' for FearlessCoppeR.")
        y11s1 = data.get("lifetime", y11s1)

    operators = y11s1.get('operators', [])
    maps = y11s1.get('maps', [])
    summary = y11s1.get('summary', {})
        
    print(f"[*] [Charts Generator] Rendering 8 Premium Charts for {username}")
    print(f"[*] [Charts Generator] Active Map Count: {len(maps)} | Operator Pool: {len(operators)}")
    
    # Configure output directories
    base_dir = os.path.join('output', 'charts')
    compat_dir = os.path.join('output', 'charts', username)
    
    # 1. map_winrate_overview.png
    print("[+] Rendering: map_winrate_overview.png")
    generate_map_winrate_overview(maps, username, [
        os.path.join(base_dir, 'map_winrate_overview.png'),
        os.path.join(compat_dir, 'map_winrate_overview.png')
    ])
    
    # 2. map_attack_vs_defence.png
    print("[+] Rendering: map_attack_vs_defence.png")
    generate_map_attack_vs_defence(maps, username, [
        os.path.join(base_dir, 'map_attack_vs_defence.png'),
        os.path.join(compat_dir, 'map_attack_vs_defence.png')
    ])
    
    # 3. operator_quadrant.png
    print("[+] Rendering: operator_quadrant.png")
    generate_operator_quadrant(operators, username, [
        os.path.join(base_dir, 'operator_quadrant.png'),
        os.path.join(compat_dir, 'operator_quadrant.png')
    ])
    
    # 4. attacker_kd.png
    print("[+] Rendering: attacker_kd.png")
    generate_role_kd_chart(operators, "Attacker", username, [
        os.path.join(base_dir, 'attacker_kd.png'),
        os.path.join(compat_dir, 'attacker_kd.png')
    ])
    
    # 5. defender_kd.png
    print("[+] Rendering: defender_kd.png")
    generate_role_kd_chart(operators, "Defender", username, [
        os.path.join(base_dir, 'defender_kd.png'),
        os.path.join(compat_dir, 'defender_kd.png')
    ])
    
    # 6. operator_winrate.png
    print("[+] Rendering: operator_winrate.png")
    generate_operator_winrate_chart(operators, username, [
        os.path.join(base_dir, 'operator_winrate.png'),
        os.path.join(compat_dir, 'operator_winrate.png')
    ])
    
    # 7. skill_radar.png
    print("[+] Rendering: skill_radar.png")
    generate_skill_radar(summary, operators, maps, username, [
        os.path.join(base_dir, 'skill_radar.png'),
        os.path.join(compat_dir, 'skill_radar.png')
    ])
    
    # 8. map_ban_spectrum.png
    print("[+] Rendering: map_ban_spectrum.png")
    generate_map_ban_spectrum(maps, username, [
        os.path.join(base_dir, 'map_ban_spectrum.png'),
        os.path.join(compat_dir, 'map_ban_spectrum.png')
    ])
    
    print(f"[*] All 8 Premium Charts successfully generated and saved for {username}!")

if __name__ == '__main__':
    main()
