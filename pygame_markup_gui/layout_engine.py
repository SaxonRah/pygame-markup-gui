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

        # Handle root element specially
        if is_root:
            element.layout_box.width = container_width
            element.layout_box.height = container_height
            element.layout_box.x = 0
            element.layout_box.y = 0
            element.layout_box.margin_top = element.layout_box.margin_right = 0
            element.layout_box.margin_bottom = element.layout_box.margin_left = 0
            element.layout_box.padding_top = element.layout_box.padding_right = 0
            element.layout_box.padding_bottom = element.layout_box.padding_left = 0
            element.layout_box.border_width = 0

            # Apply any explicit padding/margins from CSS for root
            style = element.computed_style
            if style.get('padding'):
                padding = self._parse_box_value(style.get('padding', '0'), container_width)
                element.layout_box.padding_top, element.layout_box.padding_right, element.layout_box.padding_bottom, element.layout_box.padding_left = padding
            if style.get('margin'):
                margin = self._parse_box_value(style.get('margin', '0'), container_width)
                element.layout_box.margin_top, element.layout_box.margin_right, element.layout_box.margin_bottom, element.layout_box.margin_left = margin
        else:
            # Calculate box model (margin, border, padding, content)
            self._calculate_box_model(element, container_width, container_height)
            # Position element relative to parent
            element.layout_box.x = parent_x + element.layout_box.margin_left
            element.layout_box.y = parent_y + element.layout_box.margin_top

        # Calculate available space for children
        child_container_width = (element.layout_box.width -
                                 element.layout_box.padding_left - element.layout_box.padding_right)
        child_container_height = (element.layout_box.height -
                                  element.layout_box.padding_top - element.layout_box.padding_bottom)

        # Layout children
        self._layout_children(element, child_container_width, child_container_height)

        # Debug layout calculations if enabled
        if self.debug_enabled and self.debugger:
            print(f"DEBUG: Laying out {element.tag} at ({element.layout_box.x}, {element.layout_box.y})")
            print(f"  Container: {container_width}x{container_height}")
            print(f"  Computed: {element.layout_box.width}x{element.layout_box.height}")

    def _calculate_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """Calculate element's box model (margin, border, padding, content)"""
        style = element.computed_style
        box = element.layout_box

        # Parse margins, padding, border (same as before)
        margin_top = self._parse_length(style.get('margin-top', '0'), container_width)
        margin_right = self._parse_length(style.get('margin-right', '0'), container_width)
        margin_bottom = self._parse_length(style.get('margin-bottom', '0'), container_width)
        margin_left = self._parse_length(style.get('margin-left', '0'), container_width)

        if 'margin' in style:
            margin = self._parse_box_value(style.get('margin', '0'), container_width)
            margin_top, margin_right, margin_bottom, margin_left = margin

        box.margin_top, box.margin_right, box.margin_bottom, box.margin_left = margin_top, margin_right, margin_bottom, margin_left

        padding_top = self._parse_length(style.get('padding-top', '0'), container_width)
        padding_right = self._parse_length(style.get('padding-right', '0'), container_width)
        padding_bottom = self._parse_length(style.get('padding-bottom', '0'), container_width)
        padding_left = self._parse_length(style.get('padding-left', '0'), container_width)

        if 'padding' in style:
            padding = self._parse_box_value(style.get('padding', '0'), container_width)
            padding_top, padding_right, padding_bottom, padding_left = padding

        box.padding_top, box.padding_right, box.padding_bottom, box.padding_left = padding_top, padding_right, padding_bottom, padding_left

        border_width = self._parse_length(style.get('border-width', '0'), container_width)
        box.border_width = border_width

        # Calculate dimensions
        width = style.get('width', 'auto')
        height = style.get('height', 'auto')

        # Calculate width (same as before)
        if width == 'auto':
            parent_display = getattr(element.parent, 'computed_style', {}).get('display',
                                                                               'block') if element.parent else 'block'

            if parent_display == 'flex':
                parent_flex_direction = getattr(
                    element.parent, 'computed_style', {}).get('flex-direction', 'row') if element.parent else 'row'

                if parent_flex_direction == 'row':
                    # This is a flex child in a row - use the container_width passed by flex layout
                    # The container_width IS the width that flex calculated for this element
                    available_width = container_width - box.margin_left - box.margin_right
                    box.width = max(0, available_width)
                    print(
                        f"FLEX CHILD {element.tag}: using flex width {box.width} (from container_width {container_width})")
                else:
                    # Column flex - use full width
                    available_width = container_width - box.margin_left - box.margin_right
                    box.width = max(0, available_width)
            elif element.tag == 'button' and element.text_content:
                text_width = len(element.text_content) * 8
                min_width = text_width + padding_left + padding_right + 20
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(min_width, min(available_width, 150))
            else:
                available_width = container_width - box.margin_left - box.margin_right
                box.width = max(0, available_width)
        else:
            box.width = self._parse_length(width, container_width)

        # CRITICAL FIX: Calculate height properly for flex children
        if height == 'auto':
            # Check if this is a flex child and parent passed explicit height
            parent_display = getattr(element.parent, 'computed_style', {}).get('display',
                                                                               'block') if element.parent else 'block'

            if parent_display == 'flex':
                # This is a flex child - use the container_height passed by flex layout
                # The container_height IS the height that flex calculated for this element
                available_height = container_height - box.margin_top - box.margin_bottom
                box.height = max(0, available_height)
                print(
                    f"FLEX CHILD {element.tag}: using flex height {box.height} (from container_height {container_height})")
            else:
                # Not a flex child - use auto height calculation
                box.height = self._calculate_auto_height(element, container_height)
                print(f"NON-FLEX {element.tag}: using auto height {box.height}")
        else:
            box.height = self._parse_length(height, container_height)
            print(f"EXPLICIT {element.tag}: using explicit height {box.height}")

    def _calculate_auto_height(self, element: HTMLElement, container_height: float) -> float:
        """Calculate automatic height for an element"""
        style = element.computed_style

        # Root elements get viewport height
        if element.tag == 'html':
            return self.viewport_height
        elif element.tag == 'body':
            margin_top = self._parse_length(style.get('margin-top', '0'))
            margin_bottom = self._parse_length(style.get('margin-bottom', '0'))
            return max(0, container_height - margin_top - margin_bottom)

        # SPECIAL CASE: File items in file list
        if (element.tag == 'div' and element.text_content.strip() and
                element.parent and 'file-list' in str(element.parent.computed_style.get('class', ''))):
            # File items should be fixed height regardless of container
            return 42  # Perfect size for file items (text + padding + border + margin)

        # Text content elements
        if element.text_content and element.text_content.strip():
            font_size = self._parse_length(style.get('font-size', '16px'))
            line_height_val = style.get('line-height', '1.2')

            try:
                if line_height_val.endswith('px'):
                    line_height = self._parse_length(line_height_val)
                else:
                    line_height = float(line_height_val) * font_size
            except:
                line_height = font_size * 1.2

            # Get padding
            padding_top = self._parse_length(style.get('padding-top', '0'))
            padding_bottom = self._parse_length(style.get('padding-bottom', '0'))

            # Handle padding shorthand
            if style.get('padding') and not padding_top:
                padding_values = self._parse_box_value(style.get('padding', '0'), 0)
                padding_top, _, padding_bottom, _ = padding_values

            total_height = line_height + padding_top + padding_bottom
            return max(total_height, 30)

        # Containers with specific styling
        if element.tag in ['div', 'section', 'main', 'aside', 'article']:
            has_background = style.get('background') or style.get('background-color')
            has_padding = style.get('padding') or style.get('padding-top')

            if has_background or has_padding:
                return min(100, container_height * 0.25)  # More conservative
            else:
                return 40  # Good default for styled divs

        # Element-specific defaults (same as before)
        height_defaults = {
            'h1': 50, 'h2': 45, 'h3': 40, 'h4': 35, 'h5': 30, 'h6': 25,
            'button': 40, 'input': 35,
            'nav': 60, 'header': 100, 'footer': 60,
            'aside': 300, 'main': 400, 'section': 250,
            'p': 30, 'span': 25
        }

        return height_defaults.get(element.tag, 30)

    def _layout_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Layout children based on their display type"""
        if not element.children:
            return

        style = element.computed_style
        display = style.get('display', 'block')

        print(
            f"\nLayouting children of {element.tag}: display={display}, available={available_width:.1f}x{available_height:.1f}")

        # Check for inline children
        has_inline_children = any(
            child.computed_style.get('display', 'block') in ['inline', 'inline-block']
            for child in element.children
        )

        if display == 'flex':
            flex_direction = style.get('flex-direction', 'row')
            if flex_direction == 'row':
                self._layout_flex_row(element, available_width, available_height)
            else:
                self._layout_flex_column(element, available_width, available_height)
        elif has_inline_children:
            self._layout_inline_children(element, available_width, available_height)
        else:
            self._layout_block_children(element, available_width, available_height)

    def _layout_flex_column(self, element: HTMLElement, available_width: float, available_height: float):
        """Complete flex column layout implementation"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top

        print(f"Flex column layout for {element.tag}: starting at y={content_y}, available_height={available_height}")

        if not element.children:
            return

        # Step 1: Collect flex information for all children
        flex_items = []
        total_fixed_height = 0
        total_flex_grow = 0

        for child in element.children:
            child_style = child.computed_style

            # Parse flex properties
            flex_grow = float(child_style.get('flex-grow', '0'))
            flex_shrink = float(child_style.get('flex-shrink', '1'))
            flex_basis = child_style.get('flex-basis', 'auto')

            # Handle flex shorthand
            if 'flex' in child_style:
                flex_parts = child_style['flex'].split()
                if len(flex_parts) >= 1:
                    flex_grow = float(flex_parts[0])
                if len(flex_parts) >= 2:
                    flex_shrink = float(flex_parts[1])
                if len(flex_parts) >= 3:
                    flex_basis = flex_parts[2]

            # Calculate base height
            if flex_basis != 'auto' and flex_basis.endswith('px'):
                base_height = float(flex_basis[:-2])
            elif child_style.get('height', 'auto') != 'auto':
                base_height = self._parse_length(child_style['height'], available_height)
            else:
                base_height = self._calculate_auto_height(child, available_height)

            flex_item = {
                'element': child,
                'flex_grow': flex_grow,
                'flex_shrink': flex_shrink,
                'flex_basis': flex_basis,
                'base_height': base_height,
                'final_height': base_height
            }

            flex_items.append(flex_item)

            if flex_grow == 0:
                total_fixed_height += base_height
            else:
                total_flex_grow += flex_grow

        # Step 2: Distribute remaining space to flex-grow items
        remaining_height = available_height - total_fixed_height

        if total_flex_grow > 0 and remaining_height > 0:
            flex_unit = remaining_height / total_flex_grow
            for item in flex_items:
                if item['flex_grow'] > 0:
                    item['final_height'] = item['flex_grow'] * flex_unit

        # Step 3: Handle flex-shrink if we're over the available space
        total_used_height = sum(item['final_height'] for item in flex_items)
        if total_used_height > available_height:
            overflow = total_used_height - available_height
            total_flex_shrink = sum(item['flex_shrink'] * item['final_height'] for item in flex_items)

            if total_flex_shrink > 0:
                for item in flex_items:
                    shrink_amount = (item['flex_shrink'] * item['final_height'] / total_flex_shrink) * overflow
                    item['final_height'] = max(0, item['final_height'] - shrink_amount)

        # Step 4: Position children
        current_y = content_y

        for item in flex_items:
            child = item['element']
            child_height = item['final_height']

            print(f"  Positioning {child.tag} at y={current_y:.1f}, height={child_height:.1f}")

            # Layout child with calculated dimensions
            self.layout(child, available_width, child_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            current_y += child_height

    def _layout_flex_row(self, element: HTMLElement, available_width: float, available_height: float):
        """Complete flex row layout implementation"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top

        print(f"Flex row layout for {element.tag}: starting at x={content_x}, available_width={available_width}")

        if not element.children:
            return

        # Step 1: Collect flex information for all children
        flex_items = []
        total_fixed_width = 0
        total_flex_grow = 0

        for child in element.children:
            child_style = child.computed_style

            # Parse flex properties
            flex_grow = float(child_style.get('flex-grow', '0'))
            flex_shrink = float(child_style.get('flex-shrink', '1'))
            flex_basis = child_style.get('flex-basis', 'auto')

            # Handle flex shorthand
            if 'flex' in child_style:
                flex_parts = child_style['flex'].split()
                if len(flex_parts) >= 1:
                    flex_grow = float(flex_parts[0])
                if len(flex_parts) >= 2:
                    flex_shrink = float(flex_parts[1])
                if len(flex_parts) >= 3:
                    flex_basis = flex_parts[2]

            # Calculate base width
            if flex_basis != 'auto':
                if flex_basis.endswith('px'):
                    base_width = float(flex_basis[:-2])
                elif flex_basis == '0%' or flex_basis == '0':
                    base_width = 0  # FIXED: Handle flex-basis: 0
                else:
                    base_width = 0  # Default for other flex-basis values
            elif child_style.get('width', 'auto') != 'auto':
                base_width = self._parse_length(child_style['width'], available_width)
            elif child.tag == 'button' and child.text_content:
                text_width = len(child.text_content) * 8
                base_width = text_width + 40  # padding + margin
            else:
                # FIXED: For flex items with flex-grow > 0, use minimal base width
                if flex_grow > 0:
                    base_width = 0  # Let flex-grow handle all the sizing
                else:
                    base_width = 100  # Default flex item width

            flex_item = {
                'element': child,
                'flex_grow': flex_grow,
                'flex_shrink': flex_shrink,
                'flex_basis': flex_basis,
                'base_width': base_width,
                'final_width': base_width
            }

            flex_items.append(flex_item)

            if flex_grow == 0:
                total_fixed_width += base_width
            else:
                total_flex_grow += flex_grow

        # Step 2: Distribute remaining space to flex-grow items
        remaining_width = available_width - total_fixed_width

        if total_flex_grow > 0 and remaining_width > 0:
            flex_unit = remaining_width / total_flex_grow
            for item in flex_items:
                if item['flex_grow'] > 0:
                    # Add distributed width to base width
                    item['final_width'] = item['base_width'] + (item['flex_grow'] * flex_unit)

        # Step 3: Handle flex-shrink if we're over the available space
        total_used_width = sum(item['final_width'] for item in flex_items)
        if total_used_width > available_width:
            overflow = total_used_width - available_width
            total_flex_shrink = sum(item['flex_shrink'] * item['final_width'] for item in flex_items)

            if total_flex_shrink > 0:
                for item in flex_items:
                    shrink_amount = (item['flex_shrink'] * item['final_width'] / total_flex_shrink) * overflow
                    item['final_width'] = max(0, item['final_width'] - shrink_amount)

        # Step 4: Position children
        current_x = content_x

        for item in flex_items:
            child = item['element']
            child_width = item['final_width']

            print(f"  Positioning {child.tag} at x={current_x:.1f}, width={child_width:.1f}")

            # Layout child with calculated dimensions
            self.layout(child, child_width, available_height, is_root=False,
                        parent_x=current_x, parent_y=content_y)

            current_x += child_width

    def _layout_block_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Complete block layout implementation"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_y = content_y
        remaining_height = available_height

        print(
            f"Block layout for {element.tag}: {len(element.children)} children, space={available_width:.1f}x{available_height:.1f}")

        for i, child in enumerate(element.children):
            # Calculate appropriate height for this child
            child_height = self._calculate_child_height(child, available_width, remaining_height)

            print(f"  Child {i} ({child.tag}): calculated height={child_height:.1f}, remaining={remaining_height:.1f}")

            # Layout child with calculated dimensions
            self.layout(child, available_width, child_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            # Calculate space used by this child (including margins)
            child_used_height = (child.layout_box.margin_top + child.layout_box.height +
                                 child.layout_box.margin_bottom)

            # Update position for next child
            current_y += child_used_height
            remaining_height = max(0, remaining_height - child_used_height)

            print(f"    Positioned at y={child.layout_box.y:.1f}, actual height={child.layout_box.height:.1f}")
            print(f"    Used space={child_used_height:.1f}, remaining={remaining_height:.1f}")

    def _calculate_child_height(self, element: HTMLElement, available_width: float, remaining_height: float) -> float:
        """Calculate the height a child should be given in block layout"""
        style = element.computed_style

        # Check for explicit height first
        height = style.get('height', 'auto')
        if height != 'auto':
            return self._parse_length(height, remaining_height)

        # Use auto height directly - no more progressive shrinking
        auto_height = self._calculate_auto_height(element, remaining_height)

        # Just ensure it doesn't exceed remaining space
        return min(auto_height, remaining_height)

    def _layout_inline_children(self, element: HTMLElement, available_width: float, available_height: float):
        """Complete inline layout implementation with proper wrapping"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_x = content_x
        current_y = content_y
        line_height = 0

        print(f"Inline layout for {element.tag}: {len(element.children)} children")

        for i, child in enumerate(element.children):
            # Calculate remaining width on current line
            used_width = current_x - content_x
            remaining_width = max(0, available_width - used_width)

            # Get child's display type
            child_display = child.computed_style.get('display', 'block')

            # Calculate child dimensions first
            if child_display == 'inline-block':
                # For inline-block elements, calculate their natural width
                child_style = child.computed_style
                child_width = child_style.get('width', 'auto')

                if child_width == 'auto':
                    if child.tag == 'button' and child.text_content:
                        text_width = len(child.text_content) * 8
                        padding_left = self._parse_length(child_style.get('padding-left', '0'))
                        padding_right = self._parse_length(child_style.get('padding-right', '0'))
                        natural_width = text_width + padding_left + padding_right + 20
                    else:
                        natural_width = min(150, remaining_width)  # Default inline-block width
                else:
                    natural_width = self._parse_length(child_width, available_width)

                # Check if child fits on current line
                child_margins = (self._parse_length(child_style.get('margin-left', '0'), available_width) +
                                 self._parse_length(child_style.get('margin-right', '0'), available_width))
                child_total_width = natural_width + child_margins

                if child_total_width > remaining_width and current_x > content_x:
                    # Wrap to next line
                    current_x = content_x
                    current_y += line_height
                    line_height = 0
                    remaining_width = available_width

                # Layout child with natural width
                self.layout(child, natural_width, available_height, is_root=False,
                            parent_x=current_x, parent_y=current_y)

                # Update position for next child
                current_x += child_total_width
                line_height = max(line_height, child.layout_box.height +
                                  child.layout_box.margin_top + child.layout_box.margin_bottom)

                print(f"  Inline-block {child.tag} at x={child.layout_box.x:.1f}, width={child.layout_box.width:.1f}")

            else:
                # Regular block element - force to new line
                if current_x > content_x:
                    current_x = content_x
                    current_y += line_height
                    line_height = 0

                # Layout child with full width
                self.layout(child, available_width, available_height, is_root=False,
                            parent_x=current_x, parent_y=current_y)

                # Move to next line
                current_y += (child.layout_box.height + child.layout_box.margin_top +
                              child.layout_box.margin_bottom)
                line_height = 0

                print(f"  Block {child.tag} at y={child.layout_box.y:.1f}, height={child.layout_box.height:.1f}")

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
