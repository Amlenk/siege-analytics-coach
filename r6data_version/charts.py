import os
import json
import matplotlib.pyplot as plt

# Premium color palette
BG_COLOR = '#181a21'        # Deep space dark background
AXES_BG = '#222530'         # Premium card dark gray background
TEXT_COLOR = '#f5f6fa'      # Crisp off-white text
GRID_COLOR = '#2f3640'      # Translucent grid lines
BASELINE_COLOR = '#e1b12c'  # Elegant gold for baselines

# Operator win rate status colors
COLOR_HIGH = '#00b894'      # Vibrant emerald green
COLOR_MID = '#f5cd79'       # Warm muted amber/gold
COLOR_LOW = '#ff7675'       # Premium soft coral/red

# K/D bar colors
COLOR_KD_HIGH = '#00cec9'   # Electric cyber-turquoise
COLOR_KD_LOW = '#a29bfe'    # Soft pastel purple

def load_processed_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_win_rates_chart(operators, username, output_dir):
    # Set up elegant dark theme
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR
    plt.rcParams['xtick.color'] = TEXT_COLOR
    plt.rcParams['ytick.color'] = TEXT_COLOR
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=BG_COLOR)
    ax.set_facecolor(AXES_BG)
    
    # Sort operators by win rate for better visual story
    ops_sorted = sorted(operators, key=lambda x: x['win_rate_float'])
    names = [op['name'] for op in ops_sorted]
    win_rates = [op['win_rate_float'] * 100 for op in ops_sorted]
    
    # Map colors based on performance
    colors = []
    for wr in win_rates:
        if wr >= 55.0:
            colors.append(COLOR_HIGH)
        elif wr >= 50.0:
            colors.append(COLOR_MID)
        else:
            colors.append(COLOR_LOW)
            
    # Draw bars
    bars = ax.barh(names, win_rates, color=colors, height=0.6, edgecolor='none', zorder=3)
    
    # Highlight 50% baseline
    ax.axvline(50.0, color=BASELINE_COLOR, linestyle='--', linewidth=1.5, zorder=2, alpha=0.8)
    ax.text(50.5, len(names) - 0.35, '50% Neutral Baseline', color=BASELINE_COLOR, fontsize=10, fontweight='semibold')
    
    # Value labels at the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", 
                va='center', ha='left', color=TEXT_COLOR, fontsize=11, fontweight='bold')
                
    # Style axes
    ax.set_title(f"Top Operator Win Rates — {username}", fontsize=16, fontweight='bold', pad=25, color=TEXT_COLOR)
    ax.set_xlabel("Win Rate (%)", fontsize=12, fontweight='semibold', labelpad=15)
    ax.set_xlim(0, 100)
    
    # Grid
    ax.grid(axis='x', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1, alpha=0.5)
    
    # Remove borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False, labelsize=11)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save chart
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'operator_win_rates.png')
    plt.savefig(out_path, dpi=300, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[r6data.eu Visualizer] Generated win rate chart at: {out_path}")

def create_kd_chart(operators, overall_kd, username, output_dir):
    # Set up dark theme
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = TEXT_COLOR
    plt.rcParams['xtick.color'] = TEXT_COLOR
    plt.rcParams['ytick.color'] = TEXT_COLOR
    plt.rcParams['font.sans-serif'] = 'Segoe UI'
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=BG_COLOR)
    ax.set_facecolor(AXES_BG)
    
    # Sort operators by KD
    ops_sorted = sorted(operators, key=lambda x: x['kd_ratio'], reverse=True)
    names = [op['name'] for op in ops_sorted]
    kds = [op['kd_ratio'] for op in ops_sorted]
    
    # Colors: higher vs lower than overall ranked KD baseline
    colors = [COLOR_KD_HIGH if kd >= overall_kd else COLOR_KD_LOW for kd in kds]
    
    # Draw bars
    bars = ax.bar(names, kds, color=colors, width=0.5, edgecolor='none', zorder=3)
    
    # Highlight overall ranked K/D baseline
    ax.axhline(overall_kd, color=BASELINE_COLOR, linestyle='--', linewidth=1.5, zorder=2, alpha=0.8)
    ax.text(-0.35, overall_kd + 0.05, f'Ranked K/D Baseline ({overall_kd:.2f})', color=BASELINE_COLOR, fontsize=10, fontweight='semibold')
    
    # Value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.05, f"{height:.2f}", 
                va='bottom', ha='center', color=TEXT_COLOR, fontsize=11, fontweight='bold')
                
    # Style axes
    ax.set_title(f"Operator K/D Ratio vs. Baseline — {username}", fontsize=16, fontweight='bold', pad=25, color=TEXT_COLOR)
    ax.set_ylabel("K/D Ratio", fontsize=12, fontweight='semibold', labelpad=15)
    ax.set_ylim(0, 2.5)
    
    # Grid
    ax.grid(axis='y', color=GRID_COLOR, linestyle=':', linewidth=1, zorder=1, alpha=0.5)
    
    # Remove borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_visible(False)
        
    ax.tick_params(left=False, bottom=False, labelsize=11)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save chart
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'operator_kd.png')
    plt.savefig(out_path, dpi=300, facecolor=BG_COLOR, bbox_inches='tight')
    plt.close()
    print(f"[r6data.eu Visualizer] Generated K/D comparison chart at: {out_path}")

def main():
    processed_path = os.path.join('data', 'stats_processed.json')
    
    if not os.path.exists(processed_path):
        print(f"Error: {processed_path} does not exist. Run stats.py first.")
        return
        
    print(f"[r6data.eu Visualizer] Loading processed stats from {processed_path}...")
    data = load_processed_data(processed_path)
    
    username = "Unknown"
    for scope in data.values():
        if isinstance(scope, dict) and 'summary' in scope:
            username = scope['summary'].get('username', 'Unknown')
            if username != "Unknown":
                break
                
    output_dir = os.path.join('output', 'charts', username)
    os.makedirs(output_dir, exist_ok=True)
    
    if 'lifetime' in data:
        operators = data['lifetime']['operators']
        operators = sorted(operators, key=lambda x: x.get('rounds_played', 0), reverse=True)[:17]
        overall_kd = data['lifetime']['summary']['kd']
    else:
        operators = data.get('top_operators', [])
        overall_kd = data.get('lifetime_ranked', {}).get('kd_ratio', 1.33)
    
    if not operators:
        print("[r6data.eu Visualizer] No operators found in processed stats.")
        return
        
    print(f"[r6data.eu Visualizer] Generating premium dark-mode charts for {username}...")
    create_win_rates_chart(operators, username, output_dir)
    create_kd_chart(operators, overall_kd, username, output_dir)
    print("[r6data.eu Visualizer] All visualization charts generated successfully!")

if __name__ == '__main__':
    main()
