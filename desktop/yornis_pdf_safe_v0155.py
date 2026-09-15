from __future__ import annotations

import multiprocessing as mp
import os
import tempfile
from pathlib import Path

from PIL import Image

PDF_TIMEOUT_SECONDS = 20.0
PDF_MAX_FILE_BYTES = 250 * 1024 * 1024
PDF_MAX_RENDER_PIXELS = 100_000_000
PDF_SCALE = 2.0


def _render_pdf_worker(pdf_path: str, output_path: str, error_path: str, scale: float, max_pixels: int) -> None:
    try:
        import pymupdf

        doc = pymupdf.open(pdf_path)
        try:
            if doc.page_count < 1:
                raise ValueError("El PDF no contiene páginas.")
            page = doc[0]
            rect = page.rect
            predicted = int(max(1.0, rect.width * scale) * max(1.0, rect.height * scale))
            if predicted > max_pixels:
                raise ValueError(f"La primera página requiere demasiados píxeles ({predicted:,}).")
            pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            actual = int(pix.width) * int(pix.height)
            if actual > max_pixels:
                raise ValueError(f"La imagen renderizada es demasiado grande ({actual:,} píxeles).")
            pix.save(output_path)
        finally:
            doc.close()
    except BaseException as exc:
        try:
            Path(error_path).write_text(f"{type(exc).__name__}: {exc}", encoding="utf-8")
        except Exception:
            pass
        raise


def render_pdf_first_page(
    path: str | os.PathLike[str],
    *,
    timeout: float = PDF_TIMEOUT_SECONDS,
    scale: float = PDF_SCALE,
    max_file_bytes: int = PDF_MAX_FILE_BYTES,
    max_pixels: int = PDF_MAX_RENDER_PIXELS,
) -> Image.Image:
    """Render page 1 in a disposable process so malformed PDFs cannot freeze the UI.

    The worker is forcibly terminated after ``timeout`` seconds. File size and
    render-pixel limits reduce the risk of resource exhaustion. The returned PIL
    image is detached from the temporary file before cleanup.
    """

    pdf = Path(path)
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    size = pdf.stat().st_size
    if size <= 0:
        raise ValueError("El PDF está vacío.")
    if size > max_file_bytes:
        raise ValueError(f"PDF demasiado grande ({size / 1024 / 1024:.1f} MB; máximo {max_file_bytes / 1024 / 1024:.0f} MB).")
    if timeout <= 0:
        raise ValueError("timeout debe ser mayor que cero")

    with tempfile.TemporaryDirectory(prefix="yornis_pdf_") as tmp:
        output = Path(tmp) / "page.png"
        error = Path(tmp) / "error.txt"
        ctx = mp.get_context("spawn")
        proc = ctx.Process(
            target=_render_pdf_worker,
            args=(str(pdf), str(output), str(error), float(scale), int(max_pixels)),
            name="YornisPDFRenderer",
            daemon=False,
        )
        proc.start()
        proc.join(timeout)
        if proc.is_alive():
            proc.terminate()
            proc.join(2.0)
            if proc.is_alive() and hasattr(proc, "kill"):
                proc.kill()
                proc.join(2.0)
            raise TimeoutError(f"El PDF tardó más de {timeout:g} s en procesarse y fue cancelado de forma segura.")

        if proc.exitcode != 0 or not output.is_file():
            detail = error.read_text(encoding="utf-8", errors="replace") if error.exists() else f"código de salida {proc.exitcode}"
            raise RuntimeError(f"No se pudo procesar el PDF: {detail}")

        with Image.open(output) as im:
            return im.convert("RGB").copy()


def install(workspace_cls) -> None:
    """Replace only PDF loading; all raster-image behavior stays inherited."""

    if getattr(workspace_cls, "_yornis_pdf_safe_v0155", False):
        return
    original = workspace_cls.load_pil

    def load_pil_safe(self, path):
        if str(path).lower().endswith(".pdf"):
            return render_pdf_first_page(path)
        return original(self, path)

    workspace_cls.load_pil = load_pil_safe
    workspace_cls._yornis_pdf_safe_v0155 = True
