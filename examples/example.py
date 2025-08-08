import pygame
import sys
from pygame_markup_gui import HTMLParser, CSSEngine, LayoutEngine, MarkupRenderer
from pygame_markup_gui.interactive_engine import InteractionManager, FormHandler, ScrollableContainer

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("HTML5/CSS Interactive Renderer")
    clock = pygame.time.Clock()

    # More complex HTML for testing interactions
    html = """
    <div class="app">
        <header class="header">
            <h1>Interactive File Manager</h1>
            <nav class="toolbar">
                <button id="new-btn" class="btn">New File</button>
                <button id="open-btn" class="btn">Open</button>
                <button id="save-btn" class="btn">Save</button>
            </nav>
        </header>

        <main class="main-content">
            <aside class="sidebar">
                <h3>Quick Access</h3>
                <button class="sidebar-btn">Desktop</button>
                <button class="sidebar-btn">Documents</button>
                <button class="sidebar-btn">Downloads</button>
            </aside>

            <section class="file-list">
                <div class="file-item" draggable="true">Projects</div>
                <div class="file-item" draggable="true">Images</div>
                <div class="file-item" draggable="true">readme.txt</div>
                <div class="file-item" draggable="true">notes.md</div>
                <div class="file-item" draggable="true">music.mp3</div>
            </section>
        </main>

        <footer class="status-bar">
            <span id="status">Ready</span>
        </footer>
    </div>
    """

    # Enhanced CSS with hover states
    css = """
    .app {
        width: 800px;
        height: 600px;
        background-color: #2b2b2b;
        display: flex;
        flex-direction: column;
        margin: 20px;
        border: 1px solid #555;
    }

    .header {
        background-color: #1e1e1e;
        padding: 10px;
        border-bottom: 1px solid #555;
    }

    h1 {
        color: white;
        font-size: 20px;
        margin: 0 0 10px 0;
    }

    .toolbar {
        display: flex;
    }

    .btn {
        background-color: #007acc;
        color: white;
        padding: 8px 16px;
        margin-right: 10px;
        border: 1px solid #005a9e;
        cursor: pointer;
    }

    .btn:hover {
        background-color: #0088ff;
    }

    .btn:active {
        background-color: #005580;
    }

    .main-content {
        display: flex;
        flex: 1;
    }

    .sidebar {
        width: 200px;
        background-color: #333;
        padding: 15px;
        border-right: 1px solid #555;
    }

    h3 {
        color: white;
        font-size: 16px;
        margin: 0 0 10px 0;
    }

    .sidebar-btn {
        display: block;
        width: 100%;
        background-color: #444;
        color: white;
        padding: 8px 12px;
        margin-bottom: 5px;
        border: 1px solid #555;
        text-align: left;
    }

    .file-list {
        flex: 1;
        padding: 15px;
        background-color: #2b2b2b;
    }

    .file-item {
        color: white;
        padding: 10px;
        margin-bottom: 8px;
        background-color: #444;
        border: 1px solid #555;
        cursor: pointer;
    }

    .file-item:hover {
        background-color: #505050;
    }

    .status-bar {
        background-color: #1a1a1a;
        padding: 5px 15px;
        border-top: 1px solid #555;
    }

    #status {
        color: #ccc;
        font-size: 12px;
    }
    """

    # Create engine instances
    parser = HTMLParser()
    css_engine = CSSEngine()
    layout_engine = LayoutEngine()
    renderer = MarkupRenderer()

    print("Parsing HTML...")
    root_element = parser.parse_fragment(html)

    print("Parsing CSS...")
    css_engine.parse_css(css)

    # Apply styles recursively
    def apply_styles_recursive(element):
        element.computed_style = css_engine.compute_style(element)
        for child in element.children:
            apply_styles_recursive(child)

    apply_styles_recursive(root_element)

    print("Calculating layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Setup enhanced interactions
    interaction_manager = InteractionManager(root_element)
    form_handler = FormHandler(interaction_manager)

    # Find and setup interactive elements
    def setup_interactions(element):
        # Setup buttons
        if element.tag == 'button':
            button_id = element.attributes.get('id', '')
            button_class = element.attributes.get('class', '')

            def make_button_handler(btn_element):
                def handler(button_event):
                    print(f"Button clicked: {btn_element.text_content}")
                    # Update status
                    status_element = find_element_by_id(root_element, 'status')
                    if status_element:
                        status_element.text_content = f"Clicked: {btn_element.text_content}"

                return handler

            form_handler.setup_button(element, make_button_handler(element))

        # Setup file items
        if 'file-item' in element.attributes.get('class', ''):
            def make_file_handler(file_element):
                def handler(file_event):
                    print(f"File selected: {file_element.text_content}")
                    status_element = find_element_by_id(root_element, 'status')
                    if status_element:
                        status_element.text_content = f"Selected: {file_element.text_content}"

                return handler

            interaction_manager.add_event_listener(element, 'click', make_file_handler(element))

            # Add drag handlers
            def drag_start_handler(drag_event):
                print(f"Started dragging: {element.text_content}")

            def drag_end_handler(drag_event):
                print(f"Stopped dragging: {element.text_content}")

            interaction_manager.add_event_listener(element, 'dragstart', drag_start_handler)
            interaction_manager.add_event_listener(element, 'dragend', drag_end_handler)

        # Recursively setup children
        for child in element.children:
            setup_interactions(child)

    def find_element_by_id(element, element_id):
        """Find element by ID"""
        if element.attributes.get('id') == element_id:
            return element
        for child in element.children:
            result = find_element_by_id(child, element_id)
            if result:
                return result
        return None

    setup_interactions(root_element)

    # Setup scrollable content
    file_list = None

    def find_file_list(element):
        nonlocal file_list
        if 'file-list' in element.attributes.get('class', ''):
            file_list = element
            return
        for child in element.children:
            find_file_list(child)

    find_file_list(root_element)
    if file_list:
        scrollable = ScrollableContainer(file_list, interaction_manager)

    # Add global event listeners for demonstration
    def global_key_handler(key_event):
        if key_event.key == pygame.K_F5:
            print("Refresh requested!")
        elif key_event.key == pygame.K_ESCAPE:
            print("Escape pressed!")

    interaction_manager.add_event_listener(root_element, 'keydown', global_key_handler)

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
                else:
                    # Let interaction manager handle it
                    if interaction_manager.handle_key_down(event.key, event.unicode):
                        need_render = True

            elif event.type == pygame.MOUSEMOTION:
                if interaction_manager.handle_mouse_motion(event.pos):
                    need_render = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if interaction_manager.handle_mouse_down(event.pos, event.button):
                    need_render = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if interaction_manager.handle_mouse_up(event.pos, event.button):
                    need_render = True

            elif event.type == pygame.MOUSEWHEEL:
                if interaction_manager.handle_mouse_wheel(event.y, pygame.mouse.get_pos()):
                    need_render = True

        # Only render when needed
        if need_render:
            # Clear screen
            screen.fill((40, 40, 40))

            # Draw debug info
            font = pygame.font.Font(None, 24)
            debug_text = font.render("Enhanced HTML Renderer - Tab to navigate, Click to interact", True,
                                     (255, 255, 255))
            screen.blit(debug_text, (10, 10))

            # Show current focus
            if interaction_manager.focused_element:
                focus_text = font.render(
                    f"Focused: {interaction_manager.focused_element.text_content or interaction_manager.focused_element.tag}",
                    True, (255, 255, 0))
                screen.blit(focus_text, (10, 35))

            # Render HTML to pygame
            try:
                renderer.render_element(root_element, screen)

                # Draw focus indicator
                if interaction_manager.focused_element and interaction_manager.focused_element.layout_box:
                    box = interaction_manager.focused_element.layout_box
                    focus_rect = pygame.Rect(int(box.x) - 2, int(box.y) - 2,
                                             int(box.width) + 4, int(box.height) + 4)
                    pygame.draw.rect(screen, (255, 165, 0), focus_rect, 2)

            except Exception as e:
                print(f"Render error: {e}")
                import traceback
                traceback.print_exc()

            need_render = False

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()