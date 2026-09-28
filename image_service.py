import os
from pathlib import Path
from typing import Optional

from app.config import get_settings


class ImageGenerationError(Exception):
    pass


class ImageService:
    def __init__(self):
        self.settings = get_settings()
        self.base_dir = Path(self.settings["image_dir"])
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.device = (self.settings["device"] or "auto").lower()
        self.model_name = self.settings["image_model"]
        self.pipe = None
        self._pipeline_error = None
        self.device_name = "cpu"
        self._model_loaded = False

    def load_model(self):
        if self._model_loaded:
            return self.pipe

        self._model_loaded = True
        try:
            import torch
            from diffusers import AutoPipelineForText2Image

            if self.device == "auto":
                detected = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                detected = self.device

            self.device_name = detected if detected in {"cuda", "cpu"} else "cpu"

            if self.device_name == "cuda" and not torch.cuda.is_available():
                self.device_name = "cpu"

            pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device_name == "cuda" else torch.float32,
            )
            pipe = pipe.to(self.device_name)
            self.pipe = pipe
            return self.pipe
        except Exception as exc:  # pragma: no cover
            self._pipeline_error = exc
            self.pipe = None
            return None

    def is_available(self) -> bool:
        if self.pipe is None and self._pipeline_error is None and not self._model_loaded:
            return self.load_model() is not None
        return self.pipe is not None

    def get_error(self) -> Optional[str]:
        return str(self._pipeline_error) if self._pipeline_error else None

    def generate_image(self, prompt: str, panel_number: int) -> Optional[str]:
        if not prompt or not prompt.strip():
            return None

        if self.pipe is None:
            self.load_model()
        if self.pipe is None:
            raise ImageGenerationError(
                "Stable Diffusion is unavailable. Please check the model configuration or try again later."
            )

        try:
            image = self.pipe(prompt=prompt, num_inference_steps=20).images[0]
            filename = f"panel_{panel_number}.png"
            output_path = self.base_dir / filename
            image.save(output_path)
            return f"/generated/images/{filename}"
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower() or "cuda" in str(exc).lower():
                raise ImageGenerationError("Image generation ran out of memory or CUDA is unavailable.") from exc
            raise ImageGenerationError("Unable to generate the illustration for this panel.") from exc
        except Exception as exc:
            raise ImageGenerationError("The story was generated, but an illustration could not be created for this panel.") from exc

    def generate_panel_image(self, panel: dict, panel_number: int) -> Optional[str]:
        try:
            return self.generate_image(panel.get("image_prompt", ""), panel_number)
        except ImageGenerationError:
            return None
