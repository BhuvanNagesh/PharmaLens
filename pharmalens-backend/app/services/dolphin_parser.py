"""Optional Dolphin-v2 layout-aware parsing for scanned PDF documents.

The heavyweight vision model is imported and loaded only when the provider is
explicitly selected by configuration. Native PDF extraction remains available
without the optional Dolphin dependencies.
"""

from __future__ import annotations

import io
import logging
import re
from functools import lru_cache
from typing import Any


logger = logging.getLogger(__name__)

_LAYOUT_PATTERN = re.compile(
    r"\[(?P<coordinates>[^\]]+)\](?P<labels>(?:\[[^\]]+\])+)",
)
_COORDINATE_PATTERN = re.compile(r"^-?\d+(?:\.\d+)?$")


class DolphinParserError(Exception):
    """Indicate that Dolphin cannot be loaded or cannot parse a PDF."""


class DolphinPdfParser:
    """Run the official Dolphin-v2 two-stage page parsing flow."""

    def __init__(
        self,
        model_path: str,
        device: str,
        max_pages: int,
        max_new_tokens: int,
    ) -> None:
        if not model_path.strip():
            raise DolphinParserError(
                "DOLPHIN_MODEL_PATH must point to a local Dolphin-v2 model or model ID."
            )

        try:
            import pymupdf
            import torch
            from PIL import Image
            from qwen_vl_utils import process_vision_info
            from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
        except ImportError as error:
            raise DolphinParserError(
                "Dolphin parsing requires torch, transformers, pymupdf, Pillow, "
                "and qwen-vl-utils. Install the optional Dolphin runtime first."
            ) from error

        self._pymupdf = pymupdf
        self._torch = torch
        self._image_class = Image
        self._process_vision_info = process_vision_info
        self._max_pages = max_pages
        self._max_new_tokens = max_new_tokens
        self._device = self._resolve_device(device, torch)

        try:
            self._processor = AutoProcessor.from_pretrained(model_path)
            self._model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_path)
            self._model.eval()
            self._model.to(self._device)
            if self._device == "cuda":
                self._model = self._model.to(dtype=torch.bfloat16)
        except Exception as error:
            raise DolphinParserError(
                "Dolphin-v2 could not be loaded. Verify the model path and available memory."
            ) from error

        self._processor.tokenizer.padding_side = "left"
        logger.info("Dolphin-v2 parser loaded on device=%s", self._device)

    @staticmethod
    def _resolve_device(requested_device: str, torch_module: Any) -> str:
        """Resolve the configured device without silently selecting unavailable CUDA."""
        normalized_device = requested_device.strip().lower()
        if normalized_device not in {"auto", "cpu", "cuda"}:
            raise DolphinParserError(
                "DOLPHIN_DEVICE must be one of: auto, cpu, or cuda."
            )
        if normalized_device == "cuda" and not torch_module.cuda.is_available():
            raise DolphinParserError("DOLPHIN_DEVICE=cuda but CUDA is not available.")
        if normalized_device == "auto":
            return "cuda" if torch_module.cuda.is_available() else "cpu"
        return normalized_device

    @staticmethod
    def _resize_image(image: Any, max_size: int = 1600, min_size: int = 28) -> Any:
        """Keep page images within the model's practical input bounds."""
        width, height = image.size
        if max(width, height) > max_size:
            scale = max_size / max(width, height)
            image = image.resize((max(1, int(width * scale)), max(1, int(height * scale))))
            width, height = image.size
        if min(width, height) < min_size:
            scale = min_size / min(width, height)
            image = image.resize((max(1, int(width * scale)), max(1, int(height * scale))))
        return image

    def _render_pdf(self, file_bytes: bytes) -> list[Any]:
        """Render PDF pages in memory without writing uploaded content to disk."""
        try:
            document = self._pymupdf.open(stream=file_bytes, filetype="pdf")
        except Exception as error:
            raise DolphinParserError("Dolphin could not open the uploaded PDF.") from error

        try:
            if not document.page_count:
                raise DolphinParserError("The uploaded PDF contains no pages.")
            if document.page_count > self._max_pages:
                raise DolphinParserError(
                    f"The PDF has {document.page_count} pages, exceeding the configured "
                    f"Dolphin limit of {self._max_pages}."
                )

            pages: list[Any] = []
            for page_number in range(document.page_count):
                page = document.load_page(page_number)
                longest_dimension = max(page.rect.width, page.rect.height)
                scale = 1600 / longest_dimension if longest_dimension else 1
                matrix = self._pymupdf.Matrix(scale, scale)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                page_image = self._image_class.open(io.BytesIO(pixmap.tobytes("png")))
                pages.append(page_image.convert("RGB"))
            return pages
        finally:
            document.close()

    def _chat(self, prompt: str, image: Any) -> str:
        """Send one image prompt through the Qwen-compatible Dolphin processor."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        text = self._processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        image_inputs, video_inputs = self._process_vision_info(messages)
        inputs = self._processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self._model.device)
        with self._torch.inference_mode():
            generated_ids = self._model.generate(
                **inputs,
                max_new_tokens=self._max_new_tokens,
                do_sample=False,
            )
        prompt_length = inputs.input_ids.shape[1]
        generated_text = self._processor.batch_decode(
            generated_ids[:, prompt_length:],
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return generated_text[0].strip() if generated_text else ""

    @staticmethod
    def _parse_layout(layout_output: str) -> list[tuple[list[float], str]]:
        """Parse Dolphin's coordinate-label reading-order representation."""
        elements: list[tuple[list[float], str]] = []
        for segment in layout_output.split("[PAIR_SEP]"):
            match = _LAYOUT_PATTERN.search(segment.strip())
            if match is None:
                continue
            coordinate_parts = match.group("coordinates").split(",")
            if len(coordinate_parts) != 4 or not all(
                _COORDINATE_PATTERN.match(part.strip()) for part in coordinate_parts
            ):
                continue
            labels = re.findall(r"\[([^\]]+)\]", match.group("labels"))
            if not labels:
                continue
            elements.append(([float(part) for part in coordinate_parts], labels[0].strip()))
        return elements

    @staticmethod
    def _crop(image: Any, coordinates: list[float]) -> Any | None:
        """Crop one layout element while clamping model coordinates to the page."""
        width, height = image.size
        x1, y1, x2, y2 = coordinates
        left = max(0, min(int(x1), width - 1))
        top = max(0, min(int(y1), height - 1))
        right = max(left + 1, min(int(x2), width))
        bottom = max(top + 1, min(int(y2), height))
        if right <= left or bottom <= top:
            return None
        return image.crop((left, top, right, bottom))

    @staticmethod
    def _element_prompt(label: str) -> str:
        """Select a deterministic extraction prompt for a layout element."""
        if label.startswith("sec_"):
            return "Transcribe this document heading exactly. Return only the heading text."
        if label == "tab":
            return (
                "Convert this table into Markdown. Preserve every cell value and row order. "
                "Return only the Markdown table."
            )
        if label == "equ":
            return "Transcribe this formula exactly in LaTeX. Return only the formula."
        if label == "fig":
            return "Describe this figure or diagram accurately in one concise sentence."
        return "Transcribe this document element exactly in reading order. Return only its text."

    @staticmethod
    def _format_element(label: str, text: str) -> str:
        """Preserve heading hierarchy while keeping model output analysis-friendly."""
        cleaned_text = text.strip()
        if not cleaned_text:
            return ""
        heading_match = re.fullmatch(r"sec_(\d+)", label)
        if heading_match:
            level = min(int(heading_match.group(1)) + 1, 6)
            return f"{'#' * level} {cleaned_text.lstrip('# ').strip()}"
        return cleaned_text

    def _parse_page(self, image: Any) -> str:
        """Run layout analysis followed by element-level extraction for one page."""
        model_image = self._resize_image(image)
        layout_output = self._chat("Parse the reading order of this document.", model_image)
        elements = self._parse_layout(layout_output)
        if not elements:
            return self._chat(
                "Transcribe this full document page in reading order as Markdown. "
                "Preserve headings, paragraphs, lists, and tables.",
                model_image,
            )

        extracted_elements: list[str] = []
        for coordinates, label in elements:
            crop = self._crop(model_image, coordinates)
            if crop is None:
                continue
            element_text = self._chat(self._element_prompt(label), crop)
            formatted_element = self._format_element(label, element_text)
            if formatted_element:
                extracted_elements.append(formatted_element)
        return "\n\n".join(extracted_elements)

    def parse_pdf(self, file_bytes: bytes) -> str:
        """Return page-aware Markdown extracted from a PDF with Dolphin-v2."""
        pages = self._render_pdf(file_bytes)
        page_texts: list[str] = []
        for page_number, page_image in enumerate(pages, start=1):
            logger.info("Dolphin-v2 parsing PDF page %d/%d", page_number, len(pages))
            page_text = self._parse_page(page_image).strip()
            if page_text:
                page_texts.append(f"<!-- Page {page_number} -->\n\n{page_text}")
        return "\n\n".join(page_texts).strip()


@lru_cache(maxsize=2)
def get_dolphin_parser(
    model_path: str,
    device: str,
    max_pages: int,
    max_new_tokens: int,
) -> DolphinPdfParser:
    """Reuse the loaded model across uploads within one backend process."""
    return DolphinPdfParser(model_path, device, max_pages, max_new_tokens)


def extract_pdf_text_with_dolphin(
    file_bytes: bytes,
    model_path: str,
    device: str,
    max_pages: int,
    max_new_tokens: int,
) -> str:
    """Extract PDF text through the configured cached Dolphin parser."""
    parser = get_dolphin_parser(model_path, device, max_pages, max_new_tokens)
    return parser.parse_pdf(file_bytes)
