from .markup_renderer import MarkupRenderer
from .enhanced_css_engine import EnhancedMarkupRenderer
from .ultra_enhanced_css_engine import UltraEnhancedMarkupRenderer
from .layout_debugger import LayoutDebugger

import pygame


class DebugRenderer(UltraEnhancedMarkupRenderer):
    """Renderer with built-in layout debugging"""

    def __init__(self):
        super().__init__()
        self.debugger = LayoutDebugger(self)
        self.debug_mode = False

    def toggle_debug(self):
        """Toggle debug overlay"""
        self.debug_mode = not self.debug_mode
        print("Debug mode is: {}".format(self.debug_mode))

    def render(self, surface: pygame.Surface, root_element, show_debug=None):
        """Render with optional debug overlay"""
        # Normal rendering
        super().render_element(root_element, surface)

        # Debug overlay if enabled
        if show_debug or self.debug_mode:
            self.debugger.render_debug_overlay(
                root_element, surface,
                show_boxes=True,
                show_text_metrics=True,
                show_computed_style=False
            )

    def render_with_debug(self, surface: pygame.Surface, root_element, show_debug=None):
        """Convenience method for conditional debug rendering"""
        # Normal rendering
        super().render_element(root_element, surface)

        # Debug overlay if requested
        if show_debug or self.debug_mode:
            self.debugger.render_debug_overlay(
                root_element, surface,
                show_boxes=True,
                show_text_metrics=True,
                show_computed_style=False
            )