# Futures Session Analytics

Interactive Python research into day-versus-overnight returns, rolling relationships, six signed magnitude buckets, and in-sample strategy diagnostics.

## Open the dashboard

After enabling GitHub Pages, open [`index.html`](index.html) or the published Pages URL. The dashboard includes a visible-period selector, OLS versus always-long strategy selector, equity curve, and rolling correlation chart.

## Run the workflow

```bash
python -m futures_session_analytics.run_pipeline
```

The workflow downloads Yahoo Finance hourly data, constructs paired sessions, runs the analysis, and writes `futures_session_analytics/index.html`.

This is an exploratory in-sample research prototype, not live performance.
