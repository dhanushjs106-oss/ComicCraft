# ComicCraft – AI Comic Story Creator

ComicCraft is a local web application for turning a short story idea into a complete AI-generated comic. It combines Google Gemini for story generation, Hugging Face Diffusers / Stable Diffusion for illustration, and ReportLab for PDF export.

## Features

- Input story prompt, character name, setting, tone, art style, and number of panels
- AI story generation using Google Gemini
- Panel-by-panel narration, dialogue, and image prompts
- Optional image generation using Stable Diffusion
- Responsive browser UI
- PDF download for the complete comic
- FastAPI backend with automatic OpenAPI docs

## Technologies

- Python
- FastAPI
- Google Gemini
- Hugging Face Diffusers
- Stable Diffusion
- HTML
- CSS
- JavaScript
- ReportLab

## Requirements

- Python 3.10 or newer
- VS Code
- Internet connection
- A valid Google Gemini API key
- Optional NVIDIA GPU for faster image generation

## Installation

```bash
git clone <project-url>
cd ComicCraft

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root by copying `.env.example` and adding your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key_here
IMAGE_MODEL=runwayml/stable-diffusion-v1-5
IMAGE_GENERATION_ENABLED=false
DEVICE=auto
HOST=127.0.0.1
PORT=8000
```

## VS Code Setup

1. Install Python.
2. Install VS Code.
3. Open the `ComicCraft` folder in VS Code.
4. Open the terminal and run:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

5. Copy `.env.example` to `.env` and add your Gemini key.
6. Start the app:

```bash
python run.py
```

Or:

```bash
uvicorn app.main:app --reload
```

7. Open the browser at:

```text
http://127.0.0.1:8000
```

## Health Check

```text
http://127.0.0.1:8000/health
```

Expected JSON:

```json
{
  "status": "healthy",
  "application": "ComicCraft"
}
```

## API Documentation

```text
http://127.0.0.1:8000/docs
```

## Testing

### Test 1: Health check
Open the health URL and confirm the server is healthy.

### Test 2: Generate Comic
Use the form and enter:

- Story: A young inventor discovers a mysterious machine.
- Character: Arun
- Setting: A futuristic city
- Tone: Adventure
- Art Style: Comic Book
- Panels: 4

Then click Generate Comic.

Verify:

- A comic title appears
- A story summary appears
- Four panels render
- Narration and dialogue are visible
- Images appear when generation succeeds

Panel image generation is disabled by default so story requests do not block while a large Stable Diffusion model is downloaded. Set `IMAGE_GENERATION_ENABLED=true` in `.env` to enable automatic illustrations; the first request may take several minutes and requires enough disk space and memory.

### Test 3: Download PDF
Click Download Comic PDF and confirm that a PDF file is downloaded.

## Troubleshooting

### Gemini API key error
- Verify `.env` exists and contains `GEMINI_API_KEY`.
- Confirm the key is valid and has access to Gemini models.

### Gemini quota error
- Check billing and quota usage for your Google project.
- Wait and retry later.

### Image generation error
- Check the `IMAGE_MODEL` value in `.env`.
- Ensure internet access is available for model downloads.
- Set `DEVICE=cpu` if GPU is not available.

### Torch / CUDA error
- Try `DEVICE=cpu` in `.env`.
- Update PyTorch to a compatible version.

### Port already in use
- Change the `PORT` in `.env`.
- Or stop the process already using the port.

### Missing Python package
- Re-run:

```bash
pip install -r requirements.txt
```

### PDF generation error
- Ensure the generated images directory exists.
- Confirm the story payload contains valid panel data.

## Notes

- The application is designed to fail gracefully when Gemini or image generation is unavailable.
- If a panel cannot be illustrated, the UI still shows the story and marks the illustration as unavailable.
- PDF generation continues even if some panel images are missing.
