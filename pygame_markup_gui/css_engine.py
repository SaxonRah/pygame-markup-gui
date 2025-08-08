import tinycss2
import re
from typing import Dict, List, Tuple
from .html_engine import HTMLElement
from .browser_defaults import BrowserDefaults


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
        self.default_styles = BrowserDefaults.DEFAULTS

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
        """Compute final style for element with proper browser defaults"""
        # Start with browser defaults instead of empty dict
        computed = BrowserDefaults.get_default_style(element.tag).copy()

        # Apply matching CSS rules (existing logic)
        matching_rules = []
        for rule in self.rules:
            if self.selector_matches(rule.selector, element):
                matching_rules.append(rule)

        # Sort by specificity and apply
        matching_rules.sort(key=lambda r: r.specificity)
        for rule in matching_rules:
            computed.update(rule.declarations)

        return computed

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
