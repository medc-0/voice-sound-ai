# TTS FastAPI Offline

This project provides a simple offline text-to-speech (TTS) web UI and API using pyttsx3.

Features

- Offline TTS using system voices (pyttsx3).
- Simple web UI to enter text, choose language (English/German) and gender (best-effort).
- Endpoint to upload a training archive (placeholder) — see notes below for training with Coqui TTS.

## Quick start (Windows, PowerShell)

1. Create a virtual environment and activate it

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the server

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

3. Open http://127.0.0.1:8000 in your browser.

## Notes on voices and languages

- pyttsx3 uses system TTS engines (SAPI5 on Windows). Available voices depend on your OS.
- The app exposes `/voices` to list installed voices. The language/gender selection uses heuristics to pick a voice.

## Custom voice training (optional, advanced)

To create a custom neural TTS voice that "learns" to sound like you, use a toolkit such as Coqui TTS or Mozilla TTS. These tools require a dataset of recorded audio and transcripts and a capable GPU for reasonable training speed.

Minimal steps (high level):

1. Prepare your dataset (many short utterances with matching transcripts). Store as WAV + text or in a Coqui-compatible structure.
2. Install Coqui TTS (or alternative) in a separate environment and follow their training recipes.
3. After training, export a TTS model and create a small script to load the model and synthesise audio for the `/audio` folder used by this app.

Resources:

- Coqui TTS: https://github.com/coqui-ai/TTS
- Documentation and examples are in the Coqui repository.

## Privacy & offline

This server and the TTS engine run locally. No audio or text is sent to third-party servers unless you optionally upload data for training and run remote tools.

## Limitations

- pyttsx3 voices are not neural and won't match custom voice cloning quality.
- True custom-voice cloning requires dataset collection and training with a neural TTS toolkit.

## Modern UI and controls

- The web UI is redesigned to be responsive and modern. It lists available system voices and allows you to select a specific `voice_id` or use automatic language/gender heuristics.
- Use the "Preview Voice" button to generate a short sample of the selected voice before synthesizing longer text.
