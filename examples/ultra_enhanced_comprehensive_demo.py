import pygame
import sys
import time
import math

from pygame_markup_gui.debug_renderer import DebugRenderer
# Import all the enhanced engines
from pygame_markup_gui.html_engine import HTMLParser
from pygame_markup_gui.ultra_enhanced_css_engine import (
    UltraEnhancedCSSEngine,
    UltraEnhancedLayoutEngine,
    UltraEnhancedMarkupRenderer,
    UltraEnhancedLayoutBox,
    TimingFunction,
    BlendMode,
    CursorType
)
from pygame_markup_gui.enhanced_css_engine import PositionType
from pygame_markup_gui.interactive_engine import InteractionManager, FormHandler

# Screen configuration
SCREEN_WIDTH = 2560/2
SCREEN_HEIGHT = 1440/2


def apply_ultra_animated_styles(element):
    """Apply animated style changes to ultra layout box"""
    if not element.layout_box or not isinstance(element.layout_box, UltraEnhancedLayoutBox):
        return

    style = element.computed_style
    box = element.layout_box

    # ULTRA TRANSFORM properties
    transform_value = style.get('transform', 'none')
    if transform_value != 'none':
        from pygame_markup_gui.enhanced_css_engine import EnhancedLayoutEngine
        box.transform = EnhancedLayoutEngine.parse_transform(None, transform_value)

    # ULTRA OPACITY properties
    opacity = style.get('opacity', '1')
    try:
        box.opacity = float(opacity)
    except:
        box.opacity = 1.0

    # ULTRA DIMENSION properties
    width = style.get('width', 'auto')
    if width != 'auto' and any(unit in width for unit in ['px', '%', 'em']):
        try:
            if width.endswith('px'):
                box.width = float(width[:-2])
            elif width.endswith('%'):
                # Would need container context for percentage
                pass
        except:
            pass

    height = style.get('height', 'auto')
    if height != 'auto' and any(unit in height for unit in ['px', '%', 'em']):
        try:
            if height.endswith('px'):
                box.height = float(height[:-2])
        except:
            pass

    # ULTRA POSITION properties
    if hasattr(box, 'position_type') and box.position_type != PositionType.STATIC:
        for prop in ['left', 'top', 'right', 'bottom']:
            value = style.get(prop)
            if value and value != 'auto':
                try:
                    if value.endswith('px'):
                        setattr(box, prop, float(value[:-2]))
                    elif value.endswith('%'):
                        # Would need container context
                        pass
                except:
                    pass

    # ULTRA COLOR properties are handled by renderer reading computed_style

    # ULTRA FILTER properties
    filter_value = style.get('filter', 'none')
    if filter_value != 'none' and hasattr(box, 'filters'):
        # Filters are parsed during style computation
        pass

    # ULTRA TYPOGRAPHY properties
    for prop in ['text-shadow', 'font-variant', 'text-indent']:
        if prop in style and hasattr(box, prop.replace('-', '_')):
            # Typography properties are applied during rendering
            pass


def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ULTRA-ENHANCED CSS ENGINE - Complete Feature Showcase")
    clock = pygame.time.Clock()

    # Ultra comprehensive HTML showcasing EVERY feature
    html = """
    <div class="ultra-showcase">
        <!-- SECTION 1: ANIMATIONS & KEYFRAMES -->
        <section class="animations-section">
            <h1 class="section-title animate-title">CSS ANIMATIONS & KEYFRAMES</h1>

            <div class="animation-gallery">
                <!-- Basic Animations -->
                <div class="demo-group">
                    <h3 class="group-title">Basic Keyframe Animations</h3>
                    <div class="animation-grid">
                        <div class="anim-box pulse-demo">Pulse</div>
                        <div class="anim-box rotate-demo">Rotate</div>
                        <div class="anim-box bounce-demo">Bounce</div>
                        <div class="anim-box shake-demo">Shake</div>
                        <div class="anim-box slide-demo">Slide</div>
                        <div class="anim-box zoom-demo">Zoom</div>
                        <div class="anim-box flip-demo">Flip</div>
                        <div class="anim-box wobble-demo">Wobble</div>
                    </div>
                </div>

                <!-- Complex Animations -->
                <div class="demo-group">
                    <h3 class="group-title">Complex Multi-Step Animations</h3>
                    <div class="animation-grid">
                        <div class="anim-box morphing-demo">Morph</div>
                        <div class="anim-box rainbow-demo">Rainbow</div>
                        <div class="anim-box elastic-demo">Elastic</div>
                        <div class="anim-box orbit-demo">Orbit</div>
                    </div>
                </div>

                <!-- Particle System -->
                <div class="demo-group">
                    <h3 class="group-title">Particle System Animations</h3>
                    <div class="particle-container">
                        <div class="particle p1"></div>
                        <div class="particle p2"></div>
                        <div class="particle p3"></div>
                        <div class="particle p4"></div>
                        <div class="particle p5"></div>
                        <div class="particle p6"></div>
                        <div class="particle p7"></div>
                        <div class="particle p8"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 2: TRANSITIONS & TIMING FUNCTIONS -->
        <section class="transitions-section">
            <h1 class="section-title">TRANSITIONS & TIMING FUNCTIONS</h1>

            <div class="timing-gallery">
                <!-- All Timing Functions -->
                <div class="demo-group">
                    <h3 class="group-title">All CSS Timing Functions</h3>
                    <div class="timing-grid">
                        <div class="timing-box linear-timing">Linear</div>
                        <div class="timing-box ease-timing">Ease</div>
                        <div class="timing-box ease-in-timing">Ease-In</div>
                        <div class="timing-box ease-out-timing">Ease-Out</div>
                        <div class="timing-box ease-in-out-timing">Ease-In-Out</div>
                        <div class="timing-box cubic-bezier-timing">Cubic-Bezier</div>
                        <div class="timing-box steps-timing">Steps</div>
                        <div class="timing-box bounce-timing">Bounce</div>
                    </div>
                </div>

                <!-- Multi-Property Transitions -->
                <div class="demo-group">
                    <h3 class="group-title">Multi-Property Transitions</h3>
                    <div class="multi-transition-grid">
                        <div class="multi-box transform-transition">Transform</div>
                        <div class="multi-box color-transition">Color</div>
                        <div class="multi-box size-transition">Size</div>
                        <div class="multi-box all-transition">All Props</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 3: ADVANCED TYPOGRAPHY -->
        <section class="typography-section">
            <h1 class="section-title">ADVANCED TYPOGRAPHY</h1>

            <div class="typography-gallery">
                <!-- Text Shadows -->
                <div class="demo-group">
                    <h3 class="group-title">Text Shadow Effects</h3>
                    <div class="text-demo-grid">
                        <p class="text-demo simple-shadow">Simple Shadow</p>
                        <p class="text-demo multiple-shadows">Multiple Shadows</p>
                        <p class="text-demo glow-text">Neon Glow</p>
                        <p class="text-demo embossed-text">Embossed Text</p>
                        <p class="text-demo outline-text">Outline Text</p>
                        <p class="text-demo fire-text">Fire Effect</p>
                    </div>
                </div>

                <!-- Text Overflow & Break -->
                <div class="demo-group">
                    <h3 class="group-title">Text Overflow & Breaking</h3>
                    <div class="text-overflow-demos">
                        <div class="overflow-box ellipsis-demo">
                            This is a very long text that should be truncated with ellipsis when it overflows
                        </div>
                        <div class="overflow-box clip-demo">
                            This text will be clipped when it overflows without any indication
                        </div>
                        <div class="break-box break-all">
                            WordBreakAllCharactersEvenInTheMiddleOfWords
                        </div>
                        <div class="break-box break-word">
                            SupercalifragilisticexpialidociousWordThatShouldBreak
                        </div>
                    </div>
                </div>

                <!-- Font Variants -->
                <div class="demo-group">
                    <h3 class="group-title">Font Variants & Features</h3>
                    <div class="font-variant-demos">
                        <p class="variant-demo small-caps-text">Small Caps Text Example</p>
                        <p class="variant-demo all-caps-text">ALL CAPS TEXT EXAMPLE</p>
                        <p class="variant-demo capitalize-text">capitalize each word example</p>
                        <p class="variant-demo lowercase-text">LOWERCASE TEXT EXAMPLE</p>
                    </div>
                </div>

                <!-- Text Indentation -->
                <div class="demo-group">
                    <h3 class="group-title">Text Indentation & Spacing</h3>
                    <div class="indentation-demos">
                        <p class="indent-demo standard-indent">
                            This paragraph has a standard text indent applied to the first line.
                            The rest of the text flows normally after the indented first line.
                        </p>
                        <p class="indent-demo large-indent">
                            This paragraph has a larger text indent to demonstrate different indentation levels.
                            Notice how only the first line is indented.
                        </p>
                        <p class="indent-demo negative-indent">
                            This paragraph demonstrates negative text indent, also known as hanging indent.
                            The first line extends to the left of the rest of the paragraph.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 4: CSS FILTERS & EFFECTS -->
        <section class="filters-section">
            <h1 class="section-title">CSS FILTERS & VISUAL EFFECTS</h1>

            <div class="filters-gallery">
                <!-- Basic Filters -->
                <div class="demo-group">
                    <h3 class="group-title">Individual Filter Effects</h3>
                    <div class="filter-grid">
                        <div class="filter-box blur-filter">Blur</div>
                        <div class="filter-box brightness-filter">Brightness</div>
                        <div class="filter-box contrast-filter">Contrast</div>
                        <div class="filter-box saturate-filter">Saturate</div>
                        <div class="filter-box hue-rotate-filter">Hue-Rotate</div>
                        <div class="filter-box sepia-filter">Sepia</div>
                        <div class="filter-box grayscale-filter">Grayscale</div>
                        <div class="filter-box invert-filter">Invert</div>
                    </div>
                </div>

                <!-- Combined Filters -->
                <div class="demo-group">
                    <h3 class="group-title">Combined Filter Effects</h3>
                    <div class="combined-filter-grid">
                        <div class="combined-filter vintage-filter">Vintage</div>
                        <div class="combined-filter dramatic-filter">Dramatic</div>
                        <div class="combined-filter neon-filter">Neon</div>
                        <div class="combined-filter dreamy-filter">Dreamy</div>
                    </div>
                </div>

                <!-- Backdrop Filters -->
                <div class="demo-group">
                    <h3 class="group-title">Backdrop Filter Effects</h3>
                    <div class="backdrop-container">
                        <div class="backdrop-demo blur-backdrop">Blur Backdrop</div>
                        <div class="backdrop-demo saturate-backdrop">Saturate Backdrop</div>
                        <div class="backdrop-demo brightness-backdrop">Brightness Backdrop</div>
                        <div class="backdrop-demo contrast-backdrop">Contrast Backdrop</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 5: CLIP PATHS & MASKING -->
        <section class="clip-section">
            <h1 class="section-title">CLIP PATHS & MASKING</h1>

            <div class="clip-gallery">
                <!-- Basic Clip Paths -->
                <div class="demo-group">
                    <h3 class="group-title">Basic Clip Path Shapes</h3>
                    <div class="clip-grid">
                        <div class="clip-box circle-clip">Circle</div>
                        <div class="clip-box ellipse-clip">Ellipse</div>
                        <div class="clip-box triangle-clip">Triangle</div>
                        <div class="clip-box hexagon-clip">Hexagon</div>
                        <div class="clip-box star-clip">Star</div>
                        <div class="clip-box diamond-clip">Diamond</div>
                    </div>
                </div>

                <!-- Advanced Clip Paths -->
                <div class="demo-group">
                    <h3 class="group-title">Advanced Clip Path Shapes</h3>
                    <div class="advanced-clip-grid">
                        <div class="advanced-clip speech-bubble">Speech Bubble</div>
                        <div class="advanced-clip arrow-clip">Arrow</div>
                        <div class="advanced-clip wave-clip">Wave</div>
                        <div class="advanced-clip zigzag-clip">Zigzag</div>
                    </div>
                </div>

                <!-- Animated Clip Paths -->
                <div class="demo-group">
                    <h3 class="group-title">Animated Clip Paths</h3>
                    <div class="animated-clip-grid">
                        <div class="animated-clip morphing-clip">Morphing</div>
                        <div class="animated-clip revealing-clip">Revealing</div>
                        <div class="animated-clip expanding-clip">Expanding</div>
                        <div class="animated-clip pulsing-clip">Pulsing</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 6: BLEND MODES & COMPOSITING -->
        <section class="blend-section">
            <h1 class="section-title">BLEND MODES & COMPOSITING</h1>

            <div class="blend-gallery">
                <!-- All Blend Modes -->
                <div class="demo-group">
                    <h3 class="group-title">All CSS Blend Modes</h3>
                    <div class="blend-grid">
                        <div class="blend-container">
                            <div class="blend-base base1"></div>
                            <div class="blend-overlay normal-blend">Normal</div>
                        </div>
                        <div class="blend-container">
                            <div class="blend-base base2"></div>
                            <div class="blend-overlay multiply-blend">Multiply</div>
                        </div>
                        <div class="blend-container">
                            <div class="blend-base base3"></div>
                            <div class="blend-overlay screen-blend">Screen</div>
                        </div>
                        <div class="blend-container">
                            <div class="blend-base base4"></div>
                            <div class="blend-overlay overlay-blend">Overlay</div>
                        </div>
                        <div class="blend-container">
                            <div class="blend-base base5"></div>
                            <div class="blend-overlay darken-blend">Darken</div>
                        </div>
                        <div class="blend-container">
                            <div class="blend-base base6"></div>
                            <div class="blend-overlay lighten-blend">Lighten</div>
                        </div>
                    </div>
                </div>

                <!-- Complex Blend Compositions -->
                <div class="demo-group">
                    <h3 class="group-title">Complex Blend Compositions</h3>
                    <div class="complex-blend-grid">
                        <div class="complex-blend-demo artistic-blend">Artistic</div>
                        <div class="complex-blend-demo duotone-blend">Duotone</div>
                        <div class="complex-blend-demo vintage-blend">Vintage</div>
                        <div class="complex-blend-demo neon-blend">Neon</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 7: USER INTERFACE & INTERACTION -->
        <section class="ui-section">
            <h1 class="section-title">USER INTERFACE & INTERACTION</h1>

            <div class="ui-gallery">
                <!-- Cursor Types -->
                <div class="demo-group">
                    <h3 class="group-title">All CSS Cursor Types</h3>
                    <div class="cursor-grid">
                        <div class="cursor-demo default-cursor">Default</div>
                        <div class="cursor-demo pointer-cursor">Pointer</div>
                        <div class="cursor-demo grab-cursor">Grab</div>
                        <div class="cursor-demo grabbing-cursor">Grabbing</div>
                        <div class="cursor-demo text-cursor">Text</div>
                        <div class="cursor-demo wait-cursor">Wait</div>
                        <div class="cursor-demo crosshair-cursor">Crosshair</div>
                        <div class="cursor-demo help-cursor">Help</div>
                        <div class="cursor-demo move-cursor">Move</div>
                        <div class="cursor-demo not-allowed-cursor">Not Allowed</div>
                        <div class="cursor-demo resize-e-cursor">Resize E</div>
                        <div class="cursor-demo resize-w-cursor">Resize W</div>
                    </div>
                </div>

                <!-- User Selection -->
                <div class="demo-group">
                    <h3 class="group-title">User Selection Controls</h3>
                    <div class="selection-demos">
                        <p class="select-demo auto-select">
                            Auto Selection: This text can be selected normally by the user.
                        </p>
                        <p class="select-demo none-select">
                            No Selection: This text cannot be selected by the user.
                        </p>
                        <p class="select-demo text-select">
                            Text Selection: This text can be selected as text.
                        </p>
                        <p class="select-demo all-select">
                            All Selection: This entire element gets selected when clicked.
                        </p>
                    </div>
                </div>

                <!-- Pointer Events -->
                <div class="demo-group">
                    <h3 class="group-title">Pointer Events Control</h3>
                    <div class="pointer-events-demos">
                        <div class="pointer-overlay">
                            <div class="pointer-base">Base Layer (clickable)</div>
                            <div class="pointer-transparent">
                                Transparent Layer (pointer-events: none)
                            </div>
                        </div>
                        <div class="pointer-auto-demo">Auto Pointer Events</div>
                        <div class="pointer-none-demo">No Pointer Events</div>
                    </div>
                </div>

                <!-- Interactive Elements -->
                <div class="demo-group">
                    <h3 class="group-title">Interactive UI Elements</h3>
                    <div class="interactive-demos">
                        <button class="ultra-button primary-btn">Primary Button</button>
                        <button class="ultra-button secondary-btn">Secondary Button</button>
                        <button class="ultra-button success-btn">Success Button</button>
                        <button class="ultra-button danger-btn">Danger Button</button>
                        <button class="ultra-button animated-btn">Animated Button</button>
                        <button class="ultra-button morphing-btn">Morphing Button</button>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 8: PERFORMANCE & OPTIMIZATION -->
        <section class="performance-section">
            <h1 class="section-title"> PERFORMANCE & OPTIMIZATION</h1>

            <div class="performance-gallery">
                <!-- Will-Change Optimization -->
                <div class="demo-group">
                    <h3 class="group-title">Will-Change Optimization</h3>
                    <div class="will-change-demos">
                        <div class="performance-box will-change-transform">
                            Will-Change: Transform
                            <div class="optimized-animation transform-optimized"></div>
                        </div>
                        <div class="performance-box will-change-opacity">
                            Will-Change: Opacity
                            <div class="optimized-animation opacity-optimized"></div>
                        </div>
                        <div class="performance-box will-change-filter">
                            Will-Change: Filter
                            <div class="optimized-animation filter-optimized"></div>
                        </div>
                        <div class="performance-box will-change-scroll">
                            Will-Change: Scroll-Position
                            <div class="optimized-animation scroll-optimized"></div>
                        </div>
                    </div>
                </div>

                <!-- Content Visibility -->
                <div class="demo-group">
                    <h3 class="group-title">Content Visibility Controls</h3>
                    <div class="content-visibility-demos">
                        <div class="visibility-box auto-visibility">
                            Content-Visibility: Auto
                            <p>This content may be skipped during rendering if off-screen.</p>
                        </div>
                        <div class="visibility-box visible-visibility">
                            Content-Visibility: Visible
                            <p>This content is always rendered regardless of position.</p>
                        </div>
                        <div class="visibility-box hidden-visibility">
                            Content-Visibility: Hidden
                            <p>This content is hidden and not rendered at all.</p>
                        </div>
                    </div>
                </div>

                <!-- Contain Property -->
                <div class="demo-group">
                    <h3 class="group-title">CSS Contain Property</h3>
                    <div class="contain-demos">
                        <div class="contain-box layout-contain">
                            Contain: Layout
                            <div class="contained-content">Contained layout impact</div>
                        </div>
                        <div class="contain-box paint-contain">
                            Contain: Paint
                            <div class="contained-content">Contained paint impact</div>
                        </div>
                        <div class="contain-box strict-contain">
                            Contain: Strict
                            <div class="contained-content">Strict containment</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 9: ADVANCED LAYOUT -->
        <section class="advanced-layout-section">
            <h1 class="section-title">ADVANCED LAYOUT FEATURES</h1>

            <div class="advanced-layout-gallery">
                <!-- Aspect Ratio -->
                <div class="demo-group">
                    <h3 class="group-title">CSS Aspect Ratio</h3>
                    <div class="aspect-ratio-demos">
                        <div class="aspect-box ratio-16-9">16:9 Aspect Ratio</div>
                        <div class="aspect-box ratio-4-3">4:3 Aspect Ratio</div>
                        <div class="aspect-box ratio-1-1">1:1 Aspect Ratio</div>
                        <div class="aspect-box ratio-21-9">21:9 Aspect Ratio</div>
                    </div>
                </div>

                <!-- Object Fit & Position -->
                <div class="demo-group">
                    <h3 class="group-title">Object Fit & Position</h3>
                    <div class="object-fit-demos">
                        <div class="object-container">
                            <div class="object-demo fill-demo">Object-Fit: Fill</div>
                        </div>
                        <div class="object-container">
                            <div class="object-demo contain-demo">Object-Fit: Contain</div>
                        </div>
                        <div class="object-container">
                            <div class="object-demo cover-demo">Object-Fit: Cover</div>
                        </div>
                        <div class="object-container">
                            <div class="object-demo scale-down-demo">Object-Fit: Scale-Down</div>
                        </div>
                    </div>
                </div>

                <!-- Position Types -->
                <div class="demo-group">
                    <h3 class="group-title">All CSS Position Types</h3>
                    <div class="position-demos">
                        <div class="position-container">
                            <div class="position-demo static-position">Static Position</div>
                            <div class="position-demo relative-position">Relative Position</div>
                            <div class="position-demo absolute-position">Absolute Position</div>
                            <div class="position-demo fixed-position">Fixed Position</div>
                            <div class="position-demo sticky-position">Sticky Position</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- SECTION 10: EXPERIMENTAL & CUTTING-EDGE -->
        <section class="experimental-section">
            <h1 class="section-title">EXPERIMENTAL & CUTTING-EDGE</h1>

            <div class="experimental-gallery">
                <!-- CSS Houdini-inspired -->
                <div class="demo-group">
                    <h3 class="group-title">Advanced CSS Techniques</h3>
                    <div class="experimental-grid">
                        <div class="experimental-demo css-art">CSS Art</div>
                        <div class="experimental-demo loading-spinner">Loading Spinner</div>
                        <div class="experimental-demo glitch-effect">Glitch Effect</div>
                        <div class="experimental-demo holographic">Holographic</div>
                    </div>
                </div>

                <!-- Performance Monitoring -->
                <div class="demo-group">
                    <h3 class="group-title">Performance Monitoring</h3>
                    <div class="performance-monitor">
                        <div class="monitor-metric fps-counter">FPS: 60</div>
                        <div class="monitor-metric animation-count">Animations: 0</div>
                        <div class="monitor-metric render-time">Render: 0ms</div>
                        <div class="monitor-metric memory-usage">Memory: 0MB</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer with ultra branding -->
        <footer class="ultra-footer">
            <div class="footer-content">
                <h2 class="footer-title">Ultra-Enhanced CSS Engine</h2>
                <p class="footer-subtitle">Complete Showcase of Modern CSS Features</p>
                <div class="feature-badges">
                    <span class="badge animations-badge">Animations</span>
                    <span class="badge transitions-badge">Transitions</span>
                    <span class="badge typography-badge">Typography</span>
                    <span class="badge filters-badge">Filters</span>
                    <span class="badge clips-badge">Clip Paths</span>
                    <span class="badge blends-badge">Blend Modes</span>
                    <span class="badge ui-badge">UI Features</span>
                    <span class="badge performance-badge">Performance</span>
                </div>
                <p class="footer-info">Demonstrating the power of modern CSS in pygame</p>
            </div>
        </footer>
    </div>
    """

    # Ultra comprehensive CSS with ALL features
    css = """
    /* === ULTRA-ENHANCED CSS KEYFRAMES === */

    /* Basic Animation Keyframes */
    @keyframes pulse {
        0%, 100% { transform: scale(1); background-color: #3498db; }
        50% { transform: scale(1.2); background-color: #e74c3c; }
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-3px); }
        20%, 40%, 60%, 80% { transform: translateX(3px); }
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes zoomIn {
        from { transform: scale(0) rotate(180deg); opacity: 0; }
        to { transform: scale(1) rotate(0deg); opacity: 1; }
    }

    @keyframes flip {
        0% { transform: perspective(400px) rotateY(0); }
        40% { transform: perspective(400px) translateZ(150px) rotateY(170deg); }
        50% { transform: perspective(400px) translateZ(150px) rotateY(190deg); }
        80% { transform: perspective(400px) rotateY(360deg); }
        100% { transform: perspective(400px) rotateY(360deg); }
    }

    @keyframes wobble {
        0%, 100% { transform: translateX(0) rotate(0deg); }
        15% { transform: translateX(-25px) rotate(-5deg); }
        30% { transform: translateX(20px) rotate(3deg); }
        45% { transform: translateX(-15px) rotate(-3deg); }
        60% { transform: translateX(10px) rotate(2deg); }
        75% { transform: translateX(-5px) rotate(-1deg); }
    }

    /* Complex Multi-Step Animations */
    @keyframes morphing {
        0% { border-radius: 0; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
        25% { border-radius: 50%; background: linear-gradient(45deg, #4ecdc4, #45b7d1); }
        50% { border-radius: 0 50% 50% 0; background: linear-gradient(45deg, #45b7d1, #96ceb4); }
        75% { border-radius: 50% 0 0 50%; background: linear-gradient(45deg, #96ceb4, #feca57); }
        100% { border-radius: 0; background: linear-gradient(45deg, #feca57, #ff6b6b); }
    }

    @keyframes rainbow {
        0% { background-color: #ff0000; }
        16.66% { background-color: #ff8800; }
        33.33% { background-color: #ffff00; }
        50% { background-color: #00ff00; }
        66.66% { background-color: #0088ff; }
        83.33% { background-color: #8800ff; }
        100% { background-color: #ff0000; }
    }

    @keyframes elastic {
        0% { transform: scale(1); }
        30% { transform: scale(1.25); }
        40% { transform: scale(0.75); }
        50% { transform: scale(1.15); }
        65% { transform: scale(0.95); }
        75% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes orbit {
        0% { transform: rotate(0deg) translateX(50px) rotate(0deg); }
        100% { transform: rotate(360deg) translateX(50px) rotate(-360deg); }
    }

    /* Particle Animations */
    @keyframes float1 {
        0%, 100% { transform: translateY(0px) translateX(0px); }
        33% { transform: translateY(-20px) translateX(10px); }
        66% { transform: translateY(-10px) translateX(-15px); }
    }

    @keyframes float2 {
        0%, 100% { transform: translateY(0px) translateX(0px) scale(1); }
        50% { transform: translateY(-30px) translateX(20px) scale(1.2); }
    }

    @keyframes sparkle {
        0%, 100% { opacity: 0; transform: scale(0); }
        50% { opacity: 1; transform: scale(1) rotate(180deg); }
    }

    /* Title Animation */
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6; }
        50% { text-shadow: 0 0 10px #fff, 0 0 20px #0073e6, 0 0 30px #0073e6; }
    }

    /* Clip Path Animations */
    @keyframes morphClip {
        0% { clip-path: circle(30%); }
        33% { clip-path: polygon(50% 0%, 0% 100%, 100% 100%); }
        66% { clip-path: polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%); }
        100% { clip-path: circle(30%); }
    }

    @keyframes revealClip {
        0% { clip-path: inset(0 100% 0 0); }
        100% { clip-path: inset(0 0% 0 0); }
    }

    @keyframes expandClip {
        0% { clip-path: circle(0%); }
        100% { clip-path: circle(70%); }
    }

    @keyframes pulseClip {
        0%, 100% { clip-path: circle(40%); }
        50% { clip-path: circle(60%); }
    }

    /* Glitch Effect */
    @keyframes glitch {
        0%, 100% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); }
        40% { transform: translate(-2px, -2px); }
        60% { transform: translate(2px, 2px); }
        80% { transform: translate(2px, -2px); }
    }

    /* Loading Spinner */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes spinBorder {
        0% { border-top-color: #3498db; }
        25% { border-right-color: #3498db; }
        50% { border-bottom-color: #3498db; }
        75% { border-left-color: #3498db; }
        100% { border-top-color: #3498db; }
    }

    /* === BASE STYLES === */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
        overflow-x: hidden;
    }

    .ultra-showcase {
        min-height: 100vh;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* === SECTION STYLES === */
    section {
        padding: 60px 40px;
        margin: 20px 0;
        position: relative;
    }

    .section-title {
        font-size: 48px;
        text-align: center;
        margin-bottom: 50px;
        color: white;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        animation: titleGlow 3s ease-in-out infinite;
        font-weight: 700;
        letter-spacing: 2px;
    }

    .animate-title {
        animation: slideIn 1s ease-out, titleGlow 3s ease-in-out infinite 1s;
    }

    /* === ANIMATION SECTION === */
    .animations-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .demo-group {
        margin: 40px 0;
    }

    .group-title {
        font-size: 24px;
        color: white;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
    }

    .animation-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        grid-gap: 20px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .anim-box {
        width: 120px;
        height: 120px;
        background: linear-gradient(45deg, #3498db, #2ecc71);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        will-change: transform;
    }

    .anim-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }

    /* Individual Animation Classes */
    .pulse-demo { animation: pulse 2s infinite; }
    .rotate-demo { animation: rotate 3s linear infinite; }
    .bounce-demo { animation: bounce 2s infinite; }
    .shake-demo { animation: shake 0.5s infinite; }
    .slide-demo { animation: slideIn 2s ease-out infinite; }
    .zoom-demo { animation: zoomIn 2s ease-in-out infinite; }
    .flip-demo { animation: flip 2s ease-in-out infinite; }
    .wobble-demo { animation: wobble 2s ease-in-out infinite; }
    .morphing-demo { animation: morphing 4s ease-in-out infinite; }
    .rainbow-demo { animation: rainbow 3s linear infinite; }
    .elastic-demo { animation: elastic 2s ease-in-out infinite; }
    .orbit-demo { animation: orbit 4s linear infinite; }

    /* Particle System */
    .particle-container {
        position: relative;
        width: 200px;
        height: 200px;
        margin: 40px auto;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    .particle {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #fff;
        border-radius: 50%;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }

    .p1 { top: 10%; left: 20%; animation: float1 3s ease-in-out infinite; }
    .p2 { top: 30%; left: 80%; animation: float2 4s ease-in-out infinite 0.5s; }
    .p3 { top: 60%; left: 10%; animation: sparkle 2s ease-in-out infinite 1s; }
    .p4 { top: 80%; left: 70%; animation: float1 3.5s ease-in-out infinite 1.5s; }
    .p5 { top: 50%; left: 50%; animation: float2 2.5s ease-in-out infinite 2s; }
    .p6 { top: 20%; left: 60%; animation: sparkle 3s ease-in-out infinite 0.8s; }
    .p7 { top: 70%; left: 30%; animation: float1 4s ease-in-out infinite 1.2s; }
    .p8 { top: 40%; left: 90%; animation: float2 3s ease-in-out infinite 1.8s; }

    /* === TRANSITIONS SECTION === */
    .transitions-section {
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
    }

    .timing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        grid-gap: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .timing-box {
        width: 150px;
        height: 80px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .timing-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.3);
        transition: left 0.5s;
    }

    .timing-box:hover::before {
        left: 100%;
    }

    /* Timing Function Classes */
    .linear-timing { transition: all 2s linear; }
    .linear-timing:hover { transform: translateX(50px); }

    .ease-timing { transition: all 2s ease; }
    .ease-timing:hover { transform: translateX(50px); }

    .ease-in-timing { transition: all 2s ease-in; }
    .ease-in-timing:hover { transform: translateX(50px); }

    .ease-out-timing { transition: all 2s ease-out; }
    .ease-out-timing:hover { transform: translateX(50px); }

    .ease-in-out-timing { transition: all 2s ease-in-out; }
    .ease-in-out-timing:hover { transform: translateX(50px); }

    .cubic-bezier-timing { transition: all 2s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
    .cubic-bezier-timing:hover { transform: translateX(50px) scale(1.1); }

    .steps-timing { transition: all 2s steps(5, end); }
    .steps-timing:hover { transform: translateX(50px); }

    .bounce-timing { transition: all 2s cubic-bezier(0.68, -0.6, 0.32, 1.6); }
    .bounce-timing:hover { transform: translateX(50px) scale(1.2); }

    /* Multi-Property Transitions */
    .multi-transition-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 800px;
        margin: 0 auto;
    }

    .multi-box {
        width: 200px;
        height: 100px;
        background: linear-gradient(45deg, #f093fb, #f5576c);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        cursor: pointer;
        border: 3px solid transparent;
    }

    .transform-transition {
        transition: transform 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    .transform-transition:hover {
        transform: rotate(10deg) scale(1.1) translateY(-10px);
    }

    .color-transition {
        transition: background 0.6s ease-in-out, color 0.6s ease-in-out;
    }
    .color-transition:hover {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        color: #333;
    }

    .size-transition {
        transition: width 0.5s ease-out, height 0.5s ease-out, border-radius 0.5s ease-out;
    }
    .size-transition:hover {
        width: 250px;
        height: 120px;
        border-radius: 50px;
    }

    .all-transition {
        transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    .all-transition:hover {
        transform: scale(1.2) rotate(-5deg);
        background: linear-gradient(45deg, #a8edea, #fed6e3);
        border-color: #fff;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    /* === TYPOGRAPHY SECTION === */
    .typography-section {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 20px;
    }

    .text-demo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        grid-gap: 30px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .text-demo {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #333;
    }

    /* Text Shadow Effects */
    .simple-shadow {
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }

    .multiple-shadows {
        text-shadow: 
            1px 1px 2px rgba(255, 0, 0, 0.8),
            2px 2px 4px rgba(0, 255, 0, 0.8),
            3px 3px 6px rgba(0, 0, 255, 0.8);
    }

    .glow-text {
        color: #fff;
        background: #333;
        text-shadow: 
            0 0 5px #fff,
            0 0 10px #fff,
            0 0 15px #0073e6,
            0 0 20px #0073e6,
            0 0 35px #0073e6,
            0 0 40px #0073e6;
        animation: pulse 2s ease-in-out infinite alternate;
    }

    .embossed-text {
        text-shadow: 
            -1px -1px 1px rgba(255, 255, 255, 0.8),
            1px 1px 1px rgba(0, 0, 0, 0.8);
        color: #999;
    }

    .outline-text {
        text-shadow: 
            -2px -2px 0 #000,
            2px -2px 0 #000,
            -2px 2px 0 #000,
            2px 2px 0 #000;
        color: #fff;
        background: #e74c3c;
    }

    .fire-text {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: transparent;
        text-shadow: 
            0 0 10px #ff6b6b,
            0 0 20px #ee5a24,
            0 0 30px #ff4757;
        animation: flicker 1.5s ease-in-out infinite alternate;
    }

    @keyframes flicker {
        0%, 100% { 
            text-shadow: 
                0 0 10px #ff6b6b,
                0 0 20px #ee5a24,
                0 0 30px #ff4757;
        }
        50% { 
            text-shadow: 
                0 0 5px #ff6b6b,
                0 0 10px #ee5a24,
                0 0 15px #ff4757;
        }
    }

    /* Text Overflow & Breaking */
    .text-overflow-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }

    .overflow-box, .break-box {
        width: 250px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        font-size: 16px;
        line-height: 1.4;
    }

    .ellipsis-demo {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .clip-demo {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: clip;
    }

    .break-all {
        word-break: break-all;
    }

    .break-word {
        overflow-wrap: break-word;
        word-break: break-word;
    }

    /* Font Variants */
    .font-variant-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        grid-gap: 20px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .variant-demo {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 20px;
        color: #333;
    }

    .small-caps-text {
        font-variant: small-caps;
        letter-spacing: 2px;
        font-weight: 600;
    }

    .all-caps-text {
        text-transform: uppercase;
        letter-spacing: 3px;
        font-weight: 700;
    }

    .capitalize-text {
        text-transform: capitalize;
        font-style: italic;
    }

    .lowercase-text {
        text-transform: lowercase;
        font-weight: 300;
    }

    /* Text Indentation */
    .indentation-demos {
        max-width: 800px;
        margin: 0 auto;
    }

    .indent-demo {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
    }

    .standard-indent {
        text-indent: 40px;
    }

    .large-indent {
        text-indent: 80px;
    }

    .negative-indent {
        text-indent: -30px;
        padding-left: 50px;
    }

    /* === FILTERS SECTION === */
    .filters-section {
        background: rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 20px;
    }

    .filter-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        grid-gap: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .filter-box {
        width: 150px;
        height: 150px;
        background: linear-gradient(45deg, #ff9a9e, #fecfef, #fecfef, #ff9a9e);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* Individual Filter Effects */
    .blur-filter:hover { filter: blur(3px); }
    .brightness-filter:hover { filter: brightness(1.8); }
    .contrast-filter:hover { filter: contrast(2); }
    .saturate-filter:hover { filter: saturate(3); }
    .hue-rotate-filter:hover { filter: hue-rotate(180deg); }
    .sepia-filter:hover { filter: sepia(1); }
    .grayscale-filter:hover { filter: grayscale(1); }
    .invert-filter:hover { filter: invert(1); }

    /* Combined Filters */
    .combined-filter-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .combined-filter {
        width: 200px;
        height: 150px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.5s ease;
    }

    .vintage-filter:hover {
        filter: sepia(0.8) contrast(1.2) brightness(0.9) saturate(1.1);
    }

    .dramatic-filter:hover {
        filter: contrast(1.8) brightness(0.7) saturate(1.5);
    }

    .neon-filter:hover {
        filter: brightness(1.5) contrast(1.3) hue-rotate(90deg) saturate(2);
    }

    .dreamy-filter:hover {
        filter: blur(1px) brightness(1.2) contrast(0.8) saturate(1.3);
    }

    /* Backdrop Filters */
    .backdrop-container {
        position: relative;
        height: 200px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        animation: gradientShift 5s ease infinite;
        border-radius: 15px;
        overflow: hidden;
    }

    .backdrop-demo {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .blur-backdrop { backdrop-filter: blur(10px); }
    .saturate-backdrop { backdrop-filter: saturate(2); }
    .brightness-backdrop { backdrop-filter: brightness(1.5); }
    .contrast-backdrop { backdrop-filter: contrast(1.8); }

    /* === CLIP PATHS SECTION === */
    .clip-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
    }

    .clip-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .clip-box {
        width: 150px;
        height: 150px;
        background: linear-gradient(45deg, #fa709a, #fee140);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    /* Basic Clip Paths */
    .circle-clip { clip-path: circle(50%); }
    .circle-clip:hover { clip-path: circle(70%); transform: scale(1.1); }

    .ellipse-clip { clip-path: ellipse(40% 50%); }
    .ellipse-clip:hover { clip-path: ellipse(60% 70%); }

    .triangle-clip { clip-path: polygon(50% 0%, 0% 100%, 100% 100%); }
    .triangle-clip:hover { clip-path: polygon(50% 0%, 20% 100%, 80% 100%); }

    .hexagon-clip { clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%); }
    .hexagon-clip:hover { clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); }

    .star-clip { clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); }
    .star-clip:hover { transform: rotate(36deg) scale(1.1); }

    .diamond-clip { clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); }
    .diamond-clip:hover { clip-path: polygon(50% 20%, 80% 50%, 50% 80%, 20% 50%); }

    /* Advanced Clip Paths */
    .advanced-clip-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .advanced-clip {
        width: 200px;
        height: 120px;
        background: linear-gradient(45deg, #a8edea, #fed6e3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #333;
        font-weight: bold;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .speech-bubble { 
        clip-path: polygon(0% 0%, 100% 0%, 100% 75%, 75% 75%, 75% 100%, 50% 75%, 0% 75%); 
    }

    .arrow-clip { 
        clip-path: polygon(0% 20%, 60% 20%, 60% 0%, 100% 50%, 60% 100%, 60% 80%, 0% 80%); 
    }

    .wave-clip { 
        clip-path: polygon(0% 0%, 100% 0%, 100% 80%, 0% 100%); 
    }

    .zigzag-clip { 
        clip-path: polygon(0% 0%, 100% 0%, 90% 50%, 100% 100%, 0% 100%, 10% 50%); 
    }

    /* Animated Clip Paths */
    .animated-clip-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        grid-gap: 30px;
        max-width: 800px;
        margin: 0 auto;
    }

    .animated-clip {
        width: 150px;
        height: 150px;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }

    .morphing-clip { animation: morphClip 4s ease-in-out infinite; }
    .revealing-clip { animation: revealClip 3s ease-in-out infinite; }
    .expanding-clip { animation: expandClip 2s ease-in-out infinite; }
    .pulsing-clip { animation: pulseClip 2s ease-in-out infinite; }

    /* === BLEND MODES SECTION === */
    .blend-section {
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
    }

    .blend-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .blend-container {
        position: relative;
        width: 200px;
        height: 150px;
        border-radius: 12px;
        overflow: hidden;
    }

    .blend-base {
        position: absolute;
        top: 0;
        left: 0;
        width: 120px;
        height: 120px;
        border-radius: 50%;
    }

    .base1 { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
    .base2 { background: linear-gradient(45deg, #667eea, #764ba2); }
    .base3 { background: linear-gradient(45deg, #f093fb, #f5576c); }
    .base4 { background: linear-gradient(45deg, #4facfe, #00f2fe); }
    .base5 { background: linear-gradient(45deg, #43e97b, #38f9d7); }
    .base6 { background: linear-gradient(45deg, #fa709a, #fee140); }

    .blend-overlay {
        position: absolute;
        top: 30px;
        left: 80px;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(45deg, #feca57, #48dbfb);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
    }

    /* Blend Mode Classes */
    .normal-blend { mix-blend-mode: normal; }
    .multiply-blend { mix-blend-mode: multiply; }
    .screen-blend { mix-blend-mode: screen; }
    .overlay-blend { mix-blend-mode: overlay; }
    .darken-blend { mix-blend-mode: darken; }
    .lighten-blend { mix-blend-mode: lighten; }

    /* Complex Blend Compositions */
    .complex-blend-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .complex-blend-demo {
        width: 200px;
        height: 150px;
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .complex-blend-demo:hover {
        transform: scale(1.05);
    }

    .artistic-blend {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }

    .artistic-blend::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle, transparent 30%, rgba(255, 255, 255, 0.3) 70%);
        mix-blend-mode: overlay;
    }

    .duotone-blend {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }

    .duotone-blend::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #667eea 0%, transparent 50%, #f093fb 100%);
        mix-blend-mode: multiply;
    }

    .vintage-blend {
        background: linear-gradient(45deg, #fa709a, #fee140);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }

    .vintage-blend::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(ellipse, rgba(139, 69, 19, 0.6) 0%, transparent 70%);
        mix-blend-mode: multiply;
    }

    .neon-blend {
        background: #000;
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        text-shadow: 0 0 10px #fff;
    }

    .neon-blend::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        mix-blend-mode: screen;
    }

    /* === USER INTERFACE SECTION === */
    .ui-section {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 20px;
    }

    .cursor-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        grid-gap: 15px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .cursor-demo {
        width: 120px;
        height: 80px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        transition: all 0.2s ease;
    }

    .cursor-demo:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Cursor Type Classes */
    .default-cursor { cursor: default; }
    .pointer-cursor { cursor: pointer; }
    .grab-cursor { cursor: grab; }
    .grabbing-cursor { cursor: grabbing; }
    .text-cursor { cursor: text; }
    .wait-cursor { cursor: wait; }
    .crosshair-cursor { cursor: crosshair; }
    .help-cursor { cursor: help; }
    .move-cursor { cursor: move; }
    .not-allowed-cursor { cursor: not-allowed; }
    .resize-e-cursor { cursor: e-resize; }
    .resize-w-cursor { cursor: w-resize; }

    /* User Selection */
    .selection-demos {
        max-width: 800px;
        margin: 0 auto;
    }

    .select-demo {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        font-size: 16px;
        line-height: 1.6;
        color: #333;
    }

    .auto-select { user-select: auto; }
    .none-select { user-select: none; }
    .text-select { user-select: text; }
    .all-select { user-select: all; }

    /* Pointer Events */
    .pointer-events-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }

    .pointer-overlay {
        position: relative;
        width: 250px;
        height: 150px;
        border-radius: 12px;
        overflow: hidden;
    }

    .pointer-base {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        cursor: pointer;
    }

    .pointer-transparent {
        position: absolute;
        top: 20px;
        left: 20px;
        right: 20px;
        bottom: 20px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #333;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        pointer-events: none;
    }

    .pointer-auto-demo {
        background: linear-gradient(45deg, #43e97b, #38f9d7);
        padding: 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        pointer-events: auto;
    }

    .pointer-none-demo {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        padding: 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        text-align: center;
        pointer-events: none;
        opacity: 0.6;
    }

    /* Interactive Elements */
    .interactive-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .ultra-button {
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .ultra-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }

    .ultra-button:hover::before {
        left: 100%;
    }

    .primary-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }

    .primary-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .secondary-btn {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        color: white;
    }

    .secondary-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(240, 147, 251, 0.4);
    }

    .success-btn {
        background: linear-gradient(45deg, #43e97b, #38f9d7);
        color: white;
    }

    .success-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(67, 233, 123, 0.4);
    }

    .danger-btn {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
    }

    .danger-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.4);
    }

    .animated-btn {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        color: white;
        animation: pulse 2s ease-in-out infinite;
    }

    .animated-btn:hover {
        animation: none;
        transform: scale(1.05);
    }

    .morphing-btn {
        background: linear-gradient(45deg, #fa709a, #fee140);
        color: white;
        border-radius: 25px;
        transition: all 0.5s ease;
    }

    .morphing-btn:hover {
        border-radius: 5px;
        background: linear-gradient(45deg, #a8edea, #fed6e3);
        color: #333;
        transform: scale(1.1);
    }

    /* === PERFORMANCE SECTION === */
    .performance-section {
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 20px;
    }

    .will-change-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .performance-box {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: #333;
        font-weight: bold;
    }

    .optimized-animation {
        width: 80px;
        height: 80px;
        margin: 15px auto;
        border-radius: 8px;
    }

    .will-change-transform {
        will-change: transform;
    }

    .transform-optimized {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        animation: rotate 3s linear infinite;
        will-change: transform;
    }

    .will-change-opacity {
        will-change: opacity;
    }

    .opacity-optimized {
        background: linear-gradient(45deg, #667eea, #764ba2);
        animation: pulse 2s ease-in-out infinite;
        will-change: opacity;
    }

    .will-change-filter {
        will-change: filter;
    }

    .filter-optimized {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        animation: rainbow 3s linear infinite;
        will-change: filter;
    }

    .will-change-scroll {
        will-change: scroll-position;
    }

    .scroll-optimized {
        background: linear-gradient(45deg, #43e97b, #38f9d7);
        animation: bounce 2s ease-in-out infinite;
        will-change: scroll-position;
    }

    /* Content Visibility */
    .content-visibility-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }

    .visibility-box {
        padding: 20px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        text-align: center;
    }

    .auto-visibility {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        content-visibility: visible;
    }

    .visible-visibility {
        background: linear-gradient(45deg, #43e97b, #38f9d7);
        content-visibility: visible;
    }

    .hidden-visibility {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        content-visibility: hidden;
    }

    /* Contain Property */
    .contain-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }

    .contain-box {
        padding: 15px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .layout-contain {
        background: linear-gradient(45deg, #667eea, #764ba2);
        contain: layout;
    }

    .paint-contain {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        contain: paint;
    }

    .strict-contain {
        background: linear-gradient(45deg, #fa709a, #fee140);
        contain: strict;
    }

    .contained-content {
        background: rgba(255, 255, 255, 0.2);
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
        font-size: 12px;
    }

    /* === ADVANCED LAYOUT SECTION === */
    .advanced-layout-section {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
    }

    /* Aspect Ratio */
    .aspect-ratio-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .aspect-box {
        background: linear-gradient(45deg, #667eea, #764ba2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
    }

    .ratio-16-9 { aspect-ratio: 16/9; }
    .ratio-4-3 { aspect-ratio: 4/3; }
    .ratio-1-1 { aspect-ratio: 1/1; }
    .ratio-21-9 { aspect-ratio: 21/9; }

    /* Object Fit */
    .object-fit-demos {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .object-container {
        width: 200px;
        height: 150px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        overflow: hidden;
    }

    .object-demo {
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
    }

    .fill-demo { object-fit: fill; }
    .contain-demo { object-fit: contain; }
    .cover-demo { object-fit: cover; }
    .scale-down-demo { object-fit: scale-down; }

    /* Position Types */
    .position-demos {
        max-width: 800px;
        margin: 0 auto;
    }

    .position-container {
        position: relative;
        height: 300px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        overflow: hidden;
    }

    .position-demo {
        width: 120px;
        height: 60px;
        background: linear-gradient(45deg, #f093fb, #f5576c);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
        text-align: center;
        margin: 10px;
    }

    .static-position { position: static; }
    .relative-position { position: relative; top: 20px; left: 20px; }
    .absolute-position { position: absolute; top: 50px; right: 50px; }
    .fixed-position { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
    .sticky-position { position: sticky; top: 10px; }

    /* === EXPERIMENTAL SECTION === */
    .experimental-section {
        background: rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(25px);
        border-radius: 20px;
    }

    .experimental-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 30px;
        max-width: 1000px;
        margin: 0 auto;
    }

    .experimental-demo {
        width: 200px;
        height: 150px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .experimental-demo:hover {
        transform: scale(1.05);
    }

    /* CSS Art */
    .css-art {
        background: conic-gradient(from 0deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff6b6b);
        animation: rotate 4s linear infinite;
        position: relative;
    }

    .css-art::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80%;
        height: 80%;
        background: #000;
        border-radius: 50%;
    }

    /* Loading Spinner */
    .loading-spinner {
        background: #333;
        position: relative;
        border-radius: 50%;
    }

    .loading-spinner::before {
        content: '';
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        bottom: 10px;
        border: 4px solid transparent;
        border-top-color: #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    /* Glitch Effect */
    .glitch-effect {
        background: linear-gradient(45deg, #ff0040, #00ff40);
        position: relative;
        animation: glitch 2s ease-in-out infinite;
    }

    .glitch-effect::before,
    .glitch-effect::after {
        content: 'Glitch Effect';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }

    .glitch-effect::before {
        color: #ff0040;
        animation: glitch 2s ease-in-out infinite reverse;
        clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%);
    }

    .glitch-effect::after {
        color: #00ff40;
        animation: glitch 2s ease-in-out infinite;
        clip-path: polygon(0 55%, 100% 55%, 100% 100%, 0 100%);
    }

    /* Holographic */
    .holographic {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        animation: gradientShift 3s ease infinite;
        position: relative;
        overflow: hidden;
    }

    .holographic::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        right: -50%;
        bottom: -50%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 2px,
            rgba(255, 255, 255, 0.1) 2px,
            rgba(255, 255, 255, 0.1) 4px
        );
        animation: shimmer 2s linear infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%); }
        100% { transform: translateX(100%) translateY(100%); }
    }

    /* Performance Monitor */
    .performance-monitor {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        grid-gap: 20px;
        max-width: 800px;
        margin: 40px auto;
    }

    .monitor-metric {
        background: rgba(0, 0, 0, 0.8);
        color: #00ff00;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        border: 1px solid #00ff00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }

    /* === FOOTER === */
    .ultra-footer {
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(30px);
        padding: 60px 40px;
        margin-top: 50px;
        text-align: center;
        border-top: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .footer-title {
        font-size: 36px;
        color: white;
        margin-bottom: 15px;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        animation: titleGlow 4s ease-in-out infinite;
    }
    
    .footer-subtitle {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 30px;
        font-style: italic;
    }
    
    .feature-badges {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 30px;
    }
    
    .badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: white;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }
    
    .badge::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .badge:hover::before {
        left: 100%;
    }
    
    .animations-badge {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        animation: pulse 3s ease-in-out infinite;
    }
    
    .transitions-badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        animation: float1 4s ease-in-out infinite 0.5s;
    }
    
    .typography-badge {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        animation: wobble 3s ease-in-out infinite 1s;
    }
    
    .filters-badge {
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        animation: rainbow 4s linear infinite;
    }
    
    .clips-badge {
        background: linear-gradient(45deg, #43e97b, #38f9d7);
        animation: morphing 5s ease-in-out infinite 1.5s;
    }
    
    .blends-badge {
        background: linear-gradient(45deg, #fa709a, #fee140);
        animation: rotate 6s linear infinite;
    }
    
    .ui-badge {
        background: linear-gradient(45deg, #a8edea, #fed6e3);
        animation: bounce 2s ease-in-out infinite 2s;
    }
    
    .performance-badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        animation: elastic 3s ease-in-out infinite 2.5s;
    }
    
    .footer-info {
        color: rgba(255, 255, 255, 0.6);
        font-size: 14px;
        margin-top: 20px;
    }
    
    /* === RESPONSIVE DESIGN === */
    @media (max-width: 1200px) {
        .section-title { font-size: 40px; }
        .animation-grid { grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); }
        .timing-grid { grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); }
    }
    
    @media (max-width: 768px) {
        section { padding: 40px 20px; }
        .section-title { font-size: 32px; }
        .footer-title { font-size: 28px; }
        
        .animation-grid,
        .timing-grid,
        .filter-grid,
        .clip-grid,
        .cursor-grid {
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            grid-gap: 15px;
        }
        
        .feature-badges {
            flex-direction: column;
            align-items: center;
        }
        
        .text-demo-grid,
        .multi-transition-grid,
        .combined-filter-grid {
            grid-template-columns: 1fr;
        }
    }
    
    @media (max-width: 480px) {
        .section-title { font-size: 24px; }
        .footer-title { font-size: 20px; }
        
        .anim-box,
        .timing-box,
        .filter-box,
        .clip-box {
            width: 80px;
            height: 80px;
            font-size: 10px;
        }
        
        .ultra-button {
            padding: 12px 20px;
            font-size: 14px;
        }
    }
    
    /* === PRINT STYLES === */
    @media print {
        .ultra-showcase {
            background: white !important;
            color: black !important;
        }
        
        .section-title,
        .group-title {
            color: black !important;
            text-shadow: none !important;
        }
        
        .anim-box,
        .timing-box,
        .filter-box,
        .clip-box,
        .cursor-demo,
        .experimental-demo {
            background: #f0f0f0 !important;
            color: black !important;
            box-shadow: none !important;
            animation: none !important;
        }
        
        .ultra-footer {
            background: #f0f0f0 !important;
            color: black !important;
        }
    }
    
    /* === ACCESSIBILITY === */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* === HIGH CONTRAST MODE === */
    @media (prefers-contrast: high) {
        .ultra-showcase {
            background: #000 !important;
        }
        
        .section-title,
        .group-title {
            color: #fff !important;
            text-shadow: 2px 2px 0 #000 !important;
        }
        
        .anim-box,
        .timing-box,
        .filter-box,
        .clip-box {
            border: 2px solid #fff !important;
        }
    }
    """

    # Create ultra-enhanced engine instances
    parser = HTMLParser()
    css_engine = UltraEnhancedCSSEngine()
    layout_engine = UltraEnhancedLayoutEngine()
    # renderer = UltraEnhancedMarkupRenderer()
    renderer = DebugRenderer()

    print("ULTRA-ENHANCED CSS ENGINE - COMPREHENSIVE DEMO")
    print("="* 80)
    print("Features Demonstrated:")
    print(" CSS @keyframes animations (20+ different animations)")
    print(" CSS transitions with all timing functions")
    print(" Advanced typography (text-shadow, overflow, variants)")
    print(" CSS filters (blur, brightness, contrast, etc.)")
    print(" Clip paths (circle, polygon, animated)")
    print(" Blend modes (multiply, screen, overlay, etc.)")
    print(" UI features (cursors, selection, pointer events)")
    print(" Performance (will-change, content-visibility)")
    print(" Advanced layout (aspect-ratio, object-fit, positioning)")
    print(" Experimental features (CSS art, glitch effects)")
    print("="* 80)

    # Parse HTML
    print("\nParsing comprehensive HTML structure...")
    root_element = parser.parse_fragment(html)
    print(f"  Parsed {len(root_element.children)} main sections")

    # Parse ultra-enhanced CSS with all features
    print("\n Parsing ultra-enhanced CSS with all modern features...")
    css_engine.parse_css(css)
    print(f"  Parsed {len(css_engine.rules)} CSS rules")
    print(f"  Parsed {len(css_engine.animation_engine.keyframes)} @keyframes")

    # Apply ultra styles recursively
    def apply_comprehensive_styles(element, depth=0):
        element.computed_style = css_engine.compute_style(element)
        
        # Count ultra features
        ultra_features = []
        style = element.computed_style
        
        if 'animation-name' in style and style['animation-name'] != 'none':
            ultra_features.append('animation')
        if 'transition-duration' in style and style['transition-duration'] != '0s':
            ultra_features.append('transition')
        if 'text-shadow' in style and style['text-shadow'] != 'none':
            ultra_features.append('text-shadow')
        if 'filter' in style and style['filter'] != 'none':
            ultra_features.append('filter')
        if 'clip-path' in style and style['clip-path'] != 'none':
            ultra_features.append('clip-path')
        if 'mix-blend-mode' in style and style['mix-blend-mode'] != 'normal':
            ultra_features.append('blend-mode')
        if 'cursor' in style and style['cursor'] != 'auto':
            ultra_features.append('cursor')
        if 'will-change' in style and style['will-change'] != 'auto':
            ultra_features.append('will-change')
        
        if ultra_features and depth < 3:  # Don't spam for deep children
            print(f"  {'  ' * depth} {element.tag}: {', '.join(ultra_features)}")
        
        for child in element.children:
            apply_comprehensive_styles(child, depth + 1)

    print("\n Applying ultra-enhanced styles...")
    apply_comprehensive_styles(root_element)

    # Calculate ultra layout
    print("\nCalculating ultra-enhanced layout...")
    layout_engine.layout(root_element, SCREEN_WIDTH, SCREEN_HEIGHT)
    print(f"  Layout calculated for {SCREEN_WIDTH}x{SCREEN_HEIGHT} viewport")

    # Setup comprehensive interactions
    interaction_manager = InteractionManager(root_element)
    form_handler = FormHandler(interaction_manager)

    def setup_comprehensive_interactions(element):
        classes = element.attributes.get('class', '')
        
        # Button interactions
        if element.tag == 'button' or 'ultra-button' in classes:
            def ultra_button_click(event):
                button_text = element.text_content or element.attributes.get('class', 'button')
                print(f"🔘 Ultra button clicked: {button_text}")
                
                # Add visual feedback animation
                element.computed_style['animation'] = 'pulse 0.3s ease-in-out'
                
                # Trigger re-layout for animation
                if hasattr(element.layout_box, 'animated_properties'):
                    element.layout_box.animated_properties['clicked'] = True
            
            interaction_manager.add_event_listener(element, 'click', ultra_button_click)
        
        # Cursor demonstration interactions
        elif 'cursor-' in classes:
            def cursor_interaction(event):
                cursor_type = classes.split('cursor-')[1].split()[0]
                print(f"Cursor interaction: {cursor_type}")
            
            interaction_manager.add_event_listener(element, 'mouseenter', cursor_interaction)
        
        # Animation box interactions
        elif 'anim-box' in classes:
            def animation_control(event):
                anim_type = classes.split('-demo')[0].split()[-1]
                print(f"Animation control: {anim_type}")
                
                # Toggle animation play state
                current_state = element.computed_style.get('animation-play-state', 'running')
                new_state = 'paused' if current_state == 'running' else 'running'
                element.computed_style['animation-play-state'] = new_state
            
            interaction_manager.add_event_listener(element, 'click', animation_control)
        
        # Timing function demonstrations
        elif 'timing-box' in classes:
            def timing_demo(event):
                timing_func = classes.split('-timing')[0].split()[-1]
                print(f"Timing function demo: {timing_func}")
            
            interaction_manager.add_event_listener(element, 'mouseenter', timing_demo)
        
        # Filter demonstrations
        elif 'filter-box' in classes:
            def filter_demo(event):
                filter_type = classes.split('-filter')[0].split()[-1]
                print(f"Filter demo: {filter_type}")
            
            interaction_manager.add_event_listener(element, 'mouseenter', filter_demo)
        
        # Clip path demonstrations
        elif 'clip-' in classes:
            def clip_demo(event):
                clip_type = classes.split('clip-')[1].split()[0]
                print(f"Clip path demo: {clip_type}")
            
            interaction_manager.add_event_listener(element, 'mouseenter', clip_demo)
        
        for child in element.children:
            setup_comprehensive_interactions(child)

    print("\n🎮 Setting up comprehensive interactions...")
    setup_comprehensive_interactions(root_element)

    # Performance monitoring
    class PerformanceMonitor:
        def __init__(self):
            self.frame_count = 0
            self.animation_frame_count = 0
            self.last_fps_update = time.time()
            self.current_fps = 60
            self.render_times = []
            self.animation_count = 0
            self.transition_count = 0
        
        def update(self, css_engine):
            self.frame_count += 1
            current_time = time.time()
            
            # Update FPS every second
            if current_time - self.last_fps_update >= 1.0:
                self.current_fps = self.frame_count
                self.frame_count = 0
                self.last_fps_update = current_time
            
            # Count active animations and transitions
            self.animation_count = len(css_engine.animation_engine.active_animations)
            self.transition_count = len(css_engine.transition_engine.active_transitions)
        
        def add_render_time(self, render_time):
            self.render_times.append(render_time)
            if len(self.render_times) > 60:  # Keep last 60 frames
                self.render_times.pop(0)
        
        def get_average_render_time(self):
            if not self.render_times:
                return 0
            return sum(self.render_times) / len(self.render_times)
        
        def get_memory_usage(self):
            # Simplified memory estimation
            return len(renderer.font_cache) + len(renderer.color_cache)

    performance_monitor = PerformanceMonitor()

    # Animation timing
    last_animation_update = time.time()
    animation_update_interval = 1.0 / 120.0  # 120 FPS for ultra-smooth animations

    # Feature showcase state
    feature_showcase_state = {
        'current_section': 0,
        'auto_advance': True,
        'section_timer': 0,
        'section_duration': 10.0  # Seconds per section
    }

    # Main ultra loop
    running = True
    fps = 120  # High FPS for ultra-smooth animations
    clock = pygame.time.Clock()

    print("\n Starting ultra-enhanced demo with comprehensive features...")
    print("Controls:")
    print(" ESC - Exit demo")
    print(" SPACE - Refresh layout")
    print(" R - Restart animations")
    print(" P - Toggle animation pause/play")
    print(" F - Toggle fullscreen")
    print(" M - Show performance metrics")
    print(" 1-9 - Jump to specific section")

    fullscreen = False
    show_metrics = True
    paused = False

    while running:
        current_time = time.time()
        frame_start_time = current_time

        # Handle events
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
                    print("Restarting all animations...")
                    css_engine.parse_css(css)  # Restart animations
                elif event.key == pygame.K_p:
                    paused = not paused
                    print(f"Animation {'paused' if paused else 'resumed'}")
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    print(f"️ Fullscreen {'enabled' if fullscreen else 'disabled'}")
                elif event.key == pygame.K_m:
                    show_metrics = not show_metrics
                    print(f"Performance metrics {'shown' if show_metrics else 'hidden'}")
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    section_num = event.key - pygame.K_1
                    print(f"Jumping to section {section_num + 1}")
                    feature_showcase_state['current_section'] = section_num

            # Enhanced interaction handling
            elif event.type == pygame.MOUSEMOTION:
                interaction_manager.handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                interaction_manager.handle_mouse_down(event.pos, event.button)

            elif event.type == pygame.MOUSEBUTTONUP:
                interaction_manager.handle_mouse_up(event.pos, event.button)

            elif event.type == pygame.MOUSEWHEEL:
                interaction_manager.handle_mouse_wheel(event.y, pygame.mouse.get_pos())

        # Update ultra animations and transitions
        if not paused and current_time - last_animation_update >= animation_update_interval:
            updated_elements = css_engine.update_animations()

            if updated_elements:
                performance_monitor.animation_frame_count += 1

                # Apply animated styles to layout boxes
                for element in updated_elements:
                    apply_ultra_animated_styles(element)

                # Periodically recalculate layout for animated elements
                if performance_monitor.animation_frame_count % 5 == 0:  # Every 5 animation frames
                    layout_engine.layout(root_element, screen.get_width(), screen.get_height())

            last_animation_update = current_time

        # Update performance monitoring
        performance_monitor.update(css_engine)

        # Clear screen with ultra dynamic background
        bg_color = (
            int(50 + 30 * math.sin(current_time * 0.5)),
            int(30 + 20 * math.sin(current_time * 0.3)),
            int(80 + 40 * math.sin(current_time * 0.7))
        )
        screen.fill(bg_color)

        # Render ultra UI
        render_start_time = time.time()
        try:
            renderer.render(screen, root_element)
            render_time = (time.time() - render_start_time) * 1000  # Convert to ms
            performance_monitor.add_render_time(render_time)

        except Exception as e:
            print(f"Ultra render error: {e}")
            import traceback
            traceback.print_exc()

        # Render ultra performance metrics
        if show_metrics:
            font = pygame.font.Font(None, 24)
            metrics_y = 10
            
            # FPS
            fps_text = font.render(f"FPS: {performance_monitor.current_fps}", True, (255, 255, 255))
            screen.blit(fps_text, (10, metrics_y))
            metrics_y += 30

            # Active animations
            anim_text = font.render(f"Animations: {performance_monitor.animation_count}", True, (100, 255, 100))
            screen.blit(anim_text, (10, metrics_y))
            metrics_y += 30

            # Active transitions
            trans_text = font.render(f"Transitions: {performance_monitor.transition_count}", True, (100, 255, 100))
            screen.blit(trans_text, (10, metrics_y))
            metrics_y += 30

            # Render time
            avg_render = performance_monitor.get_average_render_time()
            render_text = font.render(f"Render: {avg_render:.2f}ms", True, (255, 200, 100))
            screen.blit(render_text, (10, metrics_y))
            metrics_y += 30

            # Memory usage
            memory = performance_monitor.get_memory_usage()
            memory_text = font.render(f"Cache: {memory} items", True, (255, 100, 100))
            screen.blit(memory_text, (10, metrics_y))
            metrics_y += 30

            # Animation frame counter
            anim_frame_text = font.render(f"Anim Frames: {performance_monitor.animation_frame_count}", True, (200, 200, 255))
            screen.blit(anim_frame_text, (10, metrics_y))

        # Ultra status indicators
        font = pygame.font.Font(None, 32)
        
        # Title
        title_text = font.render("ULTRA-ENHANCED CSS ENGINE", True, (255, 255, 255))
        title_rect = title_text.get_rect()
        title_rect.centerx = screen.get_width() // 2
        title_rect.y = 10
        screen.blit(title_text, title_rect)

        # Feature showcase
        features_text = font.render("All Modern CSS Features Demonstrated", True, (150, 255, 150))
        features_rect = features_text.get_rect()
        features_rect.centerx = screen.get_width() // 2
        features_rect.y = 50
        screen.blit(features_text, features_rect)

        # Controls reminder
        small_font = pygame.font.Font(None, 20)
        controls_text = small_font.render("ESC=Exit | SPACE=Refresh | R=Restart | P=Pause | F=Fullscreen | M=Metrics", True, (200, 200, 200))
        controls_rect = controls_text.get_rect()
        controls_rect.centerx = screen.get_width() // 2
        controls_rect.y = screen.get_height() - 30
        screen.blit(controls_text, controls_rect)

        # Status indicators
        status_x = screen.get_width() - 200
        status_y = 10
        
        if paused:
            pause_text = small_font.render("⏸️ PAUSED", True, (255, 255, 0))
            screen.blit(pause_text, (status_x, status_y))
            status_y += 25

        if fullscreen:
            fs_text = small_font.render("️ FULLSCREEN", True, (100, 255, 100))
            screen.blit(fs_text, (status_x, status_y))

        # Display everything
        pygame.display.flip()
        clock.tick(fps)

        # Log periodic status
        frame_total = performance_monitor.frame_count + (performance_monitor.current_fps * (current_time - performance_monitor.last_fps_update))
        if int(frame_total) % (fps * 10) == 0:  # Every 10 seconds
            print(f"\nUltra Status Report:")
            print(f" Frame: {int(frame_total)}")
            print(f" FPS: {performance_monitor.current_fps}")
            print(f" Active Animations: {performance_monitor.animation_count}")
            print(f" Active Transitions: {performance_monitor.transition_count}")
            print(f" Avg Render Time: {avg_render:.2f}ms")
            print(f" Cache Items: {memory}")

    print("\nUltra-Enhanced CSS Engine Demo Completed!")
    print("="* 80)
    print("Final Statistics:")
    print(f" Total Frames Rendered: {int(frame_total)}")
    print(f" Total Animation Frames: {performance_monitor.animation_frame_count}")
    print(f" Final FPS: {performance_monitor.current_fps}")
    print(f" Final Render Time: {avg_render:.2f}ms")
    print(f" Cache Usage: {memory} items")
    print("="* 80)
    print("Features Successfully Demonstrated:")
    print("20+ CSS @keyframes animations")
    print("All CSS timing functions")
    print("Advanced typography effects")
    print("Complete CSS filter system")
    print("Clip path shapes and animations")
    print("All blend modes")
    print("UI interaction features")
    print("Performance optimizations")
    print("Advanced layout properties")
    print("Experimental CSS techniques")
    print("Ultra-Enhanced CSS Engine: Mission Accomplished!")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()