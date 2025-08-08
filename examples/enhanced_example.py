# enhanced_example_complete.py

import pygame
import sys

from pygame_markup_gui.debug_renderer import DebugRenderer
from pygame_markup_gui.html_engine import HTMLParser
from pygame_markup_gui.enhanced_css_engine import (
    EnhancedCSSEngine,
    EnhancedLayoutEngine,
    EnhancedMarkupRenderer
)
from pygame_markup_gui.interactive_engine import InteractionManager, FormHandler

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 1000


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enhanced CSS Engine - Complete Feature Showcase")
    clock = pygame.time.Clock()

    # Comprehensive HTML showcasing ALL enhanced features
    html = """
    <div class="enhanced-app">
        <!-- Enhanced Header with Background Gradient -->
        <header class="enhanced-header">
            <div class="logo-container">
                <h1 class="main-title">Enhanced CSS Engine</h1>
                <p class="subtitle">Complete Feature Showcase</p>
            </div>
            <nav class="main-nav">
                <button class="nav-btn primary">Flexbox</button>
                <button class="nav-btn secondary">Grid</button>
                <button class="nav-btn accent">Effects</button>
                <button class="nav-btn gradient">Transforms</button>
            </nav>
        </header>

        <!-- Main Content Grid Layout -->
        <main class="main-content">

            <!-- Advanced Flexbox Showcase -->
            <section class="flexbox-section">
                <h2 class="section-title">Advanced Flexbox Layout</h2>

                <!-- Flex Container with Various Properties -->
                <div class="flex-demo-container">
                    <div class="flex-item order-3 grow-2">Flex Grow 2, Order 3</div>
                    <div class="flex-item order-1 shrink-0">No Shrink, Order 1</div>
                    <div class="flex-item order-2 align-self-end">Align Self End, Order 2</div>
                </div>

                <!-- Flex Wrap Demo -->
                <div class="flex-wrap-demo">
                    <div class="wrap-item">Item 1</div>
                    <div class="wrap-item">Item 2</div>
                    <div class="wrap-item">Item 3</div>
                    <div class="wrap-item">Item 4</div>
                    <div class="wrap-item">Item 5</div>
                </div>

                <!-- Different Justify Content Options -->
                <div class="justify-demo">
                    <h4>Space Between</h4>
                    <div class="flex-space-between">
                        <span>A</span><span>B</span><span>C</span>
                    </div>
                    <h4>Space Around</h4>
                    <div class="flex-space-around">
                        <span>A</span><span>B</span><span>C</span>
                    </div>
                    <h4>Space Evenly</h4>
                    <div class="flex-space-evenly">
                        <span>A</span><span>B</span><span>C</span>
                    </div>
                </div>
            </section>

            <!-- Advanced Grid Layout with Template Areas -->
            <section class="grid-section">
                <h2 class="section-title">CSS Grid with Template Areas</h2>
                <div class="grid-template-demo">
                    <div class="grid-header">Header Area</div>
                    <div class="grid-nav">Navigation</div>
                    <div class="grid-content">Main Content Area</div>
                    <div class="grid-sidebar">Sidebar</div>
                    <div class="grid-footer">Footer Area</div>
                </div>

                <!-- Grid with Gap and Alignment -->
                <div class="grid-alignment-demo">
                    <div class="grid-cell justify-start">Start</div>
                    <div class="grid-cell justify-center">Center</div>
                    <div class="grid-cell justify-end">End</div>
                    <div class="grid-cell align-start">Top</div>
                    <div class="grid-cell align-center">Middle</div>
                    <div class="grid-cell align-end">Bottom</div>
                </div>
            </section>

            <!-- Advanced Positioning Demo -->
            <section class="positioning-section">
                <h2 class="section-title">Enhanced Positioning & Z-Index</h2>
                <div class="position-playground">
                    <div class="pos-static">Static (Normal Flow)</div>
                    <div class="pos-relative">
                        Relative Position
                        <div class="pos-absolute">Absolute Child</div>
                    </div>
                    <div class="pos-fixed">Fixed Position</div>
                    <div class="z-index-demo">
                        <div class="z-layer z1">Z-Index 1</div>
                        <div class="z-layer z3">Z-Index 3</div>
                        <div class="z-layer z2">Z-Index 2</div>
                    </div>
                </div>
            </section>

            <!-- Transform Showcase -->
            <section class="transform-section">
                <h2 class="section-title">CSS Transforms</h2>
                <div class="transform-gallery">
                    <div class="transform-item translate-demo">Translate</div>
                    <div class="transform-item scale-demo">Scale</div>
                    <div class="transform-item rotate-demo">Rotate</div>
                    <div class="transform-item skew-demo">Skew</div>
                    <div class="transform-item multi-transform">Multi Transform</div>
                </div>
            </section>

            <!-- Visual Effects Demo -->
            <section class="effects-section">
                <h2 class="section-title">Visual Effects</h2>
                <div class="effects-gallery">
                    <div class="effect-item border-radius-demo">Border Radius</div>
                    <div class="effect-item box-shadow-demo">Box Shadow</div>
                    <div class="effect-item opacity-demo">Opacity Effect</div>
                    <div class="effect-item gradient-bg-demo">Gradient Background</div>
                    <div class="effect-item multi-effect-demo">Multiple Effects</div>
                </div>
            </section>

            <!-- Typography Showcase -->
            <section class="typography-section">
                <h2 class="section-title">Enhanced Typography</h2>
                <div class="typography-examples">
                    <p class="text-transform-upper">uppercase transform</p>
                    <p class="text-transform-lower">LOWERCASE TRANSFORM</p>
                    <p class="text-transform-capitalize">capitalize transform</p>
                    <p class="text-align-center">Center Aligned Text</p>
                    <p class="text-align-right">Right Aligned Text</p>
                    <div class="line-height-demo">
                        <p class="tight-line-height">Tight line height text that demonstrates how line height affects text spacing and readability in paragraphs.</p>
                        <p class="loose-line-height">Loose line height text that demonstrates how line height affects text spacing and readability in paragraphs.</p>
                    </div>
                </div>
            </section>

            <!-- Min/Max Dimensions Demo -->
            <section class="dimensions-section">
                <h2 class="section-title">Min/Max Dimensions</h2>
                <div class="dimensions-demo">
                    <div class="min-width-demo">Min Width 200px</div>
                    <div class="max-width-demo">Max Width 150px - this text will wrap because the container has a maximum width constraint</div>
                    <div class="min-height-demo">Min Height 100px</div>
                    <div class="max-height-demo">Max Height 80px with overflow content that extends beyond the maximum height limit</div>
                </div>
            </section>
        </main>

        <!-- Enhanced Sidebar -->
        <aside class="enhanced-sidebar">
            <h3 class="sidebar-title">Enhanced Features</h3>
            <div class="feature-showcase">
                <!-- Background Image Demo -->
                <div class="bg-image-demo">
                    <p>Background Image Support</p>
                </div>

                <!-- Advanced Selectors Demo -->
                <div class="selector-demo">
                    <ul class="advanced-list">
                        <li>First Item</li>
                        <li>Second Item</li>
                        <li class="special">Special Item</li>
                        <li>Fourth Item</li>
                        <li>Last Item</li>
                    </ul>
                </div>

                <!-- Pseudo-class Demo -->
                <div class="pseudo-demo">
                    <button class="hover-btn">Hover Me</button>
                    <button class="focus-btn">Focus Me</button>
                    <input type="text" class="enhanced-input" placeholder="Enhanced Input">
                </div>
            </div>
        </aside>

        <!-- Enhanced Footer -->
        <footer class="enhanced-footer">
            <div class="footer-content">
                <p class="copyright">© 2024 Enhanced CSS Engine - Showcasing Modern CSS Features</p>
                <div class="footer-links">
                    <span class="link">Flexbox</span>
                    <span class="link">Grid</span>
                    <span class="link">Transforms</span>
                    <span class="link">Effects</span>
                </div>
            </div>
        </footer>
    </div>
    """

    # Comprehensive CSS using ALL enhanced features
    css = """
    /* Root Container with Grid Layout */
    .enhanced-app {
        display: grid;
        grid-template-columns: 1fr 300px;
        grid-template-rows: 120px 1fr 60px;
        grid-template-areas:
            "header sidebar"
            "main sidebar"
            "footer footer";
        min-height: 100vh;
        gap: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Enhanced Header with Advanced Flexbox */
    .enhanced-header {
        grid-area: header;
        background: linear-gradient(90deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 30px;
        position: relative;
        z-index: 10;
    }

    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    .main-title {
        font-size: 32px;
        color: #2d3748;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .subtitle {
        font-size: 14px;
        color: #718096;
        opacity: 0.8;
        text-transform: capitalize;
    }

    .main-nav {
        display: flex;
        gap: 15px;
        align-items: center;
    }

    .nav-btn {
        padding: 12px 24px;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .nav-btn.primary {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        box-shadow: 0 4px 15px rgba(255,107,107,0.4);
    }

    .nav-btn.secondary {
        background: linear-gradient(45deg, #5f27cd, #341f97);
        color: white;
        box-shadow: 0 4px 15px rgba(95,39,205,0.4);
    }

    .nav-btn.accent {
        background: linear-gradient(45deg, #00d2d3, #54a0ff);
        color: white;
        box-shadow: 0 4px 15px rgba(0,210,211,0.4);
    }

    .nav-btn.gradient {
        background: linear-gradient(45deg, #ffecd2, #fcb69f);
        color: #333;
        box-shadow: 0 4px 15px rgba(252,182,159,0.4);
    }

    .nav-btn:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }

    /* Main Content Grid */
    .main-content {
        grid-area: main;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto auto auto;
        gap: 20px;
        overflow-y: auto;
        max-height: 800px;
    }

    /* Section Styling */
    .main-content section {
        background: rgba(255,255,255,0.98);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        position: relative;
        transform: translateZ(0); /* GPU acceleration */
    }

    .section-title {
        color: #1a202c;
        font-size: 20px;
        margin-bottom: 20px;
        text-align: center;
        border-left: 4px solid #4f46e5;
        padding-left: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Advanced Flexbox Demonstrations */
    .flex-demo-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 15px;
        margin-bottom: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-radius: 10px;
        min-height: 80px;
    }

    .flex-item {
        padding: 15px 20px;
        background: linear-gradient(135deg, #1976d2, #1565c0);
        color: white;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 12px;
        min-width: 100px;
    }

    .order-1 { order: 1; background: linear-gradient(135deg, #388e3c, #2e7d32); }
    .order-2 { order: 2; background: linear-gradient(135deg, #f57c00, #ef6c00); }
    .order-3 { order: 3; background: linear-gradient(135deg, #d32f2f, #c62828); }
    .grow-2 { flex-grow: 2; }
    .shrink-0 { flex-shrink: 0; }
    .align-self-end { align-self: flex-end; }

    .flex-wrap-demo {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: flex-start;
        padding: 15px;
        background: linear-gradient(45deg, #fff3e0, #ffe0b2);
        border-radius: 8px;
        max-width: 300px;
        margin-bottom: 20px;
    }

    .wrap-item {
        padding: 10px 15px;
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        min-width: 80px;
        text-align: center;
    }

    .justify-demo h4 {
        font-size: 14px;
        color: #333;
        margin: 10px 0 5px 0;
    }

    .flex-space-between {
        display: flex;
        justify-content: space-between;
        background: #f5f5f5;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }

    .flex-space-around {
        display: flex;
        justify-content: space-around;
        background: #f5f5f5;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }

    .flex-space-evenly {
        display: flex;
        justify-content: space-evenly;
        background: #f5f5f5;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }

    .flex-space-between span, .flex-space-around span, .flex-space-evenly span {
        background: #4caf50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }

    /* CSS Grid with Template Areas */
    .grid-template-demo {
        display: grid;
        grid-template-columns: 200px 1fr 150px;
        grid-template-rows: 60px 1fr 40px;
        grid-template-areas:
            "header header header"
            "nav content sidebar"
            "footer footer footer";
        grid-gap: 10px;
        height: 250px;
        margin-bottom: 20px;
    }

    .grid-header {
        grid-area: header;
        background: linear-gradient(90deg, #e91e63, #ad1457);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-weight: bold;
    }

    .grid-nav {
        grid-area: nav;
        background: linear-gradient(135deg, #2196f3, #1976d2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }

    .grid-content {
        grid-area: content;
        background: linear-gradient(135deg, #4caf50, #388e3c);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-weight: bold;
    }

    .grid-sidebar {
        grid-area: sidebar;
        background: linear-gradient(135deg, #ff9800, #f57c00);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }

    .grid-footer {
        grid-area: footer;
        background: linear-gradient(90deg, #9c27b0, #7b1fa2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        font-weight: bold;
    }

    .grid-alignment-demo {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;  /* Simple fr units */
        grid-template-rows: 60px 60px;
        gap: 8px;
    }

    .grid-cell {
        background: linear-gradient(135deg, #607d8b, #455a64);
        color: white;
        display: flex;
        font-size: 12px;
        font-weight: bold;
        border-radius: 4px;
    }

    .justify-start { justify-content: flex-start; align-items: center; }
    .justify-center { justify-content: center; align-items: center; }
    .justify-end { justify-content: flex-end; align-items: center; }
    .align-start { align-items: flex-start; justify-content: center; }
    .align-center { align-items: center; justify-content: center; }
    .align-end { align-items: flex-end; justify-content: center; }

    /* Advanced Positioning */
    .position-playground {
        position: relative;
        height: 200px;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 8px;
        padding: 10px;
        overflow: visible;
    }

    .pos-static {
        position: static;
        background: #28a745;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        display: inline-block;
        margin: 5px;
        font-size: 12px;
        font-weight: bold;
    }

    .pos-relative {
        position: relative;
        top: 20px;
        left: 20px;
        background: #ffc107;
        color: #333;
        padding: 8px 12px;
        border-radius: 4px;
        display: inline-block;
        margin: 5px;
        font-size: 12px;
        font-weight: bold;
    }

    .pos-absolute {
        position: absolute;
        top: 5px;
        right: 5px;
        background: #dc3545;
        color: white;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        z-index: 2;
    }

    .pos-fixed {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: #6f42c1;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        z-index: 3;
    }

    .z-index-demo {
        position: relative;
        margin-top: 20px;
        height: 80px;
    }

    .z-layer {
        position: absolute;
        width: 60px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 10px;
        font-weight: bold;
        border-radius: 4px;
    }

    .z1 {
        background: #ff5722;
        z-index: 1;
        top: 10px;
        left: 10px;
    }

    .z2 {
        background: #2196f3;
        z-index: 2;
        top: 20px;
        left: 25px;
    }

    .z3 {
        background: #4caf50;
        z-index: 3;
        top: 30px;
        left: 40px;
    }

    /* Transform Gallery */
    .transform-gallery {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 15px;
        padding: 20px;
        background: linear-gradient(135deg, #fce4ec, #f8bbd9);
        border-radius: 8px;
    }

    .transform-item {
        height: 60px;
        background: linear-gradient(135deg, #e91e63, #c2185b);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
        transition: all 0.3s ease;
    }

    .translate-demo {
        transform: translate(10px, -5px);
    }

    .scale-demo {
        transform: scale(0.9);
    }

    .rotate-demo {
        transform: rotate(15deg);
    }

    .skew-demo {
        transform: skew(10deg, 5deg);
    }

    .multi-transform {
        transform: translate(5px, -3px) scale(1.1) rotate(-10deg);
    }

    .transform-item:hover {
        transform: scale(1.2) rotate(5deg);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }

    /* Visual Effects Gallery */
    .effects-gallery {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 15px;
        padding: 20px;
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        border-radius: 8px;
    }

    .effect-item {
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
    }

    .border-radius-demo {
        background: linear-gradient(135deg, #3f51b5, #303f9f);
        border-radius: 20px;
    }

    .box-shadow-demo {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        box-shadow: 0 8px 20px rgba(255,152,0,0.4);
    }

    .opacity-demo {
        background: linear-gradient(135deg, #009688, #00796b);
        opacity: 0.7;
    }

    .gradient-bg-demo {
        background: linear-gradient(45deg, #ff5722, #e64a19);
    }

    .multi-effect-demo {
        background: linear-gradient(135deg, #673ab7, #512da8);
        border-radius: 15px;
        box-shadow: 0 6px 18px rgba(103,58,183,0.4);
        opacity: 0.9;
        transform: scale(0.95);
    }

    /* Typography Examples */
    .typography-examples {
        background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 20px;
        border-radius: 8px;
    }

    .typography-examples p {
        margin: 10px 0;
        padding: 10px;
        background: rgba(255,255,255,0.7);
        border-radius: 6px;
        font-size: 14px;
    }

    .text-transform-upper {
        text-transform: uppercase;
        color: #d32f2f;
        font-weight: bold;
    }

    .text-transform-lower {
        text-transform: lowercase;
        color: #1976d2;
        font-weight: bold;
    }

    .text-transform-capitalize {
        text-transform: capitalize;
        color: #388e3c;
        font-weight: bold;
    }

    .text-align-center {
        text-align: center;
        background: linear-gradient(90deg, #e1f5fe, #b3e5fc);
        color: #0277bd;
        font-weight: bold;
    }

    .text-align-right {
        text-align: right;
        background: linear-gradient(90deg, #fce4ec, #f8bbd9);
        color: #c2185b;
        font-weight: bold;
    }

    .tight-line-height {
        line-height: 1.2;
        background: rgba(255,193,7,0.2);
        color: #f57c00;
    }

    .loose-line-height {
        line-height: 1.8;
        background: rgba(156,39,176,0.2);
        color: #8e24aa;
    }

    /* Min/Max Dimensions Demo */
    .dimensions-demo {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        padding: 20px;
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        border-radius: 8px;
    }

    .dimensions-demo > div {
        padding: 15px;
        background: rgba(255,255,255,0.8);
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        color: #333;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .min-width-demo {
        min-width: 200px;
        background: linear-gradient(135deg, #4fc3f7, #29b6f6);
        color: white;
    }

    .max-width-demo {
        max-width: 150px;
        background: linear-gradient(135deg, #81c784, #66bb6a);
        color: white;
    }

    .min-height-demo {
        min-height: 100px;
        background: linear-gradient(135deg, #ffb74d, #ffa726);
        color: white;
    }

    .max-height-demo {
        max-height: 80px;
        overflow: hidden;
        background: linear-gradient(135deg, #f06292, #ec407a);
        color: white;
    }

    /* Enhanced Sidebar */
    .enhanced-sidebar {
        grid-area: sidebar;
        background: rgba(255,255,255,0.98);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        max-height: 800px;
        overflow-y: auto;
    }

    .sidebar-title {
        color: #1a202c;
        font-size: 18px;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .feature-showcase {
        display: flex;
        flex-direction: column;
        gap: 20px;
    }

    .bg-image-demo {
        height: 80px;
        background: linear-gradient(135deg, #42a5f5, #1e88e5);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
    }

    /* Advanced Selectors Demo */
    .advanced-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .advanced-list li {
        padding: 10px;
        margin: 5px 0;
        background: #f5f5f5;
        border-radius: 4px;
        font-size: 12px;
        transition: all 0.3s ease;
    }

    .advanced-list li:first-child {
        background: linear-gradient(135deg, #4caf50, #388e3c);
        color: white;
        font-weight: bold;
    }

    .advanced-list li:last-child {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        font-weight: bold;
    }

    .advanced-list li:nth-child(odd) {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    }

    .advanced-list li:nth-child(even) {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
    }

    .advanced-list li.special {
        background: linear-gradient(135deg, #ffeb3b, #fbc02d);
        color: #333;
        font-weight: bold;
        border: 2px solid #f57f17;
    }

    .advanced-list li:hover {
        transform: translateX(10px) scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Pseudo-class Demo */
    .pseudo-demo {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .hover-btn, .focus-btn {
        padding: 12px 16px;
        border: none;
        border-radius: 6px;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .hover-btn:hover {
        background: linear-gradient(135deg, #818cf8, #6366f1);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99,102,241,0.4);
    }

    .focus-btn:focus {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        outline: none;
        box-shadow: 0 0 0 3px rgba(245,158,11,0.3);
    }

    .enhanced-input {
        padding: 12px;
        border: 2px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        transition: all 0.3s ease;
        background: white;
    }

    .enhanced-input:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79,70,229,0.1);
        outline: none;
    }

    .enhanced-input::placeholder {
        color: #9ca3af;
        opacity: 1;
    }

    /* Enhanced Footer */
    .enhanced-footer {
        grid-area: footer;
        background: rgba(0,0,0,0.8);
        color: white;
        border-radius: 12px;
        padding: 15px 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }

    .copyright {
        font-size: 12px;
        color: #ccc;
    }

    .footer-links {
        display: flex;
        gap: 15px;
    }

    .footer-links .link {
        padding: 6px 12px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .footer-links .link:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
        transform: translateY(-2px);
    }

    /* Responsive Design (Enhanced Media Queries Support) */
    @media (max-width: 768px) {
        .enhanced-app {
            grid-template-columns: 1fr;
            grid-template-areas:
                "header"
                "main"
                "sidebar"
                "footer";
        }

        .main-content {
            grid-template-columns: 1fr;
        }

        .main-nav {
            flex-direction: column;
            gap: 8px;
        }

        .nav-btn {
            padding: 8px 16px;
            font-size: 12px;
        }
    }
    """

    # Create enhanced engine instances
    parser = HTMLParser()
    css_engine = EnhancedCSSEngine()
    layout_engine = EnhancedLayoutEngine()
    # renderer = EnhancedMarkupRenderer()
    renderer = DebugRenderer()

    print("=== ENHANCED CSS ENGINE - COMPLETE SHOWCASE ===")
    print("Features demonstrated:")
    print("* Advanced Flexbox (justify-content, align-items, flex-wrap, order, grow/shrink)")
    print("* CSS Grid with Template Areas")
    print("* Enhanced Positioning (static, relative, absolute, fixed)")
    print("* CSS Transforms (translate, scale, rotate, skew, combined)")
    print("* Visual Effects (border-radius, box-shadow, opacity)")
    print("* Linear Gradients")
    print("* Enhanced Typography (text-transform, text-align, line-height)")
    print("* Min/Max Dimensions")
    print("* Z-Index Layering")
    print("* Advanced Selectors (nth-child, first-child, last-child, hover)")
    print("* Pseudo-class Support")

    print("\nParsing HTML...")
    root_element = parser.parse_fragment(html)

    print("Parsing Enhanced CSS...")
    css_engine.parse_css(css)

    def apply_styles_recursive(element):
        element.computed_style = css_engine.compute_style(element)
        for child in element.children:
            apply_styles_recursive(child)

    print("Applying enhanced styles...")
    apply_styles_recursive(root_element)

    print("Calculating enhanced layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)

    # Setup interactions
    interaction_manager = InteractionManager(root_element)
    form_handler = FormHandler(interaction_manager)

    def setup_enhanced_interactions(element):
        if element.tag == 'button':
            def button_handler(event):
                print(f"Enhanced button clicked: {element.text_content}")

            form_handler.setup_button(element, button_handler)

        for child in element.children:
            setup_enhanced_interactions(child)

    setup_enhanced_interactions(root_element)

    print("Starting enhanced demo with full feature set...")

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

            # Enhanced interaction handling
            elif event.type == pygame.MOUSEMOTION:
                interaction_manager.handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                interaction_manager.handle_mouse_down(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                interaction_manager.handle_mouse_up(event.pos, event.button)

        # Clear with enhanced gradient background
        screen.fill((40, 45, 55))

        # Enhanced debug info
        font = pygame.font.Font(None, 28)
        title_text = font.render("Enhanced CSS Engine - Complete Feature Showcase", True, (255, 255, 255))
        features_text = font.render("Flexbox * Grid * Transforms * Effects * Typography * Positioning", True,
                                    (200, 220, 255))

        screen.blit(title_text, (10, 10))
        screen.blit(features_text, (10, 40))

        # Render enhanced elements
        try:
            renderer.render(screen, root_element)
        except Exception as e:
            print(f"Enhanced render error: {e}")
            import traceback
            traceback.print_exc()

        pygame.display.flip()
        clock.tick(60)

    print("Enhanced CSS Engine demo completed!")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()