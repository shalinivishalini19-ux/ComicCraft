# ComicCraft - AI Comic Story Creator

Turn a story idea into a 5-panel comic with pictures, narration, dialogue and a downloadable PDF.

| Step | Tool | File |
|------|------|------|
| Panel outline | Gemini Flash | `app/gemini_flash.py` |
| Narration + dialogue | Gemini Pro | `app/gemini_pro.py` |
| Panel images | Stable Diffusion (Diffusers) | `app/image_generator.py` |
| Layout binding | Python | `app/layout_builder.py` |
| PDF export | FPDF2 | `app/exporters.py` |
| Routes / API | FastAPI | `app/routes.py`, `app/main.py` |

## Project structure

```
comiccraft/
├── app/                  main.py, routes.py, config.py, gemini_client.py, gemini_flash.py,
│                         gemini_pro.py, image_generator.py, layout_builder.py, exporters.py
├── templates/            index.html, comic_preview.html, export_success.html
├── static/               css/, img/, fonts/ (PDF font), panels/ (images), exports/ (PDFs)
├── tests/test_app.py     automated tests (AI calls mocked)
├── check_setup.py        verifies keys, models, GPU and fonts
├── .env / .env.example   API keys and settings
├── requirements.txt
└── .vscode/              debug + test settings
```

## 1. Setup in VS Code

1. Install **Python 3.10 - 3.12** (python.org) and **VS Code** with the **Python** extension.
2. Unzip the project, then in VS Code: **File > Open Folder...** and choose the `comiccraft` folder.
3. Open the terminal: **Terminal > New Terminal**.
4. Create and activate a virtual environment:

   **Windows (PowerShell)**
   ```powershell
   python -m venv comiccraft-env
   comiccraft-env\Scripts\Activate.ps1
   ```
   If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process Bypass` first (or use `comiccraft-env\Scripts\activate.bat` in Command Prompt).

   **macOS / Linux**
   ```bash
   python3 -m venv comiccraft-env
   source comiccraft-env/bin/activate
   ```
5. When VS Code asks "We noticed a new environment", click **Yes**. Otherwise press `Ctrl+Shift+P`, choose **Python: Select Interpreter** and pick `comiccraft-env`.
6. Install the dependencies (torch is large, so this takes a few minutes):
   ```bash
   pip install -r requirements.txt
   ```
   *NVIDIA GPU on Windows?* `pip` installs a CPU-only torch by default. For GPU speed run this **after** step 6:
   `pip install torch --index-url https://download.pytorch.org/whl/cu124 --force-reinstall`

## 2. Add your API key

1. Get a free Gemini key: <https://aistudio.google.com/apikey>.
2. Open `.env` and replace `your_gemini_api_key_here` with your key. Do not add quotes.
3. Check everything:
   ```bash
   python check_setup.py
   ```
   Every line should say `[ OK ]`.

**No GPU, or just want to try the app quickly?** Set `IMAGE_BACKEND=placeholder` in `.env`. Panels then get instant placeholder images and everything else (Gemini story, layout, preview, PDF) still works. Switch back to `diffusers` for real AI images.

## 3. Run the app

```bash
uvicorn app.main:app --reload
```
or press **F5** in VS Code and pick **ComicCraft: run FastAPI (uvicorn)**.

- App: <http://127.0.0.1:8000>
- Interactive API docs: <http://127.0.0.1:8000/docs>

The first real image generation downloads Stable Diffusion (about 4-5 GB, one time). A comic takes roughly 1 minute on a GPU and 5-15 minutes on a CPU. Lower `SD_STEPS` (for example `15`) or `SD_WIDTH`/`SD_HEIGHT` (for example `384`) in `.env` to speed up CPU runs.

## 4. Test it

**In the browser**
1. Open <http://127.0.0.1:8000>, keep the sample story and click **Create my comic**.
2. Read the panels on the preview page.
3. Click **Download your comic as PDF**. The PDF downloads and you land on the success page.
4. Try a different tone or art style (for example Funny + Comic Book) to regenerate the whole comic.

**API endpoints** (from `/docs`, or PowerShell/curl)
```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/test-image?prompt=a%20red%20fox%20in%20a%20forest"
curl -X POST http://127.0.0.1:8000/generate-comic/json -H "Content-Type: application/json" \
  -d '{"prompt":"A brave fox exploring an enchanted forest","character_name":"Free","setting":"forest","tone":"funny","style":"comic book"}'
```

**Automated tests** (no API key or GPU needed, AI is mocked)
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Configuration (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `GEMINI_API_KEY` | - | Required |
| `GEMINI_FLASH_MODEL` | `gemini-3.8-flash` | Panel outline |
| `GEMINI_PRO_MODEL` | `gemini-3.1-pro-preview` | Story + dialogue |
| `GEMINI_FALLBACK_MODEL` | `gemini-3.8-flash` | Used automatically if the model above fails |
| `IMAGE_BACKEND` | `diffusers` | `diffusers` or `placeholder` |
| `SD_MODEL_ID` | `stable-diffusion-v1-5/stable-diffusion-v1-5` | Hugging Face model |
| `SD_STEPS` / `SD_WIDTH` / `SD_HEIGHT` | `25` / `512` / `512` | Image quality vs speed |
| `PANEL_COUNT` | `5` | 3 to 8 panels |

Restart the server after editing `.env`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "GEMINI_API_KEY is missing" | Put your key in `.env` (not `.env.example`) and restart uvicorn. |
| "Gemini model ... was not found" | Google renames and retires models. Run `python check_setup.py`, then set `GEMINI_FLASH_MODEL` / `GEMINI_PRO_MODEL` to a listed name. |
| "quota or rate limit reached" | Wait a minute, or use a Flash model for both roles. |
| Panels show yellow placeholder boxes | Stable Diffusion failed (see the terminal log for the reason), or `IMAGE_BACKEND=placeholder` is set. |
| `CUDA out of memory` | Lower `SD_WIDTH` / `SD_HEIGHT` to `384`, or use the CPU. |
| Very slow images | You are on the CPU. Use a GPU, fewer `SD_STEPS`, or `PANEL_COUNT=3`. |
| `ModuleNotFoundError: app` | Run uvicorn from the project root (the folder containing `app/`). |
| `ModuleNotFoundError` for any other package | The virtual environment is not active. Re-run the activate command. |
| PDF text shows `?` characters | Keep `static/fonts/DejaVuSans.ttf` in place (it is included). |

## Notes on the project document

The original documentation names `gemini-1.5-flash` / `gemini-1.5-pro` and `runwayml/stable-diffusion-v1-5`. Those no longer work: Google retired the 1.5 models and the RunwayML repository was removed from Hugging Face. This project uses current equivalents (all configurable in `.env`), the maintained `google-genai` SDK instead of `google-generativeai`, and `fpdf2` instead of the old `fpdf` package.
