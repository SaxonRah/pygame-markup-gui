import pygame
from .html_engine import HTMLElement
from .markup_renderer import MarkupRenderer
from .sprite_engine import SpriteManager, SpriteRenderer


class PixelMarkupRenderer(MarkupRenderer):
    """Pixel art based renderer with sprite support"""

    def __init__(self, sprite_directory: str = "sprites"):
        super().__init__()
        self.sprite_manager = SpriteManager(sprite_directory)
        self.sprite_renderer = SpriteRenderer(self.sprite_manager)

    def render_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Render element with sprite support"""
        self._render_recursive_pixel_art(element, target_surface)

    def _render_recursive_pixel_art(self, element: HTMLElement, target_surface: pygame.Surface):
        """Enhanced recursive rendering with sprites"""
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

            # Render sprites first (background layer)
            self.sprite_renderer.render_element_sprites(element, target_surface)

            # Then render traditional CSS background (if no background sprite)
            has_bg_sprite = any(element.computed_style.get('background-sprite'))
            if not has_bg_sprite:
                self._render_background(elem_surface, element)

            # Render border (sprites or CSS)
            has_border_sprites = any([
                element.computed_style.get('corner-sprite'),
                element.computed_style.get('edge-sprite')
            ])
            if not has_border_sprites:
                self._render_border(elem_surface, element)

            # Render text content
            if element.text_content and element.text_content.strip():
                self._render_text(elem_surface, element)

            # Render icon sprite on top of text if specified
            icon_sprite = element.computed_style.get('icon-sprite')
            if icon_sprite:
                icon_config = next((config for config in self.sprite_renderer.get_sprite_configs(element)
                                    if config.sprite_type.value == 'icon'), None)
                if icon_config:
                    # Render icon on element surface
                    temp_element = type('temp', (), {
                        'layout_box': type('box', (), {'x': 0, 'y': 0, 'width': width, 'height': height})(),
                        'computed_style': element.computed_style
                    })()
                    self.sprite_renderer.render_icon_sprite(temp_element, icon_config, elem_surface)

            # Blit element to target surface with clipping
            self._blit_with_clipping(elem_surface, target_surface, x, y)

            # Store rendered surface
            element.pygame_surface = elem_surface

        except Exception as e:
            print(f"Error rendering {element.tag}: {e}")
            import traceback
            traceback.print_exc()

        # Render children recursively
        for child in element.children:
            self._render_recursive_pixel_art(child, target_surface)

    @staticmethod
    def _blit_with_clipping(elem_surface: pygame.Surface, target_surface: pygame.Surface,
                            x: int, y: int):
        """Blit with proper clipping"""
        width, height = elem_surface.get_size()

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