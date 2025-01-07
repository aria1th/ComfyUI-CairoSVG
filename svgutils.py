import io
import os
import shutil
import subprocess
import tempfile
from typing import Optional, List

from PIL import Image

# Attempt to import cairosvg, handle if not installed
try:
    import cairosvg
except ImportError as e:
    raise ImportError(
        "cairosvg is required for SVG to PNG conversion. Install via: pip install cairosvg"
    ) from e


def upscale_with_vectorization(
    pil_image: Image.Image,
    potrace_args: Optional[List[str]] = None,
    *,
    # Optional parameters for controlling the final PNG size
    scale: float = 1.0,
    output_width: Optional[int] = None,
    output_height: Optional[int] = None
) -> Image.Image:
    """
    Converts a PIL Image to SVG (via Potrace) and back to PNG (via CairoSVG).

    Parameters
    ----------
    pil_image : Image.Image
        The input PIL image.
    potrace_args : list of str, optional
        Additional command-line arguments for 'potrace'.
    scale : float, optional
        A scaling factor for rendering the final PNG via CairoSVG.
    output_width : int, optional
        The desired width of the output PNG (in pixels).
    output_height : int, optional
        The desired height of the output PNG (in pixels).

    Returns
    -------
    Image.Image
        The final PNG image rendered from the vector SVG.
    """

    # ---- Step 0: Check dependencies ----
    if not shutil.which("potrace"):
        raise RuntimeError(
            "Potrace is not installed or not found in PATH. "
            "Please install Potrace and ensure it is accessible."
        )

    # ---- Step 1: Convert RGBA to RGB to avoid alpha issues in BMP ----
    if pil_image.mode == "RGBA":
        background = Image.new("RGBA", pil_image.size, (255, 255, 255, 255))
        pil_image = Image.alpha_composite(background, pil_image).convert("RGB")

    # ---- Step 2: Convert the image to BMP in-memory ----
    bmp_bytes_io = io.BytesIO()
    try:
        pil_image.save(bmp_bytes_io, format="BMP")
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert input image to BMP in memory: {str(e)}"
        ) from e

    # ---- Step 3: Write the BMP data to a temporary file ----
    bmp_data = bmp_bytes_io.getvalue()
    with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as bmp_file:
        bmp_file_path = bmp_file.name
        bmp_file.write(bmp_data)

    svg_file_path = None

    try:
        # ---- Step 4: Invoke Potrace (BMP -> SVG) ----
        svg_fd, svg_file_path = tempfile.mkstemp(suffix=".svg")
        os.close(svg_fd)

        command = ["potrace", bmp_file_path, "-s", "-o", svg_file_path]
        if potrace_args:
            # Insert extra args right after 'potrace'
            command[1:1] = potrace_args

        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Potrace execution failed: {result.stderr}")

        # ---- Step 5: Read the SVG data ----
        try:
            with open(svg_file_path, "rb") as svg_file:
                svg_data = svg_file.read()
        except Exception as e:
            raise RuntimeError(
                f"Failed to read generated SVG file: {str(e)}"
            ) from e

        # ---- Step 6: Convert SVG -> PNG with CairoSVG, using scale or width/height ----
        try:
            png_bytes = cairosvg.svg2png(
                bytestring=svg_data,
                scale=scale,
                output_width=output_width,
                output_height=output_height
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to convert SVG to PNG using CairoSVG: {str(e)}"
            ) from e

        # ---- Step 7: Return PNG as a PIL Image ----
        try:
            output_image = Image.open(io.BytesIO(png_bytes))
            output_image.load()  # Force load
            # rgba
            return output_image.convert("RGBA")
        except Exception as e:
            raise RuntimeError(
                f"Failed to open generated PNG as PIL Image: {str(e)}"
            ) from e

        return output_image

    finally:
        # ---- Cleanup: Remove temporary files ----
        if os.path.exists(bmp_file_path):
            try:
                os.remove(bmp_file_path)
            except OSError:
                pass

        if svg_file_path and os.path.exists(svg_file_path):
            try:
                os.remove(svg_file_path)
            except OSError:
                pass


def test():
    # Load a sample image
    input_image = Image.open("test.jpg")

    # Convert to SVG and back to PNG but at double size
    # (You can also use output_width=..., output_height=... if you want exact pixel dimensions)
    output_image = upscale_with_vectorization(input_image, scale=2.0)

    # Save the final PNG image
    output_image.save("output.png")


if __name__ == "__main__":
    test()
