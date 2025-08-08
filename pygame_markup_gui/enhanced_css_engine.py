# enhanced_css_engine.py

import re
import math
import pygame
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import tinycss2

from .css_engine import CSSEngine, CSSRule
from .html_engine import HTMLElement, LayoutBox
from .layout_engine import LayoutEngine
from .markup_renderer import MarkupRenderer


class PositionType(Enum):
    STATIC = "static"
    RELATIVE = "relative"
    ABSOLUTE = "absolute"
    FIXED = "fixed"
    STICKY = "sticky"


class Display(Enum):
    BLOCK = "block"
    INLINE = "inline"
    INLINE_BLOCK = "inline-block"
    FLEX = "flex"
    GRID = "grid"
    NONE = "none"


class FlexDirection(Enum):
    ROW = "row"
    ROW_REVERSE = "row-reverse"
    COLUMN = "column"
    COLUMN_REVERSE = "column-reverse"


class JustifyContent(Enum):
    FLEX_START = "flex-start"
    FLEX_END = "flex-end"
    CENTER = "center"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"


class AlignItems(Enum):
    STRETCH = "stretch"
    FLEX_START = "flex-start"
    FLEX_END = "flex-end"
    CENTER = "center"
    BASELINE = "baseline"


@dataclass
class Transform:
    translate_x: float = 0
    translate_y: float = 0
    scale_x: float = 1
    scale_y: float = 1
    rotate: float = 0
    skew_x: float = 0
    skew_y: float = 0


@dataclass
class BoxShadow:
    offset_x: float = 0
    offset_y: float = 0
    blur_radius: float = 0
    spread_radius: float = 0
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)
    inset: bool = False


@dataclass
class Gradient:
    type: str  # 'linear' or 'radial'
    angle: float = 0  # for linear gradients
    stops: List[Tuple[float, Tuple[int, int, int, int]]] = None  # position, color


class SelectorParser:
    """Parse and match CSS selectors with full CSS3+ support"""

    def __init__(self):
        # Pseudo-class patterns
        self.pseudo_patterns = {
            'nth-child': r':nth-child\(([^)]+)\)',
            'nth-of-type': r':nth-of-type\(([^)]+)\)',
            'nth-last-child': r':nth-last-child\(([^)]+)\)',
            'first-child': r':first-child',
            'last-child': r':last-child',
            'only-child': r':only-child',
            'empty': r':empty',
            'not': r':not\(([^)]+)\)'
        }

    def selector_matches(self, selector: str, element: HTMLElement) -> bool:
        """Check if CSS selector matches element with full CSS support"""
        selector = selector.strip()

        # Handle selector lists (comma-separated)
        if ',' in selector:
            return any(self.selector_matches(s.strip(), element)
                       for s in selector.split(','))

        # Parse complex selector into parts
        selector_parts = self._parse_complex_selector(selector)

        # Match against the selector chain
        return self._match_selector_chain(selector_parts, element)

    def _parse_complex_selector(self, selector: str) -> List[dict]:
        """Parse complex selector into combinator chain"""
        # Split on combinators while preserving them
        combinator_pattern = r'\s*([>+~])\s*|\s+'
        parts = re.split(combinator_pattern, selector)

        # Clean and structure the parts
        selector_parts = []
        current_combinator = ' '  # Default descendant combinator

        for i, part in enumerate(parts):
            if not part or part.isspace():
                continue

            if part in ['>', '+', '~']:
                current_combinator = part
            else:
                # This is a selector part
                parsed_part = self._parse_simple_selector(part)
                parsed_part['combinator'] = current_combinator
                selector_parts.append(parsed_part)
                current_combinator = ' '  # Reset to descendant

        return selector_parts

    def _parse_simple_selector(self, selector: str) -> dict:
        """Parse a simple selector (no combinators)"""
        result = {
            'tag': None,
            'id': None,
            'classes': [],
            'attributes': [],
            'pseudo_classes': [],
            'pseudo_elements': [],
            'combinator': ' '
        }

        # Remove pseudo-elements first (::before, ::after, etc.)
        pseudo_element_match = re.search(r'::([a-zA-Z-]+)', selector)
        if pseudo_element_match:
            result['pseudo_elements'].append(pseudo_element_match.group(1))
            selector = re.sub(r'::([a-zA-Z-]+)', '', selector)

        # Extract and remove pseudo-classes
        for pseudo_name, pattern in self.pseudo_patterns.items():
            matches = re.findall(pattern, selector)
            for match in matches:
                result['pseudo_classes'].append({
                    'name': pseudo_name,
                    'value': match if match else None
                })
            selector = re.sub(pattern, '', selector)

        # Handle other pseudo-classes
        simple_pseudos = ['hover', 'focus', 'active', 'visited', 'link',
                          'disabled', 'enabled', 'checked', 'required', 'optional']
        for pseudo in simple_pseudos:
            pattern = f':{pseudo}'
            if pattern in selector:
                result['pseudo_classes'].append({'name': pseudo, 'value': None})
                selector = selector.replace(pattern, '')

        # Extract attribute selectors
        attr_pattern = r'\[([^\]]+)\]'
        attr_matches = re.findall(attr_pattern, selector)
        for attr_match in attr_matches:
            result['attributes'].append(self._parse_attribute_selector(attr_match))
        selector = re.sub(attr_pattern, '', selector)

        # Extract ID
        id_match = re.search(r'#([a-zA-Z][\w-]*)', selector)
        if id_match:
            result['id'] = id_match.group(1)
            selector = re.sub(r'#[a-zA-Z][\w-]*', '', selector)

        # Extract classes
        class_matches = re.findall(r'\.([a-zA-Z][\w-]*)', selector)
        result['classes'] = class_matches
        selector = re.sub(r'\.[a-zA-Z][\w-]*', '', selector)

        # What's left should be the tag name
        selector = selector.strip()
        if selector and selector != '*':
            result['tag'] = selector.lower()

        return result

    def _parse_attribute_selector(self, attr_selector: str) -> dict:
        """Parse attribute selector like [class*="button"] or [disabled]"""
        # Match [attr], [attr=value], [attr*=value], etc.
        patterns = [
            (r'^([a-zA-Z][\w-]*)\*=[\'""]?([^\'""]*?)[\'""]?$', 'contains'),
            (r'^([a-zA-Z][\w-]*)\^=[\'""]?([^\'""]*?)[\'""]?$', 'starts_with'),
            (r'^([a-zA-Z][\w-]*)\$=[\'""]?([^\'""]*?)[\'""]?$', 'ends_with'),
            (r'^([a-zA-Z][\w-]*)\|=[\'""]?([^\'""]*?)[\'""]?$', 'lang'),
            (r'^([a-zA-Z][\w-]*)\~=[\'""]?([^\'""]*?)[\'""]?$', 'word'),
            (r'^([a-zA-Z][\w-]*?)=[\'""]?([^\'""]*?)[\'""]?$', 'exact'),
            (r'^([a-zA-Z][\w-]*)$', 'exists')
        ]

        for pattern, match_type in patterns:
            match = re.match(pattern, attr_selector.strip())
            if match:
                if match_type == 'exists':
                    return {'name': match.group(1), 'operator': 'exists', 'value': None}
                else:
                    return {'name': match.group(1), 'operator': match_type, 'value': match.group(2)}

        # Fallback
        return {'name': attr_selector, 'operator': 'exists', 'value': None}

    def _match_selector_chain(self, selector_parts: List[dict], element: HTMLElement) -> bool:
        """Match a chain of selectors with combinators"""
        if not selector_parts:
            return True

        # Start from the last selector (rightmost) and work backwards
        current_element = element

        # Match the last selector against current element
        last_selector = selector_parts[-1]
        if not self._match_simple_selector(last_selector, current_element):
            return False

        if len(selector_parts) == 1:
            return True

        # Work backwards through the selector chain
        for i in range(len(selector_parts) - 2, -1, -1):
            selector_part = selector_parts[i]
            combinator = selector_parts[i + 1]['combinator']

            current_element = self._find_matching_ancestor(
                current_element, selector_part, combinator
            )

            if current_element is None:
                return False

        return True

    def _find_matching_ancestor(self, element: HTMLElement, selector_part: dict,
                                combinator: str) -> Optional[HTMLElement]:
        """Find ancestor element matching selector based on combinator"""
        if combinator == '>':  # Direct child
            if element.parent and self._match_simple_selector(selector_part, element.parent):
                return element.parent
            return None

        elif combinator == '+':  # Adjacent sibling
            if element.parent:
                siblings = element.parent.children
                try:
                    current_index = siblings.index(element)
                    if current_index > 0:
                        prev_sibling = siblings[current_index - 1]
                        if self._match_simple_selector(selector_part, prev_sibling):
                            return prev_sibling
                except ValueError:
                    pass
            return None

        elif combinator == '~':  # General sibling
            if element.parent:
                siblings = element.parent.children
                try:
                    current_index = siblings.index(element)
                    for i in range(current_index - 1, -1, -1):
                        sibling = siblings[i]
                        if self._match_simple_selector(selector_part, sibling):
                            return sibling
                except ValueError:
                    pass
            return None

        else:  # Descendant (space)
            current = element.parent
            while current:
                if self._match_simple_selector(selector_part, current):
                    return current
                current = current.parent
            return None

    def _match_simple_selector(self, selector_part: dict, element: HTMLElement) -> bool:
        """Match a simple selector against an element"""
        # Check tag
        if selector_part['tag'] and selector_part['tag'] != element.tag.lower():
            return False

        # Check ID
        if selector_part['id']:
            element_id = element.attributes.get('id', '')
            if element_id != selector_part['id']:
                return False

        # Check classes
        if selector_part['classes']:
            element_classes = set(element.attributes.get('class', '').split())
            required_classes = set(selector_part['classes'])
            if not required_classes.issubset(element_classes):
                return False

        # Check attributes
        for attr in selector_part['attributes']:
            if not self._match_attribute(element, attr):
                return False

        # Check pseudo-classes
        for pseudo in selector_part['pseudo_classes']:
            if not self._match_pseudo_class(element, pseudo):
                return False

        # Check pseudo-elements (for now, just return true - would need special handling)
        if selector_part['pseudo_elements']:
            # Pseudo-elements like ::before, ::after would need special rendering support
            pass

        return True

    def _match_attribute(self, element: HTMLElement, attr_selector: dict) -> bool:
        """Match attribute selector against element"""
        attr_name = attr_selector['name']
        operator = attr_selector['operator']
        expected_value = attr_selector['value']

        if attr_name not in element.attributes:
            return operator == 'not_exists'  # Only matches if checking for non-existence

        if operator == 'exists':
            return True

        actual_value = element.attributes[attr_name]

        if operator == 'exact':
            return actual_value == expected_value
        elif operator == 'contains':
            return expected_value in actual_value
        elif operator == 'starts_with':
            return actual_value.startswith(expected_value)
        elif operator == 'ends_with':
            return actual_value.endswith(expected_value)
        elif operator == 'word':
            # Space-separated word match
            words = actual_value.split()
            return expected_value in words
        elif operator == 'lang':
            # Language code match (en, en-US, etc.)
            return actual_value == expected_value or actual_value.startswith(expected_value + '-')

        return False

    def _match_pseudo_class(self, element: HTMLElement, pseudo: dict) -> bool:
        """Match pseudo-class against element"""
        pseudo_name = pseudo['name']
        pseudo_value = pseudo['value']

        # State-based pseudo-classes (would need state tracking)
        if pseudo_name in ['hover', 'focus', 'active']:
            # These would need integration with interaction system
            state = getattr(element, '_interaction_state', {})
            return state.get(pseudo_name, False)

        elif pseudo_name == 'disabled':
            return element.attributes.get('disabled') is not None

        elif pseudo_name == 'enabled':
            return element.attributes.get('disabled') is None

        elif pseudo_name == 'checked':
            return element.attributes.get('checked') is not None

        elif pseudo_name == 'required':
            return element.attributes.get('required') is not None

        elif pseudo_name == 'optional':
            return element.attributes.get('required') is None

        # Structural pseudo-classes
        elif pseudo_name == 'first-child':
            return element.parent and element.parent.children[0] == element

        elif pseudo_name == 'last-child':
            return element.parent and element.parent.children[-1] == element

        elif pseudo_name == 'only-child':
            return element.parent and len(element.parent.children) == 1

        elif pseudo_name == 'empty':
            return not element.children and not element.text_content.strip()

        elif pseudo_name == 'nth-child':
            return self._match_nth_expression(element, pseudo_value, 'child')

        elif pseudo_name == 'nth-of-type':
            return self._match_nth_expression(element, pseudo_value, 'type')

        elif pseudo_name == 'nth-last-child':
            return self._match_nth_expression(element, pseudo_value, 'last-child')

        elif pseudo_name == 'not':
            # Parse the inner selector and return opposite
            inner_selector = self._parse_simple_selector(pseudo_value)
            return not self._match_simple_selector(inner_selector, element)

        return False

    def _match_nth_expression(self, element: HTMLElement, expression: str, match_type: str) -> bool:
        """Match nth-child/nth-of-type expressions like 2n+1, odd, even"""
        if not element.parent:
            return False

        # Get sibling list based on type
        if match_type == 'type':
            siblings = [child for child in element.parent.children
                        if child.tag == element.tag]
        else:
            siblings = element.parent.children

        try:
            element_index = siblings.index(element)
            position = element_index + 1  # CSS is 1-indexed

            if match_type == 'last-child':
                position = len(siblings) - element_index

        except ValueError:
            return False

        # Parse nth expression
        expression = expression.strip().lower()

        if expression == 'odd':
            return position % 2 == 1
        elif expression == 'even':
            return position % 2 == 0
        elif expression.isdigit():
            return position == int(expression)
        else:
            # Parse an+b format
            return self._evaluate_nth_expression(expression, position)

    def _evaluate_nth_expression(self, expression: str, position: int) -> bool:
        """Evaluate nth expression like 2n+1, -n+3, etc."""
        # Match patterns like: 2n+1, -n+3, n, -2n, etc.
        match = re.match(r'^([+-]?\d*)n([+-]\d+)?$', expression.replace(' ', ''))

        if match:
            a_str = match.group(1)
            b_str = match.group(2)

            # Parse coefficient 'a'
            if a_str == '' or a_str == '+':
                a = 1
            elif a_str == '-':
                a = -1
            else:
                a = int(a_str)

            # Parse constant 'b'
            b = int(b_str) if b_str else 0

            # Check if position matches an + b
            if a == 0:
                return position == b
            elif a > 0:
                return position >= b and (position - b) % a == 0
            else:
                return position <= b and (b - position) % abs(a) == 0

        return False

    def calculate_specificity(self, selector: str) -> Tuple[int, int, int, int]:
        """Calculate CSS specificity (style, ids, classes+attrs+pseudos, elements)"""
        # Remove selector list comma separation for individual calculation
        if ',' in selector:
            # For selector lists, return max specificity
            return max(self.calculate_specificity(s.strip())
                       for s in selector.split(','))

        # Parse the selector
        selector_parts = self._parse_complex_selector(selector)

        style = 0  # Inline styles (not handled here)
        ids = 0
        classes = 0
        elements = 0

        for part in selector_parts:
            if part['id']:
                ids += 1

            classes += len(part['classes'])
            classes += len(part['attributes'])
            classes += len(part['pseudo_classes'])

            if part['tag'] and part['tag'] != '*':
                elements += 1

            # Pseudo-elements count as elements
            elements += len(part['pseudo_elements'])

        return (style, ids, classes, elements)


class EnhancedCSSRule:
    def __init__(self, selector: str, declarations: Dict[str, str]):
        self.selector = selector
        self.declarations = declarations
        self.selector_parser = SelectorParser()
        self.specificity = self.selector_parser.calculate_specificity(selector)

    def matches(self, element: HTMLElement) -> bool:
        """Check if this rule matches the element"""
        return self.selector_parser.selector_matches(self.selector, element)


class EnhancedLayoutBox(LayoutBox):
    """Extended layout box with enhanced positioning properties"""

    def __init__(self):
        super().__init__()  # Get all base LayoutBox properties

        # Enhanced positioning properties
        self.z_index: int = 0
        self.position_type: PositionType = PositionType.STATIC
        self.top: Optional[float] = None
        self.right: Optional[float] = None
        self.bottom: Optional[float] = None
        self.left: Optional[float] = None
        self.min_width: Optional[float] = None
        self.max_width: Optional[float] = None
        self.min_height: Optional[float] = None
        self.max_height: Optional[float] = None

        # Flexbox properties
        self.flex_grow: float = 0
        self.flex_shrink: float = 1
        self.flex_basis: Optional[float] = None
        self.order: int = 0

        # Grid properties
        self.grid_column_start: int = 1
        self.grid_column_end: int = 2
        self.grid_row_start: int = 1
        self.grid_row_end: int = 2
        self.grid_area: Optional[str] = None
        self.grid_template_areas: List[List[str]] = []

        # Visual effects
        self.opacity: float = 1.0
        self.transform: Transform = Transform()
        self.border_radius: Tuple[float, float, float, float] = (0, 0, 0, 0)
        self.box_shadows: List[BoxShadow] = []
        self.clip_path: Optional[str] = None

        # Background properties
        self.background_gradient: Optional[Gradient] = None


class EnhancedCSSEngine(CSSEngine):
    """Enhanced CSS engine extending base CSS engine with modern properties"""

    def __init__(self):
        super().__init__()  # Get all base CSS engine functionality
        self._selector_parser = SelectorParser()

        # Enhanced default styles (in addition to base styles)
        self.default_styles.update({
            # Layout defaults
            'position': 'static',
            'z-index': '0',
            'opacity': '1',
            'visibility': 'visible',
            'overflow': 'visible',
            'box-sizing': 'content-box',

            # Typography defaults
            'line-height': '1.4',
            'text-align': 'left',
            'text-decoration': 'none',
            'text-transform': 'none',
            'white-space': 'normal',
            'letter-spacing': 'normal',
            'word-spacing': 'normal',

            # Flexbox defaults
            'justify-content': 'flex-start',
            'align-items': 'stretch',
            'flex-direction': 'row',
            'flex-wrap': 'nowrap',
            'flex-grow': '0',
            'flex-shrink': '1',
            'flex-basis': 'auto',
            'order': '0',
            'gap': '0',
            'row-gap': '0',
            'column-gap': '0',

            # Grid defaults
            'grid-template-columns': 'none',
            'grid-template-rows': 'none',
            'grid-column': 'auto',
            'grid-row': 'auto',
            'justify-items': 'stretch',
            'align-content': 'stretch',
            'grid-gap': '0',
            'grid-template-areas': 'none',
            'grid-area': 'auto',

            # Background defaults
            'background-image': 'none',
            'background-repeat': 'repeat',
            'background-position': '0% 0%',
            'background-size': 'auto',
            'background-attachment': 'scroll',

            # Border defaults
            'border-radius': '0',
            'box-shadow': 'none',
            'outline': 'none',

            # Transform defaults
            'transform': 'none',
            'transform-origin': '50% 50%',
        })

    def parse_css(self, css_string: str):
        """Parse CSS string into enhanced rules"""
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

                    # Create EnhancedCSSRule instead of CSSRule
                    self.rules.append(EnhancedCSSRule(selector, declarations))
        except Exception as e:
            print(f"CSS parse error: {e}")

    # Also add these static methods to EnhancedCSSEngine (copy from base class):
    @staticmethod
    def _serialize_selector(prelude) -> str:
        """Convert selector tokens back to string"""
        return ''.join(token.serialize() for token in prelude).strip()

    @staticmethod
    def _serialize_value(value_tokens) -> str:
        """Convert value tokens back to string"""
        return ''.join(token.serialize() for token in value_tokens).strip()

    def selector_matches(self, selector: str, element: HTMLElement) -> bool:
        """Enhanced selector matching with full CSS3+ support"""
        return self._selector_parser.selector_matches(selector, element)

    def _calculate_enhanced_specificity(self, selector: str) -> Tuple[int, int, int, int]:
        """Calculate CSS specificity with enhanced support"""
        return self._selector_parser.calculate_specificity(selector)

    def compute_style(self, element: HTMLElement) -> Dict[str, str]:
        """Enhanced style computation with improved selector matching"""
        style = {}

        # Start with default styles for tag
        if element.tag in self.default_styles:
            style.update(self.default_styles[element.tag])

        # Apply matching CSS rules in specificity order
        matching_rules = []
        for rule in self.rules:
            if self.selector_matches(rule.selector, element):
                matching_rules.append(rule)

        # Sort by specificity - handle both 3-tuple and 4-tuple specificity
        def get_specificity_key(rule):
            spec = rule.specificity
            if len(spec) == 3:
                # Base CSSRule with (ids, classes, elements)
                return (0, spec[0], spec[1], spec[2])
            elif len(spec) == 4:
                # EnhancedCSSRule with (style, ids, classes, elements)
                return spec
            else:
                # Fallback
                return (0, 0, 0, 0)

        matching_rules.sort(key=get_specificity_key)

        # Apply rules
        for rule in matching_rules:
            style.update(rule.declarations)

        # Apply inline styles (highest specificity)
        if 'style' in element.attributes:
            inline_styles = self._parse_inline_style(element.attributes['style'])
            style.update(inline_styles)

        # Process enhanced shorthand properties
        self._process_enhanced_shorthand_properties(style)

        # Process calculated values
        self._process_calculated_values(style, element)

        return style

    def _process_enhanced_shorthand_properties(self, style: Dict[str, str]):
        """Process enhanced CSS shorthand properties"""

        # Border shorthand
        if 'border' in style:
            border_value = style['border']
            parts = border_value.split()
            if len(parts) >= 1:
                style['border-width'] = parts[0]
            if len(parts) >= 2:
                style['border-style'] = parts[1]
            if len(parts) >= 3:
                style['border-color'] = parts[2]

        # Margin shorthand
        if 'margin' in style:
            values = self._parse_box_shorthand(style['margin'])
            style['margin-top'] = values[0]
            style['margin-right'] = values[1]
            style['margin-bottom'] = values[2]
            style['margin-left'] = values[3]

        # Padding shorthand
        if 'padding' in style:
            values = self._parse_box_shorthand(style['padding'])
            style['padding-top'] = values[0]
            style['padding-right'] = values[1]
            style['padding-bottom'] = values[2]
            style['padding-left'] = values[3]

        # Flex shorthand
        if 'flex' in style:
            flex_parts = style['flex'].split()
            if len(flex_parts) >= 1:
                style['flex-grow'] = flex_parts[0]
            if len(flex_parts) >= 2:
                style['flex-shrink'] = flex_parts[1]
            if len(flex_parts) >= 3:
                style['flex-basis'] = flex_parts[2]

    def _parse_box_shorthand(self, value: str) -> List[str]:
        """Parse box model shorthand (margin, padding)"""
        parts = value.split()
        if len(parts) == 1:
            return [parts[0], parts[0], parts[0], parts[0]]
        elif len(parts) == 2:
            return [parts[0], parts[1], parts[0], parts[1]]
        elif len(parts) == 3:
            return [parts[0], parts[1], parts[2], parts[1]]
        elif len(parts) == 4:
            return parts
        return ['0', '0', '0', '0']

    def _process_calculated_values(self, style: Dict[str, str], element: HTMLElement):
        """Process calc() and other calculated values"""
        for prop, value in style.items():
            if 'calc(' in value:
                style[prop] = self._evaluate_calc(value, element)

    def _evaluate_calc(self, value: str, element: HTMLElement) -> str:
        """Evaluate calc() expressions (simplified)"""
        if value.startswith('calc(') and value.endswith(')'):
            expression = value[5:-1]  # Remove calc( and )
            # Basic evaluation - in real implementation would need full parser
            return expression
        return value


class EnhancedLayoutEngine(LayoutEngine):
    """Enhanced layout engine extending base with positioning, flexbox, and grid"""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 800, enable_debug=False):
        super().__init__(viewport_width, viewport_height, enable_debug)
        self.positioned_elements: List[HTMLElement] = []

    def layout(self, element: HTMLElement, container_width: float = None,
               container_height: float = None, is_root: bool = True,
               parent_x: float = 0, parent_y: float = 0):
        """Enhanced layout building on base layout with modern features"""

        if container_width is None:
            container_width = self.viewport_width
        if container_height is None:
            container_height = self.viewport_height

        # Create enhanced layout box
        element.layout_box = EnhancedLayoutBox()

        # Ensure root element uses full viewport
        if is_root:
            element.layout_box.width = container_width
            element.layout_box.height = container_height
            element.layout_box.x = 0
            element.layout_box.y = 0

        # Copy any margin/padding from base calculation
        self._calculate_box_model(element, container_width, container_height)

        # Apply enhanced style properties to layout box
        self._apply_enhanced_style_to_layout_box(element)

        # Calculate enhanced dimensions
        self._calculate_enhanced_dimensions(element, container_width, container_height)

        # Handle enhanced positioning
        self._handle_enhanced_positioning(element, container_width, container_height,
                                          is_root, parent_x, parent_y)

        # Layout children based on display mode
        display = element.computed_style.get('display', 'block')
        if display == 'flex':
            self._layout_flex_children(element)
        elif display == 'grid':
            self._layout_grid_children(element)
        else:
            self._layout_normal_children(element)

        # Apply visual effects
        self._apply_enhanced_visual_effects(element)

    def _calculate_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """Enhanced box model calculation with grid support"""
        # Call parent implementation first
        super()._calculate_box_model(element, container_width, container_height)

        # Special handling for grid containers
        style = element.computed_style
        display = style.get('display', 'block')

        if display == 'grid':
            # Ensure grid containers have reasonable minimum dimensions
            box = element.layout_box

            # For grid containers, ensure minimum width
            if box.width <= 0:
                box.width = max(200, container_width * 0.5)

            # For grid containers, ensure minimum height
            if box.height <= 0:
                box.height = max(100, container_height * 0.3)

            print(f"Grid container {element.tag} sized to: {box.width} x {box.height}")

    def _apply_enhanced_style_to_layout_box(self, element: HTMLElement):
        """Apply enhanced styles to layout box"""
        style = element.computed_style
        box = element.layout_box

        # Enhanced positioning
        box.z_index = int(self.parse_enhanced_length(style.get('z-index', '0')))

        # Position type
        position = style.get('position', 'static')
        try:
            box.position_type = PositionType(position)
        except ValueError:
            box.position_type = PositionType.STATIC

        # Grid
        # box.grid_area = style.get('grid-area', 'auto') if style.get('grid-area', 'auto') != 'auto' else None

        grid_area = style.get('grid-area', 'auto')
        if grid_area != 'auto':
            box.grid_area = grid_area

        # Parse grid template areas
        grid_template_areas = style.get('grid-template-areas', 'none')
        if grid_template_areas != 'none':
            box.grid_template_areas = self._parse_grid_template_areas(grid_template_areas)

        # Position offsets
        box.top = self._parse_length_or_none(style.get('top'))
        box.right = self._parse_length_or_none(style.get('right'))
        box.bottom = self._parse_length_or_none(style.get('bottom'))
        box.left = self._parse_length_or_none(style.get('left'))

        # Min/max dimensions
        box.min_width = self._parse_length_or_none(style.get('min-width'))
        box.max_width = self._parse_length_or_none(style.get('max-width'))
        box.min_height = self._parse_length_or_none(style.get('min-height'))
        box.max_height = self._parse_length_or_none(style.get('max-height'))

        # Flexbox properties
        box.flex_grow = float(style.get('flex-grow', '0'))
        box.flex_shrink = float(style.get('flex-shrink', '1'))
        box.flex_basis = self._parse_length_or_none(style.get('flex-basis'))
        box.order = int(style.get('order', '0'))

        # Visual properties
        box.opacity = float(style.get('opacity', '1'))
        box.border_radius = self._parse_border_radius(style.get('border-radius', '0'))
        box.box_shadows = self._parse_box_shadows(style.get('box-shadow', 'none'))
        box.transform = self.parse_transform(style.get('transform', 'none'))

    def _calculate_enhanced_dimensions(self, element: HTMLElement, container_width: float, container_height: float):
        """Calculate dimensions with enhanced constraints"""
        style = element.computed_style
        box = element.layout_box

        # Base width calculation
        width = style.get('width', 'auto')
        if width == 'auto':
            if element.tag == 'button' and element.text_content:
                text_width = len(element.text_content) * 8
                min_width = text_width + box.padding_left + box.padding_right + 20
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(min_width, min(available_width, 200))
            else:
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(0, available_width)
        else:
            box.width = self.parse_enhanced_length(width, container_width)

        # FIXED: Base height calculation - use proper container height
        height = style.get('height', 'auto')
        if height == 'auto':
            # For grid containers, ensure they take available space
            display = style.get('display', 'block')
            if display == 'grid':
                # Grid containers should use available height unless specifically set
                available_height = container_height - box.margin_top - box.margin_bottom
                box.height = max(available_height, 100)  # Minimum height for grid containers
            else:
                box.height = self._calculate_enhanced_auto_height(element)
        else:
            box.height = self.parse_enhanced_length(height, container_height)

        # Apply min/max constraints
        if box.min_width is not None:
            box.width = max(box.width, box.min_width)
        if box.max_width is not None:
            box.width = min(box.width, box.max_width)
        if box.min_height is not None:
            box.height = max(box.height, box.min_height)
        if box.max_height is not None:
            box.height = min(box.height, box.max_height)

    def _handle_enhanced_positioning(self, element: HTMLElement, container_width: float,
                                     container_height: float, is_root: bool,
                                     parent_x: float, parent_y: float):
        """Handle enhanced positioning modes"""
        box = element.layout_box

        if box.position_type == PositionType.ABSOLUTE or box.position_type == PositionType.FIXED:
            self.positioned_elements.append(element)
            self._position_absolute_element(element, container_width, container_height)
        else:
            # Normal flow positioning
            if is_root:
                box.x = box.margin_left
                box.y = box.margin_top
            else:
                box.x = parent_x + box.margin_left
                box.y = parent_y + box.margin_top

            # Apply relative positioning after normal positioning
            if box.position_type == PositionType.RELATIVE:
                self._apply_relative_positioning(element)

    def _position_absolute_element(self, element: HTMLElement, container_width: float, container_height: float):
        """Position absolutely positioned elements"""
        box = element.layout_box

        # Calculate position based on offsets
        x = 0
        y = 0

        if box.left is not None:
            x = box.left
        elif box.right is not None:
            x = container_width - box.right - box.width

        if box.top is not None:
            y = box.top
        elif box.bottom is not None:
            y = container_height - box.bottom - box.height

        box.x = x
        box.y = y

    def _apply_relative_positioning(self, element: HTMLElement):
        """Apply relative positioning offsets"""
        box = element.layout_box

        if box.left is not None:
            box.x += box.left
        elif box.right is not None:
            box.x -= box.right

        if box.top is not None:
            box.y += box.top
        elif box.bottom is not None:
            box.y -= box.bottom

    def _layout_flex_children(self, element: HTMLElement):
        """Enhanced flexbox layout with full wrap support"""
        if not element.children:
            return

        style = element.computed_style

        # Parse flex properties
        flex_direction = FlexDirection(style.get('flex-direction', 'row'))
        flex_wrap = style.get('flex-wrap', 'nowrap')
        justify_content = JustifyContent(style.get('justify-content', 'flex-start'))
        align_items = AlignItems(style.get('align-items', 'stretch'))
        align_content = style.get('align-content', 'stretch')
        gap = self.parse_enhanced_length(style.get('gap', '0'))
        row_gap = self.parse_enhanced_length(style.get('row-gap', str(gap)))
        column_gap = self.parse_enhanced_length(style.get('column-gap', str(gap)))

        # Sort children by order
        flex_children = sorted(element.children,
                               key=lambda child: getattr(child.layout_box, 'order', 0) if child.layout_box else 0)

        # Determine main and cross axis
        is_row = flex_direction in [FlexDirection.ROW, FlexDirection.ROW_REVERSE]
        is_reverse = flex_direction in [FlexDirection.ROW_REVERSE, FlexDirection.COLUMN_REVERSE]

        # Calculate available space
        container_box = element.layout_box
        if is_row:
            main_size = container_box.width - container_box.padding_left - container_box.padding_right
            cross_size = container_box.height - container_box.padding_top - container_box.padding_bottom
            main_gap = column_gap
            cross_gap = row_gap
        else:
            main_size = container_box.height - container_box.padding_top - container_box.padding_bottom
            cross_size = container_box.width - container_box.padding_left - container_box.padding_right
            main_gap = row_gap
            cross_gap = column_gap

        # First layout all children to get their natural sizes
        for child in flex_children:
            if is_row:
                child_width = main_size  # Will be adjusted later
                child_height = cross_size
            else:
                child_width = cross_size
                child_height = main_size

            self.layout(child, child_width, child_height, is_root=False, parent_x=0, parent_y=0)

        # Handle wrapping
        if flex_wrap == 'nowrap':
            self._layout_flex_single_line(element, flex_children, justify_content, align_items,
                                          main_gap, is_row, is_reverse)
        else:
            self._layout_flex_multi_line(element, flex_children, justify_content, align_items, align_content,
                                         main_gap, cross_gap, flex_wrap, is_row, is_reverse)

    def _layout_flex_single_line(self, container: HTMLElement, children: List[HTMLElement],
                                 justify_content: JustifyContent, align_items: AlignItems,
                                 gap: float, is_row: bool, is_reverse: bool):
        """Layout flex items in a single line (no wrapping)"""
        container_box = container.layout_box
        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top
        content_width = container_box.width - container_box.padding_left - container_box.padding_right
        content_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        if is_row:
            main_size = content_width
            cross_size = content_height
        else:
            main_size = content_height
            cross_size = content_width

        # Calculate flex sizes and positions
        self._calculate_flex_sizes(children, main_size, gap, is_row)

        # Reverse order if needed
        if is_reverse:
            children = list(reversed(children))

        self._position_flex_items_single_line(container, children, justify_content, align_items,
                                              gap, is_row, content_x, content_y, content_width, content_height)

    def _layout_flex_multi_line(self, container: HTMLElement, children: List[HTMLElement],
                                justify_content: JustifyContent, align_items: AlignItems, align_content: str,
                                main_gap: float, cross_gap: float, flex_wrap: str, is_row: bool, is_reverse: bool):
        """Layout flex items with wrapping support"""
        container_box = container.layout_box
        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top
        content_width = container_box.width - container_box.padding_left - container_box.padding_right
        content_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        if is_row:
            main_size = content_width
            cross_size = content_height
        else:
            main_size = content_height
            cross_size = content_width

        # Calculate flex lines (how items wrap)
        flex_lines = self._calculate_flex_lines(children, main_size, main_gap, is_row)

        # Reverse lines if wrap-reverse
        if flex_wrap == 'wrap-reverse':
            flex_lines = list(reversed(flex_lines))

        # Reverse items in each line if flex-direction is reverse
        if is_reverse:
            for line in flex_lines:
                line['items'] = list(reversed(line['items']))

        # Calculate sizes for items in each line
        for line in flex_lines:
            self._calculate_flex_sizes(line['items'], main_size, main_gap, is_row)

        # Position flex lines using align-content
        self._position_flex_lines(container, flex_lines, align_content, cross_gap, is_row,
                                  content_x, content_y, content_width, content_height)

        # Position items within each line
        for line in flex_lines:
            self._position_flex_items_in_line(line, justify_content, align_items, main_gap, is_row)

    def _calculate_flex_lines(self, children: List[HTMLElement], main_size: float, gap: float, is_row: bool) -> List[
        Dict]:
        """Calculate how flex items wrap into lines"""
        lines = []
        current_line = {'items': [], 'cross_size': 0}
        current_main_size = 0

        for child in children:
            box = child.layout_box
            if not box:
                continue

            item_main_size = box.width if is_row else box.height
            item_cross_size = box.height if is_row else box.width

            # Check if item fits on current line
            needed_size = item_main_size
            if current_line['items']:  # Add gap if not first item
                needed_size += gap

            if current_line['items'] and current_main_size + needed_size > main_size:
                # Start new line
                lines.append(current_line)
                current_line = {'items': [child], 'cross_size': item_cross_size}
                current_main_size = item_main_size
            else:
                # Add to current line
                current_line['items'].append(child)
                current_line['cross_size'] = max(current_line['cross_size'], item_cross_size)
                current_main_size += needed_size

        # Add last line if it has items
        if current_line['items']:
            lines.append(current_line)

        return lines

    def _position_flex_lines(self, container: HTMLElement, flex_lines: List[Dict], align_content: str,
                             cross_gap: float, is_row: bool, content_x: float, content_y: float,
                             content_width: float, content_height: float):
        """Position flex lines according to align-content"""
        if not flex_lines:
            return

        cross_size = content_height if is_row else content_width
        total_lines_cross_size = sum(line['cross_size'] for line in flex_lines)
        total_gaps = cross_gap * max(0, len(flex_lines) - 1)
        free_space = cross_size - total_lines_cross_size - total_gaps

        # Calculate starting position and spacing based on align-content
        if align_content == 'flex-start':
            current_cross = content_y if is_row else content_x
            line_spacing = cross_gap
        elif align_content == 'flex-end':
            current_cross = (content_y if is_row else content_x) + free_space
            line_spacing = cross_gap
        elif align_content == 'center':
            current_cross = (content_y if is_row else content_x) + free_space / 2
            line_spacing = cross_gap
        elif align_content == 'space-between':
            current_cross = content_y if is_row else content_x
            line_spacing = cross_gap + (free_space / max(1, len(flex_lines) - 1) if len(flex_lines) > 1 else 0)
        elif align_content == 'space-around':
            space_per_line = free_space / len(flex_lines) if flex_lines else 0
            current_cross = (content_y if is_row else content_x) + space_per_line / 2
            line_spacing = cross_gap + space_per_line
        elif align_content == 'space-evenly':
            space_per_gap = free_space / (len(flex_lines) + 1) if flex_lines else 0
            current_cross = (content_y if is_row else content_x) + space_per_gap
            line_spacing = cross_gap + space_per_gap
        else:  # stretch
            current_cross = content_y if is_row else content_x
            line_spacing = cross_gap
            if free_space > 0 and len(flex_lines) > 0:
                extra_per_line = free_space / len(flex_lines)
                for line in flex_lines:
                    line['cross_size'] += extra_per_line

        # Assign positions to each line
        for line in flex_lines:
            if is_row:
                line['cross_start'] = current_cross
                line['main_start'] = content_x
            else:
                line['cross_start'] = current_cross
                line['main_start'] = content_y

            current_cross += line['cross_size'] + line_spacing

    def _position_flex_items_in_line(self, line: Dict, justify_content: JustifyContent, align_items: AlignItems,
                                     gap: float, is_row: bool):
        """Position flex items within a single line"""
        items = line['items']
        if not items:
            return

        # Calculate main axis positioning
        total_item_size = sum((item.layout_box.width if is_row else item.layout_box.height) for item in items)
        total_gap = gap * max(0, len(items) - 1)

        # Get main axis size (this would need to be passed or calculated)
        # For now, estimate from first item's container
        container = items[0].parent
        if is_row:
            main_size = container.layout_box.width - container.layout_box.padding_left - container.layout_box.padding_right
            main_start = line['main_start']
        else:
            main_size = container.layout_box.height - container.layout_box.padding_top - container.layout_box.padding_bottom
            main_start = line['main_start']

        free_space = main_size - total_item_size - total_gap

        # Calculate main axis positions
        if justify_content == JustifyContent.FLEX_START:
            current_main = main_start
            item_spacing = gap
        elif justify_content == JustifyContent.FLEX_END:
            current_main = main_start + free_space
            item_spacing = gap
        elif justify_content == JustifyContent.CENTER:
            current_main = main_start + free_space / 2
            item_spacing = gap
        elif justify_content == JustifyContent.SPACE_BETWEEN:
            current_main = main_start
            item_spacing = gap + (free_space / max(1, len(items) - 1) if len(items) > 1 else 0)
        elif justify_content == JustifyContent.SPACE_AROUND:
            space_per_item = free_space / len(items) if items else 0
            current_main = main_start + space_per_item / 2
            item_spacing = gap + space_per_item
        else:  # SPACE_EVENLY
            space_per_gap = free_space / (len(items) + 1) if items else 0
            current_main = main_start + space_per_gap
            item_spacing = gap + space_per_gap

        # Position each item
        for item in items:
            box = item.layout_box

            # Main axis position
            if is_row:
                box.x = current_main
                current_main += box.width + item_spacing
            else:
                box.y = current_main
                current_main += box.height + item_spacing

            # Cross axis position (align-items)
            cross_start = line['cross_start']
            cross_size = line['cross_size']
            item_cross_size = box.height if is_row else box.width

            if align_items == AlignItems.FLEX_START:
                cross_pos = cross_start
            elif align_items == AlignItems.FLEX_END:
                cross_pos = cross_start + cross_size - item_cross_size
            elif align_items == AlignItems.CENTER:
                cross_pos = cross_start + (cross_size - item_cross_size) / 2
            else:  # STRETCH
                cross_pos = cross_start
                if is_row:
                    box.height = cross_size
                else:
                    box.width = cross_size

            if is_row:
                box.y = cross_pos
            else:
                box.x = cross_pos

    def _position_flex_items_single_line(self, container: HTMLElement, children: List[HTMLElement],
                                         justify_content: JustifyContent, align_items: AlignItems,
                                         gap: float, is_row: bool, content_x: float, content_y: float,
                                         content_width: float, content_height: float):
        """Position flex items in a single line (no wrapping)"""
        if not children:
            return

        if is_row:
            main_size = content_width
            cross_size = content_height
        else:
            main_size = content_height
            cross_size = content_width

        total_width = sum(child.layout_box.width for child in children if child.layout_box) if is_row else \
            sum(child.layout_box.height for child in children if child.layout_box)
        total_gap = gap * max(0, len(children) - 1)
        free_space = main_size - total_width - total_gap

        # Calculate starting position
        if justify_content == JustifyContent.FLEX_START:
            current_main = content_x if is_row else content_y
            item_spacing = gap
        elif justify_content == JustifyContent.FLEX_END:
            current_main = (content_x if is_row else content_y) + free_space
            item_spacing = gap
        elif justify_content == JustifyContent.CENTER:
            current_main = (content_x if is_row else content_y) + free_space / 2
            item_spacing = gap
        elif justify_content == JustifyContent.SPACE_BETWEEN:
            current_main = content_x if is_row else content_y
            item_spacing = gap + (free_space / max(1, len(children) - 1) if len(children) > 1 else 0)
        elif justify_content == JustifyContent.SPACE_AROUND:
            space_per_item = free_space / len(children) if children else 0
            current_main = (content_x if is_row else content_y) + space_per_item / 2
            item_spacing = gap + space_per_item
        else:  # SPACE_EVENLY
            space_per_gap = free_space / (len(children) + 1) if children else 0
            current_main = (content_x if is_row else content_y) + space_per_gap
            item_spacing = gap + space_per_gap

        # Position items
        for child in children:
            if child.layout_box is None:
                continue

            # Main axis positioning
            if is_row:
                child.layout_box.x = current_main
                current_main += child.layout_box.width + item_spacing
            else:
                child.layout_box.y = current_main
                current_main += child.layout_box.height + item_spacing

            # Cross axis alignment
            if align_items == AlignItems.FLEX_START:
                cross_pos = content_y if is_row else content_x
            elif align_items == AlignItems.FLEX_END:
                item_cross_size = child.layout_box.height if is_row else child.layout_box.width
                cross_pos = (content_y if is_row else content_x) + cross_size - item_cross_size
            elif align_items == AlignItems.CENTER:
                item_cross_size = child.layout_box.height if is_row else child.layout_box.width
                cross_pos = (content_y if is_row else content_x) + (cross_size - item_cross_size) / 2
            else:  # STRETCH
                cross_pos = content_y if is_row else content_x
                if is_row:
                    child.layout_box.height = cross_size
                else:
                    child.layout_box.width = cross_size

            if is_row:
                child.layout_box.y = cross_pos
            else:
                child.layout_box.x = cross_pos

    def _calculate_flex_sizes(self, children: List[HTMLElement], main_size: float, gap: float, is_row: bool):
        """Calculate sizes for flex items"""
        total_gap = gap * max(0, len(children) - 1)
        available_size = main_size - total_gap

        # Calculate base sizes and flexibility
        total_flex_grow = 0
        total_flex_shrink = 0
        used_space = 0

        for child in children:
            box = child.layout_box

            # Ensure layout box exists (should exist after layout call, but safety check)
            if box is None:
                continue

            # Get flex properties with defaults
            flex_grow = getattr(box, 'flex_grow', 0) if hasattr(box, 'flex_grow') else 0
            flex_shrink = getattr(box, 'flex_shrink', 1) if hasattr(box, 'flex_shrink') else 1
            flex_basis = getattr(box, 'flex_basis', None) if hasattr(box, 'flex_basis') else None

            # Get base size
            if is_row:
                base_size = flex_basis if flex_basis is not None else box.width
            else:
                base_size = flex_basis if flex_basis is not None else box.height

            used_space += base_size
            total_flex_grow += flex_grow
            total_flex_shrink += flex_shrink

        # Distribute free space
        free_space = available_size - used_space

        if free_space > 0 and total_flex_grow > 0:
            # Distribute extra space
            for child in children:
                box = child.layout_box
                if box is None:
                    continue

                flex_grow = getattr(box, 'flex_grow', 0) if hasattr(box, 'flex_grow') else 0
                extra = (flex_grow / total_flex_grow) * free_space

                if is_row:
                    box.width += extra
                else:
                    box.height += extra

        elif free_space < 0 and total_flex_shrink > 0:
            # Shrink items
            shrink_factor = abs(free_space) / total_flex_shrink

            for child in children:
                box = child.layout_box
                if box is None:
                    continue

                flex_shrink = getattr(box, 'flex_shrink', 1) if hasattr(box, 'flex_shrink') else 1
                shrink = flex_shrink * shrink_factor

                if is_row:
                    box.width = max(0, box.width - shrink)
                else:
                    box.height = max(0, box.height - shrink)

    def _position_flex_items(self, container: HTMLElement, children: List[HTMLElement],
                             justify_content: JustifyContent, align_items: AlignItems,
                             gap: float, is_row: bool):
        """Position flex items"""
        container_box = container.layout_box
        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top
        content_width = container_box.width - container_box.padding_left - container_box.padding_right
        content_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        if is_row:
            # Row direction
            total_width = sum(child.layout_box.width for child in children if child.layout_box)
            total_gap = gap * max(0, len(children) - 1)
            free_space = content_width - total_width - total_gap

            # Calculate starting position
            if justify_content == JustifyContent.FLEX_START:
                current_x = content_x
            elif justify_content == JustifyContent.FLEX_END:
                current_x = content_x + free_space
            elif justify_content == JustifyContent.CENTER:
                current_x = content_x + free_space / 2
            elif justify_content == JustifyContent.SPACE_BETWEEN:
                current_x = content_x
                gap = gap + (free_space / max(1, len(children) - 1)) if len(children) > 1 else gap
            elif justify_content == JustifyContent.SPACE_AROUND:
                space_per_item = free_space / len(children) if children else 0
                current_x = content_x + space_per_item / 2
                gap = gap + space_per_item
            else:  # SPACE_EVENLY
                space_per_gap = free_space / (len(children) + 1) if children else 0
                current_x = content_x + space_per_gap
                gap = gap + space_per_gap

            # Position items
            for child in children:
                if child.layout_box is None:
                    continue

                child.layout_box.x = current_x

                # Cross axis alignment
                if align_items == AlignItems.FLEX_START:
                    child.layout_box.y = content_y
                elif align_items == AlignItems.FLEX_END:
                    child.layout_box.y = content_y + content_height - child.layout_box.height
                elif align_items == AlignItems.CENTER:
                    child.layout_box.y = content_y + (content_height - child.layout_box.height) / 2
                else:  # STRETCH
                    child.layout_box.y = content_y
                    child.layout_box.height = content_height

                current_x += child.layout_box.width + gap

        else:
            # Column direction
            current_y = content_y

            for child in children:
                if child.layout_box is None:
                    continue

                child.layout_box.y = current_y

                # Cross axis alignment (horizontal)
                if align_items == AlignItems.FLEX_START:
                    child.layout_box.x = content_x
                elif align_items == AlignItems.FLEX_END:
                    child.layout_box.x = content_x + content_width - child.layout_box.width
                elif align_items == AlignItems.CENTER:
                    child.layout_box.x = content_x + (content_width - child.layout_box.width) / 2
                else:  # STRETCH
                    child.layout_box.x = content_x
                    child.layout_box.width = content_width

                current_y += child.layout_box.height + gap

    def _layout_grid_children(self, element: HTMLElement):
        """Enhanced CSS Grid layout with proper area support"""
        if not element.children:
            return

        style = element.computed_style
        print(f"\n=== ENHANCED GRID LAYOUT FOR {element.tag} ===")

        # Parse grid properties
        columns_str = style.get('grid-template-columns', 'none')
        rows_str = style.get('grid-template-rows', 'none')
        areas_str = style.get('grid-template-areas', 'none')
        gap = self.parse_enhanced_length(style.get('gap', '0'))

        print(f"Grid columns: '{columns_str}'")
        print(f"Grid rows: '{rows_str}'")
        print(f"Gap: {gap}")

        # Parse templates with proper repeat() support
        columns = self._parse_grid_template(columns_str)
        rows = self._parse_grid_template(rows_str)

        print(f"Parsed columns: {columns}")
        print(f"Parsed rows: {rows}")

        # Parse grid template areas
        grid_areas = []
        if areas_str != 'none':
            grid_areas = self._parse_grid_template_areas(areas_str)

        # If no explicit columns/rows but we have areas, derive from areas
        if grid_areas:
            if not columns or columns == ['none']:
                columns = ['1fr'] * len(grid_areas[0])
            if not rows or rows == ['none']:
                rows = ['1fr'] * len(grid_areas)

        # Default fallback
        if not columns or columns == ['none']:
            columns = ['1fr']
        if not rows or rows == ['none']:
            rows = ['1fr']

        print(f"Final columns: {columns}")
        print(f"Final rows: {rows}")

        # Calculate container dimensions
        container_box = element.layout_box
        container_width = container_box.width - container_box.padding_left - container_box.padding_right
        container_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        # Ensure minimum container size
        container_width = max(100, container_width)
        container_height = max(100, container_height)

        print(f"Container size: {container_width} x {container_height}")

        # Calculate track sizes with proper repeat support
        column_sizes = self._calculate_grid_track_sizes(columns, container_width, gap, len(columns))
        row_sizes = self._calculate_grid_track_sizes(rows, container_height, gap, len(rows))

        print(f"Column sizes: {column_sizes}")
        print(f"Row sizes: {row_sizes}")

        # Validate sizes
        if not column_sizes or not row_sizes:
            print("Invalid grid sizes, falling back to normal layout")
            self._layout_normal_children(element)
            return

        # Create area name to grid position mapping
        area_map = {}
        if grid_areas:
            area_map = self._create_grid_area_map(grid_areas)

        print(f"Area map: {area_map}")

        # Position children
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top

        # Filter valid children
        valid_children = []
        for child in element.children:
            if (hasattr(child, 'tag') and
                    child.tag not in ['comment', 'text'] and
                    'Comment' not in str(child.tag)):
                valid_children.append(child)

        print(f"Valid children: {[child.tag for child in valid_children]}")

        # Track used grid cells
        used_cells = set()

        # Place children with explicit grid-area
        auto_placement_children = []

        for child in valid_children:
            grid_area = child.computed_style.get('grid-area', 'auto')
            print(f"Child {child.tag} has grid-area: '{grid_area}'")

            if grid_area != 'auto' and grid_area in area_map:
                # Place in named grid area
                row_start, col_start, row_end, col_end = area_map[grid_area]

                # Validate bounds
                if (row_start < len(row_sizes) and col_start < len(column_sizes) and
                        row_end <= len(row_sizes) and col_end <= len(column_sizes)):

                    self._place_grid_item_at_position(child, row_start, col_start, row_end, col_end,
                                                      content_x, content_y, column_sizes, row_sizes, gap)

                    # Mark cells as used
                    for r in range(row_start, row_end):
                        for c in range(col_start, col_end):
                            used_cells.add((r, c))
                else:
                    print(f"Grid area bounds invalid for {child.tag}")
                    auto_placement_children.append(child)
            else:
                auto_placement_children.append(child)

        # Auto-place remaining children with proper bounds checking
        current_row = 0
        current_col = 0

        for child in auto_placement_children:
            # Find next available cell
            placed = False
            attempts = 0
            max_attempts = len(row_sizes) * len(column_sizes) + 10

            while current_row < len(row_sizes) and not placed and attempts < max_attempts:
                attempts += 1

                while current_col < len(column_sizes):
                    if (current_row, current_col) not in used_cells:
                        # Place child
                        self._place_grid_item_at_position(child, current_row, current_col,
                                                          current_row + 1, current_col + 1,
                                                          content_x, content_y, column_sizes, row_sizes, gap)

                        used_cells.add((current_row, current_col))
                        current_col += 1
                        placed = True
                        break

                    current_col += 1

                if not placed:
                    current_col = 0
                    current_row += 1

            if not placed:
                print(f"Warning: Could not place {child.tag} in grid after {attempts} attempts")
                # Fall back to normal positioning
                child_x = content_x
                child_y = content_y + current_row * 50  # Basic fallback positioning
                self.layout(child, 100, 50, is_root=False, parent_x=child_x, parent_y=child_y)

    def _place_grid_item_at_position(self, child: HTMLElement, row_start: int, col_start: int,
                                     row_end: int, col_end: int, content_x: float, content_y: float,
                                     column_sizes: List[float], row_sizes: List[float], gap: float):

        # Validate indices
        if (row_start >= len(row_sizes) or col_start >= len(column_sizes) or
                row_end > len(row_sizes) or col_end > len(column_sizes)):
            print(f"Invalid grid position for {child.tag}")
            return

        # Calculate position with proper gap handling
        x = content_x
        for i in range(col_start):
            x += column_sizes[i]
            if i > 0:  # Don't add gap before first column
                x += gap

        y = content_y
        for i in range(row_start):
            y += row_sizes[i]
            if i > 0:  # Don't add gap before first row
                y += gap

        # Calculate size spanning multiple cells
        width = sum(column_sizes[col_start:col_end])
        if col_end - col_start > 1:  # Add gaps between spanned columns
            width += gap * (col_end - col_start - 1)

        height = sum(row_sizes[row_start:row_end])
        if row_end - row_start > 1:  # Add gaps between spanned rows
            height += gap * (row_end - row_start - 1)

        # Ensure positive dimensions
        width = max(0, width)
        height = max(0, height)

        # Layout the child with corrected bounds checking
        self.layout(child, width, height, is_root=False, parent_x=x, parent_y=y)

    def _validate_layout_box(self, element: HTMLElement):
        """Validate and fix layout box coordinates"""
        if not element.layout_box:
            return

        box = element.layout_box

        # Ensure non-negative positions for non-absolutely positioned elements
        if not hasattr(box, 'position_type') or box.position_type != PositionType.ABSOLUTE:
            box.x = max(0, box.x)
            box.y = max(0, box.y)

        # Ensure non-negative dimensions
        box.width = max(0, box.width)
        box.height = max(0, box.height)

        # Clamp to viewport bounds if necessary
        if box.x + box.width > self.viewport_width:
            box.width = max(0, self.viewport_width - box.x)

        if box.y + box.height > self.viewport_height:
            box.height = max(0, self.viewport_height - box.y)

    def _create_grid_area_map(self, grid_areas: List[List[str]]) -> Dict[str, Tuple[int, int, int, int]]:
        """Create mapping from area names to grid bounds (row_start, col_start, row_end, col_end)"""
        area_map = {}

        for row_idx, row in enumerate(grid_areas):
            for col_idx, area_name in enumerate(row):
                if area_name != '.' and area_name != 'none':
                    if area_name not in area_map:
                        # Initialize with current position
                        area_map[area_name] = [row_idx, col_idx, row_idx + 1, col_idx + 1]
                    else:
                        # Extend the area bounds
                        bounds = area_map[area_name]
                        bounds[0] = min(bounds[0], row_idx)  # min row
                        bounds[1] = min(bounds[1], col_idx)  # min col
                        bounds[2] = max(bounds[2], row_idx + 1)  # max row
                        bounds[3] = max(bounds[3], col_idx + 1)  # max col

        # Convert to tuples
        return {name: tuple(bounds) for name, bounds in area_map.items()}

    def _place_grid_item_in_area(self, child: HTMLElement, area_bounds: Tuple[int, int, int, int],
                                 content_x: float, content_y: float, column_sizes: List[float],
                                 row_sizes: List[float], gap: float, used_cells: set):
        """Place a grid item in a named area"""
        row_start, col_start, row_end, col_end = area_bounds

        # Calculate position
        x = content_x + sum(column_sizes[:col_start]) + gap * col_start
        y = content_y + sum(row_sizes[:row_start]) + gap * row_start

        # Calculate size (spans multiple cells)
        width = sum(column_sizes[col_start:col_end]) + gap * (col_end - col_start - 1)
        height = sum(row_sizes[row_start:row_end]) + gap * (row_end - row_start - 1)

        # Layout the child
        self.layout(child, width, height, is_root=False, parent_x=x, parent_y=y)

        # Mark cells as used
        for r in range(row_start, row_end):
            for c in range(col_start, col_end):
                used_cells.add((r, c))

    def _parse_grid_template_areas(self, areas_value: str) -> List[List[str]]:
        """Parse grid-template-areas property"""
        if areas_value == 'none' or not areas_value:
            return []

        # Extract quoted strings
        import re
        quoted_areas = re.findall(r'"([^"]*)"', areas_value)

        grid_areas = []
        for area_row in quoted_areas:
            # Split by whitespace
            area_names = area_row.strip().split()
            if area_names:
                grid_areas.append(area_names)

        return grid_areas

    def _parse_grid_template(self, template: str) -> List[str]:
        """Parse grid template with proper repeat() function support"""
        if template == 'none' or not template:
            return []

        # Handle repeat() functions
        expanded_tracks = []

        # Split by whitespace but handle repeat() functions properly
        parts = self._split_grid_template(template)

        for part in parts:
            if part.startswith('repeat(') and part.endswith(')'):
                repeat_tracks = self._parse_repeat_function(part)
                expanded_tracks.extend(repeat_tracks)
            else:
                expanded_tracks.append(part)

        return expanded_tracks

    def _split_grid_template(self, template: str) -> List[str]:
        """Split grid template while preserving repeat() functions"""
        parts = []
        current_part = ""
        paren_depth = 0

        i = 0
        while i < len(template):
            char = template[i]

            if char == '(':
                paren_depth += 1
                current_part += char
            elif char == ')':
                paren_depth -= 1
                current_part += char

                # If we've closed all parentheses and have a complete part
                if paren_depth == 0 and current_part.strip():
                    parts.append(current_part.strip())
                    current_part = ""
            elif char.isspace() and paren_depth == 0:
                # Only split on whitespace when not inside parentheses
                if current_part.strip():
                    parts.append(current_part.strip())
                    current_part = ""
            else:
                current_part += char

            i += 1

        # Add any remaining part
        if current_part.strip():
            parts.append(current_part.strip())

        return parts

    def _parse_repeat_function(self, repeat_str: str) -> List[str]:
        """Parse repeat(count, tracks) into expanded track list"""
        if not repeat_str.startswith('repeat(') or not repeat_str.endswith(')'):
            return [repeat_str]

        # Extract content between parentheses
        content = repeat_str[7:-1]  # Remove 'repeat(' and ')'

        # Find the first comma that separates count from tracks
        comma_pos = self._find_top_level_comma(content)

        if comma_pos == -1:
            print(f"Invalid repeat function: {repeat_str}")
            return []

        count_str = content[:comma_pos].strip()
        tracks_str = content[comma_pos + 1:].strip()

        # Parse count
        try:
            if count_str.isdigit():
                count = int(count_str)
            elif count_str in ['auto-fill', 'auto-fit']:
                # For now, default to a reasonable number for auto-fill/auto-fit
                # In a full implementation, this would be calculated based on container size
                return [tracks_str] * 3  # Default to 3 columns
            else:
                print(f"Invalid repeat count: {count_str}")
                return []
        except ValueError:
            print(f"Invalid repeat count: {count_str}")
            return []

        # Limit count to prevent memory issues
        count = min(count, 100)

        # Parse and expand tracks
        track_parts = self._split_grid_template(tracks_str)
        expanded = []

        for _ in range(count):
            expanded.extend(track_parts)

        return expanded

    def _find_top_level_comma(self, content: str) -> int:
        """Find the first comma that's not inside parentheses"""
        paren_depth = 0

        for i, char in enumerate(content):
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                return i

        return -1

    def _calculate_grid_track_sizes(self, tracks: List[str], container_size: float,
                                    gap: float, track_count: int) -> List[float]:
        """Calculate grid track sizes with proper fr unit support"""
        if not tracks:
            return [container_size]

        # Use actual track count from expanded tracks
        actual_track_count = len(tracks)

        if actual_track_count == 0:
            return [container_size]

        total_gap = gap * max(0, actual_track_count - 1)
        available_size = max(0, container_size - total_gap)

        print(f"Calculating track sizes: tracks={tracks}, container={container_size}, gap={gap}")
        print(f"Available size after gaps: {available_size}")

        sizes = []
        fr_tracks = []
        used_size = 0

        # First pass: calculate fixed sizes
        for i, track in enumerate(tracks):
            if track.endswith('fr'):
                try:
                    fr_value = float(track[:-2])
                    fr_tracks.append((i, fr_value))
                    sizes.append(0)  # Will be calculated later
                except ValueError:
                    sizes.append(0)
            elif track == 'auto':
                sizes.append(0)  # Will be calculated later
            elif track.endswith('px'):
                try:
                    size = float(track[:-2])
                    sizes.append(size)
                    used_size += size
                except ValueError:
                    sizes.append(0)
            elif track.endswith('%'):
                try:
                    percentage = float(track[:-1]) / 100.0
                    size = container_size * percentage
                    sizes.append(size)
                    used_size += size
                except ValueError:
                    sizes.append(0)
            else:
                try:
                    # Try to parse as plain number (px)
                    size = float(track)
                    sizes.append(size)
                    used_size += size
                except ValueError:
                    sizes.append(0)

        # Second pass: distribute remaining space to fr units
        remaining_size = max(0, available_size - used_size)
        total_fr = sum(fr for _, fr in fr_tracks)

        print(f"Used size: {used_size}, Remaining: {remaining_size}, Total fr: {total_fr}")

        if total_fr > 0 and remaining_size > 0:
            fr_unit_size = remaining_size / total_fr
            for i, fr in fr_tracks:
                sizes[i] = fr * fr_unit_size

        # Third pass: handle auto tracks
        auto_count = tracks.count('auto')
        if auto_count > 0:
            current_used = sum(sizes)
            auto_remaining = max(0, available_size - current_used)
            auto_size = auto_remaining / auto_count if auto_count > 0 else 0

            for i, track in enumerate(tracks):
                if track == 'auto':
                    sizes[i] = auto_size

        # Ensure all sizes are non-negative
        sizes = [max(0, size) for size in sizes]

        print(f"Final track sizes: {sizes}")

        return sizes

    def _layout_normal_children(self, element: HTMLElement):
        """Normal flow layout"""
        # Use enhanced block layout from base, but with improved positioning
        if not element.children:
            return

        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        available_width = element.layout_box.width - element.layout_box.padding_left - element.layout_box.padding_right
        available_height = element.layout_box.height - element.layout_box.padding_top - element.layout_box.padding_bottom

        current_y = content_y

        for child in element.children:
            child_x = content_x
            child_y = current_y

            # Recursive layout
            self.layout(child, available_width, available_height, is_root=False,
                        parent_x=child_x, parent_y=child_y)

            current_y += (child.layout_box.margin_top + child.layout_box.height + child.layout_box.margin_bottom)

    @staticmethod
    def _apply_enhanced_visual_effects(element: HTMLElement):
        """Apply enhanced visual effects"""
        style = element.computed_style
        box = element.layout_box

        # Visibility
        visibility = style.get('visibility', 'visible')
        if visibility == 'hidden':
            box.opacity = 0

    def parse_enhanced_length(self, value: str, container_size: float = 0) -> float:
        """Enhanced length parsing with more units"""
        if not value or value == 'auto':
            return 0

        try:
            if value.endswith('px'):
                return float(value[:-2])
            elif value.endswith('%'):
                return container_size * (float(value[:-1]) / 100)
            elif value.endswith('em'):
                return float(value[:-2]) * 16
            elif value.endswith('rem'):
                return float(value[:-3]) * 16
            elif value.endswith('vh'):
                return self.viewport_height * (float(value[:-2]) / 100)
            elif value.endswith('vw'):
                return self.viewport_width * (float(value[:-2]) / 100)
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0

    def _parse_length_or_none(self, value: Optional[str]) -> Optional[float]:
        """Parse length or return None"""
        if value is None or value == 'auto':
            return None
        return self.parse_enhanced_length(value)

    def _calculate_enhanced_auto_height(self, element: HTMLElement) -> float:
        """Enhanced auto height calculation"""
        style = element.computed_style

        if element.text_content and element.text_content.strip():
            font_size = self.parse_enhanced_length(style.get('font-size', '16px'))
            line_height = style.get('line-height', '1.4')

            if line_height.endswith('px'):
                line_height_value = self.parse_enhanced_length(line_height)
            else:
                try:
                    line_height_value = float(line_height) * font_size
                except:
                    line_height_value = font_size * 1.4

            padding_height = self.parse_enhanced_length(style.get('padding-top', '0')) + \
                             self.parse_enhanced_length(style.get('padding-bottom', '0'))

            return max(line_height_value + padding_height, 40)

        # Enhanced element-specific heights
        display = style.get('display', 'block')
        if display == 'grid':
            return 200  # Grid containers need more space
        elif display == 'flex':
            return 100  # Flex containers need reasonable space
        elif element.tag == 'h1':
            return 60
        elif element.tag == 'h2':
            return 50
        elif element.tag in ['input', 'button']:
            return 40
        elif element.tag == 'div':
            return 80  # Increased from 50
        elif element.tag in ['section', 'main', 'aside']:
            return 150  # Container elements need more space

        return 50  # Increased default from 30

    def parse_transform(self, transform_value: str) -> Transform:
        """Parse CSS transform property"""
        transform = Transform()

        if transform_value == 'none':
            return transform

        # Parse transform functions
        for func_match in re.finditer(r'(\w+)\(([^)]+)\)', transform_value):
            func_name = func_match.group(1)
            args = [arg.strip() for arg in func_match.group(2).split(',')]

            if func_name == 'translateX':
                transform.translate_x = self.parse_enhanced_length(args[0])
            elif func_name == 'translateY':
                transform.translate_y = self.parse_enhanced_length(args[0])
            elif func_name == 'translate':
                transform.translate_x = self.parse_enhanced_length(args[0])
                if len(args) > 1:
                    transform.translate_y = self.parse_enhanced_length(args[1])
            elif func_name == 'scaleX':
                transform.scale_x = float(args[0])
            elif func_name == 'scaleY':
                transform.scale_y = float(args[0])
            elif func_name == 'scale':
                scale = float(args[0])
                transform.scale_x = scale
                transform.scale_y = scale
            elif func_name == 'rotate':
                angle_str = args[0]
                if angle_str.endswith('deg'):
                    angle = float(angle_str[:-3])
                    transform.rotate = math.radians(angle)
                elif angle_str.endswith('rad'):
                    transform.rotate = float(angle_str[:-3])
            # ADD THESE SKEW CASES:
            elif func_name == 'skewX':
                angle_str = args[0]
                if angle_str.endswith('deg'):
                    transform.skew_x = math.radians(float(angle_str[:-3]))
                elif angle_str.endswith('rad'):
                    transform.skew_x = float(angle_str[:-3])
            elif func_name == 'skewY':
                angle_str = args[0]
                if angle_str.endswith('deg'):
                    transform.skew_y = math.radians(float(angle_str[:-3]))
                elif angle_str.endswith('rad'):
                    transform.skew_y = float(angle_str[:-3])
            elif func_name == 'skew':
                # skew(x) or skew(x, y)
                angle_x_str = args[0]
                if angle_x_str.endswith('deg'):
                    transform.skew_x = math.radians(float(angle_x_str[:-3]))
                elif angle_x_str.endswith('rad'):
                    transform.skew_x = float(angle_x_str[:-3])

                if len(args) > 1:
                    angle_y_str = args[1]
                    if angle_y_str.endswith('deg'):
                        transform.skew_y = math.radians(float(angle_y_str[:-3]))
                    elif angle_y_str.endswith('rad'):
                        transform.skew_y = float(angle_y_str[:-3])

        return transform

    def _parse_border_radius(self, border_radius: str) -> Tuple[float, float, float, float]:
        """Parse border-radius property"""
        if border_radius == '0' or border_radius == 'none':
            return (0, 0, 0, 0)

        values = border_radius.split()
        parsed_values = [self.parse_enhanced_length(v) for v in values]

        if len(parsed_values) == 1:
            return (parsed_values[0],) * 4
        elif len(parsed_values) == 2:
            return (parsed_values[0], parsed_values[1], parsed_values[0], parsed_values[1])
        elif len(parsed_values) == 3:
            return (parsed_values[0], parsed_values[1], parsed_values[2], parsed_values[1])
        else:
            return tuple(parsed_values[:4])

    def _parse_box_shadows(self, box_shadow: str) -> List[BoxShadow]:
        """Parse box-shadow property"""
        if box_shadow == 'none':
            return []

        shadows = []
        shadow_parts = box_shadow.split()

        if len(shadow_parts) >= 2:
            shadow = BoxShadow()
            shadow.offset_x = self.parse_enhanced_length(shadow_parts[0])
            shadow.offset_y = self.parse_enhanced_length(shadow_parts[1])

            if len(shadow_parts) >= 3:
                shadow.blur_radius = self.parse_enhanced_length(shadow_parts[2])
            if len(shadow_parts) >= 4:
                shadow.spread_radius = self.parse_enhanced_length(shadow_parts[3])
            if len(shadow_parts) >= 5:
                shadow.color = self._parse_enhanced_color(shadow_parts[4])

            shadows.append(shadow)

        return shadows

    def _parse_enhanced_color(self, color_string: str) -> Tuple[int, int, int, int]:
        """Parse color to RGBA tuple"""
        if color_string.startswith('#'):
            if len(color_string) == 7:
                r = int(color_string[1:3], 16)
                g = int(color_string[3:5], 16)
                b = int(color_string[5:7], 16)
                return (r, g, b, 255)

        # Default to black
        return (0, 0, 0, 255)


class EnhancedMarkupRenderer(MarkupRenderer):
    """Enhanced renderer extending base with transforms, gradients, and effects"""

    def __init__(self):
        super().__init__()  # Get all base renderer functionality
        self.transform_cache = {}
        self.gradient_cache = {}
        self.image_cache = {}
        self.background_image_cache = {}

    def render_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Enhanced rendering building on base functionality"""
        if not element.layout_box:
            return

        box = element.layout_box
        if box.width <= 0 or box.height <= 0:
            return

        # Check for enhanced effects
        has_transform = hasattr(box, 'transform') and self._has_transform(box.transform)
        has_opacity = hasattr(box, 'opacity') and box.opacity < 1.0
        has_shadows = hasattr(box, 'box_shadows') and box.box_shadows

        if has_transform or has_opacity or has_shadows:
            self._render_enhanced_element(element, target_surface)
        else:
            self._render_normal_element(element, target_surface)

        # Render children
        for child in element.children:
            self.render_element(child, target_surface)

    def _render_enhanced_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Render element with enhanced effects"""
        box = element.layout_box

        # Create element surface
        elem_surface = pygame.Surface((int(box.width), int(box.height)), pygame.SRCALPHA)

        # Render content using enhanced methods
        self._render_enhanced_content(element, elem_surface)

        # Apply shadows
        if hasattr(box, 'box_shadows') and box.box_shadows:
            elem_surface = self._apply_box_shadows(elem_surface, box.box_shadows)

        # Apply transforms
        if hasattr(box, 'transform') and self._has_transform(box.transform):
            elem_surface = self._apply_transforms(elem_surface, box.transform)

        # Apply opacity
        if hasattr(box, 'opacity') and box.opacity < 1.0:
            self._apply_opacity(elem_surface, box.opacity)

        # Position on target (handle transformed positioning)
        if hasattr(box, 'transform') and self._has_transform(box.transform):
            # Calculate center for transformed elements
            center_x = box.x + box.width / 2
            center_y = box.y + box.height / 2
            rect = elem_surface.get_rect()
            rect.center = (center_x, center_y)
            target_surface.blit(elem_surface, rect)
        else:
            target_surface.blit(elem_surface, (int(box.x), int(box.y)))

    def _render_normal_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Render element without advanced effects using enhanced base methods"""
        box = element.layout_box

        # Create element surface
        elem_surface = pygame.Surface((int(box.width), int(box.height)), pygame.SRCALPHA)

        # Render content
        self._render_enhanced_content(element, elem_surface)

        # Blit to target
        target_surface.blit(elem_surface, (int(box.x), int(box.y)))

    def _render_enhanced_content(self, element: HTMLElement, surface: pygame.Surface):
        """Render element content with enhanced features"""

        # Enhanced background rendering
        self._render_enhanced_background(surface, element)

        # Enhanced border rendering
        self._render_enhanced_border(surface, element)

        # Enhanced text rendering
        if element.text_content and element.text_content.strip():
            self._render_enhanced_text(surface, element)

    def _render_enhanced_background(self, surface: pygame.Surface, element: HTMLElement):
        """Enhanced background rendering with images and gradients"""
        style = element.computed_style

        # Check for background-image first
        background_image = style.get('background-image', 'none')

        if background_image != 'none' and not background_image.startswith('linear-gradient'):
            # Handle background image
            bg_image = self._load_background_image(background_image)
            if bg_image:
                self._render_background_image(surface, bg_image, style, element.layout_box)
                return  # Skip solid color if image loaded successfully

        # Check for gradient
        background = style.get('background', '')
        gradient_def = None

        if background_image.startswith('linear-gradient'):
            gradient_def = background_image
        elif 'linear-gradient' in background:
            # Extract gradient from background shorthand
            import re
            match = re.search(r'linear-gradient\([^)]+\)', background)
            if match:
                gradient_def = match.group(0)

        if gradient_def:
            self._render_linear_gradient_background(surface, gradient_def, element.layout_box)
        else:
            # Solid color background
            bg_color = style.get('background-color', 'transparent')
            if bg_color and bg_color != 'transparent':
                color = self._parse_color(bg_color)
                if color:
                    if hasattr(element.layout_box, 'border_radius'):
                        self._fill_rounded_rect(surface, color, element.layout_box.border_radius)
                    else:
                        surface.fill(color)

    def _render_background_image(self, surface: pygame.Surface, image: pygame.Surface,
                                 style: Dict[str, str], layout_box):
        """Render background image with positioning and scaling"""
        target_width, target_height = surface.get_size()

        # Get background properties
        bg_repeat = style.get('background-repeat', 'repeat')
        bg_size = style.get('background-size', 'auto')
        bg_position = style.get('background-position', '0% 0%')

        # Scale image according to background-size
        scaled_image = self._scale_background_image(image, bg_size, target_width, target_height)

        # Create pattern according to background-repeat
        pattern_surface = self._create_background_pattern(scaled_image, bg_repeat, target_width, target_height)

        # Apply background-position (simplified - just handle basic cases)
        final_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)

        # Parse position
        pos_parts = bg_position.split()
        x_pos = y_pos = 0

        if len(pos_parts) >= 1:
            if pos_parts[0].endswith('%'):
                x_percent = float(pos_parts[0][:-1]) / 100
                x_pos = int((target_width - scaled_image.get_width()) * x_percent)
            elif pos_parts[0] == 'center':
                x_pos = (target_width - scaled_image.get_width()) // 2
            elif pos_parts[0] == 'right':
                x_pos = target_width - scaled_image.get_width()

        if len(pos_parts) >= 2:
            if pos_parts[1].endswith('%'):
                y_percent = float(pos_parts[1][:-1]) / 100
                y_pos = int((target_height - scaled_image.get_height()) * y_percent)
            elif pos_parts[1] == 'center':
                y_pos = (target_height - scaled_image.get_height()) // 2
            elif pos_parts[1] == 'bottom':
                y_pos = target_height - scaled_image.get_height()

        # Blit pattern to final surface
        if bg_repeat == 'no-repeat':
            final_surface.blit(scaled_image, (x_pos, y_pos))
        else:
            final_surface.blit(pattern_surface, (0, 0))

        # Apply to target surface (with border-radius if applicable)
        if hasattr(layout_box, 'border_radius') and any(r > 0 for r in layout_box.border_radius):
            self._apply_rounded_mask(final_surface, layout_box.border_radius)

        surface.blit(final_surface, (0, 0))

    def _fill_rounded_rect(self, surface: pygame.Surface, color: Tuple[int, int, int],
                           border_radius: Tuple[float, float, float, float]):
        """Fill rectangle with proper rounded corners"""
        rect = surface.get_rect()
        width, height = rect.size

        # Clamp radii to not exceed half the width/height
        max_radius_x = width // 2
        max_radius_y = height // 2

        tl_radius = min(int(border_radius[0]), max_radius_x, max_radius_y)
        tr_radius = min(int(border_radius[1]), max_radius_x, max_radius_y)
        br_radius = min(int(border_radius[2]), max_radius_x, max_radius_y)
        bl_radius = min(int(border_radius[3]), max_radius_x, max_radius_y)

        if all(r == 0 for r in [tl_radius, tr_radius, br_radius, bl_radius]):
            surface.fill(color)
            return

        # Create mask surface
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw rounded rectangle using multiple shapes
        # Main rectangles (avoid overlapping corners)
        main_rect = pygame.Rect(tl_radius, 0, width - tl_radius - tr_radius, height)
        if main_rect.width > 0:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), main_rect)

        side_rect = pygame.Rect(0, tl_radius, width, height - tl_radius - bl_radius)
        if side_rect.height > 0:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), side_rect)

        # Draw corner circles
        if tl_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (tl_radius, tl_radius), tl_radius)

        if tr_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (width - tr_radius, tr_radius), tr_radius)

        if br_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (width - br_radius, height - br_radius), br_radius)

        if bl_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (bl_radius, height - bl_radius), bl_radius)

        # Fill with color using mask
        color_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color_surface.fill(color)
        color_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(color_surface, (0, 0))

    def _draw_rounded_border(self, surface: pygame.Surface, color: Tuple[int, int, int],
                             border_radius: Tuple[float, float, float, float], width: int):
        """Draw border with accurate rounded corners"""
        rect = surface.get_rect()
        surf_width, surf_height = rect.size

        # Clamp radii
        max_radius_x = surf_width // 2
        max_radius_y = surf_height // 2

        tl_radius = min(int(border_radius[0]), max_radius_x, max_radius_y)
        tr_radius = min(int(border_radius[1]), max_radius_x, max_radius_y)
        br_radius = min(int(border_radius[2]), max_radius_x, max_radius_y)
        bl_radius = min(int(border_radius[3]), max_radius_x, max_radius_y)

        if all(r == 0 for r in [tl_radius, tr_radius, br_radius, bl_radius]):
            pygame.draw.rect(surface, color, rect, width)
            return

        # Draw border lines (avoiding corners)
        # Top line
        if surf_width > tl_radius + tr_radius:
            start_x = tl_radius
            end_x = surf_width - tr_radius
            for i in range(width):
                pygame.draw.line(surface, color, (start_x, i), (end_x, i))

        # Bottom line
        if surf_width > bl_radius + br_radius:
            start_x = bl_radius
            end_x = surf_width - br_radius
            for i in range(width):
                pygame.draw.line(surface, color, (start_x, surf_height - 1 - i), (end_x, surf_height - 1 - i))

        # Left line
        if surf_height > tl_radius + bl_radius:
            start_y = tl_radius
            end_y = surf_height - bl_radius
            for i in range(width):
                pygame.draw.line(surface, color, (i, start_y), (i, end_y))

        # Right line
        if surf_height > tr_radius + br_radius:
            start_y = tr_radius
            end_y = surf_height - br_radius
            for i in range(width):
                pygame.draw.line(surface, color, (surf_width - 1 - i, start_y), (surf_width - 1 - i, end_y))

        # Draw corner arcs
        if tl_radius > 0:
            self._draw_corner_arc(surface, color, (tl_radius, tl_radius), tl_radius, width, 180, 270)

        if tr_radius > 0:
            self._draw_corner_arc(surface, color, (surf_width - tr_radius, tr_radius), tr_radius, width, 270, 360)

        if br_radius > 0:
            self._draw_corner_arc(surface, color, (surf_width - br_radius, surf_height - br_radius), br_radius, width,
                                  0, 90)

        if bl_radius > 0:
            self._draw_corner_arc(surface, color, (bl_radius, surf_height - bl_radius), bl_radius, width, 90, 180)

    def _draw_corner_arc(self, surface: pygame.Surface, color: Tuple[int, int, int],
                         center: Tuple[int, int], radius: int, width: int, start_angle: int, end_angle: int):
        """Draw an arc for rounded corner border"""
        # Simple implementation using multiple circles
        for i in range(width):
            inner_radius = max(0, radius - i)
            if inner_radius > 0:
                # Draw arc by drawing points along the circle
                import math
                for angle in range(start_angle, end_angle + 1, 2):
                    radian = math.radians(angle)
                    x = center[0] + int(inner_radius * math.cos(radian))
                    y = center[1] + int(inner_radius * math.sin(radian))

                    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                        surface.set_at((x, y), color)

    def _apply_rounded_mask(self, surface: pygame.Surface, border_radius: Tuple[float, float, float, float]):
        """Apply rounded mask to surface (for background images)"""
        width, height = surface.get_size()

        # Create mask
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Use the same logic as _fill_rounded_rect but create a mask
        tl_radius = min(int(border_radius[0]), width // 2, height // 2)
        tr_radius = min(int(border_radius[1]), width // 2, height // 2)
        br_radius = min(int(border_radius[2]), width // 2, height // 2)
        bl_radius = min(int(border_radius[3]), width // 2, height // 2)

        if all(r == 0 for r in [tl_radius, tr_radius, br_radius, bl_radius]):
            return  # No rounding needed

        # Draw rounded rectangle mask
        # Main rectangles
        main_rect = pygame.Rect(tl_radius, 0, width - tl_radius - tr_radius, height)
        if main_rect.width > 0:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), main_rect)

        side_rect = pygame.Rect(0, tl_radius, width, height - tl_radius - bl_radius)
        if side_rect.height > 0:
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), side_rect)

        # Corner circles
        if tl_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (tl_radius, tl_radius), tl_radius)
        if tr_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (width - tr_radius, tr_radius), tr_radius)
        if br_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (width - br_radius, height - br_radius), br_radius)
        if bl_radius > 0:
            pygame.draw.circle(mask_surface, (255, 255, 255, 255), (bl_radius, height - bl_radius), bl_radius)

        # Apply mask to surface
        surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _load_background_image(self, image_url: str) -> Optional[pygame.Surface]:
        """Load background image from URL or file path"""
        if image_url in self.image_cache:
            return self.image_cache[image_url]

        try:
            # Handle different URL formats
            if image_url.startswith('url('):
                # Extract path from url() function
                import re
                match = re.match(r'url\(["\']?([^"\']+)["\']?\)', image_url)
                if match:
                    image_path = match.group(1)
                else:
                    return None
            else:
                image_path = image_url

            # Try to load image
            if image_path.startswith('http'):
                # For web URLs, would need additional handling
                print(f"Web URLs not supported yet: {image_path}")
                return None
            else:
                # Local file path
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    self.image_cache[image_url] = image
                    return image
                except pygame.error:
                    # Try relative to current directory or assets folder
                    import os
                    possible_paths = [
                        image_path,
                        os.path.join('assets', image_path),
                        os.path.join('images', image_path),
                        os.path.join('assets', 'images', image_path)
                    ]

                    for path in possible_paths:
                        try:
                            if os.path.exists(path):
                                image = pygame.image.load(path).convert_alpha()
                                self.image_cache[image_url] = image
                                return image
                        except pygame.error:
                            continue

                    print(f"Could not load background image: {image_path}")
                    return None

        except Exception as e:
            print(f"Error loading background image {image_url}: {e}")
            return None

    def _create_background_pattern(self, image: pygame.Surface, bg_repeat: str,
                                   target_width: int, target_height: int) -> pygame.Surface:
        """Create background pattern based on background-repeat"""
        if bg_repeat == 'no-repeat':
            # Single image, no repeat
            bg_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            bg_surface.blit(image, (0, 0))
            return bg_surface

        elif bg_repeat == 'repeat-x':
            # Repeat horizontally only
            bg_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            image_width = image.get_width()

            for x in range(0, target_width, image_width):
                bg_surface.blit(image, (x, 0))
            return bg_surface

        elif bg_repeat == 'repeat-y':
            # Repeat vertically only
            bg_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            image_height = image.get_height()

            for y in range(0, target_height, image_height):
                bg_surface.blit(image, (0, y))
            return bg_surface

        else:  # 'repeat' or default
            # Repeat both directions
            bg_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            image_width, image_height = image.get_size()

            for y in range(0, target_height, image_height):
                for x in range(0, target_width, image_width):
                    bg_surface.blit(image, (x, y))
            return bg_surface

    def _scale_background_image(self, image: pygame.Surface, bg_size: str,
                                target_width: int, target_height: int) -> pygame.Surface:
        """Scale background image according to background-size"""
        if bg_size == 'auto':
            return image

        elif bg_size == 'contain':
            # Scale to fit entirely within container
            img_width, img_height = image.get_size()
            scale_x = target_width / img_width
            scale_y = target_height / img_height
            scale = min(scale_x, scale_y)

            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return pygame.transform.scale(image, (new_width, new_height))

        elif bg_size == 'cover':
            # Scale to cover entire container
            img_width, img_height = image.get_size()
            scale_x = target_width / img_width
            scale_y = target_height / img_height
            scale = max(scale_x, scale_y)

            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            return pygame.transform.scale(image, (new_width, new_height))

        elif 'px' in bg_size or '%' in bg_size:
            # Specific size
            parts = bg_size.split()
            if len(parts) >= 2:
                width_str, height_str = parts[0], parts[1]
            else:
                width_str = height_str = parts[0]

            # Parse dimensions
            if width_str.endswith('%'):
                new_width = int(target_width * float(width_str[:-1]) / 100)
            elif width_str.endswith('px'):
                new_width = int(width_str[:-2])
            else:
                new_width = image.get_width()

            if height_str.endswith('%'):
                new_height = int(target_height * float(height_str[:-1]) / 100)
            elif height_str.endswith('px'):
                new_height = int(height_str[:-2])
            else:
                new_height = image.get_height()

            return pygame.transform.scale(image, (new_width, new_height))

        return image

    def _render_linear_gradient_background(self, surface: pygame.Surface, gradient_def: str, layout_box):
        """Render linear gradient background"""
        width, height = surface.get_size()

        if width <= 0 or height <= 0:
            return

        # Parse gradient definition
        gradient_info = self._parse_linear_gradient(gradient_def)
        if not gradient_info:
            return

        angle, colors, stops = gradient_info

        # Create gradient surface using the efficient 2-pixel method
        if len(colors) >= 2:
            gradient_surface = self._create_gradient_surface(colors, stops, angle, width, height)
            surface.blit(gradient_surface, (0, 0))

    def _parse_linear_gradient(self, gradient_def: str):
        """Parse linear gradient definition"""
        if not gradient_def.startswith('linear-gradient'):
            return None

        # Extract content between parentheses
        import re
        match = re.match(r'linear-gradient\s*\(\s*(.+)\s*\)', gradient_def)
        if not match:
            return None

        content = match.group(1)
        parts = [part.strip() for part in content.split(',')]

        # Default values
        angle = 180  # Default to top to bottom (180 degrees)
        colors = []
        stops = []

        # Parse parts
        i = 0

        # Check if first part is an angle or direction
        if parts and ('deg' in parts[0] or parts[0] in ['to top', 'to bottom', 'to left', 'to right', 'to top right',
                                                        'to bottom right', 'to top left', 'to bottom left']):
            angle_part = parts[0]
            i = 1

            if 'deg' in angle_part:
                try:
                    angle = float(angle_part.replace('deg', '').strip())
                except:
                    angle = 180
            elif angle_part == 'to top':
                angle = 0
            elif angle_part == 'to bottom':
                angle = 180
            elif angle_part == 'to left':
                angle = 270
            elif angle_part == 'to right':
                angle = 90
            elif angle_part == 'to top right':
                angle = 45
            elif angle_part == 'to bottom right':
                angle = 135
            elif angle_part == 'to top left':
                angle = 315
            elif angle_part == 'to bottom left':
                angle = 225

        # Parse color stops
        while i < len(parts):
            part = parts[i].strip()

            # Extract color and optional stop position
            color_match = re.match(r'(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|[a-zA-Z]+)(\s+(\d+%?))?', part)
            if color_match:
                color_str = color_match.group(1)
                stop_str = color_match.group(3) if color_match.group(3) else None

                color = self._parse_color_to_rgb(color_str)
                if color:
                    colors.append(color)

                    if stop_str:
                        if stop_str.endswith('%'):
                            stop = float(stop_str[:-1]) / 100.0
                        else:
                            stop = float(stop_str) / 100.0  # Assume percentage
                    else:
                        # Auto-distribute stops
                        if len(colors) == 1:
                            stop = 0.0
                        elif len(colors) == 2 and len(stops) == 1:
                            stop = 1.0
                        else:
                            stop = (len(colors) - 1) / max(1, len(parts) - i - 1)

                    stops.append(stop)

            i += 1

        # Ensure we have at least 2 colors
        if len(colors) < 2:
            colors = [(102, 126, 234), (118, 75, 162)]  # Default gradient
            stops = [0.0, 1.0]

        return (angle, colors, stops)

    def _parse_linear_gradient(self, gradient_def: str):
        """Parse linear gradient definition"""
        if not gradient_def.startswith('linear-gradient'):
            return None

        # Extract content between parentheses
        import re
        match = re.match(r'linear-gradient\s*\(\s*(.+)\s*\)', gradient_def)
        if not match:
            return None

        content = match.group(1)
        parts = [part.strip() for part in content.split(',')]

        # Default values
        angle = 180  # Default to top to bottom (180 degrees)
        colors = []
        stops = []

        # Parse parts
        i = 0

        # Check if first part is an angle or direction
        if parts and ('deg' in parts[0] or parts[0] in ['to top', 'to bottom', 'to left', 'to right', 'to top right',
                                                        'to bottom right', 'to top left', 'to bottom left']):
            angle_part = parts[0]
            i = 1

            if 'deg' in angle_part:
                try:
                    angle = float(angle_part.replace('deg', '').strip())
                except:
                    angle = 180
            elif angle_part == 'to top':
                angle = 0
            elif angle_part == 'to bottom':
                angle = 180
            elif angle_part == 'to left':
                angle = 270
            elif angle_part == 'to right':
                angle = 90
            elif angle_part == 'to top right':
                angle = 45
            elif angle_part == 'to bottom right':
                angle = 135
            elif angle_part == 'to top left':
                angle = 315
            elif angle_part == 'to bottom left':
                angle = 225

        # Parse color stops
        while i < len(parts):
            part = parts[i].strip()

            # Extract color and optional stop position
            color_match = re.match(r'(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|[a-zA-Z]+)(\s+(\d+%?))?', part)
            if color_match:
                color_str = color_match.group(1)
                stop_str = color_match.group(3) if color_match.group(3) else None

                color = self._parse_color_to_rgb(color_str)
                if color:
                    colors.append(color)

                    if stop_str:
                        if stop_str.endswith('%'):
                            stop = float(stop_str[:-1]) / 100.0
                        else:
                            stop = float(stop_str) / 100.0  # Assume percentage
                    else:
                        # Auto-distribute stops
                        if len(colors) == 1:
                            stop = 0.0
                        elif len(colors) == 2 and len(stops) == 1:
                            stop = 1.0
                        else:
                            stop = (len(colors) - 1) / max(1, len(parts) - i - 1)

                    stops.append(stop)

            i += 1

        # Ensure we have at least 2 colors
        if len(colors) < 2:
            colors = [(102, 126, 234), (118, 75, 162)]  # Default gradient
            stops = [0.0, 1.0]

        return (angle, colors, stops)

    def _create_gradient_surface(self, colors, stops, angle, width, height):
        """Create gradient surface using efficient method"""

        # For simplicity, handle common angles
        if 135 <= angle <= 225:  # Roughly top-to-bottom
            return self._create_vertical_gradient(colors, width, height)
        elif 45 <= angle <= 135 or 225 <= angle <= 315:  # Roughly left-to-right or right-to-left
            return self._create_horizontal_gradient(colors, width, height, angle > 180)
        else:  # Diagonal - use vertical for now
            return self._create_vertical_gradient(colors, width, height)

    def _create_vertical_gradient(self, colors, width, height):
        """Create vertical gradient (top to bottom)"""
        if len(colors) < 2:
            return pygame.Surface((width, height), pygame.SRCALPHA)

        start_color = colors[0]
        end_color = colors[-1]

        # Create a 1-pixel wide gradient
        gradient_strip = pygame.Surface((1, height), pygame.SRCALPHA)

        for y in range(height):
            # Calculate interpolation factor (0.0 to 1.0)
            factor = y / (height - 1) if height > 1 else 0

            # Interpolate between start and end colors
            r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)

            gradient_strip.set_at((0, y), (r, g, b))

        # Scale the strip to full width
        return pygame.transform.scale(gradient_strip, (width, height))

    def _create_horizontal_gradient(self, colors, width, height, reverse=False):
        """Create horizontal gradient (left to right)"""
        if len(colors) < 2:
            return pygame.Surface((width, height), pygame.SRCALPHA)

        start_color = colors[0] if not reverse else colors[-1]
        end_color = colors[-1] if not reverse else colors[0]

        # Create a 1-pixel high gradient
        gradient_strip = pygame.Surface((width, 1), pygame.SRCALPHA)

        for x in range(width):
            # Calculate interpolation factor (0.0 to 1.0)
            factor = x / (width - 1) if width > 1 else 0

            # Interpolate between start and end colors
            r = int(start_color[0] + (end_color[0] - start_color[0]) * factor)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * factor)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * factor)

            gradient_strip.set_at((x, 0), (r, g, b))

        # Scale the strip to full height
        return pygame.transform.scale(gradient_strip, (width, height))

    def _parse_color_to_rgb(self, color_str: str):
        """Parse color string to RGB tuple"""
        if color_str.startswith('#'):
            if len(color_str) == 4:  # #RGB
                r = int(color_str[1], 16) * 17
                g = int(color_str[2], 16) * 17
                b = int(color_str[3], 16) * 17
                return (r, g, b)
            elif len(color_str) == 7:  # #RRGGBB
                r = int(color_str[1:3], 16)
                g = int(color_str[3:5], 16)
                b = int(color_str[5:7], 16)
                return (r, g, b)

        elif color_str.startswith('rgb'):
            import re
            match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
            if match:
                return tuple(int(x) for x in match.groups())

        # Named colors
        color_map = {
            'red': (255, 0, 0), 'green': (0, 128, 0), 'blue': (0, 0, 255),
            'white': (255, 255, 255), 'black': (0, 0, 0), 'gray': (128, 128, 128),
            'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255),
            'orange': (255, 165, 0), 'purple': (128, 0, 128), 'brown': (165, 42, 42)
        }

        return color_map.get(color_str.lower(), (128, 128, 128))

    def _render_gradient_background(self, surface: pygame.Surface, gradient_def: str, layout_box):
        """Render linear gradient background"""
        # Parse gradient (simplified)
        if 'linear-gradient' in gradient_def:
            # Extract colors (very basic parsing)
            width, height = surface.get_size()

            # Default gradient from top to bottom
            start_color = (100, 150, 255)  # Light blue
            end_color = (50, 100, 200)  # Darker blue

            # Try to extract colors from gradient definition
            if '#' in gradient_def:
                # Very basic color extraction
                colors = re.findall(r'#[0-9a-fA-F]{6}', gradient_def)
                if len(colors) >= 2:
                    start_color = self._hex_to_rgb(colors[0])
                    end_color = self._hex_to_rgb(colors[1])

            # Render gradient
            for y in range(height):
                ratio = y / height if height > 0 else 0
                r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
                g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
                b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

                pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    def _render_enhanced_border(self, surface: pygame.Surface, element: HTMLElement):
        """Enhanced border rendering with radius"""
        style = element.computed_style
        border_width = self._parse_length(style.get('border-width', '0'))

        if border_width > 0:
            border_color = self._parse_color(style.get('border-color', '#000000'))

            # FIX: Ensure border_color is never None
            if border_color is None:
                border_color = (0, 0, 0)  # Default to black

            if hasattr(element.layout_box, 'border_radius'):
                self._draw_rounded_border(surface, border_color, element.layout_box.border_radius, int(border_width))
            else:
                pygame.draw.rect(surface, border_color, surface.get_rect(), int(border_width))

    def _render_enhanced_text(self, surface: pygame.Surface, element: HTMLElement):
        """Enhanced text rendering with transforms and alignment"""
        style = element.computed_style
        text = element.text_content.strip()

        if not text:
            return

        # Apply text transforms
        text_transform = style.get('text-transform', 'none')
        if text_transform == 'uppercase':
            text = text.upper()
        elif text_transform == 'lowercase':
            text = text.lower()
        elif text_transform == 'capitalize':
            text = text.title()

        # Get enhanced font
        font = self.get_enhanced_font(style)
        color = self._parse_color(style.get('color', '#000000'))

        if font and color:
            # Render text
            text_surface = font.render(text, True, color)

            # Enhanced text alignment
            text_align = style.get('text-align', 'left')
            x = 0

            if text_align == 'center':
                x = (surface.get_width() - text_surface.get_width()) // 2
            elif text_align == 'right':
                x = surface.get_width() - text_surface.get_width()

            # Position with padding
            padding_left = getattr(element.layout_box, 'padding_left', 0)
            padding_top = getattr(element.layout_box, 'padding_top', 0)

            x = max(x, padding_left)
            y = padding_top

            # Enhanced vertical centering
            available_height = surface.get_height() - padding_top * 2
            if available_height > text_surface.get_height():
                y = padding_top + (available_height - text_surface.get_height()) // 2

            surface.blit(text_surface, (x, y))

    def _has_transform(self, transform: Transform) -> bool:
        """Check if element has any transforms"""
        return (transform.translate_x != 0 or transform.translate_y != 0 or
                transform.scale_x != 1 or transform.scale_y != 1 or
                transform.rotate != 0 or transform.skew_x != 0 or transform.skew_y != 0)

    def _apply_transforms(self, surface: pygame.Surface, transform: Transform) -> pygame.Surface:
        """Apply CSS transforms to surface"""
        result_surface = surface

        # Apply scale
        if transform.scale_x != 1 or transform.scale_y != 1:
            new_width = int(surface.get_width() * transform.scale_x)
            new_height = int(surface.get_height() * transform.scale_y)
            result_surface = pygame.transform.scale(result_surface, (new_width, new_height))

        # Apply skew transforms BEFORE rotation
        if transform.skew_x != 0 or transform.skew_y != 0:
            result_surface = self._apply_skew_transform(result_surface, transform.skew_x, transform.skew_y)

        # Apply rotation
        if transform.rotate != 0:
            angle_degrees = math.degrees(transform.rotate)
            result_surface = pygame.transform.rotate(result_surface, -angle_degrees)

        return result_surface

    def _apply_skew_transform(self, surface: pygame.Surface, skew_x: float, skew_y: float) -> pygame.Surface:
        """Apply skew transformation using pixel manipulation"""
        if skew_x == 0 and skew_y == 0:
            return surface

        width, height = surface.get_size()

        # Calculate new bounds after skewing
        # Skew can make the image larger, so calculate worst-case bounds
        max_x_offset = int(abs(math.tan(skew_x)) * height) if skew_x != 0 else 0
        max_y_offset = int(abs(math.tan(skew_y)) * width) if skew_y != 0 else 0

        new_width = width + max_x_offset
        new_height = height + max_y_offset

        # Create new surface with expanded bounds
        skewed_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)

        # Get pixel array for efficient manipulation
        source_array = pygame.surfarray.array3d(surface)
        source_alpha = pygame.surfarray.array_alpha(surface)

        # Apply skew transformation pixel by pixel
        for y in range(height):
            for x in range(width):
                # Calculate skewed position
                skewed_x = x + int(math.tan(skew_x) * y)
                skewed_y = y + int(math.tan(skew_y) * x)

                # Check bounds
                if 0 <= skewed_x < new_width and 0 <= skewed_y < new_height:
                    try:
                        color = tuple(source_array[x, y]) + (source_alpha[x, y],)
                        skewed_surface.set_at((skewed_x, skewed_y), color)
                    except IndexError:
                        pass  # Skip if out of bounds

        return skewed_surface

    def _apply_gaussian_blur(self, surface: pygame.Surface, blur_radius: float) -> pygame.Surface:
        """Apply real Gaussian blur effect"""
        if blur_radius <= 0:
            return surface

        # Convert blur radius to kernel size (must be odd)
        kernel_size = max(3, int(blur_radius * 2) | 1)  # Ensure odd number

        # Create Gaussian kernel
        kernel = self._create_gaussian_kernel(kernel_size, blur_radius / 3.0)

        # Apply separable blur (horizontal then vertical for efficiency)
        blurred = self._apply_separable_blur(surface, kernel)

        return blurred

    def _create_gaussian_kernel(self, size: int, sigma: float) -> List[float]:
        """Create 1D Gaussian kernel"""
        kernel = []
        center = size // 2
        sum_values = 0

        for i in range(size):
            x = i - center
            value = math.exp(-(x * x) / (2 * sigma * sigma))
            kernel.append(value)
            sum_values += value

        # Normalize kernel
        return [v / sum_values for v in kernel]

    def _apply_separable_blur(self, surface: pygame.Surface, kernel: List[float]) -> pygame.Surface:
        """Apply separable Gaussian blur (horizontal then vertical)"""
        width, height = surface.get_size()
        kernel_size = len(kernel)
        radius = kernel_size // 2

        # First pass: horizontal blur
        h_blurred = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            for x in range(width):
                r, g, b, a = 0, 0, 0, 0

                for i, k_val in enumerate(kernel):
                    sample_x = max(0, min(width - 1, x + i - radius))
                    pixel = surface.get_at((sample_x, y))

                    r += pixel[0] * k_val
                    g += pixel[1] * k_val
                    b += pixel[2] * k_val
                    a += pixel[3] * k_val

                h_blurred.set_at((x, y), (int(r), int(g), int(b), int(a)))

        # Second pass: vertical blur
        v_blurred = pygame.Surface((width, height), pygame.SRCALPHA)

        for y in range(height):
            for x in range(width):
                r, g, b, a = 0, 0, 0, 0

                for i, k_val in enumerate(kernel):
                    sample_y = max(0, min(height - 1, y + i - radius))
                    pixel = h_blurred.get_at((x, sample_y))

                    r += pixel[0] * k_val
                    g += pixel[1] * k_val
                    b += pixel[2] * k_val
                    a += pixel[3] * k_val

                v_blurred.set_at((x, y), (int(r), int(g), int(b), int(a)))

        return v_blurred

    def _apply_box_shadows(self, surface: pygame.Surface, shadows: List[BoxShadow]) -> pygame.Surface:
        """Apply box shadows"""

        # TODO: Use Real Blue
        # _apply_gaussian_blur, _create_gaussian_kernel, _apply_separable_blur

        if not shadows:
            return surface

        # Calculate bounds needed for shadows
        max_offset = max(abs(s.offset_x) + s.blur_radius for s in shadows)
        max_offset = max(max_offset, max(abs(s.offset_y) + s.blur_radius for s in shadows))

        # Create larger surface
        extra = int(max_offset * 2)
        shadow_surface = pygame.Surface(
            (surface.get_width() + extra, surface.get_height() + extra),
            pygame.SRCALPHA
        )

        # Render shadows
        for shadow in shadows:
            # Create shadow
            shadow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            shadow_surf.fill(shadow.color[:3])

            # Position shadow
            shadow_x = int(extra // 2 + shadow.offset_x)
            shadow_y = int(extra // 2 + shadow.offset_y)

            if shadow.blur_radius > 0:
                shadow_surf.set_alpha(max(50, 255 - int(shadow.blur_radius * 20)))

            shadow_surface.blit(shadow_surf, (shadow_x, shadow_y))

        # Render original surface on top
        shadow_surface.blit(surface, (extra // 2, extra // 2))

        return shadow_surface

    def _apply_opacity(self, surface: pygame.Surface, opacity: float):
        """Apply opacity to surface"""
        if opacity < 1.0:
            alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, int(opacity * 255)))
            surface.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _fill_rounded_rect(self, surface: pygame.Surface, color: Tuple[int, int, int],
                           border_radius: Tuple[float, float, float, float]):
        """Fill rectangle with rounded corners (simplified)"""
        rect = surface.get_rect()

        if all(r == 0 for r in border_radius):
            surface.fill(color)
        else:
            # Simplified rounded rectangle
            radius = int(border_radius[0])  # Use first radius for all corners
            if radius > 0:
                # Draw main rectangles
                pygame.draw.rect(surface, color, rect.inflate(-radius * 2, 0))
                pygame.draw.rect(surface, color, rect.inflate(0, -radius * 2))

                # Draw corners
                pygame.draw.circle(surface, color, (radius, radius), radius)
                pygame.draw.circle(surface, color, (rect.width - radius, radius), radius)
                pygame.draw.circle(surface, color, (radius, rect.height - radius), radius)
                pygame.draw.circle(surface, color, (rect.width - radius, rect.height - radius), radius)
            else:
                surface.fill(color)

    def _draw_rounded_border(self, surface: pygame.Surface, color: Tuple[int, int, int],
                             border_radius: Tuple[float, float, float, float], width: int):
        """Draw border with rounded corners (simplified)"""
        rect = surface.get_rect()

        if all(r == 0 for r in border_radius):
            pygame.draw.rect(surface, color, rect, int(width))
        else:
            # Simplified - just draw normal border
            pygame.draw.rect(surface, color, rect, int(width))

    def get_enhanced_font(self, style: Dict[str, str]) -> Optional[pygame.font.Font]:
        """Get font with enhanced properties"""
        font_family = style.get('font-family', 'Arial')
        font_size = max(8, int(self._parse_length(style.get('font-size', '16px'))))
        font_weight = style.get('font-weight', 'normal')
        font_style = style.get('font-style', 'normal')

        font_key = (font_family, font_size, font_weight, font_style)

        if font_key not in self.font_cache:
            try:
                bold = font_weight in ['bold', '700', '800', '900']
                italic = font_style == 'italic'
                self.font_cache[font_key] = pygame.font.SysFont(font_family, font_size, bold=bold, italic=italic)
            except:
                self.font_cache[font_key] = pygame.font.Font(None, font_size)

        return self.font_cache[font_key]

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

