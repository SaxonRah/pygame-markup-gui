# ultra_enhanced_example.py

import pygame
import sys
import time

# from pygame_markup_gui import css_engine
from pygame_markup_gui import enhanced_css_engine
from pygame_markup_gui.enhanced_css_engine import PositionType
from pygame_markup_gui.html_engine import HTMLParser
from pygame_markup_gui.ultra_enhanced_css_engine import UltraEnhancedCSSEngine, UltraEnhancedLayoutEngine, \
    UltraEnhancedMarkupRenderer, UltraEnhancedLayoutBox
# from pygame_markup_gui.ultra_enhanced_css_engine import UltraEnhancedMarkupRenderer
from pygame_markup_gui.debug_renderer import DebugRenderer
from pygame_markup_gui.interactive_engine import InteractionManager

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000



def _apply_animated_style_to_layout_box(element):
    """Apply animated style changes to layout box"""
    if not element.layout_box or not isinstance(element.layout_box, UltraEnhancedLayoutBox):
        return

    style = element.computed_style
    box = element.layout_box

    # TRANSFORM properties (position, rotation, scale)
    transform_value = style.get('transform', 'none')
    if transform_value != 'none':
        box.transform = enhanced_css_engine.EnhancedLayoutEngine.parse_transform(None, transform_value)

    # OPACITY properties
    opacity = style.get('opacity', '1')
    try:
        box.opacity = float(opacity)
    except:
        box.opacity = 1.0

    # DIMENSION properties (width, height)
    width = style.get('width', 'auto')
    if width != 'auto' and width.replace('.', '').replace('px', '').isdigit():
        box.width = float(width.replace('px', ''))

    height = style.get('height', 'auto')
    if height != 'auto' and height.replace('.', '').replace('px', '').isdigit():
        box.height = float(height.replace('px', ''))

    # POSITION properties (left, top, right, bottom)
    if hasattr(box, 'position_type') and box.position_type != PositionType.STATIC:
        left = style.get('left')
        if left and left != 'auto':
            box.left = enhanced_css_engine.EnhancedLayoutEngine.parse_enhanced_length(None, left)

        top = style.get('top')
        if top and top != 'auto':
            box.top = enhanced_css_engine.EnhancedLayoutEngine.parse_enhanced_length(None, top)

    # COLOR properties (background-color, border-color)
    # These are handled by the renderer reading computed_style directly

    # MARGIN/PADDING properties
    margin_left = style.get('margin-left', '0')
    if margin_left != '0':
        box.margin_left = enhanced_css_engine.EnhancedLayoutEngine.parse_enhanced_length(None, margin_left)

    # BORDER properties
    border_width = style.get('border-width', '0')
    if border_width != '0':
        box.border_width = enhanced_css_engine.EnhancedLayoutEngine.parse_enhanced_length(None, border_width)

    # Z-INDEX properties
    z_index = style.get('z-index', '0')
    try:
        box.z_index = int(z_index)
    except:
        box.z_index = 0


def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ultra-Enhanced CSS Engine Demo - Animations & Advanced Effects")
    clock = pygame.time.Clock()

    # Ultra-enhanced HTML showcasing cutting-edge features
    html = """
    <div class="ultra-app">
        <div class="animated-header">
            <h1 class="logo-text">Ultra CSS Engine</h1>
            <div class="header-particles">
                <div class="particle"></div>
                <div class="particle"></div>
                <div class="particle"></div>
            </div>
        </div>

        <nav class="ultra-nav">
            <button class="ultra-btn primary">Animations</button>
            <button class="ultra-btn secondary">Typography</button>
            <button class="ultra-btn accent">Filters</button>
            <button class="ultra-btn gradient">Effects</button>
        </nav>

        <main class="ultra-main">
            <section class="showcase-grid">
                <div class="demo-card animations-demo">
                    <h3 class="card-title">CSS Animations</h3>
                    <div class="animation-box pulse-box"></div>
                    <div class="animation-box rotate-box"></div>
                    <div class="animation-box bounce-box"></div>
                    <p class="card-description">Keyframe animations with timing functions</p>
                </div>

                <div class="demo-card typography-demo">
                    <h3 class="card-title shadow-text">Advanced Typography</h3>
                    <p class="text-shadow-demo">Text with shadows</p>
                    <p class="text-overflow-demo">This is a very long text that should overflow with ellipsis</p>
                    <p class="small-caps-demo">Small Caps Text</p>
                    <p class="card-description">Text shadows, overflow, transformations</p>
                </div>

                <div class="demo-card filters-demo">
                    <h3 class="card-title">CSS Filters</h3>
                    <div class="filter-box blur-demo">Blur</div>
                    <div class="filter-box brightness-demo">Bright</div>
                    <div class="filter-box contrast-demo">Contrast</div>
                    <p class="card-description">Blur, brightness, contrast filters</p>
                </div>

                <div class="demo-card clip-path-demo">
                    <h3 class="card-title">Clip Paths</h3>
                    <div class="clip-circle">Circle</div>
                    <div class="clip-polygon">Polygon</div>
                    <p class="card-description">Circle and polygon clipping</p>
                </div>

                <div class="demo-card blend-modes-demo">
                    <h3 class="card-title">Blend Modes</h3>
                    <div class="blend-container">
                        <div class="blend-base"></div>
                        <div class="blend-overlay multiply-blend">Multiply</div>
                    </div>
                    <p class="card-description">CSS blend modes and compositing</p>
                </div>

                <div class="demo-card cursor-demo">
                    <h3 class="card-title">UI Properties</h3>
                    <div class="cursor-pointer">Pointer cursor</div>
                    <div class="cursor-grab">Grab cursor</div>
                    <div class="no-select">User-select: none</div>
                    <p class="card-description">Cursor types and user interaction</p>
                </div>
            </section>

            <section class="performance-section">
                <h2 class="perf-title">Performance Features</h2>
                <div class="perf-grid">
                    <div class="perf-card will-change-demo">
                        <h4>Will-Change Optimization</h4>
                        <div class="optimized-element">GPU Accelerated</div>
                    </div>

                    <div class="perf-card content-visibility-demo">
                        <h4>Content Visibility</h4>
                        <div class="visible-content">Always Visible</div>
                        <div class="hidden-content">Conditionally Hidden</div>
                    </div>
                </div>
            </section>

            <section class="transitions-section">
                <h2 class="transitions-title">CSS Transitions</h2>
                <div class="transition-demo-grid">
                    <div class="transition-card ease-in">Ease In</div>
                    <div class="transition-card ease-out">Ease Out</div>
                    <div class="transition-card ease-in-out">Ease In-Out</div>
                    <div class="transition-card linear">Linear</div>
                </div>
            </section>
        </main>

        <footer class="ultra-footer">
            <div class="footer-content">
                <p class="footer-text">Ultra-Enhanced CSS Engine - Next Generation Web Rendering</p>
                <div class="footer-badges">
                    <span class="badge">Animations</span>
                    <span class="badge">Transitions</span>
                    <span class="badge">Filters</span>
                    <span class="badge">Typography</span>
                </div>
            </div>
        </footer>
    </div>
    """

    # Ultra-enhanced CSS with cutting-edge features
    css = """
    /* Ultra-enhanced keyframe animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); background-color: #3498db; }
        50% { transform: scale(1.1); background-color: #e74c3c; }
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-20px); }
        60% { transform: translateY(-10px); }
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-10px) rotate(1deg); }
        66% { transform: translateY(-5px) rotate(-1deg); }
    }

    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }

    /* Base ultra styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .ultra-app {
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Arial', sans-serif;
        animation: fadeInUp 1s ease-out;
        will-change: transform;
    }

    /* Animated header */
    .animated-header {
        position: relative;
        text-align: center;
        padding: 40px 0;
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        overflow: hidden;
    }

    .logo-text {
        font-size: 48px;
        color: white;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3), 
                     0 0 20px rgba(255, 255, 255, 0.5);
        animation: float 3s ease-in-out infinite;
        font-variant: small-caps;
        letter-spacing: 2px;
        text-rendering: optimizeLegibility;
    }

    .header-particles {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }

    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        animation: float 4s ease-in-out infinite;
    }

    .particle:nth-child(1) {
        top: 20%;
        left: 20%;
        animation-delay: 0s;
    }

    .particle:nth-child(2) {
        top: 60%;
        left: 80%;
        animation-delay: 1s;
    }

    .particle:nth-child(3) {
        top: 80%;
        left: 40%;
        animation-delay: 2s;
    }

    /* Ultra navigation */
    .ultra-nav {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 30px;
        background: rgba(255, 255, 255, 0.1);
    }

    .ultra-btn {
        padding: 15px 30px;
        border: none;
        border-radius: 25px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
        user-select: none;
        will-change: transform;
    }

    .ultra-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: left 0.5s;
    }

    .ultra-btn:hover::before {
        left: 100%;
    }

    .ultra-btn.primary {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }

    .ultra-btn.primary:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
        filter: brightness(1.1);
    }

    .ultra-btn.secondary {
        background: linear-gradient(45deg, #5f27cd, #341f97);
        color: white;
        box-shadow: 0 4px 15px rgba(95, 39, 205, 0.4);
    }

    .ultra-btn.secondary:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(95, 39, 205, 0.6);
        filter: brightness(1.1);
    }

    .ultra-btn.accent {
        background: linear-gradient(45deg, #00d2d3, #54a0ff);
        color: white;
        box-shadow: 0 4px 15px rgba(0, 210, 211, 0.4);
    }

    .ultra-btn.accent:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0, 210, 211, 0.6);
        filter: brightness(1.1) contrast(1.1);
    }

    .ultra-btn.gradient {
        background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        box-shadow: 0 4px 15px rgba(252, 182, 159, 0.4);
    }

    .ultra-btn.gradient:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(252, 182, 159, 0.6);
        filter: brightness(1.1) saturate(1.2);
    }

    /* Main content */
    .ultra-main {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px 20px;
    }

    /* Showcase grid */
    .showcase-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        grid-gap: 30px;
        margin-bottom: 50px;
    }

    .demo-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        will-change: transform;
    }

    .demo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        animation: shimmer 2s linear infinite;
    }

    .demo-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.4);
    }

    .card-title {
        font-size: 24px;
        margin-bottom: 20px;
        color: #333;
        font-weight: 700;
        text-align: center;
    }

    .card-description {
        margin-top: 20px;
        color: #666;
        font-size: 14px;
        text-align: center;
        font-style: italic;
    }

    /* Animations demo */
    .animations-demo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .animation-box {
        width: 60px;
        height: 60px;
        margin: 10px;
        border-radius: 8px;
        display: inline-block;
    }

    .pulse-box {
        animation: pulse 2s infinite;
    }

    .rotate-box {
        background-color: #e74c3c;
        animation: rotate 3s linear infinite;
    }

    .bounce-box {
        background-color: #f39c12;
        animation: bounce 2s infinite;
    }

    /* Typography demo */
    .typography-demo {
        text-align: center;
    }

    .shadow-text {
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3),
                     0 0 10px rgba(102, 126, 234, 0.5);
        color: #667eea;
    }

    .text-shadow-demo {
        font-size: 18px;
        color: #333;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        margin: 15px 0;
    }

    .text-overflow-demo {
        width: 200px;
        margin: 15px auto;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        border: 1px solid #dee2e6;
    }

    .small-caps-demo {
        font-variant: small-caps;
        font-size: 16px;
        letter-spacing: 2px;
        color: #495057;
        margin: 15px 0;
    }

    /* Filters demo */
    .filters-demo {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .filter-box {
        width: 100px;
        height: 60px;
        margin: 10px;
        background: linear-gradient(45deg, #ff9a9e 0%, #fecfef 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .blur-demo:hover {
        filter: blur(3px);
    }

    .brightness-demo:hover {
        filter: brightness(1.5);
    }

    .contrast-demo:hover {
        filter: contrast(2);
    }

    /* Clip path demo */
    .clip-path-demo {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .clip-circle {
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #fa709a 0%, #fee140 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin: 10px;
        clip-path: circle(50%);
        transition: all 0.3s ease;
    }

    .clip-circle:hover {
        clip-path: circle(70%);
        transform: scale(1.1);
    }

    .clip-polygon {
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin: 10px;
        clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
        transition: all 0.3s ease;
    }

    .clip-polygon:hover {
        clip-path: polygon(50% 0%, 20% 100%, 80% 100%);
        transform: scale(1.1);
    }

    /* Blend modes demo */
    .blend-modes-demo {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .blend-container {
        position: relative;
        width: 150px;
        height: 100px;
        margin: 20px 0;
    }

    .blend-base {
        position: absolute;
        top: 0;
        left: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 50%;
    }

    .blend-overlay {
        position: absolute;
        top: 20px;
        left: 50px;
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #feca57, #48dbfb);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }

    .multiply-blend {
        mix-blend-mode: multiply;
    }

    /* Cursor demo */
    .cursor-demo {
        text-align: center;
    }

    .cursor-pointer {
        cursor: pointer;
        background-color: #3498db;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 5px;
        display: inline-block;
        transition: background-color 0.3s ease;
    }

    .cursor-pointer:hover {
        background-color: #2980b9;
    }

    .cursor-grab {
        cursor: grab;
        background-color: #e67e22;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 5px;
        display: inline-block;
        transition: all 0.3s ease;
    }

    .cursor-grab:active {
        cursor: grabbing;
        transform: scale(0.95);
    }

    .no-select {
        user-select: none;
        background-color: #9b59b6;
        color: white;
        padding: 10px;
        border-radius: 4px;
        margin: 5px;
        display: inline-block;
    }

    /* Performance section */
    .performance-section {
        margin: 50px 0;
        text-align: center;
    }

    .perf-title {
        font-size: 36px;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 30px;
    }

    .perf-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        grid-gap: 20px;
    }

    .perf-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    .will-change-demo .optimized-element {
        width: 100px;
        height: 100px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 8px;
        margin: 15px auto;
        will-change: transform;
        animation: float 2s ease-in-out infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
    }

    .content-visibility-demo .visible-content {
        content-visibility: visible;
        background-color: #2ecc71;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    .content-visibility-demo .hidden-content {
        content-visibility: hidden;
        background-color: #e74c3c;
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }

    /* Transitions section */
    .transitions-section {
        margin: 50px 0;
        text-align: center;
    }

    .transitions-title {
        font-size: 36px;
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 30px;
    }

    .transition-demo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }

    .transition-card {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 30px;
        border-radius: 12px;
        font-weight: bold;
        cursor: pointer;
        transform: scale(1);
    }

    .transition-card.ease-in {
        transition: all 0.5s ease-in;
    }

    .transition-card.ease-out {
        transition: all 0.5s ease-out;
    }

    .transition-card.ease-in-out {
        transition: all 0.5s ease-in-out;
    }

    .transition-card.linear {
        transition: all 0.5s linear;
    }

    .transition-card:hover {
        transform: scale(1.1) rotate(5deg);
        background: linear-gradient(45deg, #764ba2, #667eea);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }

    /* Ultra footer */
    .ultra-footer {
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 40px 0;
        margin-top: 50px;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
    }

    .footer-text {
        font-size: 18px;
        margin-bottom: 20px;
        opacity: 0.9;
    }

    .footer-badges {
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }

    .badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        animation: float 3s ease-in-out infinite;
    }

    .badge:nth-child(1) { animation-delay: 0s; }
    .badge:nth-child(2) { animation-delay: 0.5s; }
    .badge:nth-child(3) { animation-delay: 1s; }
    .badge:nth-child(4) { animation-delay: 1.5s; }

    /* Responsive design */
    @media (max-width: 768px) {
        .logo-text {
            font-size: 36px;
        }

        .ultra-nav {
            flex-direction: column;
            align-items: center;
        }

        .showcase-grid {
            grid-template-columns: 1fr;
        }

        .transition-demo-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 480px) {
        .logo-text {
            font-size: 28px;
        }

        .transition-demo-grid {
            grid-template-columns: 1fr;
        }

        .footer-badges {
            flex-direction: column;
            align-items: center;
        }
    }
    """

    # Create ultra-enhanced engine instances
    parser = HTMLParser()
    css_engine = UltraEnhancedCSSEngine()  # Ultra features with animations
    layout_engine = UltraEnhancedLayoutEngine()  # Animation-aware layout
    # renderer = UltraEnhancedMarkupRenderer()  # Advanced effects rendering
    renderer = DebugRenderer()  # Advanced effects rendering

    print("Ultra-Enhanced CSS Engine Demo")
    print("Features: Animations, Transitions, Filters, Advanced Typography, Blend Modes")

    # Parse HTML
    print("Parsing HTML...")
    root_element = parser.parse_fragment(html)

    # Parse ultra-enhanced CSS with keyframes
    print("Parsing Ultra-Enhanced CSS with @keyframes...")
    css_engine.parse_css(css)

    # Apply ultra styles recursively
    def apply_ultra_styles(element):
        element.computed_style = css_engine.compute_style(element)
        print(f"   Ultra-styling {element.tag} with {len(element.computed_style)} properties")

        # Check for ultra-specific properties
        ultra_props = []
        if 'animation-name' in element.computed_style and element.computed_style['animation-name'] != 'none':
            ultra_props.append('animation')
        if 'transition-duration' in element.computed_style and element.computed_style['transition-duration'] != '0s':
            ultra_props.append('transition')
        if 'text-shadow' in element.computed_style and element.computed_style['text-shadow'] != 'none':
            ultra_props.append('text-shadow')
        if 'filter' in element.computed_style and element.computed_style['filter'] != 'none':
            ultra_props.append('filter')

        if ultra_props:
            print(f"     Ultra properties: {', '.join(ultra_props)}")

        for child in element.children:
            apply_ultra_styles(child)

    print("Applying ultra-enhanced styles...")
    apply_ultra_styles(root_element)

    # Calculate ultra layout
    print("Calculating ultra-enhanced layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Setup ultra interactions
    interaction_manager = InteractionManager(root_element)

    def setup_ultra_interactions(element):
        if element.tag == 'button':
            def ultra_click_handler(event):
                print(f"Ultra button clicked: {element.text_content}")
                # Ultra visual feedback with animation
                element.computed_style['animation'] = 'pulse 0.3s ease-in-out'

        elif 'cursor-' in element.attributes.get('class', ''):
            def cursor_handler(event):
                print(f"🖱Ultra cursor interaction: {element.text_content}")

        # Ultra hover effects
        if 'transition-card' in element.attributes.get('class', ''):
            def transition_hover_handler(event):
                print(f"Ultra transition triggered: {element.text_content}")

        for child in element.children:
            setup_ultra_interactions(child)

    setup_ultra_interactions(root_element)

    # Animation timing
    last_animation_update = time.time()
    animation_update_interval = 1.0 / 60.0  # 60 FPS for smooth animations

    # Main loop
    running = True
    fps = 60
    frame_count = 0
    animation_frame_count = 0

    print("Starting ultra-enhanced demo...")
    print("Ultra features demonstrated:")
    print("  * CSS @keyframes animations (pulse, rotate, bounce, float)")
    print("  * CSS transitions with timing functions")
    print("  * Advanced typography (text-shadow, text-overflow, font-variant)")
    print("  * CSS filters (blur, brightness, contrast)")
    print("  * Clip paths (circle, polygon)")
    print("  * Mix blend modes")
    print("  * Advanced cursor types")
    print("  * Performance optimizations (will-change, content-visibility)")

    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    renderer.toggle_debug()
                elif event.key == pygame.K_SPACE:
                    print("Refreshing ultra layout...")
                    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)
                elif event.key == pygame.K_r:
                    print("Restarting animations...")
                    css_engine.parse_css(css)  # Restart all animations

            # Ultra interaction handling
            elif event.type == pygame.MOUSEMOTION:
                interaction_manager.handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                interaction_manager.handle_mouse_down(event.pos, event.button)

            elif event.type == pygame.MOUSEBUTTONUP:
                interaction_manager.handle_mouse_up(event.pos, event.button)

        # Update ultra animations
        if current_time - last_animation_update >= animation_update_interval:
            updated_elements = css_engine.update_animations()

            if updated_elements:
                animation_frame_count += 1

                # Re-apply animated styles and re-layout affected elements
                for element in updated_elements:
                    # Re-apply the updated computed style to the layout box
                    if hasattr(element.layout_box, 'animated_properties'):
                        _apply_animated_style_to_layout_box(element)

                # Force a layout recalculation for animated elements
                # Only do this occasionally to maintain performance
                if animation_frame_count % 3 == 0:  # Every 3 animation frames
                    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

                if animation_frame_count % 60 == 0:  # Every second at 60fps
                    print(f"Updated {len(updated_elements)} animated elements")

            last_animation_update = current_time

        # Clear screen with ultra gradient effect
        screen.fill((26, 35, 58))

        # Render ultra UI
        try:
            # renderer.render_element(root_element, screen)
            renderer.render(screen, root_element)

            # Ultra debug info
            if frame_count % (fps * 3) == 0:  # Every 3 seconds
                active_animations = len(css_engine.animation_engine.active_animations)
                active_transitions = len(css_engine.transition_engine.active_transitions)
                print(f"Ultra stats: {fps} FPS, {active_animations} animations, {active_transitions} transitions")

            # Ultra performance indicator
            font = pygame.font.Font(None, 28)
            perf_text = font.render(f"Ultra CSS Engine - {fps} FPS", True, (255, 255, 255))
            screen.blit(perf_text, (10, 10))

            # Show ultra features indicator
            features_text = font.render("Animations * Transitions * Filters * Advanced Typography", True,
                                        (100, 255, 150))
            screen.blit(features_text, (10, 40))

            # Animation counter
            anim_text = font.render(f"Animation Frame: {animation_frame_count}", True, (255, 200, 100))
            screen.blit(anim_text, (10, 70))

        except Exception as e:
            print(f"Ultra render error: {e}")
            import traceback
            traceback.print_exc()

        pygame.display.flip()
        clock.tick(fps)
        frame_count += 1

    print("Ultra-Enhanced CSS Engine Demo ended")
    print(f"Final stats: {frame_count} total frames, {animation_frame_count} animation frames")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
