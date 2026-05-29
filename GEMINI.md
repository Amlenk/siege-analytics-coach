# Siege Analysis Project

## What this does
Fetches Rainbow Six Siege ranked stats via tracker.gg API 
and generates a coaching report.

## Data source
tracker.gg public API — key is in .env as TRACKER_GG_API_KEY

## When I ask for analysis, always:
1. Fetch fresh data from the API first
2. Save raw data to /data/raw/
3. Run stats calculations
4. Generate a markdown report in /output/
