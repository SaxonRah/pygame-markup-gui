from typing import Dict


class BrowserDefaults:
    """Exact browser default styles for common elements"""

    # These are actual chrome/firefox defaults
    DEFAULTS = {
        'html': {
            'display': 'block',
            'margin': '0',
            'padding': '0'
        },
        'body': {
            'display': 'block',
            'margin': '8px',  # crucial!
            'padding': '0',
            'font-family': '-webkit-body',  # system font
            'font-size': '16px',
            'line-height': '1.2'
        },
        'div': {
            'display': 'block',
            'margin': '0',
            'padding': '0'
        },
        'h1': {
            'display': 'block',
            'font-size': '2em',
            'margin-top': '0.67em',
            'margin-bottom': '0.67em',
            'margin-left': '0',
            'margin-right': '0',
            'font-weight': 'bold'
        },
        'h2': {
            'display': 'block',
            'font-size': '1.5em',
            'margin-top': '0.83em',
            'margin-bottom': '0.83em',
            'margin-left': '0',
            'margin-right': '0',
            'font-weight': 'bold'
        },
        'p': {
            'display': 'block',
            'margin-top': '1em',
            'margin-bottom': '1em',
            'margin-left': '0',
            'margin-right': '0'
        },
        'button': {
            'display': 'inline-block',
            'padding': '1px 6px',  # Very specific!
            'margin': '0',
            'border': '2px outset #767676',  # default button border
            'background-color': '#f0f0f0',
            'color': '#000',
            'font': '11px system-ui',  # platform specific
            'text-align': 'center',
            'cursor': 'default'
        },
        'input': {
            'display': 'inline-block',
            'padding': '1px 2px',
            'margin': '0',
            'border': '2px inset #767676',
            'background-color': '#fff',
            'font': '11px system-ui'
        }
    }

    @classmethod
    def get_default_style(cls, tag_name: str) -> Dict[str, str]:
        """Get browser default style for element"""
        return cls.DEFAULTS.get(tag_name.lower(), {})