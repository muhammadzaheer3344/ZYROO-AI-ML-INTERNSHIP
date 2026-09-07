from pathlib import Path
import runpy


APP_PATH = Path(__file__).parent / "WEEK 1 TASK 1 AI Document Intelligence and Workflow Platform" / "app.py"

runpy.run_path(str(APP_PATH), run_name="__main__")
