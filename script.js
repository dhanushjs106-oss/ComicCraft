const form = document.getElementById('comic-form');
const generateBtn = document.getElementById('generate-btn');
const statusBox = document.getElementById('status-box');
const previewContainer = document.getElementById('preview-container');

let currentComic = null;
let isGenerating = false;

function setStatus(message, type = '') {
  statusBox.textContent = message;
  statusBox.className = 'status-box';
  if (type) {
    statusBox.classList.add(type);
  }
}

function showLoadingProgress(step) {
  setStatus(step, '');
}

function renderComic(comic) {
  currentComic = comic;
  previewContainer.className = 'preview-container';
  previewContainer.innerHTML = `
    <div class="comic-header">
      <h2>${comic.title}</h2>
      <p class="comic-summary">${comic.summary}</p>
    </div>
    <div class="panel-grid">
      ${comic.panels
        .map(
          (panel, index) => `
            <article class="comic-panel-card">
              <div class="panel-number">Panel ${panel.panel_number}</div>
              ${
                panel.image_url
                  ? `<img class="panel-image" src="${panel.image_url}" alt="Panel ${panel.panel_number}" />`
                  : `<div class="panel-image placeholder">Illustration unavailable for this panel.</div>`
              }
              <div class="panel-body">
                <h4>Story</h4>
                <p class="panel-description"><strong>Description:</strong> ${panel.description}</p>
                <p class="panel-narration"><strong>Narration:</strong> ${panel.narration}</p>
                <p class="panel-dialogue"><strong>Dialogue:</strong> ${panel.dialogue}</p>
              </div>
            </article>
          `
        )
        .join('')}
    </div>
    <div class="actions">
      <button id="download-pdf-btn" class="secondary-btn" type="button">Download Comic PDF</button>
    </div>
  `;

  const downloadBtn = document.getElementById('download-pdf-btn');
  downloadBtn.addEventListener('click', downloadComicPdf);
}

async function downloadComicPdf() {
  if (!currentComic) {
    setStatus('Generate a comic first before downloading the PDF.', 'error');
    return;
  }

  try {
    const response = await fetch('/api/download-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(currentComic),
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({ detail: 'PDF generation failed.' }));
      throw new Error(errorPayload.detail || 'PDF generation failed.');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'comiccraft_comic.pdf';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setStatus('PDF downloaded successfully.', 'success');
  } catch (error) {
    setStatus(error.message || 'Unable to download the PDF.', 'error');
  }
}

async function handleSubmit(event) {
  event.preventDefault();

  if (isGenerating) {
    return;
  }

  const formData = new FormData(form);
  const payload = {
    story_prompt: formData.get('story_prompt')?.toString().trim() || '',
    character_name: formData.get('character_name')?.toString().trim() || '',
    setting: formData.get('setting')?.toString().trim() || '',
    tone: formData.get('tone')?.toString().trim() || 'Adventure',
    art_style: formData.get('art_style')?.toString().trim() || 'Comic Book',
    panel_count: Number(formData.get('panel_count') || 4),
  };

  if (!payload.story_prompt || !payload.character_name || !payload.setting) {
    setStatus('Please complete the story prompt, character name, and setting.', 'error');
    return;
  }

  isGenerating = true;
  generateBtn.disabled = true;
  generateBtn.textContent = 'Creating your comic...';
  showLoadingProgress('Generating story...');

  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || 'Unable to generate the comic.');
    }

    showLoadingProgress('Creating comic panels...');
    renderComic(data);
    setStatus('Comic generated successfully.', 'success');
  } catch (error) {
    previewContainer.className = 'preview-container';
    previewContainer.innerHTML = '<div class="empty-state">Unable to create your comic right now.</div>';
    setStatus(error.message || 'An unexpected error occurred.', 'error');
  } finally {
    isGenerating = false;
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Comic';
  }
}

form.addEventListener('submit', handleSubmit);
