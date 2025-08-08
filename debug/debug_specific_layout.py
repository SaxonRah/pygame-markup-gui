import pygame
import sys

from pygame_markup_gui import HTMLParser
from pygame_markup_gui.browser_defaults import BrowserDefaults
from pygame_markup_gui.layout_debugger import LayoutDebugger
from pygame_markup_gui.precise_font_renderer import PreciseTextRenderer
from pygame_markup_gui.ultra_enhanced_css_engine import (
    UltraEnhancedMarkupRenderer, UltraEnhancedLayoutEngine, UltraEnhancedCSSEngine
)


def debug_specific_layout(html_content: str, css_content: str):
    """Debug specific layout issues with visual comparison"""

    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1400, 900))  # Wider to fit debug info
    pygame.display.set_caption("Layout Debug - ESC to quit")
    clock = pygame.time.Clock()

    # Your existing engines
    css_engine = UltraEnhancedCSSEngine()
    layout_engine = UltraEnhancedLayoutEngine()
    renderer = UltraEnhancedMarkupRenderer()

    # Add our debugging tools
    debugger = LayoutDebugger(renderer)
    text_renderer = PreciseTextRenderer()

    # Parse
    parser = HTMLParser()
    root_element = parser.parse(html_content)

    # Apply styles with browser defaults
    def apply_styles_with_browser_defaults(element):
        # Start with browser defaults
        browser_defaults = BrowserDefaults.get_default_style(element.tag)

        # Apply CSS rules
        css_styles = css_engine.compute_style(element)

        # Merge (CSS overrides defaults)
        element.computed_style = {**browser_defaults, **css_styles}

        for child in element.children:
            apply_styles_with_browser_defaults(child)

    css_engine.parse_css(css_content)
    apply_styles_with_browser_defaults(root_element)

    # Layout - FIX: Your layout is getting wrong container heights
    print("=== DEBUGGING LAYOUT ISSUES ===")
    print(f"Root element: {root_element.tag}")
    print(
        f"Body computed styles: {root_element.find_by_tag('body').computed_style if root_element.find_by_tag('body') else 'No body'}")

    layout_engine.layout(root_element, 1200, 800)

    # Create debug surface
    debug_surface = pygame.Surface((1200, 800), pygame.SRCALPHA)
    debug_surface.fill((40, 40, 40))  # Dark background to see elements

    # Render with debugging
    renderer.render_element(root_element, debug_surface)
    debugger.render_debug_overlay(root_element, debug_surface,
                                  show_boxes=True, show_text_metrics=True)

    # Display loop
    running = True
    show_debug = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                    print(f"Debug overlay: {'ON' if show_debug else 'OFF'}")

        # Clear screen
        screen.fill((20, 20, 20))

        # Render normal version
        normal_surface = pygame.Surface((1200, 800), pygame.SRCALPHA)
        normal_surface.fill((40, 40, 40))
        renderer.render_element(root_element, normal_surface)
        screen.blit(normal_surface, (0, 0))

        # Render debug overlay if enabled
        if show_debug:
            debug_overlay = pygame.Surface((1200, 800), pygame.SRCALPHA)
            debugger.render_debug_overlay(root_element, debug_overlay,
                                          show_boxes=True, show_text_metrics=True)
            screen.blit(debug_overlay, (0, 0))

        # Instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "ESC: Quit",
            "D: Toggle debug overlay",
            f"Debug: {'ON' if show_debug else 'OFF'}"
        ]

        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (1220, 20 + i * 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# But first, let's fix some obvious issues in your console output
def debug_layout_calculations():
    """Let's debug why your layouts are getting wrong sizes"""

    # Looking at your output, I see several problems:
    print("=== LAYOUT CALCULATION ISSUES ===")
    print("1. HTML element: 1200x30 (should be 1200x800)")
    print("2. Body element: 1200x30 (should fill HTML minus margin)")
    print("3. Flexbox not working: sidebar getting 1120px instead of 200px")
    print("4. Heights are too small across the board")
    print()

    # The core issues seem to be:
    print("SUSPECTED PROBLEMS:")
    print("A. Auto height calculation is broken - everything gets ~30px")
    print("B. Flexbox layout is not properly constraining widths")
    print("C. Container heights aren't propagating correctly")
    print("D. Parent/child relationship issues in height calculation")
    print()

    print("Let's check a simple element calculation:")

    # Create a minimal test
    css_engine = UltraEnhancedCSSEngine()
    layout_engine = UltraEnhancedLayoutEngine()

    # Add browser defaults to your CSS engine
    css_engine.default_styles.update({
        'html': {'display': 'block', 'margin': '0', 'padding': '0'},
        'body': {'display': 'block', 'margin': '8px', 'padding': '0', 'font-size': '16px'},
        'div': {'display': 'block', 'margin': '0', 'padding': '0'},
        'h1': {'display': 'block', 'font-size': '2em', 'margin': '0.67em 0', 'font-weight': 'bold'},
    })

    return css_engine, layout_engine


# First run the diagnostic
debug_layout_calculations()

# Test with your Interactive File Manager HTML
test_html = """
<html>
<body>
    <div class="container">
        <h1>Interactive File Manager</h1>
        <div class="toolbar">
            <button class="btn">New File</button>
            <button class="btn">Open</button>
            <button class="btn">Save</button>
        </div>
        <div class="content">
            <div class="sidebar">
                <h3>Quick Access</h3>
                <div class="item">Desktop</div>
                <div class="item">Documents</div>
                <div class="item">Downloads</div>
            </div>
            <div class="main">
                <h3>Projects</h3>
                <div class="file">readme.txt</div>
                <div class="file">notes.md</div>
                <div class="file">music.mp3</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

test_css = """
body { margin: 0; padding: 20px; background: #333; color: white; font-family: Arial; }
.container { background: #444; padding: 20px; }
.toolbar { margin-bottom: 20px; }
.btn { background: #007acc; color: white; border: none; padding: 8px 16px; margin-right: 10px; cursor: pointer; }
.content { display: flex; gap: 20px; }
.sidebar { flex: 0 0 200px; background: #555; padding: 15px; }
.main { flex: 1; background: #555; padding: 15px; }
.item, .file { padding: 5px 0; cursor: pointer; }
"""

if __name__ == "__main__":
    # Run debug
    debug_specific_layout(test_html, test_css)