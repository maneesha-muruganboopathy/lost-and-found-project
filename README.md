# Lost and Found Matcher

## Run in VS Code terminal (Windows)
1. Extract the ZIP and open the extracted folder in VS Code.
2. Open Terminal and run:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
If PowerShell blocks activation, install dependencies with `python -m pip install -r requirements.txt`, then run `python main.py`.

## Input CSVs
Edit `data/lost.csv` and `data/found.csv`. Columns are `id,date,report`; date format is `YYYY-MM-DD`. Example rows are included.

## AI extraction (optional)
Set `OPENAI_API_KEY` in the terminal environment to enable AI extraction. Without it, keyword extraction runs offline. The fallback may miss information, so review vague reports.
PowerShell example (terminal session only): `$env:OPENAI_API_KEY="your-key-here"`
Never put your key in source code.

## Outputs
- `output/matches.csv`: suggested pairs, sorted by score
- `output/no_match.csv`: lost reports with no suggestion
- `output/unclaimed.csv`: found reports matched to none
- `output/summary.txt`: counts and multiple-claim alerts

Matches are suggestions only; ownership is never automatically decided.
