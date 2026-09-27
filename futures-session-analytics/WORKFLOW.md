# Workflow

```mermaid
flowchart LR
    A[Yahoo Finance hourly bars] --> B[fetch_preprocess_data.py]
    B --> C[Timezone conversion and session pairing]
    C --> D[main_analysis.py]
    D --> E[Rolling diagnostics and six buckets]
    D --> F[In-sample OLS and equity metrics]
    E --> G[generate_dashboard.py]
    F --> G
    G --> H[dashboard_template.html + embedded JSON]
    H --> I[index.html]
    I --> J[GitHub Pages interactive dashboard]
```

Run locally from the parent project directory:

```bash
FSA_USE_CACHED=1 python -m futures_session_analytics.generate_dashboard
python -m http.server 8000 --directory futures_session_analytics
```

For a fresh Yahoo download, omit `FSA_USE_CACHED=1`.
