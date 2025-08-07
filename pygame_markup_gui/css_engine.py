import tinycss2
import re
from typing import Dict, List, Tuple
from .html_engine import HTMLElement


class CSSRule:
    def __init__(self, selector: str, declarations: Dict[str, str]):
        self.selector = selector
        self.declarations = declarations
        self.specificity = self._calculate_specificity(selector)

    @staticmethod
    def _calculate_specificity(selector: str) -> Tuple[int, int, int]:
        """Calculate CSS specificity (a, b, c) where a=ids, b=classes+attrs, c=elements"""
        ids = len(re.findall(r'#\w+', selector))
        classes = len(re.findall(r'[.:][\w-]+', selector))  # classes and pseudo-classes
        elements = len(re.findall(r'(?<![#.])\b[a-z]\w*', selector))
        return ids, classes, elements


class CSSEngine:
    """Parse and apply CSS to HTML elements"""

    def __init__(self):
        self.rules: List[CSSRule] = []
        self.default_styles = {
            # HTML5 default styles
            'html': {'display': 'block'},
            'body': {'display': 'block', 'margin': '8px'},
            'div': {'display': 'block'},
            'span': {'display': 'inline'},
            'p': {'display': 'block', 'margin': '1em 0'},
            'h1': {'display': 'block', 'font-size': '2em', 'margin': '0.67em 0', 'font-weight': 'bold'},
            'h2': {'display': 'block', 'font-size': '1.5em', 'margin': '0.75em 0', 'font-weight': 'bold'},
            'button': {'display': 'inline-block', 'padding': '4px 8px', 'border': '1px solid #ccc'},
            'input': {'display': 'inline-block', 'padding': '4px', 'border': '1px solid #ccc'},
        }

    def parse_css(self, css_string: str):
        """Parse CSS string into rules"""
        try:
            stylesheet = tinycss2.parse_stylesheet(css_string)

            for rule in stylesheet:
                if rule.type == 'qualified-rule':
                    # Extract selector
                    selector = self._serialize_selector(rule.prelude)

                    # Extract declarations
                    declarations = {}
                    for declaration in tinycss2.parse_declaration_list(rule.content):
                        if declaration.type == 'declaration':
                            prop_name = declaration.name
                            prop_value = self._serialize_value(declaration.value)
                            declarations[prop_name] = prop_value

                    self.rules.append(CSSRule(selector, declarations))
        except Exception as e:
            print(f"CSS parse error: {e}")

    @staticmethod
    def _serialize_selector(prelude) -> str:
        """Convert selector tokens back to string"""
        return ''.join(token.serialize() for token in prelude).strip()

    @staticmethod
    def _serialize_value(value_tokens) -> str:
        """Convert value tokens back to string"""
        return ''.join(token.serialize() for token in value_tokens).strip()

    def compute_style(self, element: HTMLElement) -> Dict[str, str]:
        """Compute final computed style for element"""
        style = {}

        # Start with default styles for tag
        if element.tag in self.default_styles:
            style.update(self.default_styles[element.tag])

        # Apply matching CSS rules in specificity order
        matching_rules = []
        for rule in self.rules:
            if self.selector_matches(rule.selector, element):
                matching_rules.append(rule)

        # Sort by specificity
        matching_rules.sort(key=lambda r: r.specificity)

        # Apply rules
        for rule in matching_rules:
            style.update(rule.declarations)

        # Apply inline styles (highest specificity)
        if 'style' in element.attributes:
            inline_styles = self._parse_inline_style(element.attributes['style'])
            style.update(inline_styles)

        return style

    @staticmethod
    def selector_matches(selector: str, element: HTMLElement) -> bool:
        """Check if CSS selector matches element"""
        # Simplified selector matching - handles basic selectors
        selector = selector.strip()

        # ID selector
        if selector.startswith('#'):
            return element.attributes.get('id') == selector[1:]

        # Class selector
        elif selector.startswith('.'):
            classes = element.attributes.get('class', '').split()
            return selector[1:] in classes

        # Tag selector
        else:
            # Handle compound selectors (space-separated)
            parts = selector.split()
            if len(parts) == 1:
                return element.tag == selector
            else:
                # For now, just match the last part (descendant selector)
                return element.tag == parts[-1]

    def _parse_inline_style(self, style_string: str) -> Dict[str, str]:
        """Parse inline style attribute"""
        declarations = {}
        try:
            for declaration in tinycss2.parse_declaration_list(style_string):
                if declaration.type == 'declaration':
                    declarations[declaration.name] = self._serialize_value(declaration.value)
        except Exception as e:
            print(f"Inline style parse error: {e}")
        return declarations
