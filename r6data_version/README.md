# R6Data.eu API Siege Stats & Coaching Analysis

This project folder contains a data-driven coaching report generator utilizing the high-speed REST API from [r6data.eu](https://r6data.eu).

## Prerequisites

1.  **Obtain an API Key**:
    *   Visit [r6data.eu](https://r6data.eu) and create an account.
    *   Generate a free API key from your developer dashboard.
2.  **Configure Environment**:
    *   Open the [.env](file:///z:/Gemini%20Stuff/siege-analysis/r6data_version/.env) file in this folder.
    *   Set `R6DATA_API_KEY` to your generated key:
        ```env
        R6DATA_API_KEY=your_key_here
        ```
    *   Ensure your `UBISOFT_USERNAME` and `UBISOFT_PLATFORM` are correct (default is `Amlenk` on `ubi` / Ubisoft Connect).

## Running the Pipeline

You can run the script to fetch your latest stats and generate the coaching report:

```bash
# 1. Fetch fresh stats from r6data.eu and save to data/raw/
python fetch_stats.py

# 2. Run calculations and compile a deeply insightful, data-driven report
python generate_report.py
```

The output report will be generated at [r6data_version/output/coaching_report.md](file:///z:/Gemini%20Stuff/siege-analysis/r6data_version/output/coaching_report.md) with active suggestions and advice.
