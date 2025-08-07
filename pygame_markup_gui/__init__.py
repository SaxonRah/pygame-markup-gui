"""
pygame_markup_gui - A pygame-based HTML5/CSS3 rendering engine

This package provides HTML parsing, CSS styling, layout calculation, and rendering
capabilities for pygame applications, with support for sprites, interactivity, and animations.
"""

__version__ = "0.1.0"
__author__ = "Robert Valentine"

# Core HTML/CSS engines
from .html_engine import HTMLParser, HTMLElement, LayoutBox
from .css_engine import CSSEngine, CSSRule
from .layout_engine import LayoutEngine

# Renderers
from .markup_renderer import (MarkupRenderer)
from .pixel_markup_renderer import PixelMarkupRenderer

# Sprite system
from .sprite_engine import (
    SpriteManager,
    SpriteRenderer,
    SpriteCSSEngine,
    SpriteType,
    SpriteConfig,
    CSSSprite
)

# Interactive system
from .interactive_engine import (
    InteractionManager,
    FormHandler,
    ScrollableContainer,
    InteractiveEvent,
    EventPhase,
    ElementState,
    AccessibilityHelper
)


# Convenience functions for quick setup
def create_simple_renderer(sprite_directory="sprites"):
    """
    Create a basic HTML/CSS renderer with all components.

    Args:
        sprite_directory: Directory containing sprite assets

    Returns:
        tuple: (parser, css_engine, layout_engine, renderer)
    """
    parser = HTMLParser()
    css_engine = CSSEngine()
    layout_engine = LayoutEngine()
    renderer = MarkupRenderer()

    return parser, css_engine, layout_engine, renderer


def create_enhanced_renderer(sprite_directory="sprites"):
    """
    Create an enhanced HTML/CSS renderer with sprite support.

    Args:
        sprite_directory: Directory containing sprite assets

    Returns:
        tuple: (parser, css_engine, layout_engine, renderer)
    """
    parser = HTMLParser()
    css_engine = CSSEngine()
    layout_engine = LayoutEngine()
    renderer = PixelMarkupRenderer(sprite_directory)

    # Extend CSS engine with sprite support
    SpriteCSSEngine.extend_css_engine(css_engine)

    return parser, css_engine, layout_engine, renderer


def create_interactive_renderer(sprite_directory="sprites", viewport_width=1200, viewport_height=800):
    """
    Create a full-featured interactive HTML/CSS renderer.

    Args:
        sprite_directory: Directory containing sprite assets
        viewport_width: Viewport width in pixels
        viewport_height: Viewport height in pixels

    Returns:
        tuple: (parser, css_engine, layout_engine, renderer, interaction_manager)
    """
    parser = HTMLParser()
    css_engine = CSSEngine()
    layout_engine = LayoutEngine(viewport_width, viewport_height)
    renderer = PixelMarkupRenderer(sprite_directory)

    # Extend CSS engine with sprite support
    SpriteCSSEngine.extend_css_engine(css_engine)

    # Note: interaction_manager needs to be created after parsing HTML
    # since it requires a root element

    return parser, css_engine, layout_engine, renderer


def render_html_to_pygame(html, css, surface, sprite_directory="sprites"):
    """
    Convenience function to render HTML/CSS directly to a pygame surface.

    Args:
        html: HTML string to render
        css: CSS string for styling
        surface: Target pygame surface
        sprite_directory: Directory containing sprite assets

    Returns:
        HTMLElement: Root element for further manipulation
    """
    # Create components
    parser, css_engine, layout_engine, renderer = create_enhanced_renderer(sprite_directory)

    # Parse and style
    root_element = parser.parse_fragment(html)
    css_engine.parse_css(css)

    # Apply styles recursively
    def apply_styles_recursive(element):
        element.computed_style = css_engine.compute_style(element)
        for child in element.children:
            apply_styles_recursive(child)

    apply_styles_recursive(root_element)

    # Layout and render
    layout_engine.layout(root_element, surface.get_width(), surface.get_height())
    renderer.render_element(root_element, surface)

    return root_element


# Export main classes for easy access
__all__ = [
    # Core engines
    'HTMLParser', 'HTMLElement', 'LayoutBox',
    'CSSEngine', 'CSSRule',
    'LayoutEngine',

    # Renderers
    'MarkupRenderer',
    'PixelMarkupRenderer',

    # Sprite system
    'SpriteManager', 'SpriteRenderer', 'SpriteCSSEngine',
    'SpriteType', 'SpriteConfig', 'CSSSprite',

    # Interactive system
    'InteractionManager', 'FormHandler', 'ScrollableContainer',
    'InteractiveEvent', 'EventPhase', 'ElementState', 'AccessibilityHelper',

    # Convenience functions
    'create_simple_renderer',
    'create_enhanced_renderer',
    'create_interactive_renderer',
    'render_html_to_pygame'
]

# Package metadata
__title__ = "pygame_markup_gui"
__description__ = "HTML5/CSS3 rendering engine for pygame"
__url__ = "https://github.com/SaxonRah/pygame_markup_gui"
__license__ = "MIT"
