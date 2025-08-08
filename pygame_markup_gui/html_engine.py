import html5lib
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class LayoutBox:
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    margin_top: float = 0
    margin_right: float = 0
    margin_bottom: float = 0
    margin_left: float = 0
    padding_top: float = 0
    padding_right: float = 0
    padding_bottom: float = 0
    padding_left: float = 0
    border_width: float = 0


class HTMLElement:
    """Wrapper around html5lib parsed element with pygame rendering info"""

    def __init__(self, element=None, tag=None, text=None):
        self.element = element
        self.tag = tag or self._get_tag_name(element)
        self.attributes = self._get_attributes(element)
        self.text_content = text or self._get_text_content(element)
        self.children = []

        # Pygame-specific properties
        self.computed_style = {}
        self.layout_box = None
        self.pygame_surface = None
        self.parent = None

        # Skip processing comments entirely
        if self.tag == 'comment':
            return

        # Parse children if element provided
        if element is not None:
            self._parse_children(element)

    def _parse_children(self, element):
        """Parse child elements"""
        if element is None:
            return

        try:
            for child in element:
                if child is not None:
                    child_elem = HTMLElement(child)
                    # Skip comments and empty text nodes
                    if (child_elem.tag != 'comment' and
                            (child_elem.tag != 'text' or child_elem.text_content.strip())):
                        child_elem.parent = self
                        self.children.append(child_elem)
        except (TypeError, AttributeError):
            pass

    @staticmethod
    def _get_tag_name(element) -> str:
        """Get tag name from html5lib element"""
        if element is None:
            return 'text'

        # Better comment detection
        element_str = str(element)
        element_type = str(type(element))

        # Check if this is a comment node
        if ('Comment' in element_type or
                'comment' in element_type.lower() or
                element_str.startswith('<!--') or
                'Comment' in element_str):
            return 'comment'

        if hasattr(element, 'tag'):
            tag = element.tag
            if '}' in str(tag):  # Namespace
                tag_name = str(tag).split('}')[1]
                return tag_name
            return str(tag)
        elif hasattr(element, 'name'):
            return str(element.name)
        else:
            return 'text'

    @staticmethod
    def _get_attributes(element) -> Dict[str, str]:
        """Get attributes from html5lib element"""
        if element is None:
            return {}

        if hasattr(element, 'attrib'):
            return dict(element.attrib)
        elif hasattr(element, 'attributes'):
            attrs = {}
            for name, value in element.attributes.items():
                if isinstance(name, tuple):
                    name = name[1]  # Remove namespace
                attrs[str(name)] = str(value)
            return attrs
        return {}

    @staticmethod
    def _get_text_content(element) -> str:
        """Get text content from element"""
        if element is None:
            return ''

        if hasattr(element, 'text') and element.text:
            return str(element.text).strip()
        elif hasattr(element, 'value') and element.value:
            return str(element.value).strip()
        elif not hasattr(element, 'tag') and not hasattr(element, 'name'):  # Text node
            return str(element).strip()
        return ''

    def find_by_tag(self, tag_name: str) -> Optional['HTMLElement']:
        """Find first child with given tag name"""
        if self.tag == tag_name:
            return self
        for child in self.children:
            result = child.find_by_tag(tag_name)
            if result:
                return result
        return None

    def debug_print(self, indent=0):
        """Debug print the element tree"""
        prefix = "  " * indent
        print(f"{prefix}{self.tag}: '{self.text_content}' {self.attributes}")
        for child in self.children:
            child.debug_print(indent + 1)


class HTMLParser:
    """Parse HTML5 into our element tree"""

    def __init__(self):
        self.parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("etree"))

    def parse(self, html_string: str) -> HTMLElement:
        """Parse HTML string into element tree"""
        # Wrap in basic HTML structure if needed
        if not html_string.strip().startswith('<html'):
            html_string = f"<html><body>{html_string}</body></html>"

        document = self.parser.parse(html_string)
        return HTMLElement(document)

    def parse_fragment(self, html_fragment: str) -> HTMLElement:
        """Parse HTML fragment into a container element"""
        fragment = self.parser.parseFragment(html_fragment)

        # Create a container element
        container = HTMLElement(tag='div')

        for elem in fragment:
            if elem is not None:
                # Better comment filtering
                element_str = str(elem)
                element_type = str(type(elem))

                # Skip all comment variations
                if ('Comment' in element_type or
                        'comment' in element_type.lower() or
                        element_str.startswith('<!--')):
                    continue

                child_elem = HTMLElement(elem)
                if child_elem.tag != 'comment':  # Additional safety check
                    child_elem.parent = container
                    if child_elem.tag not in ['text'] or child_elem.text_content.strip():
                        container.children.append(child_elem)

        return container
