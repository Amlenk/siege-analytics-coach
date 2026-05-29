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
    ops_sorted = sorted(operators, key=lambda x: x['kd'], reverse=True)
    
    names = [op['name'] for op in ops_sorted]
    kds = [op['kd'] for op in ops_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    colors = [COLOR_RED if kd < 1.0 else COLOR_TEAL for kd in kds]
    
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, kds, color=colors, height=0.6, zorder=3)
    
    ax.axvline(1.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(1.02, -0.5, 'Neutral K/D (1.0)', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2, f"{width:.2f}",
                va='center', ha='left', color=TEXT_COLOR, fontsize=10, fontweight='bold')
                
    ax.set_title(f"Operator K/D — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("K/D Ratio", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    ax.set_xlim(0, max(kds) + 0.2)
    ax.invert_yaxis()
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[r6data.eu Visualizer] Saved: {output_path}")

def generate_winrate_chart(operators, username, output_path):
    for op in operators:
        op['win_rate_val'] = float(op['win_rate'].replace('%', '').strip())
        
    ops_sorted = sorted(operators, key=lambda x: x['win_rate_val'], reverse=True)
    
    names = [op['name'] for op in ops_sorted]
    win_rates = [op['win_rate_val'] for op in ops_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    colors = [COLOR_RED if wr < 50.0 else COLOR_TEAL for wr in win_rates]
    
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, win_rates, color=colors, height=0.6, zorder=3)
    
    ax.axvline(50.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(50.5, -0.5, '50% Neutral Win Rate', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1.0, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=TEXT_COLOR, fontsize=10, fontweight='bold')
                
    ax.set_title(f"Operator Win Rate % — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("Win Rate %", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[r6data.eu Visualizer] Saved: {output_path}")

def generate_map_chart(maps, username, output_path):
    maps_sorted = sorted(maps, key=lambda x: x['win_pct'], reverse=True)
    
    names = [m['name'] for m in maps_sorted]
    attack_pcts = [m['attack_win_pct'] for m in maps_sorted]
    defence_pcts = [m['defence_win_pct'] for m in maps_sorted]
    
    fig, ax = plt.subplots(figsize=(14, 10), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    
    y_pos = np.arange(len(names))
    height = 0.35
    
    rects_att = ax.barh(y_pos - height/2, attack_pcts, height, label='Attack Win %', color=COLOR_ORANGE, zorder=3)
    rects_def = ax.barh(y_pos + height/2, defence_pcts, height, label='Defence Win %', color=COLOR_BLUE, zorder=3)
    
    ax.axvline(50.0, color=REF_LINE_COLOR, linestyle='--', linewidth=2, zorder=2)
    ax.text(50.5, -0.7, '50% Neutral Win Rate', color=REF_LINE_COLOR, fontsize=10, fontweight='bold')
    
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1)
    ax.set_axisbelow(True)
    
    for rect in rects_att:
        width = rect.get_width()
        ax.text(width + 0.8, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=COLOR_ORANGE, fontsize=8, fontweight='bold')
                
    for rect in rects_def:
        width = rect.get_width()
        ax.text(width + 0.8, rect.get_y() + rect.get_height()/2, f"{width:.1f}%",
                va='center', ha='left', color=COLOR_BLUE, fontsize=8, fontweight='bold')
                
    ax.set_title(f"Map Attack vs Defence Win % — Y11S1 ({username})", fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel("Win %", fontsize=12, fontweight='bold', labelpad=15)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11, fontweight='semibold')
    
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    
    ax.legend(facecolor=BG_COLOR, edgecolor='none', loc='lower right', labelcolor=TEXT_COLOR, fontsize=11)
    
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[r6data.eu Visualizer] Saved: {output_path}")

def main():
    setup_common_params()
    data_path = os.path.join('data', 'stats_processed.json')
    print(f"[r6data.eu Visualizer] Loading data from {data_path}...")
    if not os.path.exists(data_path):
        print(f"Error: {data_path} does not exist. Run stats.py first.")
        return
    data = load_data(data_path)
    
    y11s1_data = data.get('y11s1', {})
    operators = y11s1_data.get('operators', [])
    maps = y11s1_data.get('maps', [])
    
    username = y11s1_data.get('summary', {}).get('username', 'Unknown')
    charts_dir = os.path.join('output', 'charts', username)
    os.makedirs(charts_dir, exist_ok=True)
    
    print(f"[r6data.eu Visualizer] Loaded {len(operators)} operators and {len(maps)} maps for Y11S1 (Player: {username}).")
    
    generate_kd_chart(operators, username, os.path.join(charts_dir, 'operator_kd.png'))
    generate_winrate_chart(operators, username, os.path.join(charts_dir, 'operator_winrate.png'))
    generate_map_chart(maps, username, os.path.join(charts_dir, 'map_attack_vs_defence.png'))
    print("[r6data.eu Visualizer] Y11S1 comparison charts generated successfully!")

if __name__ == '__main__':
    main()
