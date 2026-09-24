# ShivAI

**Desktop app** — offline voice/text AI assistant ("India's First Offline AGI Assistant"). CLI-based; no LLM dependency, no API keys.

## Run

```bash
python main_entry.py --text     # text-only mode (recommended headless; verified working)
python main_entry.py            # interactive mode (voice in+out on a desktop with mic/speaker)
python main_entry.py --debug    # debug logging
```

Optional config: copy `config.example.yaml` to `config.yaml` and edit.

## Deps (pyproject.toml)

```bash
pip install pyttsx3 SpeechRecognition vosk pyautogui keyboard pyperclip psutil opencv-python pillow
```

## Notes

- Mic/speaker/TTS paths need real audio hardware (and eSpeak on Linux) — cannot be verified headless. Text-only mode boots and runs verified.
- Windows-specific bits (winshell etc.) are only used on Windows.
