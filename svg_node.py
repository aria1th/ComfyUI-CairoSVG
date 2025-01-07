from .svgutils import upscale_with_vectorization
from .autonode import node_wrapper, validate, get_node_names_mappings
from .utils.converter import PILHandlingHodes

# upscale_with_vectorization is a function that converts a PIL Image to SVG (via Potrace) and back to PNG (via CairoSVG).
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

classes = []
node = node_wrapper(classes)


@node
class ResizeImageNode:
    FUNCTION = "resize_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image(image, width, height, method):
        image = PILHandlingHodes.handle_input(image)
        return (image.resize((width, height), ResizeImageNode.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }

@node
class VectorizedUpscaleScaling:
    FUNCTION = "vectorized_upscale"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Vectorized Upscale (With Scaling)"
    @staticmethod
    def vectorized_upscale(image, scale):
        image = PILHandlingHodes.handle_input(image)
        return (upscale_with_vectorization(image, scale=scale),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "scale": ("FLOAT", {"default": 2.0}),
            },
        }

@node
class VectorizedUpscaleSize:
    FUNCTION = "vectorized_upscale_size"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Vectorized Upscale (With Size)"
    @staticmethod
    def vectorized_upscale_size(image, width, height):
        image = PILHandlingHodes.handle_input(image)
        return (upscale_with_vectorization(image, output_width=width, output_height=height),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 512}),
                "height": ("INT", {"default": 512}),
            },
        }

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
validate(classes)
