import os
import json

# Define the attacker/defender sets as requested
ATTACKER_OPERATORS = {
    "Ace", "Thermite", "Hibana", "Zero", "Sledge", "Gridlock",
    "Nomad", "Ash", "Twitch", "Flores", "Lion", "Jackal",
    "Capitão", "Buck", "Blackbeard", "Iana", "Montagne", "Fuze",
    "Dokkaebi", "Maverick", "Kali", "Amaru", "Osa", "Sens",
    "Grim", "Thatcher", "Ram", "Brava", "Blitz", "Deimos",
    "Zofia", "Striker", "Rauora", "Solid Snake", "IQ", "Nøkk",
    "Ying", "Glaz"
}
DEFENDER_OPERATORS = {
    "Lesion", "Thorn", "Aruni", "Mute", "Melusi", "Bandit",
    "Castle", "Doc", "Alibi", "Jäger", "Valkyrie", "Echo",
    "Maestro", "Pulse", "Smoke", "Frost", "Kapkan", "Rook",
    "Vigil", "Mozzie", "Goyo", "Warden", "Oryx", "Thunderbird",
    "Solis", "Fenrir", "Skopos", "Azami", "Tubarão", "Sentry",
    "Denari", "Clash", "Tachanka"
}

# Mapping of custom coaching advice templates for each operator with >= 50 rounds
COACHING_DATA = {
    "Azami": {
        "Pros": "Outstanding win rate of {win_rate} and high combat effectiveness with a {kd} K/D ratio across {rounds} rounds.",
        "Focus_Areas": "Ensure that you are not over-relying on aggressive dry peeks, as maintaining this {win_rate} win rate in Champion lobbies requires high-value anchor survival.",
        "Tactical_Strategy": "On weak maps like Skyscraper, use Kiba Barriers to block critical lines of sight from external terraces, forcing attackers into close-range choke points where your high mechanical skill dominates."
    },
    "Aruni": {
        "Pros": "Excellent defensive sustainability with a massive {kd} K/D ratio over {rounds} rounds.",
        "Focus_Areas": "A win rate of {win_rate} is solid, but it can be improved by coordinating your Surya Gates with active teammate crossfires.",
        "Tactical_Strategy": "On Coastline, place Surya Gates on high-traffic windows (e.g., VIP or Penthouse) to drain attacker utility and prevent rapid entry rushes."
    },
    "Thorn": {
        "Pros": "Elite fragging power with an incredible {kd} K/D ratio and a very strong {win_rate} win rate.",
        "Focus_Areas": "While your mechanical kill rate is spectacular, ensure you are utilizing your Razorbloom Shells to herd attackers rather than just trying to get kills with them.",
        "Tactical_Strategy": "On Clubhouse, hide Razorbloom Shells under the floorboards of CCTV stairs or Cash room windows to delay late-round executes and force attackers into your crosshair."
    },
    "Thermite": {
        "Pros": "Great individual gunplay with a {kd} K/D ratio, showing you are highly capable in gunfights even on support.",
        "Focus_Areas": "A sub-par {win_rate} win rate indicates that your Exothermic Charges are not translating into opened walls before you get eliminated.",
        "Tactical_Strategy": "On Clubhouse, coordinate with Thatcher or Flores to clear wall denial on CCTV or church, and prioritize opening the wall before seeking aggressive engagements."
    },
    "Mute": {
        "Pros": "Outstanding site lockdown capability with a {win_rate} win rate and {kd} K/D ratio.",
        "Focus_Areas": "Your performance is already elite, but ensure you are optimizing jammer placement to block both drones and hard breaches on key walls.",
        "Tactical_Strategy": "On Oregon, place Signal Jammers at the top of main stairs and laundry stairs to completely deny attacker drone intel during their crucial setup phase."
    },
    "Melusi": {
        "Pros": "Superb site denial and high survivability, boasting an elite {win_rate} win rate and a {kd} K/D ratio.",
        "Focus_Areas": "With a {win_rate} win rate, you are playing Melusi near-perfectly, but ensure you aren't leaving your Banshees in easily destructible lanes.",
        "Tactical_Strategy": "On Villa, place Banshees around the 90-degree hallway and vault entrance to slow down attackers and swing them while they are slowed and deafened."
    },
    "Gridlock": {
        "Pros": "High individual combat impact with a {kd} K/D ratio across {rounds} rounds.",
        "Focus_Areas": "A disappointing {win_rate} win rate reveals a disconnect between your kills and securing the defuser plant.",
        "Tactical_Strategy": "On Bank, use your Trax Stingers to block the square stairs and elevator exits, completely denying roamer retakes while your team secures the basement plant."
    },
    "Rauora": {
        "Pros": "Solid round contribution with {rounds} rounds played and a {kd} K/D ratio.",
        "Focus_Areas": "A {win_rate} win rate indicates a struggle to convert your entries and pushes into round wins on this operator.",
        "Tactical_Strategy": "On Coastline, utilize your visual screening tools to cover your team's approach from the courtyard, allowing your hard breachers to establish crossfires without defender sightlines."
    },
    "Grim": {
        "Pros": "Decent support utility usage over {rounds} rounds, maintaining a {kd} K/D ratio.",
        "Focus_Areas": "An underwhelming {win_rate} win rate highlights that your Kawan Bee Hives are not being used to actively squeeze roamers out of critical map zones.",
        "Tactical_Strategy": "On Skyscraper, shoot your Bee Hives into the tea room and karaoke rotations to pinpoint active defenders and clear them for your entry fraggers."
    },
    "Nomad": {
        "Pros": "Highly respectable {kd} K/D ratio, showing that you win your isolated fights when watching the flank.",
        "Focus_Areas": "A very low {win_rate} win rate suggests that your Airjabs are either being destroyed or placed in areas where teammates cannot trade.",
        "Tactical_Strategy": "On Theme Park, place Airjabs on the initiation staircase and arcade doors to fully secure your team's flank, allowing them to focus on the site execute."
    },
    "Hibana": {
        "Pros": "Respectable mechanical execution with a {kd} K/D ratio over {rounds} rounds.",
        "Focus_Areas": "An abysmal {win_rate} win rate shows a major failure in converting your X-KAIROS hatches/walls opening into actual round wins.",
        "Tactical_Strategy": "On Clubhouse, focus entirely on opening the kitchen and server hatches to force basement anchors out of their comfortable hiding spots (e.g., blue and church)."
    },
    "Flores": {
        "Pros": "Good trade capability with a {kd} K/D ratio and a solid headshot rate of {hs}.",
        "Focus_Areas": "A {win_rate} win rate shows that your RCE-Ratero drones are not destroying enough defender utility to pave the way for a successful push.",
        "Tactical_Strategy": "On Kafe Dostoyevsky, use your Ratero drones to clear the deployable shields and Kaid claws on 3F/Piano site before your team begins their execute."
    },
    "Smoke": {
        "Pros": "Exceptional late-round clutch potential with an elite {win_rate} win rate and a solid {kd} K/D ratio.",
        "Focus_Areas": "Maintain your survival into the last 45 seconds of the round, as your gas canisters are the most valuable resource for denying the plant.",
        "Tactical_Strategy": "On Clubhouse, anchor in church or behind the blue desk and save your gas canisters to shut down late basement rushes through the main dirt tunnel."
    },
    "Fenrir": {
        "Pros": "Strong presence and solid combat performance, holding a {win_rate} win rate and a {kd} K/D ratio.",
        "Focus_Areas": "Be mindful of F-NATT mine placement to ensure they are not easily shot by attackers from doorways.",
        "Tactical_Strategy": "On Border, deploy your F-NATT mines inside the ventilation and workshop sites behind deployable cover, swinging attackers the second they are blinded."
    },
    "Osa": {
        "Pros": "Outstanding mechanical performance with a spectacular {kd} K/D ratio across {rounds} rounds.",
        "Focus_Areas": "A {win_rate} win rate indicates that your Talon Shields are being used passively rather than establishing aggressive lines of sight.",
        "Tactical_Strategy": "On Chalet, deploy your Talon Shield on the master bedroom window to lock down the solarium rotations and prevent defenders from retaking the balcony."
    },
    "Twitch": {
        "Pros": "Top-tier gunfighting efficiency with a stellar {kd} K/D ratio and excellent headshot rate of {hs}.",
        "Focus_Areas": "A {win_rate} win rate suggests that you are prioritizing individual kills over utilizing your Shock Drones to clear Mira windows and active denial.",
        "Tactical_Strategy": "On Oregon, use your Shock Drone during the prep phase to destroy Mute jammers and Bandit batteries, ensuring your hard breacher can open the laundry wall immediately."
    },
    "Denari": {
        "Pros": "Consistent defensive utility usage with a {win_rate} win rate and a {kd} K/D ratio.",
        "Focus_Areas": "Work on improving your position trading to push your K/D higher and secure more late-round scenarios.",
        "Tactical_Strategy": "On Skyscraper, utilize your unique gadget to delay attacks on the exhibition site, coordinating with an active roamer to pinch attackers."
    },
    "Blackbeard": {
        "Pros": "Decent mechanical effort over {rounds} rounds, despite operating with a very low {win_rate} win rate.",
        "Focus_Areas": "An abysmal {kd} K/D ratio and {win_rate} win rate indicate that Blackbeard is a major liability in your current champion-level playstyle.",
        "Tactical_Strategy": "On Kafe Dostoyevsky, if you must play Blackbeard, hold tight angles on the skylight or 3F windows to cut off defender rotations, avoiding direct horizontal entry gunfights."
    },
    "Lesion": {
        "Pros": "Good defensive contribution with {rounds} rounds played and a solid {win_rate} win rate.",
        "Focus_Areas": "A K/D ratio of {kd} is slightly below your average, suggesting you are taking early engagements before your Gu Mines can accumulate.",
        "Tactical_Strategy": "On Oregon, throw Gu Mines at the bottom of white stairs and attic drop-downs to gain early intel and prevent quick, silent plays by the attackers."
    },
    "Tubarão": {
        "Pros": "Excellent utility-fragging hybrid, holding a strong {win_rate} win rate and a {kd} K/D ratio.",
        "Focus_Areas": "Make sure you are coordinating your Zoto Canisters with Bandit batteries or Kaid claws to permanently destroy breach charges.",
        "Tactical_Strategy": "On Chalet, use your Zoto Canisters on the main garage wall to freeze and delay hard breachers, buying valuable time for your basement anchors."
    },
    "Ace": {
        "Pros": "Reliable hard-breaching presence with {rounds} rounds played and a positive {kd} K/D ratio.",
        "Focus_Areas": "A terrible {win_rate} win rate suggests that you are failing to open the primary walls or are getting picked off early in the round.",
        "Tactical_Strategy": "On Clubhouse, prioritize opening the CCTV outer wall from the safety of the platform, and do not peek the garage or red stairs until the breach is secured."
    },
    "Solid Snake": {
        "Pros": "Good round commitment with {rounds} rounds played, maintaining utility presence.",
        "Focus_Areas": "A low K/D of {kd} and poor win rate of {win_rate} indicate a struggle to secure key entries and establish map control.",
        "Tactical_Strategy": "On Villa, utilize your stealth and flanking capability to clear the top-floor roamers before they can rotate back to site, coordinating with your main entry tools to pinpoint active anchors."
    },
    "Maverick": {
        "Pros": "Solid entry gunplay with a {kd} K/D ratio and a respectable {win_rate} win rate.",
        "Focus_Areas": "Work on refining your blowtorch efficiency to open hatches quickly without exposing yourself to vertical pre-fires.",
        "Tactical_Strategy": "On Clubhouse, open a line of sight at the bottom of the CCTV wall to clear defender utility anchoring behind the server rack before your main breacher opens the wall."
    },
    "Lion": {
        "Pros": "High mechanical skill with a {kd} K/D ratio, showing excellent individual threat response.",
        "Focus_Areas": "A poor {win_rate} win rate suggests that your EE-ONE-D scans are being activated randomly rather than during active executes or defuser plants.",
        "Tactical_Strategy": "On Bank, activate your scans precisely when your team starts smoke-planting in the basement, freezing defenders in place and allowing easy vertical sprays."
    },
    "Thatcher": {
        "Pros": "Phenomenal K/D ratio of {kd} across {rounds} rounds, showcasing outstanding mechanical gunplay.",
        "Focus_Areas": "A win rate of {win_rate} is disappointing for a primary support, indicating that you are surviving too long without getting the main walls open.",
        "Tactical_Strategy": "On Kafe Dostoyevsky, ensure your EMPs are deployed to clear Kaid claws on the kitchen wall, and play close to your hard breacher to trade them out immediately."
    },
    "Jackal": {
        "Pros": "Elite mechanical fragger, holding an exceptional {kd} K/D ratio across {rounds} rounds.",
        "Focus_Areas": "A sub-optimal {win_rate} win rate suggests that you are hunting footprints in isolated areas rather than tracking roamers that threaten the main execute.",
        "Tactical_Strategy": "On Coastline, scan footprints early in the penthouse and theater areas to flush out roamers, driving them into the crosshairs of your rooftop anchors."
    }
}

MAP_TACTICAL_CORRECTIONS = {
    "Bank": "On Bank ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), prioritize clear of the CEO offices using Flores or Zero before attempting to open the main lobby walls, avoiding early roamer flanks from square stairs.",
    "Kafe Dostoyevsky": "On Kafe Dostoyevsky ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), establish top-down control by clearing 3F/Piano first with Gridlock or Nomad flank-watches before attempting to execute onto the 2F/1F sites.",
    "Border": "On Border ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), execute faster vertical control from the security room and break the floor above Armory lockers to flush out defenders anchoring behind half-wall.",
    "Nighthaven Labs": "On Nighthaven Labs ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), establish early control of the kitchen and pantry hallway before attempting a hard-breach of the outer wall, ensuring flank watch covers the warehouse run-outs.",
    "Chalet": "On Chalet ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), clear the solar/trophy rooms when attacking kitchen, and ensure that flank-watch grids or airjabs are placed on the library stairs and fireplace run-outs.",
    "Fortress": "On Fortress ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), utilize vertical plays from the roof and second-floor floors to clear Kaid/Bandit denial on the main site walls, as horizontal entries are heavily choke-pointed.",
    "Villa": "On Villa ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), prioritize clearing the study/aviary areas before pushing into Games/Aviary, and always bring a Thatcher or Flores to disable active denial from below.",
    "Oregon": "On Oregon ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), ensure a systematic sweep of the meeting room and attic to isolate the kids' room defenders, rather than tunnel-visioning on the main master bedroom windows.",
    "Consulate": "On Consulate ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), execute a coordinated push into the garage/basement by taking yellow stairs and security room control first, neutralizing defender active denial on the main garage door.",
    "Clubhouse": "On Clubhouse ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), when attacking CCTV/Cash, ensure that garage control is secured early to establish safe crossfires and cover the hard breacher on the main wall.",
    "Coastline": "On Coastline ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), coordinate roof and window angles to trap roamers inside penthouse or kitchen, avoiding uncoordinated individual entry duels that favor defender crossfires.",
    "Theme Park": "On Theme Park ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), clear the yellow corridor and drug lab areas before pushing into the main site, using Gridlock traps to secure the bunk room rotations.",
    "Skyscraper": "On Skyscraper ({att:.1f}% attack vs {def_:.1f}% defence — a {gap:.1f}-point gap), improve external window control on exhibition and tea room, and use Nomad's Airjabs to shut down aggressive defender run-outs from the terrace balconies."
}

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_role(op_name):
    if op_name in ATTACKER_OPERATORS:
        return "Attacker"
    elif op_name in DEFENDER_OPERATORS:
        return "Defender"
    else:
        return "Defender"

def main():
    processed_path = os.path.join('data', 'stats_processed.json')

    if not os.path.exists(processed_path):
        print(f"Error: {processed_path} does not exist.")
        return

    print("[r6data.eu Compiler] Loading processed stats...")
    data = load_data(processed_path)
    
    y11 = data['y11s1']
    summary = y11['summary']
    operators = y11['operators']
    maps = y11['maps']

    overall_kd = summary['kd']
    overall_wr = summary['win_rate']
    ranked_rating = summary['ranked_rating']
    username = summary.get('username', 'Unknown')
    platform = summary.get('platform', 'ubi')
    
    report_path = os.path.join('output', f'{username}_report.md')

    # Filter out operators with < 20 rounds entirely
    filtered_ops = [o for o in operators if o['rounds_played'] >= 20]

    # Calculate Attacker and Defender statistics
    att_wins = sum(o['wins'] for o in filtered_ops if get_role(o['name']) == 'Attacker')
    att_losses = sum(o['losses'] for o in filtered_ops if get_role(o['name']) == 'Attacker')
    def_wins = sum(o['wins'] for o in filtered_ops if get_role(o['name']) == 'Defender')
    def_losses = sum(o['losses'] for o in filtered_ops if get_role(o['name']) == 'Defender')
    att_wr = (att_wins / (att_wins + att_losses) * 100) if (att_wins + att_losses) > 0 else 0
    def_wr = (def_wins / (def_wins + def_losses) * 100) if (def_wins + def_losses) > 0 else 0

    print("[r6data.eu Compiler] Compiling markdown report sections...")
    
    worst_map = min(maps, key=lambda x: x['win_pct']) if maps else None
    worst_map_name = worst_map['name'] if worst_map else "Skyscraper"
    worst_map_wr = worst_map['win_rate'] if worst_map else "28.6%"
    worst_map_att_wr = worst_map['attack_win_pct'] if worst_map else 22.4
    
    if overall_kd < 0.85:
        asymmetry_note = ""
        asymmetry_gap = def_wr - att_wr
        if asymmetry_gap > 10.0:
            asymmetry_note = (
                f" This is further compounded by a severe execution gap between defense ({def_wr:.1f}%) and "
                f"attack ({att_wr:.1f}%), indicating that passive anchor play on defense is saving rounds "
                f"while attack executes completely stall due to lack of entry power."
            )
        diagnosis = (
            f"For {username}, the primary performance bottleneck in Y11S1 is a critical deficiency in "
            f"individual combat efficiency, holding a sub-par K/D of {overall_kd:.2f}. Losing early engagements and "
            f"failing to win trade-frags frequently leaves the team in disadvantaged 4v5 scenarios. This combat "
            f"weakness is especially evident on maps like {worst_map_name} where their win rate is heavily "
            f"depressed to {worst_map_wr}.{asymmetry_note}"
        )
    elif overall_kd < 1.00:
        diagnosis = (
            f"For {username}, the biggest performance bottleneck in Y11S1 lies in passive gunfight presence, "
            f"maintaining a neutral K/D of {overall_kd:.2f}. While holding their own in isolated duels, a lack of "
            f"opening entry impact limits their ability to break open rounds, resulting in a sub-optimal "
            f"{overall_wr} overall win rate. This is particularly evident on maps like {worst_map_name} where "
            f"their win rate is constrained to {worst_map_wr} due to a lack of offensive momentum."
        )
    else:
        asymmetry_gap = def_wr - att_wr
        if asymmetry_gap > 10.0:
            diagnosis = (
                f"{username}'s biggest performance bottleneck in Y11S1 is a severe asymmetry between attack and "
                f"defense round execution, as evidenced by a {att_wr:.1f}% attack win rate compared to a "
                f"{def_wr:.1f}% defense win rate. Despite maintaining a strong individual gunfighter profile with "
                f"a dominant {overall_kd:.2f} K/D, high individual lethality is not translating into objective wins "
                f"on attack. This is particularly critical on maps like {worst_map_name} where their attack win rate "
                f"falls to an abysmal {worst_map_att_wr:.1f}%."
            )
        else:
            diagnosis = (
                f"{username} maintains a balanced execution profile in Y11S1, with a strong K/D of {overall_kd:.2f}. "
                f"However, their primary bottleneck lies in converting strong general play into consistent round victories "
                f"(holding a {overall_wr} overall win rate). This challenge is prominent on maps like {worst_map_name} "
                f"(holding a {worst_map_wr} win rate), where tactical coordination during executes needs significant refinement."
            )
            
    sec1 = f"""### Section 1: Executive Summary

- **Y11S1 K/D:** {overall_kd:.2f}
- **Y11S1 Win Rate:** {overall_wr}
- **Ranked Rating:** {ranked_rating}

{diagnosis}
"""

    sorted_maps = sorted(maps, key=lambda x: x['win_pct'], reverse=True)
    map_rows = []
    for m in sorted_maps:
        map_rows.append(
            f"| {m['name']} | {m['matches']} | {m['win_rate']} | {m['attack_win_rate']} | {m['defense_win_rate']} | {m['kd_ratio']:.2f} | {m['headshot_percentage']} |"
        )
    
    map_table = "\n".join(map_rows)
    
    sec2 = f"""### Section 2: Map Performance Overview

| Map | Rounds | Win% | Attack Win% | Defence Win% | K/D | HS% |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{map_table}

![Map Attack vs Defence](output/charts/{username}/map_attack_vs_defence.png)
"""

    top_3 = sorted_maps[:3]
    top_map_texts = []
    for m in top_3:
        if m['name'] == 'Lair':
            text = f"**Lair** ({m['win_rate']} Win%): Strong defense ({m['defense_win_rate']} win rate) paired with relatively solid attack win rate ({m['attack_win_rate']}, well above the average) creates the most balanced map environment, showing excellent site understanding and rotation control."
        elif m['name'] == 'Bank':
            text = f"**Bank** ({m['win_rate']} Win%): An impressive {m['defense_win_rate']} defense win rate driven by highly effective roam setups and lockouts in the basement/vault areas, keeping attackers constantly at bay."
        elif m['name'] == 'Kafe Dostoyevsky':
            text = f"**Kafe Dostoyevsky** ({m['win_rate']} Win%): Outstanding combat execution with a stellar {m['kd_ratio']:.2f} K/D ratio on this map, showing that deep map knowledge and dominant mechanical skills are winning the crucial gunfights."
        else:
            text = f"**{m['name']}** ({m['win_rate']} Win%): Exceptional performance with {m['matches']} rounds and a strong {m['kd_ratio']:.2f} K/D ratio showing dominant mechanical presence."
        top_map_texts.append(f"- {text}")
        
    bottom_3 = sorted_maps[-3:]
    bottom_map_texts = []
    for m in bottom_3:
        if m['name'] == 'Emerald Plains':
            text = f"**Emerald Plains** ({m['win_rate']} Win%): A complete shutdown on defense and attack in its single played match (0% win rate), indicating that the map's complex corridor rotations and vertical angles remain unfamiliar or unpracticed."
        elif m['name'] == 'Outback':
            text = f"**Outback** ({m['win_rate']} Win%): Extremely low defense win rate of {m['defense_win_rate']} and equal attack win rate of {m['attack_win_rate']} in {m['matches']} matches, indicating a failure to establish solid roams on defense."
        elif m['name'] == 'Skyscraper':
            text = f"**Skyscraper** ({m['win_rate']} Win%): A severe failure on attack with an abysmal {m['attack_win_rate']} win rate despite a dominant {m['defense_win_rate']} defense win rate in {m['matches']} matches, pointing to a critical inability to clear defender utility."
        else:
            text = f"**{m['name']}** ({m['win_rate']} Win%): Struggles on attack side holding a low {m['attack_win_rate']} win rate, highlighting a key failure in executing site entry and utility clearing."
        bottom_map_texts.append(f"- {text}")
        
    sec3 = f"""### Section 3: Best & Worst Maps

#### Top 3 Maps (Protect / Veto)
{top_map_texts[0]}
{top_map_texts[1]}
{top_map_texts[2]}

#### Bottom 3 Maps (Ban / Avoid)
{bottom_map_texts[0]}
{bottom_map_texts[1]}
{bottom_map_texts[2]}
"""

    asymmetry_texts = []
    for m in sorted_maps:
        gap = m['defence_win_pct'] - m['attack_win_pct']
        if gap > 10:
            name = m['name']
            if name in MAP_TACTICAL_CORRECTIONS:
                correction = MAP_TACTICAL_CORRECTIONS[name].format(
                    att=m['attack_win_pct'],
                    def_=m['defence_win_pct'],
                    gap=gap
                )
            else:
                correction = f"On {name} ({m['attack_win_pct']:.1f}% attack vs {m['defence_win_pct']:.1f}% defence — a {gap:.1f}-point gap), prioritize clear of key areas and establish better team positioning on the attack side."
            asymmetry_texts.append(f"- **{name}**: {correction}")
            
    sec4 = f"""### Section 4: Attack vs Defence Asymmetry

The following maps exhibit a critical attack win rate deficit of more than 10 percentage points compared to defensive win rates. Direct tactical adjustments are required on each map:

{"\n".join(asymmetry_texts)}
"""

    attackers = [o for o in filtered_ops if get_role(o['name']) == "Attacker"]
    defenders = [o for o in filtered_ops if get_role(o['name']) == "Defender"]

    attackers_sorted = sorted(attackers, key=lambda x: x['rounds_played'], reverse=True)
    defenders_sorted = sorted(defenders, key=lambda x: x['rounds_played'], reverse=True)

    attacker_rows = []
    for o in attackers_sorted:
        sample_str = "⚠️" if o['small_sample'] or o['rounds_played'] < 50 else "--"
        attacker_rows.append(
            f"| {o['name']} | {o['rounds_played']} | {o['kd_ratio']:.2f} | {o['win_rate']} | {o['headshot_percentage']} | {o['success_index']:.4f} | {sample_str} |"
        )
    attacker_table = "\n".join(attacker_rows)

    defender_rows = []
    for o in defenders_sorted:
        sample_str = "⚠️" if o['small_sample'] or o['rounds_played'] < 50 else "--"
        defender_rows.append(
            f"| {o['name']} | {o['rounds_played']} | {o['kd_ratio']:.2f} | {o['win_rate']} | {o['headshot_percentage']} | {o['success_index']:.4f} | {sample_str} |"
        )
    defender_table = "\n".join(defender_rows)

    sec5 = f"""### Section 5: Operator Tables

#### Attackers

| Operator | Rounds | K/D | Win% | HS% | Success Index | Sample |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{attacker_table}

#### Defenders

| Operator | Rounds | K/D | Win% | HS% | Success Index | Sample |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
{defender_table}

#### Visual Operator Performance
![Operator Win Rates](output/charts/{username}/operator_winrate.png)

![Operator K/D Comparison](output/charts/{username}/operator_kd.png)
"""

    coaching_sections = []
    all_ops_sorted = sorted(filtered_ops, key=lambda x: x['rounds_played'], reverse=True)
    
    for o in all_ops_sorted:
        name = o['name']
        role = get_role(name)
        rounds = o['rounds_played']
        kd = o['kd_ratio']
        win_rate_clean = o['win_rate']
        win_rate_val = win_rate_clean.replace('%', '')
        
        if rounds >= 50:
            if name in COACHING_DATA:
                pros_text = COACHING_DATA[name]["Pros"].format(
                    win_rate=win_rate_clean,
                    kd=f"{kd:.2f}",
                    rounds=rounds,
                    hs=o['headshot_percentage']
                )
                focus_text = COACHING_DATA[name]["Focus_Areas"].format(
                    win_rate=win_rate_clean,
                    kd=f"{kd:.2f}",
                    rounds=rounds,
                    hs=o['headshot_percentage']
                )
                strat_text = COACHING_DATA[name]["Tactical_Strategy"]
            else:
                pros_text = f"Robust fragging output and map pressure with a {kd:.2f} K/D across {rounds} rounds."
                focus_text = f"Improve round win conversion from the current {win_rate_clean} by adjusting late-round positioning."
                strat_text = "Coordinate closely with team utility and prioritize site line lockouts over un-traded roaming duels."
                
            coaching_sections.append(
                f"#### {name} ({role}) — {rounds} rounds | K/D: {kd:.2f} | Win%: {win_rate_val}%\n\n"
                f"**Pros:** {pros_text}\n\n"
                f"**Focus Areas:** {focus_text}\n\n"
                f"**Tactical Strategy:** {strat_text}"
            )
        else:
            coaching_sections.append(
                f"#### {name} ({role}) — {rounds} rounds | K/D: {kd:.2f} | Win%: {win_rate_val}%\n\n"
                f"*Small sample — monitor over next 3–5 sessions*"
            )

    sec6 = "### Section 6: Operator Coaching Engine\n\n" + "\n\n---\n\n".join(coaching_sections)

    ban_map1 = bottom_3[0]['name']
    ban_map2 = bottom_3[1]['name']
    protect_map1 = top_3[0]['name']
    protect_map2 = top_3[1]['name']
    
    attackers_dynamic = [o for o in operators if get_role(o['name']) == 'Attacker']
    attackers_dynamic = sorted(attackers_dynamic, key=lambda x: x['rounds_played'], reverse=True)
    
    defenders_dynamic = [o for o in operators if get_role(o['name']) == 'Defender']
    defenders_dynamic = sorted(defenders_dynamic, key=lambda x: x['rounds_played'], reverse=True)
    
    if attackers_dynamic:
        top_att_3 = attackers_dynamic[:3]
        att_list_str = ", ".join([f"{o['name']} ({o['kd_float']:.2f} K/D, {o['win_rate']} WR)" for o in top_att_3])
        
        asymmetry_gap = def_wr - att_wr
        if asymmetry_gap > 10.0:
            asymmetry_str = (
                f"With a severe {asymmetry_gap:.1f} percentage point deficit between your defense ({def_wr:.1f}%) and "
                f"attack ({att_wr:.1f}%) win rates, your individual gunplay is not translating to round wins."
            )
        else:
            asymmetry_str = (
                f"Your attack win rate ({att_wr:.1f}%) is relatively balanced with your defense win rate ({def_wr:.1f}%), "
                f"showing a cohesive understanding of both phases."
            )
            
        most_played_att = top_att_3[0]
        att_spec_str = (
            f"On your most played attacker, `{most_played_att['name']}` ({most_played_att['kd_float']:.2f} K/D, {most_played_att['win_rate']} WR), "
            f"prioritize objective control: ensure the main walls or hatches are opened within the first 90 seconds. "
        )
        if len(top_att_3) > 1:
            second_att = top_att_3[1]
            att_spec_str += (
                f"When flexing to `{second_att['name']}` ({second_att['kd_float']:.2f} K/D, {second_att['win_rate']} WR), "
                f"coordinate with your team's entry operators to trade out kills rather than seeking isolated engagements."
            )
            
        tip1 = (
            f"**Optimizing Attacker Executions and Objective Focus:** "
            f"{username} currently relies on these top attacker tools: {att_list_str}. {asymmetry_str} {att_spec_str} "
            f"Shifting focus entirely to dynamic utility clearing and plant setup will directly solve your entry and post-plant bottlenecks."
        )
    else:
        tip1 = (
            "**Establish a Structured Attacker Operator Pool:** "
            "No attacker rounds were found in the current season data. To improve your offensive win rate, establish a core "
            "pool of 2-3 attackers (such as Thermite for hard breach, Nomad for flank watch, or Ace for versatility) "
            "and focus on systematic wall clears and trade-fragging with your team."
        )
        
    if defenders_dynamic:
        top_def_3 = defenders_dynamic[:3]
        def_list_str = ", ".join([f"{o['name']} ({o['kd_float']:.2f} K/D, {o['win_rate']} WR)" for o in top_def_3])
        
        most_played_def = top_def_3[0]
        def_spec_str = (
            f"Your defense is spearheaded by `{most_played_def['name']}` where you hold a `{most_played_def['kd_float']:.2f}` K/D "
            f"and a `{most_played_def['win_rate']}` win rate."
        )
        
        if len(top_def_3) > 1:
            second_def = top_def_3[1]
            def_spec_str += (
                f" Similarly, `{second_def['name']}` ({second_def['kd_float']:.2f} K/D, {second_def['win_rate']} WR) "
                f"provides strong utility coverage."
            )
            
        tip2 = (
            f"**Capitalizing on Defensive Strengths and Site Setup:** "
            f"Leveraging your top defensive operators: {def_list_str}. {def_spec_str} "
            f"Ensure your setups block key attacker drone routes in the early prep phase. "
            f"Focus on coordinating your gadget placement with active teammate crossfires to force attackers "
            f"into high-risk choke points where your mechanical skill dominates."
        )
    else:
        tip2 = (
            "**Establish a Cohesive Defensive Anchor and Roam Pool:** "
            "No defender rounds were found in the current season data. To stabilize your site defenses, "
            "select a couple of highly impactful meta defenders (like Mute or Lesion for utility/intel denial, "
            "or Smoke for late-round plant denial) and practice site setups that force attackers into tight angles."
        )
        
    tip3 = (
        "**Stack and Coordinate to Counter Ranked 2.0 Matchmaking:** "
        f"Since matchmaking in Y11S1 (Ranked 2.0) operates on hidden MMR rather than visible rank, your strong overall "
        f"K/D of {overall_kd:.2f} and {overall_wr} win rate matches you against highly coordinated Champion-level stacks. "
        "Solo-queuing heavily penalizes high mechanical output due to lack of trade-fragging. To maximize your "
        "impact, pre-stack with a consistent team, assign clear roles, and actively ban problematic maps like "
        f"**{ban_map1}** and **{ban_map2}** while protecting high-performing maps like **{protect_map1}** and **{protect_map2}**."
    )
    
    sec7 = f"""### Section 7: Ranked Climbing Tips (Y11S1 — Ranked 2.0)

Based on your current Y11S1 statistics, implement the following tactical vetos and strategic adaptations to climb the Champion leaderboards:

- **Top 2 Maps to Ban:** **{ban_map1}** and **{ban_map2}** (your lowest win rate maps)
- **Top 2 Maps to Protect/Veto:** **{protect_map1}** and **{protect_map2}** (your highest win rate maps)

#### 3 Actionable Climbing Tips:

1. {tip1}
2. {tip2}
3. {tip3}
"""

    # Assemble the entire report
    full_report = f"""# Rainbow Six Siege Tactical Coaching Report (Y11S1 Scope)
**Prepared for:** `{username}` ({platform.upper()})
**Standing:** `{ranked_rating}`

---

{sec1}

---

{sec2}

---

{sec3}

---

{sec4}

---

{sec5}

---

{sec6}

---

{sec7}
"""

    # Write the report
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
        
    print(f"[r6data.eu Compiler] Successfully wrote the report to {report_path}")

    # Generate Premium Standalone HTML Report
    html_path = report_path.replace('_report.md', '_report.html')
    
    import base64
    def get_base64_img(img_path):
        if not os.path.exists(img_path):
            return ""
        try:
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"Error encoding image {img_path}: {e}")
            return ""
            
    # Base64 charts for 100% self-contained file
    charts_dir = os.path.join('output', 'charts', username)
    map_chart_b64 = get_base64_img(os.path.join(charts_dir, 'map_attack_vs_defence.png'))
    winrate_chart_b64 = get_base64_img(os.path.join(charts_dir, 'operator_winrate.png'))
    kd_chart_b64 = get_base64_img(os.path.join(charts_dir, 'operator_kd.png'))

    # Format Map Rows
    map_rows_html = ""
    for m in sorted_maps:
        map_rows_html += f"""
        <tr>
            <td style="font-weight: 600; color: #f5f6fa;">{m['name']}</td>
            <td>{m['matches']}</td>
            <td style="font-weight: 600; color: {'#00b894' if m['win_rate_float'] >= 0.50 else '#ff7675'};">{m['win_rate']}</td>
            <td>{m['attack_win_rate']}</td>
            <td>{m['defense_win_rate']}</td>
            <td style="font-weight: 600; color: {'#00cec9' if m['kd_ratio'] >= 1.0 else '#a29bfe'};">{m['kd_ratio']:.2f}</td>
            <td>{m['headshot_percentage']}</td>
        </tr>
        """

    # Format Asymmetry list
    asymmetry_html = ""
    for m in sorted_maps:
        gap = m['defence_win_pct'] - m['attack_win_pct']
        if gap > 10:
            name = m['name']
            if name in MAP_TACTICAL_CORRECTIONS:
                correction = MAP_TACTICAL_CORRECTIONS[name].format(
                    att=m['attack_win_pct'],
                    def_=m['defence_win_pct'],
                    gap=gap
                )
            else:
                correction = f"On {name} ({m['attack_win_pct']:.1f}% attack vs {m['defence_win_pct']:.1f}% defence — a {gap:.1f}-point gap), prioritize clear of key areas and establish better team positioning on the attack side."
            asymmetry_html += f"""
            <div style="background: rgba(255, 118, 117, 0.05); border-left: 4px solid #ff7675; padding: 16px; border-radius: 8px; margin-bottom: 12px; font-size: 0.95rem; line-height: 1.5;">
                <strong>{name} Deficit:</strong> {correction}
            </div>
            """

    # Format Attacker Rows
    attacker_rows_html = ""
    for o in attackers_sorted:
        sample_str = '<span style="color: #ff9f43; font-weight: bold;">⚠️ Small Sample</span>' if o['small_sample'] else '<span style="color: #a0a5c0;">--</span>'
        attacker_rows_html += f"""
        <tr>
            <td style="font-weight: 600; color: #f5f6fa;">{o['name']}</td>
            <td>{o['rounds_played']}</td>
            <td style="font-weight: 600; color: {'#00cec9' if o['kd_ratio'] >= 1.0 else '#a29bfe'};">{o['kd_ratio']:.2f}</td>
            <td style="font-weight: 600; color: {'#00b894' if o['win_rate_float'] >= 0.50 else '#ff7675'};">{o['win_rate']}</td>
            <td>{o['headshot_percentage']}</td>
            <td>{o['success_index']:.4f}</td>
            <td>{sample_str}</td>
        </tr>
        """

    # Format Defender Rows
    defender_rows_html = ""
    for o in defenders_sorted:
        sample_str = '<span style="color: #ff9f43; font-weight: bold;">⚠️ Small Sample</span>' if o['small_sample'] else '<span style="color: #a0a5c0;">--</span>'
        defender_rows_html += f"""
        <tr>
            <td style="font-weight: 600; color: #f5f6fa;">{o['name']}</td>
            <td>{o['rounds_played']}</td>
            <td style="font-weight: 600; color: {'#00cec9' if o['kd_ratio'] >= 1.0 else '#a29bfe'};">{o['kd_ratio']:.2f}</td>
            <td style="font-weight: 600; color: {'#00b894' if o['win_rate_float'] >= 0.50 else '#ff7675'};">{o['win_rate']}</td>
            <td>{o['headshot_percentage']}</td>
            <td>{o['success_index']:.4f}</td>
            <td>{sample_str}</td>
        </tr>
        """

    # Format Operator Coaching Blocks
    coaching_html = ""
    for o in all_ops_sorted:
        name = o['name']
        role = get_role(name)
        rounds = o['rounds_played']
        kd = o['kd_ratio']
        win_rate_clean = o['win_rate']
        win_rate_val = win_rate_clean.replace('%', '')
        
        if rounds >= 50:
            if name in COACHING_DATA:
                pros_text = COACHING_DATA[name]["Pros"].format(
                    win_rate=win_rate_clean,
                    kd=f"{kd:.2f}",
                    rounds=rounds,
                    hs=o['headshot_percentage']
                )
                focus_text = COACHING_DATA[name]["Focus_Areas"].format(
                    win_rate=win_rate_clean,
                    kd=f"{kd:.2f}",
                    rounds=rounds,
                    hs=o['headshot_percentage']
                )
                strat_text = COACHING_DATA[name]["Tactical_Strategy"]
            else:
                pros_text = f"Robust fragging output and map pressure with a {kd:.2f} K/D across {rounds} rounds."
                focus_text = f"Improve round win conversion from the current {win_rate_clean} by adjusting late-round positioning."
                strat_text = "Coordinate closely with team utility and prioritize site line lockouts over un-traded roaming duels."
                
            coaching_html += f"""
            <div style="background: #161720; border: 1px solid #262837; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.35);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #262837; padding-bottom: 12px; margin-bottom: 16px;">
                    <span style="font-size: 1.3rem; font-weight: 800; color: #f5f6fa;">{name}</span>
                    <span style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 6px 12px; border-radius: 20px; background: { 'rgba(84, 160, 255, 0.15)' if role == 'Attacker' else 'rgba(0, 206, 201, 0.15)' }; color: { '#54a0ff' if role == 'Attacker' else '#00cec9' };">{role}</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; text-align: center; background: #1d1e2a; padding: 12px; border-radius: 8px;">
                    <div><div style="font-size: 0.75rem; color: #a0a5c0; text-transform: uppercase; font-weight: 700;">Rounds</div><div style="font-size: 1.15rem; font-weight: 800; color: #f5f6fa; margin-top: 4px;">{rounds}</div></div>
                    <div><div style="font-size: 0.75rem; color: #a0a5c0; text-transform: uppercase; font-weight: 700;">K/D</div><div style="font-size: 1.15rem; font-weight: 800; color: #00cec9; margin-top: 4px;">{kd:.2f}</div></div>
                    <div><div style="font-size: 0.75rem; color: #a0a5c0; text-transform: uppercase; font-weight: 700;">Win Rate</div><div style="font-size: 1.15rem; font-weight: 800; color: #00b894; margin-top: 4px;">{win_rate_clean}</div></div>
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #d1d4e0;">
                    <p style="margin-bottom: 12px;"><strong>PROS:</strong> {pros_text}</p>
                    <p style="margin-bottom: 12px;"><strong>FOCUS AREAS:</strong> {focus_text}</p>
                    <p style="margin-bottom: 0;"><strong>TACTICAL STRATEGY:</strong> <span style="color: #f5cd79; font-weight: 500;">{strat_text}</span></p>
                </div>
            </div>
            """
        else:
            coaching_html += f"""
            <div style="background: #161720; border: 1px solid #262837; border-radius: 12px; padding: 16px; margin-bottom: 16px; opacity: 0.65; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.1rem; font-weight: 700; color: #f5f6fa; margin-right: 12px;">{name}</span>
                    <span style="font-size: 0.8rem; color: #a0a5c0;">{rounds} rounds | K/D: {kd:.2f} | Win%: {win_rate_val}%</span>
                </div>
                <div style="font-style: italic; font-size: 0.85rem; color: #ff9f43; font-weight: 500;">⚠️ Small Sample — monitor over next 3–5 sessions</div>
            </div>
            """

    # HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R6 Tactical Coaching Report — {username}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0c0d12;
            --card-bg: #161720;
            --text-primary: #f5f6fa;
            --text-secondary: #a0a5c0;
            --accent-gold: #e1b12c;
            --accent-teal: #00cec9;
            --accent-red: #ff7675;
            --accent-green: #00b894;
            --accent-blue: #54a0ff;
            --border-color: #262837;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            display: flex;
            min-height: 100vh;
        }}
        
        #sidebar {{
            width: 300px;
            background-color: #12131b;
            border-right: 1px solid var(--border-color);
            height: 100vh;
            position: fixed;
            padding: 30px 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            z-index: 100;
        }}
        
        #main-content {{
            margin-left: 300px;
            padding: 50px;
            width: calc(100% - 300px);
            max-width: 1200px;
            box-sizing: border-box;
        }}
        
        .logo-section {{
            margin-bottom: 40px;
        }}
        
        .logo-title {{
            font-size: 1.4rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, var(--accent-gold), var(--accent-teal));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .logo-sub {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 2px;
            margin-top: 4px;
        }}
        
        .nav-item {{
            display: flex;
            align-items: center;
            padding: 14px 18px;
            border-radius: 10px;
            color: var(--text-secondary);
            text-decoration: none;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .nav-item:hover {{
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-primary);
        }}
        
        .nav-item.active {{
            background: rgba(0, 206, 201, 0.1);
            color: var(--accent-teal);
            border-color: rgba(0, 206, 201, 0.2);
        }}
        
        .player-tag {{
            background: #1c1d29;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border-color);
            margin-top: auto;
        }}
        
        .player-name {{
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--text-primary);
        }}
        
        .player-platform {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--accent-teal);
            font-weight: 700;
            margin-top: 4px;
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }}
        
        .card-title {{
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 24px;
            color: var(--accent-gold);
            display: flex;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-box {{
            background: #1d1e2a;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border-left: 4px solid var(--accent-teal);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-val {{
            font-size: 2.2rem;
            font-weight: 900;
            margin-top: 8px;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.4s ease forwards;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(15px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 0.95rem;
        }}
        
        th, td {{
            padding: 16px 20px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: #12131b;
            color: var(--text-secondary);
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 1.5px;
        }}
        
        tr:hover {{
            background-color: rgba(255,255,255,0.015);
        }}
        
        .chart-img {{
            max-width: 100%;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin: 20px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.5);
        }}
        
        .veto-card {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .veto-box {{
            padding: 24px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
        }}
        
        .veto-ban {{
            background: rgba(255, 118, 117, 0.05);
            border-left: 4px solid var(--accent-red);
        }}
        
        .veto-protect {{
            background: rgba(0, 184, 148, 0.05);
            border-left: 4px solid var(--accent-green);
        }}
        
        .veto-header {{
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}
        
        .veto-val {{
            font-size: 1.5rem;
            font-weight: 800;
        }}
        
        .tip-box {{
            background: #1c1d29;
            border: 1px solid var(--border-color);
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            line-height: 1.6;
            font-size: 0.98rem;
        }}
        
        .tip-number {{
            display: inline-block;
            background: var(--accent-gold);
            color: var(--bg-color);
            font-weight: 900;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            text-align: center;
            line-height: 24px;
            margin-right: 10px;
            font-size: 0.85rem;
        }}
        
        .diagnosis-text {{
            font-size: 1.1rem;
            line-height: 1.7;
            color: #d1d4e0;
            border-left: 4px solid var(--accent-gold);
            padding-left: 20px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="logo-section">
            <div class="logo-title">ANTIGRAVITY R6</div>
            <div class="logo-sub">TACTICAL COACHING</div>
        </div>
        
        <div style="flex-grow: 1; margin-top: 20px;">
            <div class="nav-item active" onclick="switchTab('sec-summary', this)">Executive Summary</div>
            <div class="nav-item" onclick="switchTab('sec-maps', this)">Map Performance</div>
            <div class="nav-item" onclick="switchTab('sec-asymmetry', this)">Asymmetry Analytics</div>
            <div class="nav-item" onclick="switchTab('sec-operators', this)">Operator Database</div>
            <div class="nav-item" onclick="switchTab('sec-coaching', this)">Coaching Engine</div>
            <div class="nav-item" onclick="switchTab('sec-climbing', this)">Climbing Tips</div>
        </div>
        
        <div class="player-tag">
            <div class="player-name">{username}</div>
            <div class="player-platform">{platform.upper()} — {ranked_rating}</div>
        </div>
    </div>

    <div id="main-content">
        
        <!-- SECTION 1: Summary -->
        <div id="sec-summary" class="tab-content active">
            <div class="card">
                <div class="card-title">Y11S1 Performance Index</div>
                <div class="stats-grid">
                    <div class="stat-box" style="border-left-color: var(--accent-gold);">
                        <div class="stat-label">Season K/D</div>
                        <div class="stat-val" style="color: var(--accent-gold);">{overall_kd:.2f}</div>
                    </div>
                    <div class="stat-box" style="border-left-color: var(--accent-green);">
                        <div class="stat-label">Win Rate</div>
                        <div class="stat-val" style="color: var(--accent-green);">{overall_wr}</div>
                    </div>
                    <div class="stat-box" style="border-left-color: var(--accent-blue);">
                        <div class="stat-label">Rank Standing</div>
                        <div class="stat-val" style="color: var(--accent-blue); font-size: 1.5rem; line-height: 2.2rem; font-weight: 800; margin-top: 8px;">{ranked_rating}</div>
                    </div>
                </div>
                <div style="margin-top: 30px;">
                    <div class="stat-label" style="margin-bottom: 10px;">Primary Performance Diagnosis</div>
                    <p class="diagnosis-text">{diagnosis}</p>
                </div>
            </div>
        </div>
        
        <!-- SECTION 2: Maps -->
        <div id="sec-maps" class="tab-content">
            <div class="card">
                <div class="card-title">Map Performance Registry</div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Map</th>
                                <th>Rounds</th>
                                <th>Win%</th>
                                <th>Attack Win%</th>
                                <th>Defence Win%</th>
                                <th>K/D</th>
                                <th>HS%</th>
                            </tr>
                        </thead>
                        <tbody>
                            {map_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Visual Map Win Rates Split</div>
                <div class="chart-container">
                    <img src="{map_chart_b64}" class="chart-img" alt="Map Attack vs Defence split" />
                </div>
            </div>
        </div>
        
        <!-- SECTION 3: Asymmetry -->
        <div id="sec-asymmetry" class="tab-content">
            <div class="card">
                <div class="card-title">Attack vs Defence Asymmetry</div>
                <p style="color: var(--text-secondary); margin-bottom: 20px; line-height: 1.5;">
                    The following active competitive maps exhibit an attack win rate deficit of more than 10 percentage points compared to defense. Implement these targeted adjustments:
                </p>
                {asymmetry_html}
            </div>
            
            <div class="card">
                <div class="card-title">Best & Worst Map splits</div>
                <div class="veto-card">
                    <div class="veto-box veto-protect">
                        <div class="veto-header">Top 2 Maps (Protect / Veto)</div>
                        <div class="veto-val" style="color: var(--accent-green);">{protect_map1} & {protect_map2}</div>
                    </div>
                    <div class="veto-box veto-ban">
                        <div class="veto-header">Lowest 2 Maps (Ban / Avoid)</div>
                        <div class="veto-val" style="color: var(--accent-red);">{ban_map1} & {ban_map2}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- SECTION 4: Operators -->
        <div id="sec-operators" class="tab-content">
            <div class="card">
                <div class="card-title">Attacker Operator Registry</div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Operator</th>
                                <th>Rounds</th>
                                <th>K/D</th>
                                <th>Win%</th>
                                <th>HS%</th>
                                <th>Success Index</th>
                                <th>Sample Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {attacker_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Defender Operator Registry</div>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Operator</th>
                                <th>Rounds</th>
                                <th>K/D</th>
                                <th>Win%</th>
                                <th>HS%</th>
                                <th>Success Index</th>
                                <th>Sample Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {defender_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Visual Operator Performance Analytics</div>
                <div class="chart-container">
                    <img src="{winrate_chart_b64}" class="chart-img" style="margin-bottom: 30px;" alt="Operator Win rates" />
                    <img src="{kd_chart_b64}" class="chart-img" alt="Operator K/D ratios" />
                </div>
            </div>
        </div>
        
        <!-- SECTION 5: Coaching -->
        <div id="sec-coaching" class="tab-content">
            <div class="card" style="border: none; background: transparent; padding: 0; box-shadow: none;">
                <div class="card-title" style="border-bottom: 1px solid var(--border-color); padding-bottom: 12px; margin-bottom: 24px;">Operator Coaching Engine</div>
                {coaching_html}
            </div>
        </div>
        
        <!-- SECTION 6: Climbing Tips -->
        <div id="sec-climbing" class="tab-content">
            <div class="card">
                <div class="card-title">Ranked 2.0 Strategic Climbing Tips</div>
                <div class="veto-card" style="margin-bottom: 30px;">
                    <div class="veto-box veto-ban">
                        <div class="veto-header">Active Veto Phase (Maps to Ban)</div>
                        <div class="veto-val" style="color: var(--accent-red);">{ban_map1} & {ban_map2}</div>
                    </div>
                    <div class="veto-box veto-protect">
                        <div class="veto-header">Comfort Protect Vetoes</div>
                        <div class="veto-val" style="color: var(--accent-green);">{protect_map1} & {protect_map2}</div>
                    </div>
                </div>
                
                <div class="tip-box">
                    <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 10px; color: var(--accent-gold);">
                        <span class="tip-number">1</span> Attack Strategy & Objective Opening
                    </div>
                    <p style="color: #d1d4e0; font-size: 0.95rem; line-height: 1.6;">{tip1}</p>
                </div>
                
                <div class="tip-box">
                    <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 10px; color: var(--accent-teal);">
                        <span class="tip-number">2</span> Defense Synergy & Choke Lockdown
                    </div>
                    <p style="color: #d1d4e0; font-size: 0.95rem; line-height: 1.6;">{tip2}</p>
                </div>
                
                <div class="tip-box">
                    <div style="font-weight: 800; font-size: 1.1rem; margin-bottom: 10px; color: var(--accent-blue);">
                        <span class="tip-number">3</span> Hidden MMR and Stack Management
                    </div>
                    <p style="color: #d1d4e0; font-size: 0.95rem; line-height: 1.6;">{tip3}</p>
                </div>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId, navElement) {{
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => {{
                content.classList.remove('active');
            }});
            
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {{
                item.classList.remove('active');
            }});
            
            document.getElementById(tabId).classList.add('active');
            navElement.classList.add('active');
            
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
    </script>
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"[r6data.eu Compiler] Successfully compiled standalone premium HTML report to: {html_path}")

if __name__ == '__main__':
    main()
