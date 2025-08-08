# main_ultra_renderer.py

import pygame
import sys
import os
import time
from typing import Dict, List, Optional

from pygame_markup_gui.debug_renderer import DebugRenderer
# Import all your engines
from pygame_markup_gui.html_engine import HTMLParser, HTMLElement
from pygame_markup_gui.ultra_enhanced_css_engine import (
    UltraEnhancedCSSEngine,
    UltraEnhancedLayoutEngine,
    UltraEnhancedMarkupRenderer
)

from pygame_markup_gui.interactive_engine import InteractionManager, FormHandler
from pygame_markup_gui.sprite_engine import SpriteCSSEngine


class UltraComprehensiveRenderer:
    """Complete application using your ultra-enhanced engines"""

    def __init__(self, width: int = 1400, height: int = 900):
        # Initialize pygame
        pygame.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Ultra Comprehensive HTML/CSS Renderer")

        # Initialize your engines
        self.html_parser = HTMLParser()
        self.css_engine = UltraEnhancedCSSEngine()
        self.layout_engine = UltraEnhancedLayoutEngine(width, height)
        # self.renderer = UltraEnhancedMarkupRenderer()
        self.renderer = DebugRenderer()

        # Extend CSS engine with sprite support
        SpriteCSSEngine.extend_css_engine(self.css_engine)

        # Document and interaction state
        self.root_element: Optional[HTMLElement] = None
        self.interaction_manager: Optional[InteractionManager] = None
        self.form_handler: Optional[FormHandler] = None

        # Rendering state
        self.needs_rerender = True
        self.scroll_offset_y = 0
        self.scroll_offset_x = 0
        self.max_scroll_y = 0
        self.max_scroll_x = 0

        # Performance tracking
        self.last_animation_update = time.time()
        self.frame_count = 0
        self.fps_timer = time.time()
        self.current_fps = 60

        # Create background gradient
        self.background_surface = self._create_background()

    def _create_background(self) -> pygame.Surface:
        """Create animated background gradient"""
        bg = pygame.Surface((self.width, self.height))

        # Create a shifting gradient background
        for y in range(self.height):
            ratio = y / self.height
            r = int(100 + 50 * ratio)
            g = int(120 + 30 * ratio)
            b = int(200 + 55 * ratio)
            pygame.draw.line(bg, (r, g, b), (0, y), (self.width, y))

        return bg

    def load_files(self, html_file: str, css_file: str) -> bool:
        """Load and parse HTML and CSS files"""
        try:
            # Load HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Load CSS
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()

            print(f"Loading {html_file} and {css_file}...")
            return self._process_content(html_content, css_content)

        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return False
        except Exception as e:
            print(f"Error loading files: {e}")
            return False

    def _process_content(self, html_content: str, css_content: str) -> bool:
        """Process HTML and CSS content through your engines"""
        try:
            # Parse HTML using your engine
            print("Parsing HTML...")
            self.root_element = self.html_parser.parse(html_content)

            if not self.root_element:
                print("Failed to parse HTML")
                return False

            print(f"Parsed HTML tree with root: {self.root_element.tag}")

            # Parse CSS using your ultra engine
            print("Parsing CSS...")
            self.css_engine.parse_css(css_content)
            print(f"Parsed {len(self.css_engine.rules)} CSS rules")

            # Apply computed styles recursively
            print("Computing styles...")
            self._apply_styles_recursive(self.root_element)

            # Setup interactions
            print("Setting up interactions...")
            self._setup_interactions()

            # Perform layout using your ultra engine
            print("Calculating layout...")
            self.layout_engine.layout(self.root_element, self.width, self.height)

            # Calculate scroll bounds
            self._calculate_scroll_bounds()

            print("Content processed successfully!")
            self.needs_rerender = True
            return True

        except Exception as e:
            print(f"Error processing content: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _apply_styles_recursive(self, element: HTMLElement):
        """Apply computed styles recursively using your ultra engine"""
        element.computed_style = self.css_engine.compute_style(element)

        for child in element.children:
            self._apply_styles_recursive(child)

    def _setup_interactions(self):
        """Setup interaction handling"""
        if not self.root_element:
            return

        self.interaction_manager = InteractionManager(self.root_element)
        self.form_handler = FormHandler(self.interaction_manager)

        # Find and setup interactive elements
        self._setup_interactive_elements_recursive(self.root_element)

    def _setup_interactive_elements_recursive(self, element: HTMLElement):
        """Setup interactive elements recursively"""
        if element.tag == 'button':
            self.form_handler.setup_button(
                element,
                lambda event: self._handle_button_click(element, event)
            )

        # Add hover effects for demo boxes
        if 'anim-box' in element.attributes.get('class', ''):
            self.interaction_manager.add_event_listener(
                element, 'mouseenter',
                lambda event: self._handle_demo_hover(element, True)
            )
            self.interaction_manager.add_event_listener(
                element, 'mouseleave',
                lambda event: self._handle_demo_hover(element, False)
            )

        for child in element.children:
            self._setup_interactive_elements_recursive(child)

    def _handle_button_click(self, button: HTMLElement, event):
        """Handle button clicks"""
        print(f"Button clicked: {button.text_content}")

        # Add click animation
        if button.computed_style:
            button.computed_style['animation'] = 'pulse 0.3s ease-out'
            self.needs_rerender = True

    def _handle_demo_hover(self, element: HTMLElement, hovered: bool):
        """Handle hover effects on demo elements"""
        if not element.computed_style:
            return

        if hovered:
            # Enhance the element on hover
            element.computed_style['transform'] = 'scale(1.1) translateY(-5px)'
            element.computed_style['box-shadow'] = '0 8px 25px rgba(0,0,0,0.3)'
        else:
            # Reset to normal
            element.computed_style.pop('transform', None)
            element.computed_style.pop('box-shadow', None)

        self.needs_rerender = True

    def _calculate_scroll_bounds(self):
        """Calculate maximum scroll bounds"""
        if not self.root_element or not self.root_element.layout_box:
            return

        # Find the bottom-most and right-most elements
        max_y = self._find_max_bounds_recursive(self.root_element, 'bottom')
        max_x = self._find_max_bounds_recursive(self.root_element, 'right')

        self.max_scroll_y = max(0, max_y - self.height + 100)  # Add some padding
        self.max_scroll_x = max(0, max_x - self.width + 100)

        print(f"Scroll bounds: x={self.max_scroll_x}, y={self.max_scroll_y}")

    def _find_max_bounds_recursive(self, element: HTMLElement, direction: str) -> float:
        """Find maximum bounds recursively"""
        if not element.layout_box:
            return 0

        box = element.layout_box
        if direction == 'bottom':
            current_max = box.y + box.height
        else:  # right
            current_max = box.x + box.width

        for child in element.children:
            child_max = self._find_max_bounds_recursive(child, direction)
            current_max = max(current_max, child_max)

        return current_max

    def handle_events(self) -> bool:
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_d:
                    self.renderer.toggle_debug()
                elif event.key == pygame.K_F5:
                    # Reload files
                    self._reload_files()
                elif event.key == pygame.K_UP:
                    self._scroll(0, 50)
                elif event.key == pygame.K_DOWN:
                    self._scroll(0, -50)
                elif event.key == pygame.K_LEFT:
                    self._scroll(50, 0)
                elif event.key == pygame.K_RIGHT:
                    self._scroll(-50, 0)

            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling
                self._scroll(0, event.y * 30)
                if self.interaction_manager:
                    self.interaction_manager.handle_mouse_wheel(event.y, pygame.mouse.get_pos())

            elif event.type == pygame.MOUSEMOTION:
                if self.interaction_manager:
                    # Adjust mouse position for scroll offset
                    adjusted_pos = (
                        event.pos[0] - self.scroll_offset_x,
                        event.pos[1] - self.scroll_offset_y
                    )
                    if self.interaction_manager.handle_mouse_motion(adjusted_pos):
                        self.needs_rerender = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.interaction_manager:
                    adjusted_pos = (
                        event.pos[0] - self.scroll_offset_x,
                        event.pos[1] - self.scroll_offset_y
                    )
                    if self.interaction_manager.handle_mouse_down(adjusted_pos, event.button):
                        self.needs_rerender = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.interaction_manager:
                    adjusted_pos = (
                        event.pos[0] - self.scroll_offset_x,
                        event.pos[1] - self.scroll_offset_y
                    )
                    if self.interaction_manager.handle_mouse_up(adjusted_pos, event.button):
                        self.needs_rerender = True

        return True

    def _scroll(self, delta_x: int, delta_y: int):
        """Handle scrolling"""
        old_x, old_y = self.scroll_offset_x, self.scroll_offset_y

        self.scroll_offset_x = max(0, min(self.max_scroll_x, self.scroll_offset_x + delta_x))
        self.scroll_offset_y = max(0, min(self.max_scroll_y, self.scroll_offset_y + delta_y))

        if old_x != self.scroll_offset_x or old_y != self.scroll_offset_y:
            self.needs_rerender = True

    def _reload_files(self):
        """Reload HTML and CSS files"""
        print("Reloading files...")
        if self.load_files('ultra_comprehensive.html', 'ultra_comprehensive.css'):
            print("Files reloaded successfully!")
        else:
            print("Failed to reload files")

    def update(self):
        """Update animations and dynamic content"""
        current_time = time.time()

        # Update animations using your ultra engine
        if self.css_engine and current_time - self.last_animation_update > 0.016:  # ~60fps
            updated_elements = self.css_engine.update_animations()

            if updated_elements:
                self.needs_rerender = True
                # Re-layout animated elements
                for element in updated_elements:
                    if element.layout_box:
                        # Trigger re-layout for animated properties that affect layout
                        animated_props = getattr(element.layout_box, 'animated_properties', {})
                        layout_props = ['width', 'height', 'margin', 'padding', 'transform']

                        if any(prop in animated_props for prop in layout_props):
                            # Re-layout this branch
                            self._relayout_element(element)

            self.last_animation_update = current_time

        # Update FPS counter
        self.frame_count += 1
        if current_time - self.fps_timer >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.fps_timer = current_time

    def _relayout_element(self, element: HTMLElement):
        """Re-layout a specific element and its children"""
        if element.parent and element.parent.layout_box:
            # Get available space from parent
            parent_box = element.parent.layout_box
            available_width = parent_box.width - parent_box.padding_left - parent_box.padding_right
            available_height = parent_box.height - parent_box.padding_top - parent_box.padding_bottom

            # Re-layout
            self.layout_engine.layout(
                element, available_width, available_height,
                is_root=False,
                parent_x=parent_box.x + parent_box.padding_left,
                parent_y=parent_box.y + parent_box.padding_top
            )

    def render(self):
        """Render everything using your ultra renderer"""
        if not self.needs_rerender or not self.root_element:
            return

        # Clear screen with animated background
        self.screen.blit(self.background_surface, (0, 0))

        # Create a surface for the scrollable content
        content_surface = pygame.Surface((
            self.width + abs(self.max_scroll_x),
            self.height + abs(self.max_scroll_y)
        ), pygame.SRCALPHA)

        # Render using your ultra-enhanced renderer
        try:
            self.renderer.render(content_surface, self.root_element)
        except Exception as e:
            print(f"Rendering error: {e}")
            import traceback
            traceback.print_exc()

        # Blit the scrolled portion to screen
        scroll_rect = pygame.Rect(
            self.scroll_offset_x, self.scroll_offset_y,
            self.width, self.height
        )

        self.screen.blit(content_surface, (0, 0), scroll_rect)

        # Draw UI overlay
        self._draw_ui_overlay()

        self.needs_rerender = False

    def _draw_ui_overlay(self):
        """Draw UI overlay with controls and info"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, self.height - 60))

        # Create font
        try:
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 18)
        except:
            font = pygame.font.SysFont('Arial', 24)
            small_font = pygame.font.SysFont('Arial', 18)

        # Info text
        info_text = f"FPS: {self.current_fps} | Scroll: {self.scroll_offset_x},{self.scroll_offset_y} | Elements: {self._count_elements()}"
        text_surface = small_font.render(info_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, self.height - 50))

        # Controls text
        controls_text = "Controls: Arrow Keys/Mouse Wheel=Scroll | F5=Reload | ESC=Exit"
        controls_surface = small_font.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (10, self.height - 25))

        # Scroll indicators
        if self.max_scroll_y > 0:
            # Vertical scroll bar
            scroll_height = max(20, (self.height * self.height) // (self.height + self.max_scroll_y))
            scroll_y = (self.scroll_offset_y * (self.height - scroll_height)) // max(1, self.max_scroll_y)

            pygame.draw.rect(self.screen, (100, 100, 100),
                             (self.width - 15, 0, 15, self.height - 60))
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (self.width - 15, scroll_y, 15, scroll_height))

    def _count_elements(self) -> int:
        """Count total elements in the tree"""
        if not self.root_element:
            return 0
        return self._count_elements_recursive(self.root_element)

    def _count_elements_recursive(self, element: HTMLElement) -> int:
        """Count elements recursively"""
        count = 1
        for child in element.children:
            count += self._count_elements_recursive(child)
        return count

    def run(self):
        """Main application loop"""
        clock = pygame.time.Clock()
        running = True

        print("\n" + "=" * 60)
        print("Ultra Comprehensive HTML/CSS Renderer")
        print("=" * 60)
        print("Loading ultra_comprehensive.html and ultra_comprehensive.css...")

        # Load the files
        if not self.load_files('ultra_comprehensive.html', 'ultra_comprehensive.css'):
            print("Failed to load files. Make sure ultra_comprehensive.html and ultra_comprehensive.css exist.")
            return

        print("\nRenderer started successfully!")
        print("\nControls:")
        print("- Arrow Keys or Mouse Wheel: Scroll")
        print("- F5: Reload files")
        print("- ESC: Exit")
        print("- Hover over elements to see interactions")
        print("\nRendering with all your ultra-enhanced features:")
        print("* CSS Grid and Flexbox layouts")
        print("* CSS Animations and Transitions")
        print("* Advanced Typography and Text Effects")
        print("* Visual Filters and Clip Paths")
        print("* Interactive Elements with Event Handling")
        print("* Transform Support (rotate, scale, skew)")
        print("* Backdrop Filters and Blend Modes")
        print("* Performance Optimizations")
        print("-" * 60)

        while running:
            # Handle events
            running = self.handle_events()

            # Update animations and interactions
            self.update()

            # Render
            self.render()

            # Update display
            pygame.display.flip()

            # Control frame rate
            clock.tick(60)

        pygame.quit()


def main():
    """Main entry point"""
    print("Initializing Ultra Comprehensive HTML/CSS Renderer...")

    # Check if files exist
    if not os.path.exists('ultra_comprehensive.html'):
        print("Error: ultra_comprehensive.html not found!")
        print("Please make sure the file exists in the current directory.")
        return

    if not os.path.exists('ultra_comprehensive.css'):
        print("Error: ultra_comprehensive.css not found!")
        print("Please make sure the file exists in the current directory.")
        return

    # Create and run the renderer
    try:
        renderer = UltraComprehensiveRenderer(1400, 900)
        renderer.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()