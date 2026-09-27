"""One-command workflow: fetch, analyze, and render the interactive dashboard."""
from .generate_dashboard import generate_dashboard
if __name__ == "__main__": print(f"Dashboard written to {generate_dashboard()}")
