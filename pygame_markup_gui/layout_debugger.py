import pygame

from pygame_markup_gui import HTMLElement


class LayoutDebugger:
    """Visual debugging tool for layout differences"""

    def __init__(self, renderer):
        self.renderer = renderer
        self.debug_colors = {
            'content': (0, 100, 255, 80),  # Blue
            'padding': (0, 255, 0, 60),  # Green
            'border': (255, 100, 0, 80),  # Orange
            'margin': (255, 0, 0, 40),  # Red
            'text_baseline': (255, 0, 255, 255)  # Magenta line
        }

    def render_debug_overlay(self, element: HTMLElement, surface: pygame.Surface,
                             show_boxes=True, show_text_metrics=True, show_computed_style=False):
        """Render debug overlay showing all layout calculations"""

        if not element.layout_box:
            return

        # Draw box model layers
        if show_boxes:
            self._draw_box_model(element, surface)

        # Draw text metrics
        if show_text_metrics and element.text_content.strip():
            self._draw_text_metrics(element, surface)

        # Show computed style info
        if show_computed_style:
            self._draw_style_info(element, surface)

        # Recursively debug children
        for child in element.children:
            self.render_debug_overlay(child, surface, show_boxes, show_text_metrics)

    def _draw_box_model(self, element: HTMLElement, surface: pygame.Surface):
        """Draw the CSS box model visually"""
        box = element.layout_box

        # Content box (blue)
        content_rect = (int(box.x), int(box.y), int(box.width), int(box.height))
        self._draw_debug_rect(surface, content_rect, self.debug_colors['content'])

        # Padding box (green)
        if hasattr(box, 'padding_left'):
            padding_rect = (
                int(box.x - box.padding_left),
                int(box.y - box.padding_top),
                int(box.width + box.padding_left + box.padding_right),
                int(box.height + box.padding_top + box.padding_bottom)
            )
            self._draw_debug_rect(surface, padding_rect, self.debug_colors['padding'])

        # Border box (orange)
        if hasattr(box, 'border_width') and box.border_width > 0:
            border_rect = (
                int(box.x - box.padding_left - box.border_width),
                int(box.y - box.padding_top - box.border_width),
                int(box.width + box.padding_left + box.padding_right + box.border_width * 2),
                int(box.height + box.padding_top + box.padding_bottom + box.border_width * 2)
            )
            self._draw_debug_rect(surface, border_rect, self.debug_colors['border'])

        # Margin box (red)
        if hasattr(box, 'margin_left'):
            margin_rect = (
                int(box.x - box.padding_left - box.border_width - box.margin_left),
                int(box.y - box.padding_top - box.border_width - box.margin_top),
                int(box.width + box.padding_left + box.padding_right + box.border_width * 2 + box.margin_left + box.margin_right),
                int(box.height + box.padding_top + box.padding_bottom + box.border_width * 2 + box.margin_top + box.margin_bottom)
            )
            self._draw_debug_rect(surface, margin_rect, self.debug_colors['margin'])

        # Element label
        font = pygame.font.Font(None, 16)
        label = f"{element.tag}#{element.attributes.get('id', '')}.{'.'.join(element.attributes.get('class', '').split())}"
        label_surface = font.render(label, True, (255, 255, 255))
        surface.blit(label_surface, (int(box.x), int(box.y - 20)))

    def _draw_text_metrics(self, element: HTMLElement, surface: pygame.Surface):
        """Draw text baseline and metrics"""
        if not element.text_content.strip():
            return

        style = element.computed_style
        box = element.layout_box

        # Get font metrics
        font = self.renderer.get_enhanced_font(style) if hasattr(self.renderer, '_get_enhanced_font') else None
        if not font:
            return

        # Calculate text baseline (this is often where issues are!)
        padding_top = getattr(box, 'padding_top', 0)
        text_y = box.y + padding_top

        # Draw baseline line
        baseline_y = text_y + font.get_ascent()
        pygame.draw.line(surface, self.debug_colors['text_baseline'],
                         (int(box.x), int(baseline_y)),
                         (int(box.x + box.width), int(baseline_y)), 2)

        # Show font metrics
        ascent = font.get_ascent()
        descent = font.get_descent()
        line_height = ascent + descent

        # Draw font boundary box
        font_rect = (int(box.x), int(text_y), int(box.width), int(line_height))
        pygame.draw.rect(surface, (255, 255, 0, 40), font_rect)

    def _draw_debug_rect(self, surface: pygame.Surface, rect: tuple, color: tuple):
        """Draw a debug rectangle with transparency"""
        debug_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        debug_surface.fill(color)
        surface.blit(debug_surface, (rect[0], rect[1]))

        # Draw border
        pygame.draw.rect(surface, color[:3], rect, 1)

    def _draw_style_info(self, element: HTMLElement, surface: pygame.Surface):
        """Draw computed style information"""
        box = element.layout_box
        font = pygame.font.Font(None, 14)

        # Show key computed values
        info_lines = [
            f"W: {box.width:.1f} H: {box.height:.1f}",
            f"X: {box.x:.1f} Y: {box.y:.1f}",
        ]

        if hasattr(box, 'margin_top'):
            info_lines.append(
                f"M: {box.margin_top:.1f},{box.margin_right:.1f},{box.margin_bottom:.1f},{box.margin_left:.1f}")
        if hasattr(box, 'padding_top'):
            info_lines.append(
                f"P: {box.padding_top:.1f},{box.padding_right:.1f},{box.padding_bottom:.1f},{box.padding_left:.1f}")

        # Render info box
        for i, line in enumerate(info_lines):
            text_surface = font.render(line, True, (255, 255, 255))
            bg_surface = pygame.Surface((text_surface.get_width() + 4, text_surface.get_height() + 2))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(180)

            y_offset = int(box.y + box.height + 5 + i * 16)
            surface.blit(bg_surface, (int(box.x), y_offset))
            surface.blit(text_surface, (int(box.x + 2), y_offset + 1))