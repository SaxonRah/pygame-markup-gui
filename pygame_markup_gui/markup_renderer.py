import pygame
from typing import Dict, Optional, Tuple
from .html_engine import HTMLElement


class BaseMarkupRenderer:
    """Render HTML/CSS to pygame surfaces"""

    def __init__(self):
        pygame.font.init()
        self.font_cache = {}
        self.color_cache = {}

    def render_element(self, target_surface: pygame.Surface, element: HTMLElement):
        """Render element and all children to target surface using absolute positioning"""

        # Use precise text rendering
        if element.text_content.strip():
            self._render_text(target_surface, element)

        # Render children
        for child in element.children:
            self.render_element(target_surface, child)

        self._render_recursive(element, target_surface)

    def _render_recursive(self, element: HTMLElement, target_surface: pygame.Surface):
        """Recursively render element and all children"""
        if not element.layout_box:
            return

        box = element.layout_box
        if box.width <= 0 or box.height <= 0:
            return

        try:
            # Get absolute position and size
            x = int(box.x)
            y = int(box.y)
            width = int(box.width)
            height = int(box.height)

            # Check if element is within target surface bounds
            if (x >= target_surface.get_width() or y >= target_surface.get_height() or
                    x + width <= 0 or y + height <= 0):
                return

            # Create surface for this element
            elem_surface = pygame.Surface((width, height), pygame.SRCALPHA)

            # Render background
            self._render_background(elem_surface, element)

            # Render border
            self._render_border(elem_surface, element)

            # Render text content
            if element.text_content and element.text_content.strip():
                self._render_text(elem_surface, element)

            # Blit element to target surface
            # Clamp position to target surface bounds
            target_x = max(0, min(x, target_surface.get_width() - 1))
            target_y = max(0, min(y, target_surface.get_height() - 1))

            # Calculate clipped blit area
            src_rect = pygame.Rect(0, 0, width, height)
            dst_rect = pygame.Rect(target_x, target_y, width, height)

            # Adjust for clipping
            if x < 0:
                src_rect.x = -x
                src_rect.width += x
                dst_rect.x = 0
                dst_rect.width += x

            if y < 0:
                src_rect.y = -y
                src_rect.height += y
                dst_rect.y = 0
                dst_rect.height += y

            if dst_rect.right > target_surface.get_width():
                diff = dst_rect.right - target_surface.get_width()
                src_rect.width -= diff
                dst_rect.width -= diff

            if dst_rect.bottom > target_surface.get_height():
                diff = dst_rect.bottom - target_surface.get_height()
                src_rect.height -= diff
                dst_rect.height -= diff

            # Blit if there's something to blit
            if src_rect.width > 0 and src_rect.height > 0:
                target_surface.blit(elem_surface, dst_rect, src_rect)

            # Store rendered surface for debugging
            element.pygame_surface = elem_surface

        except Exception as e:
            print(f"Error rendering {element.tag}: {e}")
            import traceback
            traceback.print_exc()

        # Render all children recursively
        for child in element.children:
            self._render_recursive(child, target_surface)

    def _render_background(self, surface: pygame.Surface, element: HTMLElement):
        """Render background color"""
        style = element.computed_style
        bg_color = style.get('background-color', 'transparent')

        if bg_color and bg_color != 'transparent':
            color = self._parse_color(bg_color)
            if color:
                surface.fill(color)

    def _render_border(self, surface: pygame.Surface, element: HTMLElement):
        """Render border"""
        style = element.computed_style
        border_width_str = style.get('border-width', '0')
        border_style = style.get('border-style', 'solid')

        if border_style != 'none':
            border_width = self._parse_length(border_width_str)
            if border_width > 0:
                border_color = self._parse_color(style.get('border-color', '#000000'))
                if border_color:
                    pygame.draw.rect(surface, border_color, surface.get_rect(), int(border_width))

    def _render_text(self, surface: pygame.Surface, element: HTMLElement):
        """Render text content"""
        style = element.computed_style
        text = element.text_content.strip()

        if not text:
            return

        print(f"Rendering text '{text}' for {element.tag} (class: {element.attributes.get('class', '')})")

        # Get font and color
        font = self._get_font(style)
        color = self._parse_color(style.get('color', '#000000'))

        print(f"  Font: {font}, Color: {color}")
        print(f"  Surface size: {surface.get_size()}")
        print(f"  Element computed style color: {style.get('color', 'none')}")

        if font and color:
            try:
                # Render text with anti-aliasing
                text_surface = font.render(text, True, color)

                # Position text with padding
                padding_left = element.layout_box.padding_left if hasattr(element.layout_box, 'padding_left') else 0
                padding_top = element.layout_box.padding_top if hasattr(element.layout_box, 'padding_top') else 0

                x = int(padding_left)
                y = int(padding_top)

                # Center vertically if there's extra space
                available_height = surface.get_height() - padding_top * 2
                if available_height > text_surface.get_height():
                    y = int(padding_top + (available_height - text_surface.get_height()) / 2)

                print(f"  Blitting text at ({x}, {y}) to surface {surface.get_size()}")

                # Ensure position is within bounds
                if (x >= 0 and y >= 0 and
                        x < surface.get_width() and y < surface.get_height() and
                        x + text_surface.get_width() > 0 and y + text_surface.get_height() > 0):

                    # Clip text to surface bounds
                    clip_rect = pygame.Rect(x, y, text_surface.get_width(), text_surface.get_height())
                    clip_rect.clamp_ip(surface.get_rect())

                    if clip_rect.width > 0 and clip_rect.height > 0:
                        surface.blit(text_surface, (x, y))
                        print(f"  Successfully rendered text '{text}'")
                else:
                    print(f"  Text position ({x}, {y}) is outside surface bounds {surface.get_size()}")

            except Exception as e:
                print(f"Error rendering text '{text}': {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"  Cannot render text - font: {font}, color: {color}")

    def _get_font(self, style: Dict[str, str]) -> Optional[pygame.font.Font]:
        """Get pygame font from CSS style"""
        font_family = style.get('font-family', 'Arial')
        font_size = max(8, int(self._parse_length(style.get('font-size', '16px'))))
        font_weight = style.get('font-weight', 'normal')

        font_key = (font_family, font_size, font_weight)

        if font_key not in self.font_cache:
            try:
                bold = font_weight == 'bold' or font_weight == '700'
                self.font_cache[font_key] = pygame.font.SysFont(font_family, font_size, bold=bold)
            except:
                self.font_cache[font_key] = pygame.font.Font(None, font_size)

        return self.font_cache[font_key]

    def _parse_color(self, color_string: str) -> Optional[pygame.Color]:
        """Parse CSS color to pygame Color with proper hex handling"""
        if not color_string or color_string == 'transparent':
            return None

        if color_string in self.color_cache:
            return self.color_cache[color_string]

        try:
            color = None

            if color_string.startswith('#'):
                # Handle hex colors, including shorthand
                hex_color = self._expand_hex_color(color_string)
                if hex_color:
                    # Parse hex manually since pygame.Color is unreliable
                    hex_color = hex_color[1:]  # Remove #
                    if len(hex_color) == 6:
                        r = int(hex_color[0:2], 16)
                        g = int(hex_color[2:4], 16)
                        b = int(hex_color[4:6], 16)
                        color = pygame.Color(r, g, b)

            elif color_string.startswith('rgb'):
                import re
                match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_string)
                if match:
                    r, g, b = map(int, match.groups())
                    color = pygame.Color(r, g, b)

            else:
                # Named colors
                color_map = {
                    'red': (255, 0, 0), 'green': (0, 128, 0), 'blue': (0, 0, 255),
                    'white': (255, 255, 255), 'black': (0, 0, 0), 'gray': (128, 128, 128),
                    'grey': (128, 128, 128), 'yellow': (255, 255, 0), 'cyan': (0, 255, 255),
                    'magenta': (255, 0, 255), 'orange': (255, 165, 0), 'purple': (128, 0, 128),
                    'brown': (165, 42, 42), 'pink': (255, 192, 203), 'lime': (0, 255, 0),
                    'navy': (0, 0, 128), 'olive': (128, 128, 0), 'teal': (0, 128, 128),
                    'silver': (192, 192, 192), 'maroon': (128, 0, 0)
                }
                if color_string.lower() in color_map:
                    r, g, b = color_map[color_string.lower()]
                    color = pygame.Color(r, g, b)

            if color:
                self.color_cache[color_string] = color
            return color

        except Exception as e:
            print(f"Error parsing color '{color_string}': {e}")
            return None

    def _expand_hex_color(self, hex_color: str) -> Optional[str]:
        """Expand shorthand hex colors like #333 to #333333"""
        if not hex_color.startswith('#'):
            return None

        hex_part = hex_color[1:]

        # 3-digit shorthand (e.g., #333 -> #333333)
        if len(hex_part) == 3:
            return f"#{hex_part[0]}{hex_part[0]}{hex_part[1]}{hex_part[1]}{hex_part[2]}{hex_part[2]}"

        # 6-digit full hex
        elif len(hex_part) == 6:
            return hex_color

        # Invalid hex
        return None

    def _parse_length(self, value: str) -> float:
        """Parse length value"""
        if not value:
            return 0

        try:
            if value.endswith('px'):
                return float(value[:-2])
            elif value.endswith('%'):
                return float(value[:-1])  # Would need context for percentage
            elif value.endswith('em'):
                return float(value[:-2]) * 16
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0


class MarkupRenderer(BaseMarkupRenderer):
    """Precise text rendering that matches browser behavior"""

    def __init__(self):
        super().__init__()
        self.metrics_cache = {}

    def render_text_precise(self, surface: pygame.Surface, element: HTMLElement):
        """Render text with browser-precise positioning"""
        text = element.text_content.strip()
        if not text:
            return None

        style = element.computed_style
        box = element.layout_box

        # Get font with precise metrics
        font_info = self._get_precise_font(style)
        font = font_info['font']
        metrics = font_info['metrics']

        # Parse color
        color = self._parse_color(style.get('color', '#000000'))
        if not color:
            return None

        # Calculate precise text position
        text_pos = self._calculate_precise_text_position(text, font, metrics, box, style)

        # Render with precise baseline
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, text_pos)

        return text_pos  # For debugging

    def _get_precise_font(self, style: Dict[str, str]) -> Dict:
        """Get font with precise metrics matching browsers"""
        font_family = style.get('font-family', 'Arial').strip('\'"')
        font_size = self._parse_font_size(style.get('font-size', '16px'))
        font_weight = style.get('font-weight', 'normal')
        font_style = style.get('font-style', 'normal')

        cache_key = (font_family, font_size, font_weight, font_style)

        if cache_key not in self.font_cache:
            # Try to get system font that matches browser behavior
            bold = font_weight in ['bold', '700', '800', '900']
            italic = font_style == 'italic'

            try:
                # Try system font first (more accurate)
                font = pygame.font.SysFont(font_family, font_size, bold=bold, italic=italic)
            except:
                # Fallback to default font
                font = pygame.font.Font(None, font_size)

            # Calculate precise metrics
            metrics = self._calculate_font_metrics(font, font_size)

            self.font_cache[cache_key] = {
                'font': font,
                'metrics': metrics
            }

        return self.font_cache[cache_key]

    def _calculate_font_metrics(self, font: pygame.font.Font, font_size: int) -> Dict:
        """Calculate precise font metrics"""
        # Test character for metrics
        test_char = 'M'  # Em square reference

        ascent = font.get_ascent()
        descent = font.get_descent()
        line_height = ascent + descent

        # Calculate more precise metrics
        test_surface = font.render(test_char, True, (0, 0, 0))
        char_width = test_surface.get_width()
        char_height = test_surface.get_height()

        return {
            'ascent': ascent,
            'descent': descent,
            'line_height': line_height,
            'char_width': char_width,
            'char_height': char_height,
            'font_size': font_size,
            'em_ratio': char_width / font_size if font_size > 0 else 1.0
        }

    def _calculate_precise_text_position(self, text: str, font: pygame.font.Font,
                                         metrics: Dict, box, style: Dict[str, str]) -> Tuple[int, int]:
        """Calculate text position exactly like browsers do"""

        # Get text alignment
        text_align = style.get('text-align', 'left')

        # Get line height (crucial!)
        line_height_value = style.get('line-height', '1.2')
        if line_height_value.endswith('px'):
            line_height = float(line_height_value[:-2])
        else:
            try:
                multiplier = float(line_height_value)
                line_height = metrics['font_size'] * multiplier
            except:
                line_height = metrics['line_height']

        # Calculate text surface size
        text_surface = font.render(text, True, (0, 0, 0))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()

        # Calculate x position (horizontal alignment)
        padding_left = getattr(box, 'padding_left', 0)
        padding_right = getattr(box, 'padding_right', 0)
        available_width = box.width - padding_left - padding_right

        if text_align == 'left':
            x = box.x + padding_left
        elif text_align == 'center':
            x = box.x + padding_left + (available_width - text_width) / 2
        elif text_align == 'right':
            x = box.x + box.width - padding_right - text_width
        else:
            x = box.x + padding_left

        # Calculate y position (vertical alignment) - this is the tricky part!
        padding_top = getattr(box, 'padding_top', 0)
        padding_bottom = getattr(box, 'padding_bottom', 0)
        available_height = box.height - padding_top - padding_bottom

        # Browser-like vertical centering
        if available_height > line_height:
            # Center the line height in available space
            y_offset = (available_height - line_height) / 2
            y = box.y + padding_top + y_offset
        else:
            # Just use padding
            y = box.y + padding_top

        return (int(x), int(y))

    def _parse_font_size(self, font_size_str: str) -> int:
        """Parse font size with browser-like defaults"""
        if font_size_str.endswith('px'):
            return int(float(font_size_str[:-2]))
        elif font_size_str.endswith('em'):
            return int(float(font_size_str[:-2]) * 16)
        elif font_size_str.endswith('%'):
            return int(float(font_size_str[:-1]) / 100 * 16)
        else:
            # Named sizes
            named_sizes = {
                'xx-small': 9, 'x-small': 10, 'small': 13,
                'medium': 16, 'large': 18, 'x-large': 24, 'xx-large': 32
            }
            return named_sizes.get(font_size_str.lower(), 16)