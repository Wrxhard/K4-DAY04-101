# Streamlit UI - IT Helpdesk Agent

## Requirements

- Python 3.10 or newer.
- One supported provider API key.
- Run commands from `starter_v0/`.

## Setup on Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add one key to `.env`, for example `OPENAI_API_KEY`. Never commit `.env` or
paste a key into the UI. The app automatically selects the first configured
provider. `DAY04_UI_PROVIDER`, `DAY04_UI_MODEL`, `DAY04_UI_VERSION`,
`DAY04_UI_HISTORY_WINDOW`, and `DAY04_UI_MAX_TOOL_ROUNDS` may override UI
defaults.

## Verify and run

```powershell
python -m compileall -q .
python scripts/preflight_provider.py --provider openai
python -m streamlit run app.py
```

Open `http://localhost:8501/`. Use the same provider in preflight and the UI.
Provider and version are locked after the first message so transcript metadata
cannot change during a session. Select **Hội thoại mới** to change them.

Run the deterministic UI regression suite without provider quota:

```powershell
python -m unittest ui_tests.test_streamlit_app -v
```

Run all five required scenarios through Streamlit with a live provider:

```powershell
python scripts/check_ui_demo.py --provider openai --model gpt-4o-mini
```

The live checker returns a nonzero exit code when observed tool/status behavior
does not match the lab scenario. It preserves the run under
`artifacts/evidence/ui/live_<timestamp>/` for review.

## Evidence and transcripts

Each session writes a complete JSON transcript after every turn to
`transcripts/`. The sidebar shows the active path, save result, artifact
version, prompt hash, tools hash, and a download button. This directory is
ignored by Git because live transcripts may contain user input. Review a
transcript for secrets before copying selected evidence into a tracked report
or evidence directory.

The UI reuses `run_model_tool_loop()` and displays tool names, arguments,
results/errors, and round numbers. `waiting_for_user`, `provider_error`, and
`max_tool_rounds` remain distinct runtime states.

## Known limitations

- Model behavior is nondeterministic; rehearse demo scenarios with the final
  artifact and provider.
- A model may ask a clarification in plain text without calling `clarify`.
  The UI truthfully shows runtime status and does not infer or fabricate a tool
  event. Record this as an agent failure.
- The app is synchronous: one session waits for the provider call to finish,
  while a spinner shows that processing is in progress.
- External device search additionally requires `TAVILY_API_KEY`.
