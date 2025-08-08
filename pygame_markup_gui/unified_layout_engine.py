# unified_working_layout_engine.py
from dataclasses import field, dataclass

from .html_engine import HTMLElement, LayoutBox
from typing import List, Tuple, Dict, Any, Optional
import re


@dataclass
class WorkingLayoutBox(LayoutBox):
    """Unified layout box with all features from base, enhanced, and ultra"""

    # Base LayoutBox properties
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

    # Enhanced properties
    z_index: int = 0
    position_type: str = 'static'
    top: Optional[float] = None
    right: Optional[float] = None
    bottom: Optional[float] = None
    left: Optional[float] = None
    transform = None
    grid_area: Optional[str] = None

    # Ultra properties - Use field() for mutable defaults
    animations: List = field(default_factory=list)
    transitions: List = field(default_factory=list)
    animated_properties: Dict[str, Any] = field(default_factory=dict)
    filters: List = field(default_factory=list)
    clip_path: Optional[str] = None
    rotation: float = 0
    scale: float = 1.0
    opacity: float = 1.0

    def __post_init__(self):
        """Initialize base LayoutBox properties"""
        # Initialize inherited properties from LayoutBox
        if not hasattr(self, 'x'):
            self.x = 0
        if not hasattr(self, 'y'):
            self.y = 0
        if not hasattr(self, 'width'):
            self.width = 0
        if not hasattr(self, 'height'):
            self.height = 0
        if not hasattr(self, 'margin_top'):
            self.margin_top = 0
            self.margin_right = 0
            self.margin_bottom = 0
            self.margin_left = 0
        if not hasattr(self, 'padding_top'):
            self.padding_top = 0
            self.padding_right = 0
            self.padding_bottom = 0
            self.padding_left = 0
        if not hasattr(self, 'border_width'):
            self.border_width = 0


class UnifiedLayoutEngine:
    """Complete working layout engine with base + enhanced + ultra features"""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 800, enable_debug=False):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.debug_enabled = enable_debug

        # Ultra-specific
        self.keyframes = {}
        self.animation_time = 0

    def layout(self, element: HTMLElement, container_width: float = None,
               container_height: float = None, is_root: bool = True,
               parent_x: float = 0, parent_y: float = 0):
        """Main layout method handling all features"""

        if container_width is None:
            container_width = self.viewport_width
        if container_height is None:
            container_height = self.viewport_height

        # Create unified layout box
        element.layout_box = WorkingLayoutBox()

        # Root element setup
        if is_root:
            element.layout_box.width = container_width
            element.layout_box.height = container_height
            element.layout_box.x = 0
            element.layout_box.y = 0
            self._set_default_margins_padding(element.layout_box)
        else:
            # Calculate box model
            self._calculate_unified_box_model(element, container_width, container_height)
            element.layout_box.x = parent_x
            element.layout_box.y = parent_y

        # Apply positioning BEFORE children layout
        self._apply_positioning(element, parent_x, parent_y)

        # Layout children based on display type
        display = element.computed_style.get('display', 'block')

        if display == 'grid':
            self._layout_grid_working(element)
        elif display == 'flex':
            self._layout_flex_working(element)
        else:
            self._layout_block_working(element)

        # Apply transforms and ultra features AFTER layout
        self._apply_transforms(element)
        self._apply_ultra_effects(element)

        if self.debug_enabled:
            print(f"Laid out {element.tag} at ({element.layout_box.x:.1f}, {element.layout_box.y:.1f}) "
                  f"size {element.layout_box.width:.1f}x{element.layout_box.height:.1f}")

    def _calculate_unified_box_model(self, element: HTMLElement, container_width: float, container_height: float):
        """Calculate box model with all features working"""
        style = element.computed_style
        box = element.layout_box

        # Parse margins and padding
        self._parse_margins_padding(element, container_width)

        # Parse border
        border_width = self._parse_length(style.get('border-width', '0'), container_width)
        box.border_width = border_width

        # Calculate width
        width = style.get('width', 'auto')
        if width == 'auto':
            # Handle flex children
            parent_display = getattr(element.parent, 'computed_style', {}).get('display',
                                                                               'block') if element.parent else 'block'

            if parent_display == 'flex':
                parent_flex_direction = getattr(element.parent, 'computed_style', {}).get('flex-direction',
                                                                                          'row') if element.parent else 'row'

                if parent_flex_direction == 'row':
                    # Width calculated by flex - use flex-basis or intrinsic width
                    flex_basis = style.get('flex-basis', 'auto')
                    if flex_basis != 'auto' and flex_basis.endswith('px'):
                        box.width = float(flex_basis[:-2])
                    elif element.tag == 'button' and element.text_content:
                        text_width = len(element.text_content) * 8
                        box.width = text_width + box.padding_left + box.padding_right + 20
                    else:
                        box.width = 100  # Default flex item width
                else:
                    # Column flex - use full width
                    available_width = container_width - box.margin_left - box.margin_right
                    box.width = max(0, available_width)
            else:
                # Regular block width
                if element.tag == 'button' and element.text_content:
                    text_width = len(element.text_content) * 8
                    min_width = text_width + box.padding_left + box.padding_right + 20
                    available_width = container_width - box.margin_left - box.margin_right
                    box.width = max(min_width, min(available_width, 150))
                else:
                    available_width = container_width - box.margin_left - box.margin_right
                    box.width = max(0, available_width)
        else:
            box.width = self._parse_length(width, container_width)

        # Calculate height
        height = style.get('height', 'auto')
        if height == 'auto':
            # Check if parent is flex and this should use flex height
            parent_display = getattr(element.parent, 'computed_style', {}).get('display',
                                                                               'block') if element.parent else 'block'

            if parent_display == 'flex':
                # This is flex child - use container_height from flex calculation
                available_height = container_height - box.margin_top - box.margin_bottom
                box.height = max(0, available_height)
            else:
                # Use auto height calculation
                box.height = self._calculate_auto_height(element, container_height)
        else:
            box.height = self._parse_length(height, container_height)

    def _layout_grid_working(self, element: HTMLElement):
        """WORKING CSS Grid implementation"""
        style = element.computed_style

        if self.debug_enabled:
            print(f"\n=== GRID LAYOUT: {element.tag} ===")

        # Parse grid template areas
        areas_str = style.get('grid-template-areas', 'none')
        if areas_str == 'none':
            self._layout_grid_simple_columns(element)
            return

        # Extract quoted area strings
        quoted_areas = re.findall(r'"([^"]*)"', areas_str)
        if not quoted_areas:
            self._layout_grid_simple_columns(element)
            return

        # Build grid structure
        grid = []
        for area_row in quoted_areas:
            row_areas = area_row.strip().split()
            if row_areas:
                grid.append(row_areas)

        if not grid:
            self._layout_grid_simple_columns(element)
            return

        rows = len(grid)
        cols = len(grid[0]) if grid else 1

        # Calculate container space
        container_box = element.layout_box
        available_width = container_box.width - container_box.padding_left - container_box.padding_right
        available_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        gap = self._parse_length(style.get('gap', '10px'))

        # Parse track sizes
        columns_str = style.get('grid-template-columns', '1fr 250px')
        rows_str = style.get('grid-template-rows', '80px 1fr 50px')

        column_sizes = self._parse_grid_tracks_working(columns_str, available_width, cols, gap)
        row_sizes = self._parse_grid_tracks_working(rows_str, available_height, rows, gap)

        if self.debug_enabled:
            print(f"Grid: {rows}x{cols}, columns: {column_sizes}, rows: {row_sizes}")

        # Create area bounds mapping
        area_bounds = {}
        for r in range(rows):
            for c in range(cols):
                if r < len(grid) and c < len(grid[r]):
                    area_name = grid[r][c]
                    if area_name != '.':
                        if area_name not in area_bounds:
                            area_bounds[area_name] = [r, c, r + 1, c + 1]
                        else:
                            # Extend bounds
                            bounds = area_bounds[area_name]
                            bounds[0] = min(bounds[0], r)
                            bounds[1] = min(bounds[1], c)
                            bounds[2] = max(bounds[2], r + 1)
                            bounds[3] = max(bounds[3], c + 1)

        # Position children by grid area
        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top

        for child in element.children:
            grid_area = child.computed_style.get('grid-area', 'auto')

            if grid_area in area_bounds:
                row_start, col_start, row_end, col_end = area_bounds[grid_area]

                # Calculate position
                x = content_x
                for i in range(col_start):
                    x += column_sizes[i] + (gap if i > 0 else 0)

                y = content_y
                for i in range(row_start):
                    y += row_sizes[i] + (gap if i > 0 else 0)

                # Calculate size
                width = sum(column_sizes[col_start:col_end])
                if col_end - col_start > 1:
                    width += gap * (col_end - col_start - 1)

                height = sum(row_sizes[row_start:row_end])
                if row_end - row_start > 1:
                    height += gap * (row_end - row_start - 1)

                # Layout child
                self.layout(child, width, height, is_root=False, parent_x=x, parent_y=y)

                if self.debug_enabled:
                    print(f"  Placed {child.tag} in {grid_area} at ({x:.1f}, {y:.1f}) size {width:.1f}x{height:.1f}")

    def _parse_grid_tracks_working(self, tracks_str: str, available_space: float, count: int, gap: float) -> List[
        float]:
        """Working grid track parser"""
        if not tracks_str or tracks_str == 'none':
            space_per_track = (available_space - gap * max(0, count - 1)) / count
            return [max(0, space_per_track)] * count

        tracks = tracks_str.split()
        if len(tracks) < count:
            # Extend with 1fr
            tracks.extend(['1fr'] * (count - len(tracks)))
        elif len(tracks) > count:
            # Truncate
            tracks = tracks[:count]

        sizes = []
        fr_tracks = []
        used_space = 0

        # First pass: handle fixed sizes
        for i, track in enumerate(tracks):
            if track.endswith('px'):
                size = float(track[:-2])
                sizes.append(size)
                used_space += size
            elif track.endswith('fr'):
                fr_value = float(track[:-2])
                fr_tracks.append((i, fr_value))
                sizes.append(0)  # Placeholder
            else:
                # Treat as fr
                fr_tracks.append((i, 1.0))
                sizes.append(0)

        # Second pass: distribute remaining space to fr units
        gap_space = gap * max(0, count - 1)
        remaining_space = max(0, available_space - used_space - gap_space)
        total_fr = sum(fr for _, fr in fr_tracks)

        if total_fr > 0 and remaining_space > 0:
            fr_unit = remaining_space / total_fr
            for i, fr in fr_tracks:
                sizes[i] = fr * fr_unit

        return [max(0, size) for size in sizes]

    def _layout_flex_working(self, element: HTMLElement):
        """Working flexbox implementation using existing working code"""
        style = element.computed_style
        flex_direction = style.get('flex-direction', 'row')

        if flex_direction == 'row':
            self._layout_flex_row_working(element)
        else:
            self._layout_flex_column_working(element)

    def _layout_flex_row_working(self, element: HTMLElement):
        """Working flex row layout"""
        container_box = element.layout_box
        available_width = container_box.width - container_box.padding_left - container_box.padding_right
        available_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top

        if not element.children:
            return

        # Calculate flex item sizes
        flex_items = []
        total_fixed_width = 0
        total_flex_grow = 0

        for child in element.children:
            child_style = child.computed_style

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
            if flex_basis != 'auto' and flex_basis.endswith('px'):
                base_width = float(flex_basis[:-2])
            elif flex_basis == '0%' or flex_basis == '0':
                base_width = 0  # FIXED: Handle flex-basis: 0
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
                'base_width': base_width,
                'final_width': base_width
            }

            flex_items.append(flex_item)

            if flex_grow == 0:
                total_fixed_width += base_width
            else:
                total_flex_grow += flex_grow

        # Distribute remaining space
        remaining_width = available_width - total_fixed_width

        if total_flex_grow > 0 and remaining_width > 0:
            flex_unit = remaining_width / total_flex_grow
            for item in flex_items:
                if item['flex_grow'] > 0:
                    item['final_width'] = item['flex_grow'] * flex_unit

        # Position children
        current_x = content_x

        for item in flex_items:
            child = item['element']
            child_width = item['final_width']

            # Layout child
            self.layout(child, child_width, available_height, is_root=False,
                        parent_x=current_x, parent_y=content_y)

            current_x += child_width

    def _layout_flex_column_working(self, element: HTMLElement):
        """Working flex column layout"""
        container_box = element.layout_box
        available_width = container_box.width - container_box.padding_left - container_box.padding_right
        available_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top

        if not element.children:
            return

        # Calculate flex item heights
        flex_items = []
        total_fixed_height = 0
        total_flex_grow = 0

        for child in element.children:
            child_style = child.computed_style

            flex_grow = float(child_style.get('flex-grow', '0'))
            flex_basis = child_style.get('flex-basis', 'auto')

            # Handle flex shorthand
            if 'flex' in child_style:
                flex_parts = child_style['flex'].split()
                if len(flex_parts) >= 1:
                    flex_grow = float(flex_parts[0])
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
                'base_height': base_height,
                'final_height': base_height
            }

            flex_items.append(flex_item)

            if flex_grow == 0:
                total_fixed_height += base_height
            else:
                total_flex_grow += flex_grow

        # Distribute remaining space
        remaining_height = available_height - total_fixed_height

        if total_flex_grow > 0 and remaining_height > 0:
            flex_unit = remaining_height / total_flex_grow
            for item in flex_items:
                if item['flex_grow'] > 0:
                    item['final_height'] = item['flex_grow'] * flex_unit

        # Position children
        current_y = content_y

        for item in flex_items:
            child = item['element']
            child_height = item['final_height']

            # Layout child
            self.layout(child, available_width, child_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            current_y += child_height

    def _layout_block_working(self, element: HTMLElement):
        """Working block layout"""
        container_box = element.layout_box
        available_width = container_box.width - container_box.padding_left - container_box.padding_right
        available_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top
        current_y = content_y

        for child in element.children:
            # Calculate child height
            child_height = self._calculate_auto_height(child, available_height)

            # Layout child
            self.layout(child, available_width, child_height, is_root=False,
                        parent_x=content_x, parent_y=current_y)

            # Move down
            current_y += child.layout_box.height + child.layout_box.margin_top + child.layout_box.margin_bottom

    def _layout_grid_simple_columns(self, element: HTMLElement):
        """Simple grid fallback for when template areas aren't specified"""
        container_box = element.layout_box
        available_width = container_box.width - container_box.padding_left - container_box.padding_right
        available_height = container_box.height - container_box.padding_top - container_box.padding_bottom

        # Default 2x2 grid
        cols = 2
        rows = 2

        gap = self._parse_length(element.computed_style.get('gap', '15px'))

        col_width = (available_width - gap) / cols
        row_height = (available_height - gap) / rows

        content_x = container_box.x + container_box.padding_left
        content_y = container_box.y + container_box.padding_top

        for i, child in enumerate(element.children):
            if i >= cols * rows:
                break

            col = i % cols
            row = i // cols

            x = content_x + col * (col_width + gap)
            y = content_y + row * (row_height + gap)

            self.layout(child, col_width, row_height, is_root=False, parent_x=x, parent_y=y)

    def _apply_positioning(self, element: HTMLElement, parent_x: float, parent_y: float):
        """Apply CSS positioning"""
        style = element.computed_style
        position = style.get('position', 'static')

        if position == 'absolute':
            top = style.get('top', 'auto')
            left = style.get('left', 'auto')
            right = style.get('right', 'auto')
            bottom = style.get('bottom', 'auto')

            if top != 'auto':
                element.layout_box.y = self._parse_length(top)
            if left != 'auto':
                element.layout_box.x = self._parse_length(left)
            elif right != 'auto':
                element.layout_box.x = self.viewport_width - element.layout_box.width - self._parse_length(right)

        elif position == 'relative':
            top = style.get('top', 'auto')
            left = style.get('left', 'auto')

            if top != 'auto':
                element.layout_box.y += self._parse_length(top)
            if left != 'auto':
                element.layout_box.x += self._parse_length(left)

    def _apply_transforms(self, element: HTMLElement):
        """Apply CSS transforms"""
        style = element.computed_style
        transform = style.get('transform', 'none')

        if transform != 'none' and element.layout_box:
            # Parse transform functions
            if 'rotate(' in transform:
                match = re.search(r'rotate\(([^)]+)\)', transform)
                if match:
                    angle_str = match.group(1)
                    element.layout_box.rotation = float(angle_str.replace('deg', ''))

            if 'scale(' in transform:
                match = re.search(r'scale\(([^)]+)\)', transform)
                if match:
                    scale_str = match.group(1)
                    element.layout_box.scale = float(scale_str)

            if 'translate(' in transform:
                match = re.search(r'translate\(([^)]+)\)', transform)
                if match:
                    translate_str = match.group(1)
                    parts = translate_str.split(',')
                    if len(parts) >= 2:
                        x_offset = self._parse_length(parts[0].strip())
                        y_offset = self._parse_length(parts[1].strip())
                        element.layout_box.x += x_offset
                        element.layout_box.y += y_offset

    def _apply_ultra_effects(self, element: HTMLElement):
        """Apply ultra-level effects"""
        style = element.computed_style

        # Opacity
        opacity = style.get('opacity', '1')
        try:
            element.layout_box.opacity = float(opacity)
        except:
            element.layout_box.opacity = 1.0

        # Filters
        filter_value = style.get('filter', 'none')
        if filter_value != 'none':
            element.layout_box.filters = self._parse_filters(filter_value)

        # Clip path
        clip_path = style.get('clip-path', 'none')
        if clip_path != 'none':
            element.layout_box.clip_path = clip_path

    # Helper methods
    def _calculate_auto_height(self, element: HTMLElement, container_height: float) -> float:
        """Calculate automatic height"""
        style = element.computed_style

        if element.tag == 'html':
            return self.viewport_height
        elif element.tag == 'body':
            return container_height

        # Text content
        if element.text_content and element.text_content.strip():
            font_size = self._parse_length(style.get('font-size', '16px'))
            padding_height = (self._parse_length(style.get('padding-top', '0')) +
                              self._parse_length(style.get('padding-bottom', '0')))
            return max(font_size * 1.5 + padding_height, 30)

        # Element defaults
        height_map = {
            'h1': 50, 'h2': 45, 'h3': 40, 'button': 40, 'nav': 60,
            'header': 100, 'footer': 60, 'aside': 300, 'main': 400, 'section': 200
        }

        return height_map.get(element.tag, 40)

    def _parse_margins_padding(self, element: HTMLElement, container_width: float):
        """Parse margins and padding"""
        style = element.computed_style
        box = element.layout_box

        # Margins
        if 'margin' in style:
            margin_values = self._parse_box_value(style['margin'], container_width)
            box.margin_top, box.margin_right, box.margin_bottom, box.margin_left = margin_values
        else:
            box.margin_top = self._parse_length(style.get('margin-top', '0'), container_width)
            box.margin_right = self._parse_length(style.get('margin-right', '0'), container_width)
            box.margin_bottom = self._parse_length(style.get('margin-bottom', '0'), container_width)
            box.margin_left = self._parse_length(style.get('margin-left', '0'), container_width)

        # Padding
        if 'padding' in style:
            padding_values = self._parse_box_value(style['padding'], container_width)
            box.padding_top, box.padding_right, box.padding_bottom, box.padding_left = padding_values
        else:
            box.padding_top = self._parse_length(style.get('padding-top', '0'), container_width)
            box.padding_right = self._parse_length(style.get('padding-right', '0'), container_width)
            box.padding_bottom = self._parse_length(style.get('padding-bottom', '0'), container_width)
            box.padding_left = self._parse_length(style.get('padding-left', '0'), container_width)

    def _set_default_margins_padding(self, box):
        """Set default margins and padding for root"""
        box.margin_top = box.margin_right = box.margin_bottom = box.margin_left = 0
        box.padding_top = box.padding_right = box.padding_bottom = box.padding_left = 0
        box.border_width = 0

    def _parse_box_value(self, value: str, container_size: float) -> Tuple[float, float, float, float]:
        """Parse margin/padding shorthand"""
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

    def _parse_length(self, value: str, container_size: float = 0) -> float:
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
            elif value.endswith('rem'):
                return float(value[:-3]) * 16
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0

    def _parse_filters(self, filter_value: str) -> List[str]:
        """Parse CSS filter functions"""
        filters = []
        # Simple filter parsing
        if 'blur(' in filter_value:
            filters.append('blur')
        if 'brightness(' in filter_value:
            filters.append('brightness')
        return filters