from .html_engine import HTMLElement, LayoutBox


class LayoutEngine:
    """CSS-compliant layout engine for pygame"""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 800):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    def layout(self, element: HTMLElement, container_width: float = None, container_height: float = None,
               is_root: bool = True, parent_x: float = 0, parent_y: float = 0):
        """Calculate layout for element tree"""
        if container_width is None:
            container_width = self.viewport_width
        if container_height is None:
            container_height = self.viewport_height

        print(
            f"Laying out {element.tag} with container size: {container_width} x {container_height}, is_root: {is_root}")

        # Step 1: Calculate dimensions only
        element.layout_box = LayoutBox()
        self._calculate_box_model(element, container_width, container_height)

        # Step 2: Position element (using parent coordinates)
        if is_root:
            element.layout_box.x = element.layout_box.margin_left
            element.layout_box.y = element.layout_box.margin_top
        else:
            element.layout_box.x = parent_x + element.layout_box.margin_left
            element.layout_box.y = parent_y + element.layout_box.margin_top

        print(f"Positioned {element.tag} at ({element.layout_box.x}, {element.layout_box.y})")

        # Step 3: Layout children using element's actual position
        self._layout_children(element)

        # Step 4: Recalculate height if it was auto and we have children
        if element.computed_style.get('height', 'auto') == 'auto' and element.children:
            self._recalculate_auto_height(element)

        print(
            f"Final layout for {element.tag}: {element.layout_box.width} x {element.layout_box.height} at ({element.layout_box.x}, {element.layout_box.y})")

    def _calculate_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """Calculate element's box model (margin, border, padding, content) - DIMENSIONS ONLY"""
        style = element.computed_style
        box = element.layout_box

        print(f"Calculating box model for {element.tag}: container={container_width}x{container_height}")

        # Parse margins
        margin_top = self._parse_length(style.get('margin-top', '0'), container_width)
        margin_right = self._parse_length(style.get('margin-right', '0'), container_width)
        margin_bottom = self._parse_length(style.get('margin-bottom', '0'), container_width)
        margin_left = self._parse_length(style.get('margin-left', '0'), container_width)

        if 'margin' in style:
            margin = self._parse_box_value(style.get('margin', '0'), container_width)
            margin_top, margin_right, margin_bottom, margin_left = margin

        box.margin_top, box.margin_right, box.margin_bottom, box.margin_left = margin_top, margin_right, margin_bottom, margin_left

        # Parse padding
        padding_top = self._parse_length(style.get('padding-top', '0'), container_width)
        padding_right = self._parse_length(style.get('padding-right', '0'), container_width)
        padding_bottom = self._parse_length(style.get('padding-bottom', '0'), container_width)
        padding_left = self._parse_length(style.get('padding-left', '0'), container_width)

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

        print(f"CSS width: {width}, height: {height}")

        # Calculate width
        if width == 'auto':
            if element.tag == 'button' and element.text_content:
                text_width = len(element.text_content) * 8
                min_width = text_width + padding_left + padding_right + 20
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(min_width, min(available_width, 150))
            else:
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(0, available_width)
        else:
            box.width = self._parse_length(width, container_width)

        # Calculate height
        if height == 'auto':
            box.height = self._calculate_auto_height(element)
        else:
            box.height = self._parse_length(height, container_height)

        print(f"Calculated size: {box.width} x {box.height}")

    def _parse_box_value(self, value: str, container_size: float = 0) -> tuple[float, float, float, float] | tuple[
        float, ...] | tuple[int, int, int, int]:
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
                return float(value[:-2]) * 16
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0

    def _calculate_auto_height(self, element: HTMLElement) -> float:
        """Calculate automatic height based on content"""
        style = element.computed_style

        if element.text_content.strip():
            font_size = self._parse_length(style.get('font-size', '16px'))
            line_height_val = style.get('line-height', '1.4')
            if line_height_val.endswith('px'):
                line_height = self._parse_length(line_height_val)
            else:
                try:
                    line_height = float(line_height_val) * font_size
                except:
                    line_height = font_size * 1.4

            padding_height = self._parse_length(style.get('padding-top', '0')) + self._parse_length(
                style.get('padding-bottom', '0'))
            return max(line_height + padding_height, 30)

        # Default heights for specific elements
        if element.tag == 'h1':
            return 60
        elif element.tag == 'h2':
            return 50
        elif element.tag in ['input', 'button']:
            return 40
        elif element.tag == 'div':
            return 50

        return 30

    @staticmethod
    def _recalculate_auto_height(element: HTMLElement):
        """Recalculate height for auto-height elements after laying out children"""
        if element.computed_style.get('height', 'auto') != 'auto':
            return

        if not element.children:
            return

        # Find the bottom-most child
        max_child_bottom = 0
        for child in element.children:
            if child.layout_box:
                child_bottom = child.layout_box.y + child.layout_box.height + child.layout_box.margin_bottom
                max_child_bottom = max(max_child_bottom, child_bottom)

        # Calculate new height to contain all children
        element_content_top = element.layout_box.y + element.layout_box.padding_top
        new_content_height = max_child_bottom - element_content_top
        new_height = new_content_height + element.layout_box.padding_bottom

        # Ensure minimum height
        element.layout_box.height = max(new_height, 30)

        print(f"Recalculated height for {element.tag}: {element.layout_box.height}")

    def _layout_children(self, element: HTMLElement):
        """Layout child elements"""
        if not element.children:
            return

        style = element.computed_style
        display = style.get('display', 'block')

        print(f"Laying out children of {element.tag} with display: {display}")

        # Calculate available space for children
        available_width = (
                element.layout_box.width - element.layout_box.padding_left - element.layout_box.padding_right)
        available_height = (
                element.layout_box.height - element.layout_box.padding_top - element.layout_box.padding_bottom)

        # Check if any children have inline-block display
        has_inline_blocks = any(
            child.computed_style.get('display', 'block') == 'inline-block' for child in element.children)

        if display == 'flex':
            self._layout_flex_children(element, available_width, available_height)
        elif has_inline_blocks:
            self._layout_inline_children(element, available_width, available_height)
        else:
            self._layout_block_children(element, available_width, available_height)

    def _layout_block_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout children as block elements (vertically stacked)"""
        # Calculate parent's content area start position
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_y = content_y

        print(f"Block layout starting at content area: x={content_x}, y={content_y}")

        for i, child in enumerate(element.children):
            print(f"  Laying out child {i}: {child.tag}")

            # Calculate child's position within parent's content area
            child_x = content_x
            child_y = current_y

            # Layout child at its correct position
            remaining_height = available_height - (current_y - content_y)
            self.layout(child, available_width, remaining_height, is_root=False, parent_x=child_x, parent_y=child_y)

            print(f"  Positioned {child.tag} at ({child.layout_box.x},"
                  f" {child.layout_box.y}), size: {child.layout_box.width}x{child.layout_box.height}")

            # Update position for next child
            current_y += (child.layout_box.margin_top + child.layout_box.height + child.layout_box.margin_bottom)

    def _layout_inline_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout children with inline-block elements horizontally"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_x = content_x
        current_y = content_y
        line_height = 0

        print(f"Inline layout starting at content area: x={content_x}, y={content_y}")

        for i, child in enumerate(element.children):
            child_display = child.computed_style.get('display', 'block')

            # Calculate remaining width on current line
            used_width = current_x - content_x
            remaining_width = max(0, available_width - used_width)

            # Layout child to get its dimensions first
            self.layout(child, remaining_width, available_height, is_root=False, parent_x=current_x, parent_y=current_y)

            # Check if we need to wrap to next line
            child_total_width = (child.layout_box.width + child.layout_box.margin_left + child.layout_box.margin_right)

            if child_total_width > remaining_width and current_x > content_x:
                # Wrap to next line
                current_x = content_x
                current_y += line_height
                line_height = 0

                # Re-layout child on new line
                self.layout(child, available_width, available_height, is_root=False, parent_x=current_x,
                            parent_y=current_y)
                child_total_width = (
                        child.layout_box.width + child.layout_box.margin_left + child.layout_box.margin_right)

            print(
                f"  Positioned {child.tag} at ({child.layout_box.x}, {child.layout_box.y}), size: {child.layout_box.width}x{child.layout_box.height}")

            # Update position for next child
            if child_display == 'inline-block':
                current_x += child_total_width
                line_height = max(line_height,
                                  child.layout_box.height + child.layout_box.margin_top + child.layout_box.margin_bottom)
            else:
                current_x = content_x
                current_y += child.layout_box.height + child.layout_box.margin_top + child.layout_box.margin_bottom
                line_height = 0

    def _layout_flex_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout children using flexbox"""
        style = element.computed_style
        flex_direction = style.get('flex-direction', 'row')

        if flex_direction == 'column':
            self._layout_flex_column(element, available_width, available_height)
        else:
            self._layout_flex_row(element, available_width, available_height)

    def _layout_flex_column(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout flex children vertically"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_y = content_y

        for child in element.children:
            child_x = content_x
            child_y = current_y

            self.layout(child, available_width, available_height, is_root=False, parent_x=child_x, parent_y=child_y)
            current_y += child.layout_box.margin_top + child.layout_box.height + child.layout_box.margin_bottom

    def _layout_flex_row(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout flex children horizontally"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_x = content_x

        # Simple horizontal layout - equal width for flex children
        flex_children = []
        fixed_width = 0

        for child in element.children:
            child_style = child.computed_style
            width = child_style.get('width', 'auto')

            if width != 'auto':
                child_width = self._parse_length(width, available_width)
                fixed_width += child_width
            else:
                flex_children.append(child)

        # Calculate width for flexible children
        remaining_width = available_width - fixed_width
        flex_width = remaining_width / max(1, len(flex_children)) if flex_children else 0

        for child in element.children:
            child_style = child.computed_style
            width = child_style.get('width', 'auto')

            if width != 'auto':
                child_width = self._parse_length(width, available_width)
            else:
                child_width = flex_width

            child_x = current_x
            child_y = content_y

            self.layout(child, child_width, available_height, is_root=False, parent_x=child_x, parent_y=child_y)
            current_x += child_width + child.layout_box.margin_left + child.layout_box.margin_right
