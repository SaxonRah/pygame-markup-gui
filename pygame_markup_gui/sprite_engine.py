import pygame
import os
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass
from enum import Enum
from .html_engine import HTMLElement


class SpriteType(Enum):
    BACKGROUND = "background"
    CORNER = "corner"
    EDGE = "edge"
    ICON = "icon"


@dataclass
class SpriteConfig:
    """Configuration for sprite rendering"""
    sprite_type: SpriteType
    sprite_path: str
    tint_color: Optional[Tuple[int, int, int]] = None
    scale: float = 1.0
    rotation: float = 0.0
    alpha: int = 255


class SpriteManager:
    """Manages loading, caching, and transforming sprites"""

    def __init__(self, sprite_directory: str = "sprites"):
        self.sprite_directory = sprite_directory
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        self.tinted_cache: Dict[str, pygame.Surface] = {}

    def load_sprite(self, sprite_path: str) -> Optional[pygame.Surface]:
        """Load a sprite from file with caching"""
        if sprite_path in self.sprite_cache:
            return self.sprite_cache[sprite_path]

        full_path = os.path.join(self.sprite_directory, sprite_path)

        try:
            if os.path.exists(full_path):
                sprite = pygame.image.load(full_path).convert_alpha()
                self.sprite_cache[sprite_path] = sprite
                return sprite
            else:
                print(f"Sprite not found: {full_path}")
                return None
        except Exception as e:
            print(f"Error loading sprite {sprite_path}: {e}")
            return None

    def get_tinted_sprite(self, sprite_path: str, tint_color: Tuple[int, int, int],
                          alpha: int = 255) -> Optional[pygame.Surface]:
        """Get a tinted version of a sprite with caching"""
        cache_key = f"{sprite_path}_{tint_color}_{alpha}"

        if cache_key in self.tinted_cache:
            return self.tinted_cache[cache_key]

        original = self.load_sprite(sprite_path)
        if not original:
            return None

        # Create tinted version
        tinted = self._apply_tint(original, tint_color, alpha)
        self.tinted_cache[cache_key] = tinted
        return tinted

    @staticmethod
    def _apply_tint(surface: pygame.Surface, tint_color: Tuple[int, int, int],
                    alpha: int = 255) -> pygame.Surface:
        """Apply color tint to a surface"""
        # Method using BLEND modes (works well for white/grayscale sprites)
        tinted = surface.copy()

        # First zero out RGB values while preserving alpha
        tinted.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)

        # Add the new color
        tinted.fill(tint_color + (0,), None, pygame.BLEND_RGBA_ADD)

        # Apply alpha if different from 255
        if alpha != 255:
            alpha_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, alpha))
            tinted.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return tinted

    @staticmethod
    def get_rotated_sprite(sprite: pygame.Surface, rotation: float) -> pygame.Surface:
        """Get a rotated version of a sprite"""
        if rotation == 0:
            return sprite
        return pygame.transform.rotate(sprite, rotation)

    @staticmethod
    def get_scaled_sprite(sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """Get a scaled version of a sprite"""
        if scale == 1.0:
            return sprite

        new_width = int(sprite.get_width() * scale)
        new_height = int(sprite.get_height() * scale)

        # Use pygame.transform.scale for pixel art (no smoothing)
        return pygame.transform.scale(sprite, (new_width, new_height))


class CSSSprite:
    """Handles CSS sprite properties"""

    @staticmethod
    def parse_sprite_properties(element: HTMLElement) -> List[SpriteConfig]:
        """Parse CSS sprite properties from element"""
        sprites = []
        style = element.computed_style

        # Background sprite
        bg_sprite = style.get('background-sprite')
        if bg_sprite:
            config = CSSSprite._parse_sprite_config(bg_sprite, SpriteType.BACKGROUND, style)
            if config:
                sprites.append(config)

        # Corner sprites
        corner_sprite = style.get('corner-sprite')
        if corner_sprite:
            config = CSSSprite._parse_sprite_config(corner_sprite, SpriteType.CORNER, style)
            if config:
                sprites.append(config)

        # Edge sprites
        edge_sprite = style.get('edge-sprite')
        if edge_sprite:
            config = CSSSprite._parse_sprite_config(edge_sprite, SpriteType.EDGE, style)
            if config:
                sprites.append(config)

        # Icon sprite
        icon_sprite = style.get('icon-sprite')
        if icon_sprite:
            config = CSSSprite._parse_sprite_config(icon_sprite, SpriteType.ICON, style)
            if config:
                sprites.append(config)

        return sprites

    @staticmethod
    def _parse_sprite_config(sprite_value: str, sprite_type: SpriteType,
                             style: Dict[str, str]) -> Optional[SpriteConfig]:
        """Parse individual sprite configuration"""
        if not sprite_value or sprite_value == 'none':
            return None

        # Parse tint color from CSS
        tint_color = None
        sprite_tint = style.get('sprite-tint')
        if sprite_tint:
            tint_color = CSSSprite._parse_color(sprite_tint)

        # Parse other properties
        scale = CSSSprite._parse_float(style.get('sprite-scale', '1.0'))
        rotation = CSSSprite._parse_float(style.get('sprite-rotation', '0'))
        alpha = int(CSSSprite._parse_float(style.get('sprite-alpha', '255')))

        return SpriteConfig(
            sprite_type=sprite_type,
            sprite_path=sprite_value.strip(),
            tint_color=tint_color,
            scale=scale,
            rotation=rotation,
            alpha=alpha
        )

    @staticmethod
    def _parse_color(color_str: str) -> None | tuple[int, int, int] | tuple[int, ...] | Any:
        """Parse CSS color to RGB tuple"""
        if not color_str or color_str == 'transparent':
            return None

        try:
            # Handle hex colors
            if color_str.startswith('#'):
                if len(color_str) == 4:  # #RGB
                    r = int(color_str[1], 16) * 17
                    g = int(color_str[2], 16) * 17
                    b = int(color_str[3], 16) * 17
                    return r, g, b
                elif len(color_str) == 7:  # #RRGGBB
                    r = int(color_str[1:3], 16)
                    g = int(color_str[3:5], 16)
                    b = int(color_str[5:7], 16)
                    return r, g, b

            # Handle rgb() format
            elif color_str.startswith('rgb('):
                import re
                match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
                if match:
                    return tuple(int(x) for x in match.groups())

            # Handle named colors
            color_map = {
                'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
                'white': (255, 255, 255), 'black': (0, 0, 0), 'gray': (128, 128, 128),
                'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255),
                'orange': (255, 165, 0), 'purple': (128, 0, 128), 'brown': (165, 42, 42)
            }
            return color_map.get(color_str.lower())

        except Exception as e:
            print(f"Error parsing color '{color_str}': {e}")
            return None

    @staticmethod
    def _parse_float(value: str) -> float:
        """Parse float value with fallback"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0


class SpriteRenderer:
    """Renders sprites for HTML elements"""

    def __init__(self, sprite_manager: SpriteManager):
        self.sprite_manager = sprite_manager

    @staticmethod
    def get_sprite_configs(element: HTMLElement) -> List[SpriteConfig]:
        """Get all sprite configurations for an element"""
        return CSSSprite.parse_sprite_properties(element)

    def render_element_sprites(self, element: HTMLElement, target_surface: pygame.Surface):
        """Render all sprites for an element"""
        if not element.layout_box:
            return

        sprites = self.get_sprite_configs(element)

        for sprite_config in sprites:
            self._render_sprite(element, sprite_config, target_surface)

    def _render_sprite(self, element: HTMLElement, config: SpriteConfig,
                       target_surface: pygame.Surface):
        """Render a single sprite configuration"""
        if config.sprite_type == SpriteType.BACKGROUND:
            self.render_background_sprite(element, config, target_surface)
        elif config.sprite_type == SpriteType.CORNER:
            self.render_corner_sprites(element, config, target_surface)
        elif config.sprite_type == SpriteType.EDGE:
            self.render_edge_sprites(element, config, target_surface)
        elif config.sprite_type == SpriteType.ICON:
            self.render_icon_sprite(element, config, target_surface)

    def render_background_sprite(self, element: HTMLElement, config: SpriteConfig,
                                 target_surface: pygame.Surface):
        """Render a tiled background sprite"""
        box = element.layout_box

        # Load and prepare sprite
        sprite = self._get_processed_sprite(config)
        if not sprite:
            return

        # Tile the sprite across the element
        sprite_w, sprite_h = sprite.get_size()

        for y in range(int(box.y), int(box.y + box.height), sprite_h):
            for x in range(int(box.x), int(box.x + box.width), sprite_w):
                # Clip sprite to element bounds
                clip_rect = pygame.Rect(x, y, sprite_w, sprite_h)
                element_rect = pygame.Rect(box.x, box.y, box.width, box.height)
                clipped = clip_rect.clip(element_rect)

                if clipped.width > 0 and clipped.height > 0:
                    # Calculate source rect for clipping
                    src_x = clipped.x - x
                    src_y = clipped.y - y
                    src_rect = pygame.Rect(src_x, src_y, clipped.width, clipped.height)

                    try:
                        target_surface.blit(sprite, clipped, src_rect)
                    except:
                        pass  # Skip if out of bounds

    def render_corner_sprites(self, element: HTMLElement, config: SpriteConfig,
                              target_surface: pygame.Surface):
        """Render corner sprites at all 4 corners"""
        box = element.layout_box
        sprite = self._get_processed_sprite(config)
        if not sprite:
            return

        sprite_w, sprite_h = sprite.get_size()

        # Define corner positions and rotations
        corners = [
            (box.x, box.y, 0),  # Top-left
            (box.x + box.width - sprite_w, box.y, 270),  # Top-right
            (box.x + box.width - sprite_w, box.y + box.height - sprite_h, 180),  # Bottom-right
            (box.x, box.y + box.height - sprite_h, 90)  # Bottom-left
        ]

        for x, y, rotation in corners:
            rotated_sprite = self.sprite_manager.get_rotated_sprite(sprite, rotation)

            # Ensure position is within bounds
            # if (x >= 0 and y >= 0 and x < target_surface.get_width() and y < target_surface.get_height()):
            if 0 <= x < target_surface.get_width() and 0 <= y < target_surface.get_height():
                try:
                    target_surface.blit(rotated_sprite, (int(x), int(y)))
                except:
                    pass  # Skip if out of bounds

    def render_edge_sprites(self, element: HTMLElement, config: SpriteConfig,
                            target_surface: pygame.Surface):
        """Render edge sprites along all 4 edges"""
        box = element.layout_box
        sprite = self._get_processed_sprite(config)
        if not sprite:
            return

        sprite_w, sprite_h = sprite.get_size()

        # Top edge
        for x in range(int(box.x + sprite_w), int(box.x + box.width - sprite_w), sprite_w):
            try:
                target_surface.blit(sprite, (x, int(box.y)))
            except:
                pass

        # Bottom edge
        bottom_sprite = self.sprite_manager.get_rotated_sprite(sprite, 180)
        for x in range(int(box.x + sprite_w), int(box.x + box.width - sprite_w), sprite_w):
            try:
                target_surface.blit(bottom_sprite, (x, int(box.y + box.height - sprite_h)))
            except:
                pass

        # Left edge
        left_sprite = self.sprite_manager.get_rotated_sprite(sprite, 90)
        for y in range(int(box.y + sprite_h), int(box.y + box.height - sprite_h), sprite_h):
            try:
                target_surface.blit(left_sprite, (int(box.x), y))
            except:
                pass

        # Right edge
        right_sprite = self.sprite_manager.get_rotated_sprite(sprite, 270)
        for y in range(int(box.y + sprite_h), int(box.y + box.height - sprite_h), sprite_h):
            try:
                target_surface.blit(right_sprite, (int(box.x + box.width - sprite_w), y))
            except:
                pass

    def render_icon_sprite(self, element: HTMLElement, config: SpriteConfig,
                           target_surface: pygame.Surface):
        """Render a centered icon sprite"""
        box = element.layout_box
        sprite = self._get_processed_sprite(config)
        if not sprite:
            return

        sprite_w, sprite_h = sprite.get_size()

        # Center the sprite in the element
        x = box.x + (box.width - sprite_w) // 2
        y = box.y + (box.height - sprite_h) // 2

        try:
            target_surface.blit(sprite, (int(x), int(y)))
        except:
            pass  # Skip if out of bounds

    def _get_processed_sprite(self, config: SpriteConfig) -> Optional[pygame.Surface]:
        """Get a fully processed sprite (loaded, tinted, scaled, rotated)"""
        # Load base sprite
        if config.tint_color:
            sprite = self.sprite_manager.get_tinted_sprite(
                config.sprite_path, config.tint_color, config.alpha
            )
        else:
            sprite = self.sprite_manager.load_sprite(config.sprite_path)

        if not sprite:
            return None

        # Apply scaling
        if config.scale != 1.0:
            sprite = self.sprite_manager.get_scaled_sprite(sprite, config.scale)

        # Apply rotation (for non-corner/edge sprites)
        if config.rotation != 0:
            sprite = self.sprite_manager.get_rotated_sprite(sprite, config.rotation)

        return sprite


# Extension to CSS Engine to support sprite properties
class SpriteCSSEngine:
    """Extension to CSSEngine that supports sprite properties"""

    SPRITE_PROPERTIES = {
        'background-sprite', 'corner-sprite', 'edge-sprite', 'icon-sprite',
        'sprite-tint', 'sprite-scale', 'sprite-rotation', 'sprite-alpha'
    }

    @staticmethod
    def extend_css_engine(css_engine):
        """Add sprite property support to existing CSS engine"""
        # Store original compute_style method
        original_compute_style = css_engine.compute_style

        def enhanced_compute_style(element):
            # Get base computed style
            style = original_compute_style(element)

            # Add sprite-specific properties if they exist in rules
            for rule in css_engine.rules:
                if css_engine.selector_matches(rule.selector, element):
                    for prop, value in rule.declarations.items():
                        if prop in SpriteCSSEngine.SPRITE_PROPERTIES:
                            style[prop] = value

            return style

        # Replace the method
        css_engine.compute_style = enhanced_compute_style
