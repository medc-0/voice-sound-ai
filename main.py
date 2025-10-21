import os
import uuid
import threading
from typing import Optional

import pyttsx3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates


app = FastAPI(title="Offline TTS Server")

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def choose_voice(engine, language: str = "en", gender: Optional[str] = None):
    voices = engine.getProperty("voices")
    language = (language or "en").lower()
    gender = (gender or "").lower()

    def voice_matches(v):
        langs = []
        try:
            langs = [l.decode("utf-8").lower() if isinstance(l, (bytes, bytearray)) else str(l).lower() for l in getattr(v, "languages", [])]
        except Exception:
            langs = []
        name = getattr(v, "name", "").lower()
        id_ = getattr(v, "id", "").lower()
        # match language codes or name snippets
        lang_ok = any(language in l for l in langs) or language in name or language in id_
        if not lang_ok:
            # fallback: match 'german' or 'english' in name
            if language.startswith("de") and ("german" in name or "de" in id_):
                lang_ok = True
            if language.startswith("en") and ("english" in name or "en" in id_):
                lang_ok = True
        if not gender:
            return lang_ok
        if gender.startswith("f") and ("female" in name or "frau" in name or "female" in id_):
            return lang_ok
        if gender.startswith("m") and ("male" in name or "mann" in name or "male" in id_):
            return lang_ok
        return lang_ok

    for v in voices:
        if voice_matches(v):
            return v.id
    return voices[0].id if voices else None

_engine_lock = threading.Lock()


@app.get("/")
async def index(request: Request):
    """Serve the UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/speak")
async def speak(payload: dict):
    """Generate an offline WAV using pyttsx3 and return the audio URL.

    Expected JSON: {
      "text": "Hello",
      "language": "en"|"de",
      "gender": "male"|"female",
      "voice_id": "optional explicit voice id"
    }
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="'text' is required")
    language = payload.get("language", "en")
    gender = payload.get("gender")
    voice_id = payload.get("voice_id")
    rate = payload.get("rate")
    volume = payload.get("volume")

    filename = f"{uuid.uuid4().hex}.wav"
    out_path = os.path.join(AUDIO_DIR, filename)

    try:
        engine = pyttsx3.init()
        if voice_id:
            try:
                engine.setProperty("voice", voice_id)
            except Exception:
                pass
        else:
            vid = choose_voice(engine, language=language, gender=gender)
            if vid:
                engine.setProperty("voice", vid)

        if rate:
            try:
                engine.setProperty("rate", int(rate))
            except Exception:
                pass
        if volume:
            try:
                engine.setProperty("volume", float(volume))
            except Exception:
                pass

        with _engine_lock:
            engine.save_to_file(text, out_path)
            engine.runAndWait()
            try:
                engine.stop()
            except Exception:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {e}")

    return JSONResponse({"url": f"/audio/{filename}"})


@app.get("/voices")
async def list_voices():
    """Return a best-effort list of available voices on the machine."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        out = []
        for v in voices:
            langs = []
            try:
                langs = [l.decode("utf-8") if isinstance(l, (bytes, bytearray)) else str(l) for l in getattr(v, "languages", [])]
            except Exception:
                langs = []
            out.append({
                "id": getattr(v, "id", ""),
                "name": getattr(v, "name", ""),
                "languages": langs,
            })
        return JSONResponse(out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice list error: {e}")


@app.post("/train")
async def train_placeholder(request: Request):
    form = await request.form()
    upload = form.get("file")
    if not upload:
        raise HTTPException(status_code=400, detail="No file uploaded; send a ZIP of your recordings and transcripts as 'file' form field.")
    trainings = os.path.join(BASE_DIR, "trainings")
    os.makedirs(trainings, exist_ok=True)
    fname = f"upload_{uuid.uuid4().hex}.zip"
    path = os.path.join(trainings, fname)
    try:
        contents = await upload.read()
        with open(path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    return JSONResponse({"status": "saved", "path": path, "note": "Run local training (Coqui TTS or similar) using this archive; see README for guidance."})


if __name__ == "__main__":
    print("[DEBUG] - Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
