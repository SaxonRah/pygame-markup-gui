# layout_engine.py
from .html_engine import HTMLElement, LayoutBox
from .layout_debugger import LayoutDebugger


class LayoutEngine:
    """CSS-compliant layout engine for pygame"""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 800, enable_debug=False):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

        self.debug_enabled = enable_debug
        self.debugger = LayoutDebugger(renderer=None) if enable_debug else None

    def layout(self, element: HTMLElement, container_width: float = None,
               container_height: float = None, is_root: bool = True,
               parent_x: float = 0, parent_y: float = 0):
        """Main layout method with proper height propagation"""

        if container_width is None:
            container_width = self.viewport_width
        if container_height is None:
            container_height = self.viewport_height

        # Create layout box
        element.layout_box = LayoutBox()

        # Calculate box model (margin, border, padding, content)
        self._calculate_box_model(element, container_width, container_height)

        # Calculate available space for children
        child_container_width = (element.layout_box.width -
                                 element.layout_box.padding_left - element.layout_box.padding_right)
        child_container_height = (element.layout_box.height -
                                  element.layout_box.padding_top - element.layout_box.padding_bottom)

        # Position element
        if is_root:
            element.layout_box.x = element.layout_box.margin_left
            element.layout_box.y = element.layout_box.margin_top
        else:
            element.layout_box.x = parent_x + element.layout_box.margin_left
            element.layout_box.y = parent_y + element.layout_box.margin_top

        # Layout children
        self._layout_children(element, child_container_width, child_container_height)

        # Debug layout calculations if enabled
        if self.debug_enabled and self.debugger:
            print(f"DEBUG: Laying out {element.tag} at ({parent_x}, {parent_y})")
            print(f"  Container: {container_width}x{container_height}")
            print(f"  Computed: {element.layout_box.width}x{element.layout_box.height}")

    def _calculate_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """Calculate element's box model (margin, border, padding, content)"""
        style = element.computed_style
        box = element.layout_box

        # Parse margins
        margin_top = self._parse_length(style.get('margin-top', '0'), container_width)
        margin_right = self._parse_length(style.get('margin-right', '0'), container_width)
        margin_bottom = self._parse_length(style.get('margin-bottom', '0'), container_width)
        margin_left = self._parse_length(style.get('margin-left', '0'), container_width)

        # Handle margin shorthand
        if 'margin' in style:
            margin = self._parse_box_value(style.get('margin', '0'), container_width)
            margin_top, margin_right, margin_bottom, margin_left = margin

        box.margin_top, box.margin_right, box.margin_bottom, box.margin_left = margin_top, margin_right, margin_bottom, margin_left

        # Parse padding
        padding_top = self._parse_length(style.get('padding-top', '0'), container_width)
        padding_right = self._parse_length(style.get('padding-right', '0'), container_width)
        padding_bottom = self._parse_length(style.get('padding-bottom', '0'), container_width)
        padding_left = self._parse_length(style.get('padding-left', '0'), container_width)

        # Handle padding shorthand
        if 'padding' in style:
            padding = self._parse_box_value(style.get('padding', '0'), container_width)
            padding_top, padding_right, padding_bottom, padding_left = padding

        box.padding_top, box.padding_right, box.padding_bottom, box.padding_left = padding_top, padding_right, padding_bottom, padding_left

        # Parse border
        border_width = self._parse_length(style.get('border-width', '0'), container_width)
        box.border_width = border_width

        # Calculate dimensions
        width = style.get('width', 'auto')
        height = style.get('height', 'auto')

        # Calculate width
        if width == 'auto':
            if element.tag == 'button' and element.text_content:
                # Special handling for buttons
                text_width = len(element.text_content) * 8
                min_width = text_width + padding_left + padding_right + 20
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(min_width, min(available_width, 150))
            else:
                # Fill available width
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(0, available_width)
        else:
            box.width = self._parse_length(width, container_width)

        # Calculate height
        if height == 'auto':
            box.height = self._calculate_auto_height(element)
        else:
            box.height = self._parse_length(height, container_height)

    def _calculate_auto_height(self, element: HTMLElement) -> float:
        """Calculate automatic height based on content"""
        style = element.computed_style

        # ROOT ELEMENTS: Fill viewport/container
        if element.tag == 'html':
            return self.viewport_height

        if element.tag == 'body':
            # Body should fill HTML minus margins
            margin_top = self._parse_length(style.get('margin-top', '0'))
            margin_bottom = self._parse_length(style.get('margin-bottom', '0'))
            return max(self.viewport_height - margin_top - margin_bottom, 100)

        # CONTAINER ELEMENTS: Expand to fit children or reasonable default
        if element.tag in ['div', 'section', 'main', 'article', 'aside', 'header', 'footer', 'nav']:
            # Check if it has background/padding (likely a container)
            has_background = style.get('background-color') or style.get('background')
            has_padding = style.get('padding') or style.get('padding-top')

            if has_background or has_padding:
                return 200  # Reasonable container height
            else:
                return 50  # Simple div

        # TEXT ELEMENTS: Calculate based on content
        if element.text_content.strip():
            font_size = self._parse_length(style.get('font-size', '16px'))
            line_height_val = style.get('line-height', '1.2')

            if line_height_val.endswith('px'):
                line_height = self._parse_length(line_height_val)
            else:
                try:
                    line_height = float(line_height_val) * font_size
                except:
                    line_height = font_size * 1.2

            padding_height = self._parse_length(style.get('padding-top', '0')) + \
                             self._parse_length(style.get('padding-bottom', '0'))

            return max(line_height + padding_height, 30)

        # SPECIFIC ELEMENT DEFAULTS
        if element.tag == 'h1': return 60
        if element.tag == 'h2': return 50
        if element.tag == 'h3': return 40
        if element.tag == 'h4': return 35
        if element.tag == 'h5': return 30
        if element.tag == 'h6': return 25
        if element.tag in ['input', 'button']: return 40
        if element.tag == 'p': return 30

        return 30  # Fallback

    def _layout_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout children based on their display type"""
        if not element.children:
            return

        # Determine layout mode
        display = element.computed_style.get('display', 'block')

        # Check for inline children
        has_inline_children = any(
            child.computed_style.get('display', 'block') in ['inline', 'inline-block']
            for child in element.children
        )

        if has_inline_children:
            self._layout_inline_children(element, available_width, available_height)
        else:
            self._layout_block_children(element, available_width, available_height)

    def _layout_block_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout block children vertically"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_y = content_y

        for child in element.children:
            # Layout child
            self.layout(child, available_width, available_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            # Move down by child's height
            current_y += (child.layout_box.margin_top + child.layout_box.height +
                          child.layout_box.margin_bottom)

    def _layout_inline_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout inline children horizontally with wrapping"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_x = content_x
        current_y = content_y
        line_height = 0

        for child in element.children:
            # Calculate remaining width on current line
            used_width = current_x - content_x
            remaining_width = max(0, available_width - used_width)

            # Layout child to get its dimensions
            self.layout(child, remaining_width, available_height, is_root=False,
                        parent_x=current_x, parent_y=current_y)

            # Check if child fits on current line
            child_total_width = (child.layout_box.width + child.layout_box.margin_left +
                                 child.layout_box.margin_right)

            if child_total_width > remaining_width and current_x > content_x:
                # Wrap to next line
                current_x = content_x
                current_y += line_height
                line_height = 0

                # Re-layout child on new line
                self.layout(child, available_width, available_height, is_root=False,
                            parent_x=current_x, parent_y=current_y)
                child_total_width = (child.layout_box.width + child.layout_box.margin_left +
                                     child.layout_box.margin_right)

            # Update position and line height
            child.layout_box.x = current_x + child.layout_box.margin_left
            child.layout_box.y = current_y + child.layout_box.margin_top

            current_x += child_total_width
            line_height = max(line_height, child.layout_box.height +
                              child.layout_box.margin_top + child.layout_box.margin_bottom)

    def _parse_box_value(self, value: str, container_size: float = 0) -> tuple:
        """Parse margin/padding value (top, right, bottom, left)"""
        parts = value.split()
        if len(parts) == 1:
            v = self._parse_length(parts[0], container_size)
            return v, v, v, v
        elif len(parts) == 2:
            v, h = self._parse_length(parts[0], container_size), self._parse_length(parts[1], container_size)
            return v, h, v, h
        elif len(parts) == 4:
            return tuple(self._parse_length(p, container_size) for p in parts)
        return 0, 0, 0, 0

    @staticmethod
    def _parse_length(value: str, container_size: float = 0) -> float:
        """Parse CSS length value"""
        if not value or value == 'auto':
            return 0

        try:
            if value.endswith('px'):
                return float(value[:-2])
            elif value.endswith('%'):
                return container_size * (float(value[:-1]) / 100)
            elif value.endswith('em'):
                return float(value[:-2]) * 16  # Assume 16px base font size
            elif value.endswith('rem'):
                return float(value[:-3]) * 16  # Assume 16px base font size
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0
