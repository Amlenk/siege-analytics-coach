import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Premium styling constants
BG_COLOR = '#1a1a2e'
TEXT_COLOR = 'white'
GRID_COLOR = '#2d2d44'
REF_LINE_COLOR = 'gold'

# Bar colors
COLOR_RED = '#ff7675'
COLOR_TEAL = '#00cec9'
COLOR_ORANGE = '#ff9f43'
COLOR_BLUE = '#54a0ff'

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def setup_common_params():
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR
    plt.rcParams['xtick.color'] = TEXT_COLOR
    plt.rcParams['ytick.color'] = TEXT_COLOR
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['font.family'] = 'sans-serif'

def generate_kd_chart(operators, username, output_path):
    # Ensure they are sorted by K/D descending
    ops_sorted = sorted(operators, key=lambda x: x['kd'], reverse=True)
    
    names = [op['name'] for op in ops_sorted]
    kds = [op['kd'] for op in ops_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # Assign colors: below 1.0 in red, at or above in teal
    colors = [COLOR_RED if kd < 1.0 else COLOR_TEAL for kd in kds]
    
    # Plot horizontal bar chart
    # To keep the highest at the top, we can reverse the list or invert the y-axis.
    # Let's plot using y_pos and invert y-axis
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, kds, color=colors, height=0.6, zorder=3)
    
    # Add vertical reference line at K/D = 1.0
    ax.axvline(1.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(1.02, -0.5, 'Neutral K/D (1.0)', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    # Grid lines: subtle grey
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    # Add labels on the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f"{width:.2f}",
                va='center', ha='left', color=TEXT_COLOR, fontsize=10, fontweight='bold')
                
    # Labels and Titles
    ax.set_title(f"Operator K/D — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("K/D Ratio", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    # Set limit
    ax.set_xlim(0, max(kds) + 0.2)
    
    # Invert y-axis to show highest on top
    ax.invert_yaxis()
    
    # Remove borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def generate_winrate_chart(operators, username, output_path):
    # Parse the win_rate string like "62.2%" into float 62.2
    # Sort descending by win rate float value
    for op in operators:
        op['win_rate_val'] = float(op['win_rate'].replace('%', '').strip())
        
    ops_sorted = sorted(operators, key=lambda x: x['win_rate_val'], reverse=True)
    
    names = [op['name'] for op in ops_sorted]
    win_rates = [op['win_rate_val'] for op in ops_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    # Bars below 50% in red, bars at or above in teal
    colors = [COLOR_RED if wr < 50.0 else COLOR_TEAL for wr in win_rates]
    
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, win_rates, color=colors, height=0.6, zorder=3)
    
    # Add vertical reference line at 50%
    ax.axvline(50.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(50.5, -0.5, '50% Neutral Win Rate', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    # Grid lines
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    # Value labels
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1.0, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=TEXT_COLOR, fontsize=10, fontweight='bold')
                
    # Labels and Titles
    ax.set_title(f"Operator Win Rate % — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("Win Rate %", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    ax.set_xlim(0, 100)
    
    ax.invert_yaxis()
    
    # Remove borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def generate_map_chart(maps, username, output_path):
    # Grouped horizontal bar chart: all 17 maps
    # Sorted by overall win % descending (win_pct in stats_processed.json maps list since it's already sorted by win_pct descending)
    maps_sorted = sorted(maps, key=lambda x: x['win_pct'], reverse=True)
    
    names = [m['name'] for m in maps_sorted]
    attack_pcts = [m['attack_win_pct'] for m in maps_sorted]
    defence_pcts = [m['defence_win_pct'] for m in maps_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    y_pos = np.arange(len(names))
    height = 0.35
    
    # Two bars per map: Attack Win % (orange) and Defence Win % (blue)
    rects_att = ax.barh(y_pos - height/2, attack_pcts, height, label='Attack Win %', color=COLOR_ORANGE, zorder=3)
    rects_def = ax.barh(y_pos + height/2, defence_pcts, height, label='Defence Win %', color=COLOR_BLUE, zorder=3)
    
    # Add vertical reference line at 50%
    ax.axvline(50.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(50.5, -0.7, '50% Neutral Win Rate', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    # Grid lines
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    # Value labels
    for rect in rects_att:
        width = rect.get_width()
        ax.text(width + 0.8, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=COLOR_ORANGE, fontsize=8, fontweight='bold')
                
    for rect in rects_def:
        width = rect.get_width()
        ax.text(width + 0.8, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=COLOR_BLUE, fontsize=8, fontweight='bold')
                
    # Labels and Titles
    ax.set_title(f"Map Attack vs Defence Win % — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("Win %", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    ax.set_xlim(0, 100)
    
    ax.invert_yaxis()
    
    # Legend
    ax.legend(facecolor=BG_COLOR, edgecolor='none', loc='lower right', labelcolor=TEXT_COLOR, fontsize=11)
    
    # Remove borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def main():
    import sys
    setup_common_params()
    username_arg = None
    if len(sys.argv) > 1:
        username_arg = sys.argv[1].strip()
        
    if username_arg:
        data_path = os.path.join('data', f'{username_arg}_stats_processed.json')
    else:
        data_path = os.path.join('data', 'stats_processed.json')
        
    if not os.path.exists(data_path):
        # Fallback
        fallback_path = os.path.join('data', 'stats_processed.json')
        if os.path.exists(fallback_path):
            data_path = fallback_path
        else:
            print(f"Error: {data_path} does not exist. Run stats.py first.")
            return
            
    print(f"Loading data from {data_path}...")
    data = load_data(data_path)
    
    y11s1_data = data.get('y11s1', {})
    operators = y11s1_data.get('operators', [])
    maps = y11s1_data.get('maps', [])
    
    # Get username dynamically to organize output folder
    username = y11s1_data.get('summary', {}).get('username', 'Unknown')
    if username_arg and username == "Unknown":
        username = username_arg
        
    charts_dir = os.path.join('output', 'charts', username)
    os.makedirs(charts_dir, exist_ok=True)
    
    print(f"Loaded {len(operators)} operators and {len(maps)} maps for Y11S1 (Player: {username}).")
    
    # Chart 1: operator_kd_y11s1.png
    generate_kd_chart(operators, username, os.path.join(charts_dir, 'operator_kd_y11s1.png'))
    
    # Chart 2: operator_winrate_y11s1.png
    generate_winrate_chart(operators, username, os.path.join(charts_dir, 'operator_winrate_y11s1.png'))
    
    # Chart 3: map_attack_vs_defence_y11s1.png
    generate_map_chart(maps, username, os.path.join(charts_dir, 'map_attack_vs_defence_y11s1.png'))
    
    print("All charts generated successfully!")

if __name__ == '__main__':
    main()
