"""Run `python check_setup.py` to verify your ComicCraft setup before starting the server."""
import sys

from app import config


def line(ok: bool, text: str):
    print(("[ OK ] " if ok else "[FAIL] ") + text)


def check_gemini():
    if not config.GEMINI_API_KEY:
        line(False, "GEMINI_API_KEY is not set in .env")
        return
    line(True, "GEMINI_API_KEY found")
    try:
        from google import genai
        from app.gemini_client import generate_text

        client = genai.Client(api_key=config.GEMINI_API_KEY)
        names = sorted(m.name.replace("models/", "") for m in client.models.list() if "gemini" in m.name)
        print("       Gemini models your key can see (first 20):", ", ".join(names[:20]) or "none")
        for role, model in (("outline (Flash)", config.GEMINI_FLASH_MODEL), ("story (Pro)", config.GEMINI_PRO_MODEL)):
            line(model in names, f"{role} model '{model}' is listed for your key")
        reply = generate_text(config.GEMINI_FLASH_MODEL, "Reply with the single word: OK")
        line(True, f"Test request succeeded: {reply[:40]!r}")
    except Exception as exc:
        line(False, f"Gemini check failed: {exc}")


def check_images():
    print(f"       IMAGE_BACKEND={config.IMAGE_BACKEND}, SD_MODEL_ID={config.SD_MODEL_ID}")
    if config.IMAGE_BACKEND == "placeholder":
        line(True, "Placeholder images enabled (no GPU / model download needed)")
        return
    try:
        import diffusers
        import torch

        if torch.cuda.is_available():
            device = f"CUDA GPU ({torch.cuda.get_device_name(0)})"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "Apple GPU (MPS)"
        else:
            device = "CPU only - works, but each image can take 1-3 minutes"
        line(True, f"torch {torch.__version__}, diffusers {diffusers.__version__}; device: {device}")
    except ImportError as exc:
        line(False, f"Missing image libraries: {exc}. Run: pip install -r requirements.txt")


def check_pdf():
    try:
        import fpdf

        line(True, f"fpdf2 installed (version {getattr(fpdf, '__version__', 'unknown')})")
    except ImportError:
        line(False, "fpdf2 is not installed. Run: pip install -r requirements.txt")
    font = config.FONTS_DIR / "DejaVuSans.ttf"
    line(font.is_file(), f"PDF font present: {font}")


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]} | project folder: {config.BASE_DIR}\n")
    check_gemini()
    check_images()
    check_pdf()
