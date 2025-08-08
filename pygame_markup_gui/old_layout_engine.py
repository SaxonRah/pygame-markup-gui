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
        """FIXED layout with proper height propagation"""

        if container_width is None:
            container_width = self.viewport_width
        if container_height is None:
            container_height = self.viewport_height

        # Create layout box
        element.layout_box = LayoutBox()

        # Calculate box model DIMENSIONS ONLY
        self._calculate_box_model(element, container_width, container_height)

        # Fix container height for children.
        # Children should get the CONTENT area of parent, not shrinking values
        child_container_width = (element.layout_box.width -
                                 element.layout_box.padding_left - element.layout_box.padding_right)
        child_container_height = (element.layout_box.height -
                                  element.layout_box.padding_top - element.layout_box.padding_bottom)

        # ENSURE MINIMUM HEIGHTS for containers
        if element.tag in ['html', 'body', 'div'] and element.computed_style.get('background'):
            child_container_height = max(child_container_height, 200)

        print(
            f"{element.tag} gives children container: {child_container_width:.1f} x {child_container_height:.1f}")

        # Position element
        if is_root:
            element.layout_box.x = element.layout_box.margin_left
            element.layout_box.y = element.layout_box.margin_top
        else:
            element.layout_box.x = parent_x + element.layout_box.margin_left
            element.layout_box.y = parent_y + element.layout_box.margin_top

        # Layout children with container dimensions
        self._layout_children(element)#, child_container_width, child_container_height)

        # Debug layout calculations if enabled
        if self.debug_enabled and self.debugger:
            print(f"DEBUG: Laying out {element.tag} at ({parent_x}, {parent_y})")
            print(f"  Container: {container_width}x{container_height}")
            print(f"  Computed: {element.layout_box.width}x{element.layout_box.height}")

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

    def debug_calculate_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """DEBUG VERSION: Let's see what's going wrong"""

        print(f"\n=== DEBUGGING {element.tag} ===")
        print(f"Container: {container_width:.1f} x {container_height:.1f}")

        style = element.computed_style
        box = element.layout_box

        # PROBLEM 1: Check if height calculation is broken
        height = style.get('height', 'auto')
        print(f"CSS height: {height}")

        if height == 'auto':
            calculated_height = self._calculate_auto_height(element)
            print(f"Auto height calculated: {calculated_height}")

            # FIX: Root elements should fill viewport
            if element.tag == 'html':
                calculated_height = container_height
                print(f"HTML element forced to viewport height: {calculated_height}")
            elif element.tag == 'body':
                # Body should fill remaining HTML space minus margins
                parent_height = container_height
                margin_top = self._parse_length(style.get('margin-top', '0'))
                margin_bottom = self._parse_length(style.get('margin-bottom', '0'))
                calculated_height = parent_height - margin_top - margin_bottom
                print(f"Body height calculated: {calculated_height}")

            box.height = calculated_height
        else:
            box.height = self._parse_length(height, container_height)

        # PROBLEM 2: Check width calculation
        width = style.get('width', 'auto')
        print(f"CSS width: {width}")

        if width == 'auto':
            # Check for flexbox constraints
            parent_display = getattr(element.parent, 'computed_style', {}).get('display',
                                                                               'block') if element.parent else 'block'

            if parent_display == 'flex':
                # This element is a flex child - handle flex properties
                flex_basis = style.get('flex-basis', 'auto')
                flex_grow = float(style.get('flex-grow', '0'))
                flex_shrink = float(style.get('flex-shrink', '1'))

                print(f"FLEX CHILD: basis={flex_basis}, grow={flex_grow}, shrink={flex_shrink}")

                if flex_basis != 'auto':
                    if flex_basis.endswith('px'):
                        box.width = float(flex_basis[:-2])
                        print(f"Flex basis width: {box.width}")
                    else:
                        box.width = container_width
                else:
                    box.width = container_width
            else:
                box.width = container_width
        else:
            box.width = self._parse_length(width, container_width)

        print(f"Final calculated: {box.width:.1f} x {box.height:.1f}")

        return box

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
        """Calculate automatic height based on content - FIXED VERSION"""
        style = element.computed_style

        # ROOT ELEMENTS: Fill viewport/container
        if element.tag == 'html':
            return 800  # or whatever your viewport height is

        if element.tag == 'body':
            # Body should fill HTML minus margins
            html_height = 800  # Get from parent
            margin_top = self._parse_length(style.get('margin-top', '0'))
            margin_bottom = self._parse_length(style.get('margin-bottom', '0'))
            return max(html_height - margin_top - margin_bottom, 100)

        # CONTAINER ELEMENTS: Expand to fit children or reasonable default
        if element.tag in ['div', 'section', 'main', 'article', 'aside']:
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
        if element.tag in ['input', 'button']: return 40

        return 30  # Fallback

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
        # """Layout child elements"""
        # if not element.children:
        #     return
        #
        # style = element.computed_style
        # display = style.get('display', 'block')
        #
        # print(f"Laying out children of {element.tag} with display: {display}")
        #
        # # Calculate available space for children
        # available_width = (
        #         element.layout_box.width - element.layout_box.padding_left - element.layout_box.padding_right)
        # available_height = (
        #         element.layout_box.height - element.layout_box.padding_top - element.layout_box.padding_bottom)
        #
        # # Check if any children have inline-block display
        # has_inline_blocks = any(
        #     child.computed_style.get('display', 'block') == 'inline-block' for child in element.children)
        #
        # if display == 'flex':
        #     self._layout_flex_children(element, available_width, available_height)
        # elif has_inline_blocks:
        #     self._layout_inline_children(element, available_width, available_height)
        # else:
        #     self._layout_block_children(element, available_width, available_height)

        """FIXED children layout"""
        if not element.children:
            return

        style = element.computed_style
        display = style.get('display', 'block')

        available_width = (
                element.layout_box.width - element.layout_box.padding_left - element.layout_box.padding_right)
        available_height = (
                element.layout_box.height - element.layout_box.padding_top - element.layout_box.padding_bottom)

        print(
            f"\nLayout children of {element.tag}: display={display}, space={available_width:.1f}x{available_height:.1f}")

        if display == 'flex':
            # Use FIXED flexbox
            flex_direction = style.get('flex-direction', 'row')
            if flex_direction == 'row':
                self._layout_flex_row(element, available_width, available_height)
            else:
                self._layout_flex_column(element, available_width, available_height)
        else:
            # Use FIXED block layout
            self._layout_block_children(element, available_width, available_height)

    def _layout_block_children(self, element: HTMLElement, available_width: float, available_height: float):
        """FIXED block layout"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top
        current_y = content_y

        for child in element.children:
            # Give each child the FULL available height, not shrinking amounts
            self.layout(child, available_width, available_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            # Move down by child's height
            current_y += (child.layout_box.margin_top + child.layout_box.height +
                          child.layout_box.margin_bottom)

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
        """FIXED flexbox row layout"""
        content_x = element.layout_box.x + element.layout_box.padding_left
        content_y = element.layout_box.y + element.layout_box.padding_top

        print(f"\n=== FLEXBOX DEBUG: {element.tag} ===")
        print(f"Available space: {available_width:.1f} x {available_height:.1f}")

        # STEP 1: Categorize children by flex properties
        flex_children = []
        fixed_width_total = 0

        for child in element.children:
            child_style = child.computed_style

            # Parse flex shorthand: flex: grow shrink basis
            flex_grow = float(child_style.get('flex-grow', '0'))
            flex_shrink = float(child_style.get('flex-shrink', '1'))
            flex_basis = child_style.get('flex-basis', 'auto')

            # Handle flex shorthand like "0 0 200px"
            if 'flex' in child_style:
                flex_parts = child_style['flex'].split()
                if len(flex_parts) >= 3:
                    flex_grow = float(flex_parts[0])
                    flex_shrink = float(flex_parts[1])
                    flex_basis = flex_parts[2]

            # Calculate child width
            if flex_basis != 'auto' and flex_basis.endswith('px'):
                # Fixed flex-basis width
                child_width = float(flex_basis[:-2])
                fixed_width_total += child_width
                print(f"  {child.tag}: FIXED width {child_width}px (flex-basis)")
            elif flex_grow > 0:
                # Flexible width - calculate later
                child_width = 0  # Will be calculated
                print(f"  {child.tag}: FLEXIBLE (flex-grow: {flex_grow})")
            else:
                # Default auto width
                child_width = available_width  # Fallback
                print(f"  {child.tag}: AUTO width")

            flex_children.append({
                'element': child,
                'width': child_width,
                'flex_grow': flex_grow,
                'flex_shrink': flex_shrink,
                'flex_basis': flex_basis
            })

        # STEP 2: Calculate flexible widths
        remaining_width = available_width - fixed_width_total
        total_flex_grow = sum(child['flex_grow'] for child in flex_children if child['flex_grow'] > 0)

        print(f"Remaining width: {remaining_width:.1f}, Total flex-grow: {total_flex_grow}")

        if total_flex_grow > 0:
            flex_unit = remaining_width / total_flex_grow
            for child_info in flex_children:
                if child_info['flex_grow'] > 0:
                    child_info['width'] = child_info['flex_grow'] * flex_unit
                    print(f"  {child_info['element'].tag}: CALCULATED width {child_info['width']:.1f}px")

        # STEP 3: Position children
        current_x = content_x

        for child_info in flex_children:
            child = child_info['element']
            child_width = child_info['width']

            print(f"  Positioning {child.tag} at x={current_x:.1f}, width={child_width:.1f}")

            # Layout child with calculated width
            self.layout(child, child_width, available_height, is_root=False,
                        parent_x=current_x, parent_y=content_y)

            current_x += child_width