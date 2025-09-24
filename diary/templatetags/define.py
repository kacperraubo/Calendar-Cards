import typing
from django import template

register = template.Library()


@register.simple_tag
def define(val: typing.Any = None):
    """
    Define a value for use in a template.

    Example:

    ```
    {% define "Hello, World!" as greeting %}
    {{ greeting }}
    ```
    """
    return val
