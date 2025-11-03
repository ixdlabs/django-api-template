from textwrap import shorten
from typing import Any, Optional

from django.utils.safestring import mark_safe
from unfold.decorators import display


def header_img(image: Optional[Any], size: int = 50):
    image_url = image.url if image else f"https://placehold.co/{size}x{size}?text=?"
    return ["", {"path": image_url, "width": size, "height": size, "squared": True, "borderless": True}]


def header_col(text: str, color: str = "#a4eb3f"):
    color_raw = color.lstrip("#")
    letter = text[:4].upper() if text else "?"
    image_url = f"https://placehold.co/50x50/{color_raw}/000?text={letter}&font=oswald"
    return ["", {"path": image_url, "width": 50, "height": 50, "squared": True, "borderless": True}]


def _follow(obj, dotted_path: str):
    """
    Magic method to walk fields with a string.
    ```
    obj__field      => obj.field
    =value          => value
    obj__method()   => obj.method()
    obj1+obj2       => obj1 + obj2
    ```
    """

    def resolve(path):
        if path.startswith("="):
            return path.strip("=")
        value = obj
        for part in path.split("__"):
            if part == "()":
                value = value()
            else:
                value = getattr(value, part, None)
            if value is None:
                break
        return value

    # Handle +
    if "+" in dotted_path:
        parts = dotted_path.split("+")
        return "".join(str(_follow(obj, p)) for p in parts)

    # Handle single path or =value
    return resolve(dotted_path)


def make_display(
    *,
    description: str,
    primary: str,
    ordering: Optional[str] = None,
    secondary: Optional[str] = None,
    image: Optional[str] = None,
    image_text: Optional[str] = None,
    image_text_suffix: Optional[str] = None,
    image_text_color: Optional[str] = None,
    shorten_secondary: bool = False,
    secondary_suffix: Optional[str] = None,
    header: bool = False,
    label: bool | None | dict = None,
):
    """
    Build an @display-decorated list_display helper:

    ```
        _organization = make_header_display(
            description="organization",
            ordering="organization",
            primary="organization__name",
            secondary="=Organization",
            image="organization__logo",
        )
    ```

    This is equal to,

    ```
        @display(description="organization", ordering="organization", header=True)
        def _organization(self, obj):
            return [obj.organization.name, "Organization", "", {
                    "path": obj.organization.logo,
                    "width": 50,
                    "height": 50,
                    "squared": True,
                    "borderless": True
                }
            ]
    ```
    """

    def _fn(self, obj):
        primary_text = _follow(obj, primary)

        if label:
            if type(primary_text) is bool:
                return "Yes" if primary_text else "No"
            return primary_text

        if header:
            if primary_text is None:
                return ["", ""]

            secondary_text = _follow(obj, secondary) if secondary else None
            if shorten_secondary:
                secondary_text = shorten(str(secondary_text), width=100)
            if secondary_suffix:
                secondary_text = f"{secondary_text}{secondary_suffix}"

            parts = [primary_text, secondary_text]
            if image:
                parts += header_img(_follow(obj, image))
            if image_text:
                image_text_value = f"{_follow(obj, image_text)}{image_text_suffix or ' '}"
                parts += (
                    header_col(image_text_value, _follow(obj, image_text_color))
                    if image_text_color
                    else header_col(image_text_value)
                )

            return parts

        return primary_text

    return display(
        description=description,
        ordering=ordering,
        header=header,
        label=label,
    )(_fn)


def as_json_html(value) -> str:
    try:
        import json

        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer

        formatted_json = json.dumps(json.loads(value), indent=4)
        return mark_safe(highlight(formatted_json, JsonLexer(), HtmlFormatter(full=True)))
    except (json.JSONDecodeError, TypeError):
        return value
