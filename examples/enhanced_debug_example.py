# enhanced_example_debug.py

import pygame
import sys

from pygame_markup_gui.debug_renderer import DebugRenderer
from pygame_markup_gui.html_engine import HTMLParser
from pygame_markup_gui.enhanced_css_engine import (
    EnhancedCSSEngine,
    EnhancedLayoutEngine,
    EnhancedMarkupRenderer
)
from pygame_markup_gui.unified_layout_engine import UnifiedLayoutEngine

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000


def draw_debug_info(screen, root_element):
    """Draw debug information on screen"""
    font = pygame.font.Font(None, 20)

    def draw_element_bounds(element, color=(255, 0, 0), depth=0):
        if not element.layout_box:
            return

        box = element.layout_box

        # Draw element boundary
        pygame.draw.rect(screen, color,
                         (box.x, box.y, box.width, box.height), 1)

        # Draw element info
        info_text = f"{element.tag} ({box.width:.0f}x{box.height:.0f})"
        text_surface = font.render(info_text, True, color)
        screen.blit(text_surface, (box.x + 2, box.y + 2))

        # Recursively draw children with different colors
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        for child in element.children:
            draw_element_bounds(child, colors[depth % len(colors)], depth + 1)

    draw_element_bounds(root_element)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enhanced CSS Engine - Layout Debug")
    clock = pygame.time.Clock()

    # Simplified HTML to debug layout issues step by step
    html = """
    <div class="debug-app">
        <!-- Simple Header Test -->
        <header class="debug-header">
            <h1 class="debug-title">Enhanced CSS Debug</h1>
            <div class="debug-nav">
                <button class="debug-btn">Button 1</button>
                <button class="debug-btn">Button 2</button>
                <button class="debug-btn">Button 3</button>
            </div>
        </header>

        <!-- Simple Grid Test -->
        <main class="debug-main">
            <section class="debug-section">
                <h2>Flexbox Test Section</h2>
                <div class="debug-flex-container">
                    <div class="debug-flex-item">Item 1</div>
                    <div class="debug-flex-item">Item 2</div>
                    <div class="debug-flex-item">Item 3</div>
                </div>
            </section>

            <section class="debug-section">
                <h2>Grid Test Section</h2>
                <div class="debug-grid-container">
                    <div class="debug-grid-item">Grid A</div>
                    <div class="debug-grid-item">Grid B</div>
                    <div class="debug-grid-item">Grid C</div>
                    <div class="debug-grid-item">Grid D</div>
                </div>
            </section>

            <section class="debug-section">
                <h2>Transform Test Section</h2>
                <div class="debug-transform-container">
                    <div class="debug-transform-item scale-test">Scale</div>
                    <div class="debug-transform-item rotate-test">Rotate</div>
                    <div class="debug-transform-item translate-test">Translate</div>
                </div>
            </section>

            <section class="debug-section">
                <h2>Position Test Section</h2>
                <div class="debug-position-container">
                    <div class="debug-position-relative">
                        Relative
                        <div class="debug-position-absolute">Absolute</div>
                    </div>
                    <div class="debug-position-static">Static</div>
                </div>
            </section>
        </main>

        <!-- Simple Sidebar Test -->
        <aside class="debug-sidebar">
            <h3>Debug Sidebar</h3>
            <div class="debug-sidebar-content">
                <div class="debug-feature">Feature 1</div>
                <div class="debug-feature">Feature 2</div>
                <div class="debug-feature">Feature 3</div>
            </div>
        </aside>

        <!-- Simple Footer Test -->
        <footer class="debug-footer">
            <p>Debug Footer Content</p>
        </footer>
    </div>
    """

    # Simplified CSS focusing on core layout functionality
    css = """
    /* Root Grid Layout - Basic Test */
    .debug-app {
        display: grid;
        grid-template-columns: 1fr 250px;
        grid-template-rows: 80px 1fr 50px;
        grid-template-areas:
            "header sidebar"
            "main sidebar"
            "footer footer";
        width: 100%;
        height: 100vh;
        gap: 10px;
        padding: 10px;
        background-color: #f0f0f0;
        font-family: Arial, sans-serif;
    }

    /* Header Flexbox Test */
    .debug-header {
        grid-area: header;
        background-color: #4a90e2;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .debug-title {
        font-size: 24px;
        margin: 0;
    }

    .debug-nav {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .debug-btn {
        padding: 8px 16px;
        background-color: #357abd;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }

    .debug-btn:hover {
        background-color: #2968a3;
    }

    /* Main Content Grid */
    .debug-main {
        grid-area: main;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 15px;
        padding: 10px;
        background-color: white;
        border-radius: 5px;
        overflow-y: auto;
    }

    .debug-section {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
    }

    .debug-section h2 {
        margin-top: 0;
        margin-bottom: 15px;
        color: #495057;
        font-size: 18px;
        border-bottom: 2px solid #007bff;
        padding-bottom: 5px;
    }

    /* Flexbox Test */
    .debug-flex-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
    }

    .debug-flex-item {
        background-color: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
        flex: 1;
    }

    /* Grid Test */
    .debug-grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
        gap: 8px;
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        height: 120px;
    }

    .debug-grid-item {
        background-color: #28a745;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        font-weight: bold;
    }

    /* Transform Test */
    .debug-transform-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        height: 100px;
    }

    .debug-transform-item {
        background-color: #dc3545;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
    }

    .scale-test {
        transform: scale(1.2);
    }

    .rotate-test {
        transform: rotate(15deg);
    }

    .translate-test {
        transform: translate(10px, -5px);
    }

    /* Position Test */
    .debug-position-container {
        position: relative;
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        height: 100px;
    }

    .debug-position-relative {
        position: relative;
        background-color: #ffc107;
        padding: 10px;
        border-radius: 4px;
        top: 10px;
        left: 10px;
        display: inline-block;
    }

    .debug-position-absolute {
        position: absolute;
        background-color: #6f42c1;
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        top: 5px;
        right: 5px;
        font-size: 12px;
    }

    .debug-position-static {
        position: static;
        background-color: #20c997;
        color: white;
        padding: 10px;
        border-radius: 4px;
        display: inline-block;
        margin-left: 20px;
    }

    /* Sidebar Test */
    .debug-sidebar {
        grid-area: sidebar;
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid #dee2e6;
    }

    .debug-sidebar h3 {
        margin-top: 0;
        margin-bottom: 15px;
        color: #495057;
        border-bottom: 2px solid #6c757d;
        padding-bottom: 5px;
    }

    .debug-sidebar-content {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .debug-feature {
        background-color: #6c757d;
        color: white;
        padding: 10px;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
    }

    .debug-feature:nth-child(1) { background-color: #007bff; }
    .debug-feature:nth-child(2) { background-color: #28a745; }
    .debug-feature:nth-child(3) { background-color: #dc3545; }

    /* Footer Test */
    .debug-footer {
        grid-area: footer;
        background-color: #6c757d;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .debug-footer p {
        margin: 0;
        font-weight: bold;
    }

    /* Debug Borders - Optional */
    .debug-section {
        border: 2px dashed #007bff;
    }

    .debug-flex-container {
        border: 1px solid #007bff;
    }

    .debug-grid-container {
        border: 1px solid #28a745;
    }

    .debug-transform-container {
        border: 1px solid #dc3545;
    }

    .debug-position-container {
        border: 1px solid #ffc107;
    }
    """

    # Create enhanced engine instances
    parser = HTMLParser()
    css_engine = EnhancedCSSEngine()
    # layout_engine = EnhancedLayoutEngine()
    layout_engine = UnifiedLayoutEngine(enable_debug=True)
    # renderer = EnhancedMarkupRenderer()
    renderer = DebugRenderer()

    print("=== ENHANCED CSS ENGINE - LAYOUT DEBUG ===")
    print("Testing core layout functionality step by step...")

    print("\nParsing HTML...")
    root_element = parser.parse_fragment(html)

    print("Parsing CSS...")
    css_engine.parse_css(css)

    def apply_styles_recursive(element):
        element.computed_style = css_engine.compute_style(element)
        print(f"Applied styles to {element.tag}: {element.computed_style.get('display', 'block')}")
        for child in element.children:
            apply_styles_recursive(child)

    print("Applying styles...")
    apply_styles_recursive(root_element)

    print("Calculating layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Debug layout information
    def print_layout_debug(element, indent=0):
        if element.layout_box:
            prefix = "  " * indent
            print(f"{prefix}{element.tag}: pos=({element.layout_box.x:.1f}, {element.layout_box.y:.1f}) "
                  f"size=({element.layout_box.width:.1f} x {element.layout_box.height:.1f}) "
                  f"display={element.computed_style.get('display', 'block')}")
        for child in element.children:
            print_layout_debug(child, indent + 1)

    print("\nLayout Debug Information:")
    print_layout_debug(root_element)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    renderer.toggle_debug()

        # Clear screen
        screen.fill((60, 70, 80))

        # Debug info
        font = pygame.font.Font(None, 24)
        debug_text = font.render("Enhanced CSS Layout Debug - Check Console for Layout Info", True, (255, 255, 255))
        screen.blit(debug_text, (10, 10))

        # Render elements
        try:
            renderer.render(screen, root_element)

            # Draw debug boundaries
            if root_element.layout_box:
                pygame.draw.rect(screen, (255, 0, 0),
                                 (root_element.layout_box.x, root_element.layout_box.y,
                                  root_element.layout_box.width, root_element.layout_box.height), 2)

        except Exception as e:
            print(f"Render error: {e}")
            import traceback
            traceback.print_exc()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()