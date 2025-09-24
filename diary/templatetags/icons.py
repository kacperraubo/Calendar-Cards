import pathlib
import xml.etree.ElementTree as ET

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

ICON_DIR = pathlib.Path("static/images/icons/")


@register.simple_tag
def icon(icon_name, class_str="", **kwargs):
    """
    Inline an SVG icon from '/static/images/icons/'.

    Only the icon name needs to be passed in, without the file extension.
    The class_str argument is optional and can be used to add classes to the
    SVG element. Any additional keyword arguments will be added as attributes
    to the SVG element.

    Example:

    ```
    {% icon "icon-name" "icon" fill="#000" %}
    ```
    """
    path = ICON_DIR / f"{icon_name}.svg"

    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(path)

    root = tree.getroot()
    root.set("class", class_str)

    for key, value in kwargs.items():
        root.set(key, value)

    svg = ET.tostring(root, encoding="unicode", method="html")

    return mark_safe(svg)
