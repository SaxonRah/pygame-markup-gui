<p align="center">
  <img src="https://github.com/SaxonRah/pygame-markup-gui/blob/main/images/pygame_markup_gui.png?raw=true" alt="PyGame Markup GUI"/>
</p>

# NOTE: THIS IS NOT WORKING AS INTENDED
Below are screenshots of the PyGame Rendering next to actual rendered HTML/CSS.
<p align="center">
  <img src="https://github.com/SaxonRah/pygame-markup-gui/blob/main/images/basic.png?raw=true" alt="Basic"/>
</p>
<p align="center">
  <img src="https://github.com/SaxonRah/pygame-markup-gui/blob/main/images/debug_enhanced.png?raw=true" alt="Debug Enhanced"/>
</p>
<p align="center">
  <img src="https://github.com/SaxonRah/pygame-markup-gui/blob/main/images/enhanced.png?raw=true" alt="Enhanced"/>
</p>
<p align="center">
  <img src="https://github.com/SaxonRah/pygame-markup-gui/blob/main/images/ultra.png?raw=true" alt="Ultra"/>
</p>

### As you can see, it's not laying out various things correctly.

---

# PyGame Markup GUI - [Version 0.1.0]

A pygame-based HTML5/CSS3 rendering engine that allows you to create interactive user interfaces using familiar web technologies while leveraging pygame's performance and game development features.

## Features

- **HTML5 Parsing**: Parse HTML documents and fragments using html5lib
- **CSS Styling**: Complete CSS engine with selector matching, specificity, and cascading
- **Layout Engine**: CSS-compliant layout with support for block, inline-block, and flexbox
- **Interactive Elements**: Full event handling for mouse, keyboard, focus, and drag-and-drop
- **Sprite Support**: Enhanced pixel art rendering with sprite-based UI elements
- **Responsive Design**: Automatic layout calculation and reflow
- **Accessibility**: Tab navigation, focus management, and screen reader support

## Installation

### Requirements

```
pygame-ce >= 2.0.0
html5lib >= 1.1
tinycss2 >= 1.2.0
```

### Install Dependencies

```bash
pip install pygame-ce html5lib tinycss2
```

## Quick Start

### Basic HTML/CSS Rendering

```python
import pygame
from pygame_markup_gui import HTMLParser, CSSEngine, LayoutEngine, MarkupRenderer

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))

# HTML content
html = """
<div class="container">
    <h1>Hello World</h1>
    <button class="btn">Click Me</button>
</div>
"""

# CSS styling
css = """
.container {
    padding: 20px;
    background-color: #f0f0f0;
}

h1 {
    color: #333;
    text-align: center;
}

.btn {
    background-color: #007acc;
    color: white;
    padding: 10px 20px;
    border: none;
}
"""

# Create engines
parser = HTMLParser()
css_engine = CSSEngine()
layout_engine = LayoutEngine()
renderer = MarkupRenderer()

# Parse and render
root_element = parser.parse_fragment(html)
css_engine.parse_css(css)

# Apply styles
def apply_styles(element):
    element.computed_style = css_engine.compute_style(element)
    for child in element.children:
        apply_styles(child)

apply_styles(root_element)
layout_engine.layout(root_element, 800, 600)

# Render to screen
renderer.render_element(root_element, screen)
pygame.display.flip()
```

### Interactive Elements

```python
from pygame_markup_gui.interactive_engine import InteractionManager, FormHandler

# Setup interaction manager
interaction_manager = InteractionManager(root_element)
form_handler = FormHandler(interaction_manager)

# Add button click handler
button_element = root_element.find_by_tag('button')
def on_button_click(event):
    print("Button clicked!")

interaction_manager.add_event_listener(button_element, 'click', on_button_click)

# Handle pygame events
for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:
        interaction_manager.handle_mouse_down(event.pos, event.button)
    elif event.type == pygame.KEYDOWN:
        interaction_manager.handle_key_down(event.key, event.unicode)
```

### Sprite-Based Pixel Art UI

```python
from pygame_markup_gui.pixel_markup_renderer import PixelMarkupRenderer
from pygame_markup_gui.sprite_engine import SpriteCSSEngine

# Enhanced CSS with sprite properties
css = """
.window {
    corner-sprite: ui_corner.png;
    edge-sprite: ui_edge.png;
    sprite-tint: #6666aa;
}

.button {
    background-sprite: button_bg.png;
    icon-sprite: sword.png;
    sprite-scale: 2.0;
}
"""

# Use pixel art renderer
renderer = PixelMarkupRenderer(sprite_directory="assets/sprites")
SpriteCSSEngine.extend_css_engine(css_engine)
```

## Core Components

### HTML Engine (`html_engine.py`)

Parses HTML5 documents into a tree structure compatible with the rendering pipeline.

- Uses html5lib for standards-compliant parsing
- Wraps elements with pygame-specific properties
- Supports both full documents and fragments

### CSS Engine (`css_engine.py`)

Implements CSS parsing, selector matching, and style computation.

- CSS specificity calculation
- Cascading and inheritance
- Default browser styles
- Inline style support

### Layout Engine (`layout_engine.py`)

Calculates element positioning and sizing using CSS layout algorithms.

- Block and inline-block layout
- Flexbox support (row and column)
- Box model calculation (margin, padding, border)
- Automatic height calculation

### Interactive Engine (`interactive_engine.py`)

Provides comprehensive event handling and user interaction.

- Mouse events (click, hover, drag)
- Keyboard events and focus management
- Event bubbling and capturing
- Tab navigation
- Drag and drop support

### Rendering Engines

**MarkupRenderer** (`markup_renderer.py`):
- Basic HTML/CSS rendering

**PixelMarkupRenderer** (`pixel_markup_renderer.py`):
- Enhanced sprite-based rendering

### Sprite Engine (`sprite_engine.py`)

Advanced sprite system for pixel art and game UIs.

- Sprite loading and caching
- Color tinting and transformations
- CSS integration with custom properties
- Background, corner, edge, and icon sprites

## CSS Properties

### Standard CSS Properties

- `width`, `height`
- `margin`, `padding`
- `background-color`, `color`
- `border`, `border-width`, `border-color`
- `display` (block, inline-block, flex)
- `flex-direction`
- `font-size`, `font-weight`, `font-family`

### Sprite Properties

- `background-sprite`: Tiled background image
- `corner-sprite`: Corner decorations
- `edge-sprite`: Edge/border decorations
- `icon-sprite`: Centered icon
- `sprite-tint`: Color tinting
- `sprite-scale`: Size scaling
- `sprite-rotation`: Rotation angle
- `sprite-alpha`: Transparency

## Event System

The event system follows DOM-like patterns:

```python
# Add event listeners
interaction_manager.add_event_listener(element, 'click', handler)
interaction_manager.add_event_listener(element, 'mouseenter', handler)
interaction_manager.add_event_listener(element, 'keydown', handler)

# Event object properties
def my_handler(event):
    print(f"Event type: {event.type}")
    print(f"Target: {event.target.tag}")
    print(f"Position: {event.pos}")
    
    # Stop propagation
    event.stop_propagation()
```

### Supported Events

- `click`, `mousedown`, `mouseup`
- `mouseenter`, `mouseleave`, `mousemove`
- `keydown`, `focus`, `blur`
- `drag`, `dragstart`, `dragend`, `drop`
- `wheel`

## Examples

### File Manager UI

See `example.py` for a complete interactive file manager interface with:
- Toolbar with buttons
- Sidebar navigation
- Draggable file items
- Status bar updates
- Keyboard navigation

### Pixel Art Game UI

See `sprite_example.py` for a game-style interface featuring:
- Sprite-based window decorations
- Pixel art buttons
- Inventory slots
- Color tinting effects

## Architecture

The rendering pipeline follows this flow:

1. **Parse HTML** -> Element tree
2. **Parse CSS** -> Style rules
3. **Compute Styles** -> Apply CSS to elements
4. **Calculate Layout** -> Position and size elements
5. **Render** -> Draw to pygame surface
6. **Handle Interactions** -> Process user input

## Advanced Features

### Custom Elements

```python
# Create custom elements
class CustomButton(HTMLElement):
    def __init__(self):
        super().__init__(tag='custom-button')
        self.custom_property = "value"
```

### Scrollable Containers

```python
from pygame_markup_gui.interactive_engine import ScrollableContainer

scrollable = ScrollableContainer(container_element, interaction_manager)
```

### Accessibility

```python
from pygame_markup_gui.interactive_engine import AccessibilityHelper

accessibility = AccessibilityHelper(interaction_manager)
```

## Performance Tips
- Use sprite caching for repeated graphics
- Minimize layout recalculations
- Cache computed styles when possible
- Use appropriate surface sizes
- Enable dirty rectangle updates for animations

## Limitations
- Limited CSS property support compared to full browsers
- No CSS animations or transitions
- No JavaScript support
- Single-threaded rendering
- No network resource loading

## Contributing

Contributions are welcome! Areas for improvement:

- Additional CSS properties
- Animation support
- Performance optimizations
- More comprehensive flexbox implementation
- CSS Grid support
- Better text rendering

## License

This project is open source. See LICENSE file for details.
