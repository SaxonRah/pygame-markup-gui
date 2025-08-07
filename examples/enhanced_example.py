import pygame
import sys
from pygame_markup_gui.html_engine import HTMLParser
from pygame_markup_gui.css_engine import CSSEngine
from pygame_markup_gui.layout_engine import LayoutEngine
from pygame_markup_gui.pixel_markup_renderer import PixelMarkupRenderer
from pygame_markup_gui.sprite_engine import SpriteCSSEngine

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("HTML5/CSS Sprite Renderer")
    clock = pygame.time.Clock()

    # HTML with sprite-enabled elements
    html = """
    <div class="game-ui">
        <div class="window">
            <h1 class="title">Pixel Art UI</h1>
            <div class="button-container">
                <button class="pixel-btn">Start Game</button>
                <button class="pixel-btn">Options</button>
                <button class="pixel-btn">Quit</button>
            </div>
        </div>
        <div class="inventory">
            <div class="slot"></div>
            <div class="slot"></div>
            <div class="slot"></div>
        </div>
    </div>
    """

    # CSS with sprite properties
    css = """
    .game-ui {
        width: 800px;
        height: 600px;
        padding: 20px;
        background-sprite: texture_bg.png;
        sprite-tint: #4a4a4a;
    }

    .window {
        width: 400px;
        height: 300px;
        padding: 20px;
        margin: 50px;
        background-color: #2a2a2a;
        corner-sprite: ui_corner.png;
        edge-sprite: ui_edge.png;
        sprite-tint: #6666aa;
    }

    .title {
        color: white;
        text-align: center;
        margin-bottom: 20px;
        icon-sprite: crown.png;
        sprite-tint: gold;
    }

    .button-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .pixel-btn {
        padding: 12px 24px;
        color: white;
        background-color: transparent;
        corner-sprite: btn_corner.png;
        edge-sprite: btn_edge.png;
        sprite-tint: #4488ff;
        margin-bottom: 8px;
    }

    .pixel-btn:hover {
        sprite-tint: #66aaff;
    }

    .pixel-btn:active {
        sprite-tint: #2266cc;
    }

    .inventory {
        position: absolute;
        right: 50px;
        top: 50px;
        display: flex;
        gap: 5px;
    }

    .slot {
        width: 64px;
        height: 64px;
        background-sprite: slot_bg.png;
        corner-sprite: slot_corner.png;
        sprite-tint: #888888;
    }

    .slot:hover {
        sprite-tint: #aaaaaa;
    }
    """

    # Create engine instances
    parser = HTMLParser()
    css_engine = CSSEngine()
    layout_engine = LayoutEngine()

    # Enhanced renderer with sprite support
    renderer = PixelMarkupRenderer(sprite_directory="assets/sprites")

    print("Parsing HTML...")
    root_element = parser.parse_fragment(html)

    print("Parsing CSS...")
    css_engine.parse_css(css)

    # Extend CSS engine with sprite support
    SpriteCSSEngine.extend_css_engine(css_engine)

    # Apply styles recursively
    def apply_styles_recursive(element):
        element.computed_style = css_engine.compute_style(element)
        for child in element.children:
            apply_styles_recursive(child)

    apply_styles_recursive(root_element)

    print("Calculating layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Main loop
    running = True
    need_render = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if need_render:
            # Clear screen
            screen.fill((30, 30, 40))

            # Draw info
            font = pygame.font.Font(None, 24)
            info_text = font.render("Enhanced Sprite Renderer - Pixel Art UI", True, (255, 255, 255))
            screen.blit(info_text, (10, 10))

            # Render HTML with sprites
            try:
                renderer.render_element(root_element, screen)
            except Exception as e:
                print(f"Render error: {e}")
                import traceback
                traceback.print_exc()

            need_render = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()