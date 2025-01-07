
from .install import initialization

initialization()

from .svg_node import CLASS_MAPPINGS as SVGMapping, CLASS_NAMES as SVGNames


NODE_CLASS_MAPPINGS = {
}
NODE_CLASS_MAPPINGS.update(SVGMapping)


NODE_DISPLAY_NAME_MAPPINGS = {

}
NODE_DISPLAY_NAME_MAPPINGS.update(SVGNames)
