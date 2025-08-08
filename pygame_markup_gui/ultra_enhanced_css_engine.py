# ultra_enhanced_css_engine.py

import re
import math
import time
import pygame
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# Import Enhanced engines to extend them
from .enhanced_css_engine import (
    EnhancedCSSEngine,
    EnhancedLayoutEngine,
    EnhancedMarkupRenderer,
    EnhancedLayoutBox,
    Transform,
    BoxShadow
)
from .html_engine import HTMLElement


class CursorType(Enum):
    AUTO = "auto"
    DEFAULT = "default"
    POINTER = "pointer"
    TEXT = "text"
    WAIT = "wait"
    CROSSHAIR = "crosshair"
    HELP = "help"
    MOVE = "move"
    GRAB = "grab"
    GRABBING = "grabbing"
    NOT_ALLOWED = "not-allowed"
    RESIZE_E = "e-resize"
    RESIZE_W = "w-resize"
    RESIZE_N = "n-resize"
    RESIZE_S = "s-resize"


class BlendMode(Enum):
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color-dodge"
    COLOR_BURN = "color-burn"
    HARD_LIGHT = "hard-light"
    SOFT_LIGHT = "soft-light"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"


class TimingFunction(Enum):
    LINEAR = "linear"
    EASE = "ease"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    STEP_START = "step-start"
    STEP_END = "step-end"


@dataclass
class TextShadow:
    offset_x: float = 0
    offset_y: float = 0
    blur_radius: float = 0
    color: Tuple[int, int, int, int] = (0, 0, 0, 255)


@dataclass
class Filter:
    type: str  # blur, brightness, contrast, etc.
    value: float = 0
    unit: str = ""


@dataclass
class Animation:
    name: str
    duration: float = 1.0
    timing_function: TimingFunction = TimingFunction.EASE
    delay: float = 0
    iteration_count: Union[int, str] = 1
    direction: str = "normal"
    fill_mode: str = "none"
    play_state: str = "running"
    start_time: float = 0
    current_iteration: int = 0


@dataclass
class Transition:
    property: str = "all"
    duration: float = 0
    timing_function: TimingFunction = TimingFunction.EASE
    delay: float = 0
    start_time: float = 0
    start_value: Any = None
    end_value: Any = None
    active: bool = False


@dataclass
class ClipPath:
    type: str  # circle, ellipse, polygon, inset
    values: List[float] = field(default_factory=list)


class UltraEnhancedLayoutBox(EnhancedLayoutBox):
    """Ultra-enhanced layout box extending Enhanced with animation and advanced properties"""

    def __init__(self):
        super().__init__()  # Get ALL Enhanced properties + base properties

        # Animation & Transition properties (NEW - Ultra level)
        self.animations: List[Animation] = field(default_factory=list)
        self.transitions: List[Transition] = field(default_factory=list)
        self.animated_properties: Dict[str, Any] = field(default_factory=dict)

        # Typography properties (NEW - Ultra level)
        self.text_shadows: List[TextShadow] = field(default_factory=list)
        self.text_indent: float = 0
        self.text_overflow: str = "clip"
        self.word_break: str = "normal"
        self.overflow_wrap: str = "normal"
        self.font_variant: str = "normal"
        self.line_break: str = "auto"
        self.hyphens: str = "manual"
        self.text_rendering: str = "auto"

        # User Interface properties (NEW - Ultra level)
        self.cursor: CursorType = CursorType.AUTO
        self.user_select: str = "auto"
        self.pointer_events: str = "auto"
        self.resize: str = "none"
        self.caret_color: Optional[Tuple[int, int, int]] = None
        self.accent_color: Optional[Tuple[int, int, int]] = None
        self.appearance: str = "auto"
        self.outline_offset: float = 0

        # Advanced Visual Effects (NEW - Ultra level)
        self.filters: List[Filter] = field(default_factory=list)
        self.backdrop_filters: List[Filter] = field(default_factory=list)
        self.clip_path: Optional[ClipPath] = None
        self.mask: Optional[str] = None
        self.mix_blend_mode: BlendMode = BlendMode.NORMAL
        self.isolation: str = "auto"
        self.object_fit: str = "fill"
        self.object_position: Tuple[str, str] = ("50%", "50%")
        self.aspect_ratio: Optional[float] = None
        self.contain: str = "none"
        self.content_visibility: str = "visible"
        self.will_change: List[str] = field(default_factory=list)


class AnimationEngine:
    """Handles CSS animations and keyframes"""

    def __init__(self):
        self.active_animations: Dict[HTMLElement, List[Animation]] = {}
        self.keyframes: Dict[str, Dict[str, Dict[str, str]]] = {}

    def add_keyframe(self, name: str, keyframe_data: Dict[str, Dict[str, str]]):
        """Add keyframe definition"""
        self.keyframes[name] = keyframe_data

    def start_animation(self, element: HTMLElement, animation: Animation):
        """Start an animation on an element"""
        if element not in self.active_animations:
            self.active_animations[element] = []

        animation.start_time = time.time()
        self.active_animations[element].append(animation)

    def update_animations(self, current_time: float) -> List[HTMLElement]:
        """Update all active animations and return elements that need re-rendering"""
        updated_elements = []

        for element, animations in list(self.active_animations.items()):
            active_animations = []

            for animation in animations:
                if self._update_animation(element, animation, current_time):
                    active_animations.append(animation)
                    updated_elements.append(element)

            if active_animations:
                self.active_animations[element] = active_animations
            else:
                del self.active_animations[element]

        return updated_elements

    def _update_animation(self, element: HTMLElement, animation: Animation, current_time: float) -> bool:
        """Update single animation, return True if still active"""
        if animation.play_state == "paused":
            return True

        elapsed = current_time - animation.start_time - animation.delay

        if elapsed < 0:
            return True  # Still in delay phase

        duration = animation.duration
        if duration <= 0:
            return False

        # Calculate progress
        progress = elapsed / duration

        # Handle iteration count
        if isinstance(animation.iteration_count, int):
            if progress >= animation.iteration_count:
                self._apply_fill_mode(element, animation, True)
                return False

            # Get current iteration progress
            iteration = int(progress)
            if iteration != animation.current_iteration:
                animation.current_iteration = iteration

            local_progress = progress - iteration
        else:  # infinite
            local_progress = progress % 1.0

        # Apply direction
        if animation.direction in ["reverse", "alternate-reverse"]:
            if animation.direction == "reverse" or (
                    animation.direction == "alternate-reverse" and animation.current_iteration % 2 == 0):
                local_progress = 1.0 - local_progress
        elif animation.direction == "alternate" and animation.current_iteration % 2 == 1:
            local_progress = 1.0 - local_progress

        # Apply timing function
        eased_progress = self._apply_timing_function(local_progress, animation.timing_function)

        # Apply keyframe properties
        self._apply_keyframe_at_progress(element, animation, eased_progress)

        return True

    def _apply_timing_function(self, progress: float, timing_function: TimingFunction) -> float:
        """Apply timing function to progress"""
        if timing_function == TimingFunction.LINEAR:
            return progress
        elif timing_function == TimingFunction.EASE:
            return self._cubic_bezier(progress, 0.25, 0.1, 0.25, 1.0)
        elif timing_function == TimingFunction.EASE_IN:
            return self._cubic_bezier(progress, 0.42, 0, 1.0, 1.0)
        elif timing_function == TimingFunction.EASE_OUT:
            return self._cubic_bezier(progress, 0, 0, 0.58, 1.0)
        elif timing_function == TimingFunction.EASE_IN_OUT:
            return self._cubic_bezier(progress, 0.42, 0, 0.58, 1.0)
        elif timing_function == TimingFunction.STEP_START:
            return 1.0 if progress > 0 else 0.0
        elif timing_function == TimingFunction.STEP_END:
            return 1.0 if progress >= 1.0 else 0.0
        return progress

    def _cubic_bezier(self, t: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Simplified cubic bezier calculation"""
        return t * t * (3.0 - 2.0 * t)  # Smoothstep approximation

    def _apply_keyframe_at_progress(self, element: HTMLElement, animation: Animation, progress: float):
        """Apply keyframe properties at given progress"""
        if animation.name not in self.keyframes:
            return

        keyframe_data = self.keyframes[animation.name]

        # Find surrounding keyframes
        keyframe_positions = []
        for key in keyframe_data.keys():
            if key.endswith('%'):
                pos = float(key[:-1]) / 100.0
            else:
                continue  # Skip non-percentage keys
            keyframe_positions.append((pos, key))

        if not keyframe_positions:
            return

        keyframe_positions.sort()

        # Find the two keyframes to interpolate between
        prev_frame = None
        next_frame = None

        for pos, key in keyframe_positions:
            if pos <= progress:
                prev_frame = (pos, key)
            elif pos > progress and next_frame is None:
                next_frame = (pos, key)
                break

        if prev_frame is None:
            prev_frame = (keyframe_positions[0][0], keyframe_positions[0][1])
        if next_frame is None:
            next_frame = (keyframe_positions[-1][0], keyframe_positions[-1][1])

        # Apply interpolated properties
        if prev_frame and next_frame:
            self._interpolate_keyframes(element, animation, prev_frame, next_frame, progress)
        elif prev_frame:
            self._apply_keyframe_properties(element, keyframe_data[prev_frame[1]])

    def _interpolate_keyframes(self, element: HTMLElement, animation: Animation,
                               prev_frame: Tuple[float, str], next_frame: Tuple[float, str], progress: float):
        """Interpolate between two keyframes"""
        prev_pos, prev_key = prev_frame
        next_pos, next_key = next_frame

        if prev_pos == next_pos:
            local_progress = 0
        else:
            local_progress = (progress - prev_pos) / (next_pos - prev_pos)

        prev_props = self.keyframes[animation.name][prev_key]
        next_props = self.keyframes[animation.name][next_key]

        # Interpolate each property
        interpolated_props = {}
        all_props = set(prev_props.keys()) | set(next_props.keys())

        for prop in all_props:
            prev_val = prev_props.get(prop, self._get_element_property(element, prop))
            next_val = next_props.get(prop, self._get_element_property(element, prop))

            interpolated_val = self._interpolate_property_value(prop, prev_val, next_val, local_progress)
            interpolated_props[prop] = interpolated_val

        self._apply_keyframe_properties(element, interpolated_props)

    def _interpolate_property_value(self, prop: str, start_val: str, end_val: str, progress: float) -> str:
        """Interpolate between two property values"""
        # Handle numeric properties
        if prop in ['opacity', 'z-index']:
            try:
                start_num = float(start_val)
                end_num = float(end_val)
                result = start_num + (end_num - start_num) * progress
                return str(result)
            except ValueError:
                pass

        # Handle length properties
        elif prop in ['width', 'height', 'left', 'top', 'margin-left', 'padding-top', 'font-size']:
            start_num, start_unit = self._parse_length_with_unit(start_val)
            end_num, end_unit = self._parse_length_with_unit(end_val)

            if start_unit == end_unit:
                result_num = start_num + (end_num - start_num) * progress
                return f"{result_num}{start_unit}"

        # Handle color properties
        elif prop in ['color', 'background-color', 'border-color']:
            start_color = self._parse_color_to_rgba(start_val)
            end_color = self._parse_color_to_rgba(end_val)

            if start_color and end_color:
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                a = start_color[3] + (end_color[3] - start_color[3]) * progress

                if a == 1.0:
                    return f"rgb({r}, {g}, {b})"
                else:
                    return f"rgba({r}, {g}, {b}, {a})"

        # For non-interpolatable properties, use discrete change at 50%
        return end_val if progress >= 0.5 else start_val

    def _parse_length_with_unit(self, value: str) -> Tuple[float, str]:
        """Parse length value and return number and unit"""
        if not value:
            return 0, 'px'

        for unit in ['px', '%', 'em', 'rem', 'vh', 'vw']:
            if value.endswith(unit):
                return float(value[:-len(unit)]), unit

        try:
            return float(value), 'px'
        except ValueError:
            return 0, 'px'

    def _parse_color_to_rgba(self, color: str) -> Optional[Tuple[int, int, int, float]]:
        """Parse color to RGBA tuple"""
        if color.startswith('#'):
            if len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                return (r, g, b, 1.0)

        elif color.startswith('rgb'):
            match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9.]+))?\s*\)', color)
            if match:
                r, g, b = map(int, match.groups()[:3])
                a = float(match.group(4)) if match.group(4) else 1.0
                return (r, g, b, a)

        return None

    def _get_element_property(self, element: HTMLElement, prop: str) -> str:
        """Get current property value from element"""
        return element.computed_style.get(prop, "")

    def _apply_keyframe_properties(self, element: HTMLElement, properties: Dict[str, str]):
        """Apply keyframe properties to element"""
        for prop, value in properties.items():
            element.computed_style[prop] = value
            # Store in animated properties for transition system
            if hasattr(element.layout_box, 'animated_properties'):
                element.layout_box.animated_properties[prop] = value

    def _apply_fill_mode(self, element: HTMLElement, animation: Animation, finished: bool):
        """Apply animation fill mode"""
        if not finished and animation.fill_mode in ["backwards", "both"]:
            # Apply 0% keyframe (converted from 'from')
            if animation.name in self.keyframes:
                from_frame = self.keyframes[animation.name].get('0%')
                if from_frame:
                    self._apply_keyframe_properties(element, from_frame)

        elif finished and animation.fill_mode in ["forwards", "both"]:
            # Apply 100% keyframe (converted from 'to')
            if animation.name in self.keyframes:
                to_frame = self.keyframes[animation.name].get('100%')
                if to_frame:
                    self._apply_keyframe_properties(element, to_frame)


class TransitionEngine:
    """Handles CSS transitions"""

    def __init__(self):
        self.active_transitions: Dict[HTMLElement, List[Transition]] = {}

    def start_transition(self, element: HTMLElement, property: str, start_value: str, end_value: str,
                         duration: float, timing_function: TimingFunction, delay: float):
        """Start a transition"""
        if element not in self.active_transitions:
            self.active_transitions[element] = []

        # Stop any existing transition for this property
        self.active_transitions[element] = [
            t for t in self.active_transitions[element] if t.property != property
        ]

        transition = Transition(
            property=property,
            duration=duration,
            timing_function=timing_function,
            delay=delay,
            start_time=time.time(),
            start_value=start_value,
            end_value=end_value,
            active=True
        )

        self.active_transitions[element].append(transition)

    def update_transitions(self, current_time: float) -> List[HTMLElement]:
        """Update all active transitions"""
        updated_elements = []

        for element, transitions in list(self.active_transitions.items()):
            active_transitions = []

            for transition in transitions:
                if self._update_transition(element, transition, current_time):
                    active_transitions.append(transition)
                    updated_elements.append(element)

            if active_transitions:
                self.active_transitions[element] = active_transitions
            else:
                del self.active_transitions[element]

        return updated_elements

    def _update_transition(self, element: HTMLElement, transition: Transition, current_time: float) -> bool:
        """Update single transition"""
        elapsed = current_time - transition.start_time - transition.delay

        if elapsed < 0:
            return True  # Still in delay

        if elapsed >= transition.duration:
            # Transition complete
            element.computed_style[transition.property] = transition.end_value
            return False

        # Calculate progress and apply easing
        progress = elapsed / transition.duration
        eased_progress = self._apply_timing_function(progress, transition.timing_function)

        # Interpolate value
        interpolated_value = self._interpolate_values(
            transition.start_value, transition.end_value, eased_progress
        )

        element.computed_style[transition.property] = interpolated_value
        return True

    def _apply_timing_function(self, progress: float, timing_function: TimingFunction) -> float:
        """Apply timing function"""
        animation_engine = AnimationEngine()
        return animation_engine._apply_timing_function(progress, timing_function)

    def _interpolate_values(self, start_val: str, end_val: str, progress: float) -> str:
        """Interpolate between start and end values"""
        animation_engine = AnimationEngine()
        return animation_engine._interpolate_property_value("generic", start_val, end_val, progress)


class UltraEnhancedCSSEngine(EnhancedCSSEngine):
    """Ultra-enhanced CSS engine extending Enhanced with animations, typography, and effects"""

    def __init__(self):
        super().__init__()  # Get ALL Enhanced functionality + base functionality
        self.animation_engine = AnimationEngine()
        self.transition_engine = TransitionEngine()

        # Add ultra-specific properties to the enhanced defaults
        self.default_styles.update({
            # Animation properties (NEW - Ultra level)
            'animation': 'none',
            'animation-name': 'none',
            'animation-duration': '0s',
            'animation-timing-function': 'ease',
            'animation-delay': '0s',
            'animation-iteration-count': '1',
            'animation-direction': 'normal',
            'animation-fill-mode': 'none',
            'animation-play-state': 'running',

            # Transition properties (NEW - Ultra level)
            'transition': 'none',
            'transition-property': 'all',
            'transition-duration': '0s',
            'transition-timing-function': 'ease',
            'transition-delay': '0s',

            # Typography properties (NEW - Ultra level)
            'text-shadow': 'none',
            'font-variant': 'normal',
            'text-indent': '0',
            'word-break': 'normal',
            'overflow-wrap': 'normal',
            'text-overflow': 'clip',
            'line-break': 'auto',
            'hyphens': 'manual',
            'text-rendering': 'auto',
            'font-feature-settings': 'normal',

            # User interface properties (NEW - Ultra level)
            'cursor': 'auto',
            'user-select': 'auto',
            'pointer-events': 'auto',
            'resize': 'none',
            'caret-color': 'auto',
            'accent-color': 'auto',
            'appearance': 'auto',
            'outline-offset': '0',

            # Visual effects properties (NEW - Ultra level)
            'filter': 'none',
            'backdrop-filter': 'none',
            'clip-path': 'none',
            'mask': 'none',
            'mix-blend-mode': 'normal',
            'isolation': 'auto',
            'object-fit': 'fill',
            'object-position': '50% 50%',
            'aspect-ratio': 'auto',
            'contain': 'none',
            'content-visibility': 'visible',
            'will-change': 'auto'
        })

    def parse_css(self, css_string: str):
        """Ultra parsing extending Enhanced with keyframes"""
        # Get all Enhanced parsing first (which includes base parsing)
        super().parse_css(css_string)

        # Add ultra-specific parsing
        self._parse_ultra_keyframes(css_string)

    def _parse_ultra_keyframes(self, css_string: str):
        """Parse @keyframes rules"""
        keyframe_pattern = r'@keyframes\s+(\w+)\s*\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}'
        matches = re.finditer(keyframe_pattern, css_string, re.DOTALL)

        for match in matches:
            name = match.group(1)
            content = match.group(2)
            keyframe_data = self._parse_keyframe_content(content)
            self.animation_engine.add_keyframe(name, keyframe_data)

    def _parse_keyframe_content(self, content: str) -> Dict[str, Dict[str, str]]:
        """Parse keyframe content"""
        steps = {}

        step_pattern = r'(\d+%|from|to)\s*\{([^}]+)\}'
        matches = re.finditer(step_pattern, content)

        for match in matches:
            selector = match.group(1)
            declarations = match.group(2)

            # Convert from/to to percentages
            if selector == 'from':
                selector = '0%'
            elif selector == 'to':
                selector = '100%'

            steps[selector] = self._parse_declarations_string(declarations)

        return steps

    def _parse_declarations_string(self, declarations: str) -> Dict[str, str]:
        """Parse CSS declarations from string"""
        result = {}
        for declaration in declarations.split(';'):
            declaration = declaration.strip()
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                result[prop.strip()] = value.strip()
        return result

    def compute_style(self, element: HTMLElement) -> Dict[str, str]:
        """Ultra-enhanced style computation extending Enhanced"""
        # Get all Enhanced computed style first (which includes base)
        style = super().compute_style(element)

        # Process ultra-specific shorthand properties
        self._process_ultra_shorthand_properties(style)

        # Ensure we have ultra-enhanced layout box
        if not hasattr(element, 'layout_box') or element.layout_box is None:
            element.layout_box = UltraEnhancedLayoutBox()
        elif not isinstance(element.layout_box, UltraEnhancedLayoutBox):
            old_box = element.layout_box
            element.layout_box = UltraEnhancedLayoutBox()
            # Copy all enhanced properties
            for attr in dir(old_box):
                if not attr.startswith('_') and hasattr(element.layout_box, attr):
                    try:
                        setattr(element.layout_box, attr, getattr(old_box, attr))
                    except:
                        pass

        # Apply ultra-specific properties
        self._apply_ultra_properties(element, style)

        return style

    def _process_ultra_shorthand_properties(self, style: Dict[str, str]):
        """Process ultra-specific shorthand properties"""

        # Animation shorthand
        if 'animation' in style and style['animation'] != 'none':
            animation_parts = style['animation'].split()
            if animation_parts:
                for i, part in enumerate(animation_parts):
                    if i == 0 and not part.replace('.', '').replace('s', '').isdigit():
                        style['animation-name'] = part
                    elif part.endswith('s') or part.replace('.', '').isdigit():
                        if 'animation-duration' not in style:
                            style['animation-duration'] = part
                        elif 'animation-delay' not in style:
                            style['animation-delay'] = part
                    elif part in ['ease', 'linear', 'ease-in', 'ease-out', 'ease-in-out']:
                        style['animation-timing-function'] = part
                    elif part.isdigit() or part == 'infinite':
                        style['animation-iteration-count'] = part
                    elif part in ['normal', 'reverse', 'alternate', 'alternate-reverse']:
                        style['animation-direction'] = part
                    elif part in ['none', 'forwards', 'backwards', 'both']:
                        style['animation-fill-mode'] = part
                    elif part in ['running', 'paused']:
                        style['animation-play-state'] = part

        # Transition shorthand
        if 'transition' in style and style['transition'] != 'none':
            transition_parts = style['transition'].split()
            if transition_parts:
                for i, part in enumerate(transition_parts):
                    if part.endswith('s') or part.replace('.', '').isdigit():
                        if 'transition-duration' not in style:
                            style['transition-duration'] = part
                        elif 'transition-delay' not in style:
                            style['transition-delay'] = part
                    elif part in ['ease', 'linear', 'ease-in', 'ease-out', 'ease-in-out']:
                        style['transition-timing-function'] = part
                    elif i == 0:
                        style['transition-property'] = part

    def _apply_ultra_properties(self, element: HTMLElement, style: Dict[str, str]):
        """Apply all ultra-specific properties to element layout box"""
        box = element.layout_box

        # Animation properties
        self._apply_ultra_animation_properties(element, style)

        # Transition properties
        self._apply_ultra_transition_properties(element, style)

        # Typography properties
        self._apply_ultra_typography_properties(box, style)

        # User interface properties
        self._apply_ultra_ui_properties(box, style)

        # Visual effects properties
        self._apply_ultra_visual_effects_properties(box, style)

    def _apply_ultra_animation_properties(self, element: HTMLElement, style: Dict[str, str]):
        """Apply ultra animation properties"""
        animation_name = style.get('animation-name', 'none')

        if animation_name != 'none':
            # Parse animation properties
            duration = self._parse_ultra_time(style.get('animation-duration', '0s'))
            timing_function = self._parse_ultra_timing_function(style.get('animation-timing-function', 'ease'))
            delay = self._parse_ultra_time(style.get('animation-delay', '0s'))
            iteration_count = style.get('animation-iteration-count', '1')
            direction = style.get('animation-direction', 'normal')
            fill_mode = style.get('animation-fill-mode', 'none')
            play_state = style.get('animation-play-state', 'running')

            # Create animation object
            animation = Animation(
                name=animation_name,
                duration=duration,
                timing_function=timing_function,
                delay=delay,
                iteration_count=int(iteration_count) if iteration_count.isdigit() else iteration_count,
                direction=direction,
                fill_mode=fill_mode,
                play_state=play_state
            )

            # Start animation
            self.animation_engine.start_animation(element, animation)

    def _apply_ultra_transition_properties(self, element: HTMLElement, style: Dict[str, str]):
        """Apply ultra transition properties"""
        transition_property = style.get('transition-property', 'all')
        transition_duration = self._parse_ultra_time(style.get('transition-duration', '0s'))

        if transition_duration > 0:
            transition_timing_function = self._parse_ultra_timing_function(
                style.get('transition-timing-function', 'ease'))
            transition_delay = self._parse_ultra_time(style.get('transition-delay', '0s'))

            # Store transition config
            if not hasattr(element, '_transition_config'):
                element._transition_config = {}

            element._transition_config = {
                'property': transition_property,
                'duration': transition_duration,
                'timing_function': transition_timing_function,
                'delay': transition_delay
            }

    def _apply_ultra_typography_properties(self, box: UltraEnhancedLayoutBox, style: Dict[str, str]):
        """Apply ultra typography properties"""

        # Text shadow
        text_shadow = style.get('text-shadow', 'none')
        if text_shadow != 'none':
            box.text_shadows = self._parse_ultra_text_shadows(text_shadow)

        # Font variant
        box.font_variant = style.get('font-variant', 'normal')

        # Text properties
        box.text_indent = self._parse_ultra_length(style.get('text-indent', '0'))
        box.word_break = style.get('word-break', 'normal')
        box.overflow_wrap = style.get('overflow-wrap', 'normal')
        box.text_overflow = style.get('text-overflow', 'clip')
        box.line_break = style.get('line-break', 'auto')
        box.hyphens = style.get('hyphens', 'manual')
        box.text_rendering = style.get('text-rendering', 'auto')

    def _apply_ultra_ui_properties(self, box: UltraEnhancedLayoutBox, style: Dict[str, str]):
        """Apply ultra user interface properties"""

        # Cursor
        cursor_value = style.get('cursor', 'auto')
        try:
            box.cursor = CursorType(cursor_value)
        except ValueError:
            box.cursor = CursorType.AUTO

        # User interaction
        box.user_select = style.get('user-select', 'auto')
        box.pointer_events = style.get('pointer-events', 'auto')
        box.resize = style.get('resize', 'none')

        # Colors
        caret_color = style.get('caret-color', 'auto')
        if caret_color != 'auto':
            box.caret_color = self._parse_ultra_color_to_rgb(caret_color)

        accent_color = style.get('accent-color', 'auto')
        if accent_color != 'auto':
            box.accent_color = self._parse_ultra_color_to_rgb(accent_color)

        # Appearance and outline
        box.appearance = style.get('appearance', 'auto')
        box.outline_offset = self._parse_ultra_length(style.get('outline-offset', '0'))

    def _apply_ultra_visual_effects_properties(self, box: UltraEnhancedLayoutBox, style: Dict[str, str]):
        """Apply ultra visual effects properties"""

        # Filters
        filter_value = style.get('filter', 'none')
        if filter_value != 'none':
            box.filters = self._parse_ultra_filters(filter_value)

        backdrop_filter_value = style.get('backdrop-filter', 'none')
        if backdrop_filter_value != 'none':
            box.backdrop_filters = self._parse_ultra_filters(backdrop_filter_value)

        # Clip path
        clip_path = style.get('clip-path', 'none')
        if clip_path != 'none':
            box.clip_path = self._parse_ultra_clip_path(clip_path)

        # Mask
        mask = style.get('mask', 'none')
        if mask != 'none':
            box.mask = mask

        # Blend mode
        blend_mode = style.get('mix-blend-mode', 'normal')
        try:
            box.mix_blend_mode = BlendMode(blend_mode)
        except ValueError:
            box.mix_blend_mode = BlendMode.NORMAL

        # Other properties
        box.isolation = style.get('isolation', 'auto')
        box.object_fit = style.get('object-fit', 'fill')

        object_position = style.get('object-position', '50% 50%')
        pos_parts = object_position.split()
        if len(pos_parts) >= 2:
            box.object_position = (pos_parts[0], pos_parts[1])

        # Aspect ratio
        aspect_ratio = style.get('aspect-ratio', 'auto')
        if aspect_ratio != 'auto':
            try:
                if '/' in aspect_ratio:
                    w, h = aspect_ratio.split('/')
                    box.aspect_ratio = float(w) / float(h)
                else:
                    box.aspect_ratio = float(aspect_ratio)
            except ValueError:
                pass

        box.contain = style.get('contain', 'none')
        box.content_visibility = style.get('content-visibility', 'visible')

        # Will change
        will_change = style.get('will-change', 'auto')
        if will_change != 'auto':
            box.will_change = [prop.strip() for prop in will_change.split(',')]

    def update_animations(self) -> List[HTMLElement]:
        """Update all animations and transitions - Ultra functionality"""
        current_time = time.time()

        updated_elements = []
        updated_elements.extend(self.animation_engine.update_animations(current_time))
        updated_elements.extend(self.transition_engine.update_transitions(current_time))

        return list(set(updated_elements))  # Remove duplicates

    # Ultra-specific parsing methods
    def _parse_ultra_time(self, time_value: str) -> float:
        """Parse time value in seconds"""
        if time_value.endswith('ms'):
            return float(time_value[:-2]) / 1000.0
        elif time_value.endswith('s'):
            return float(time_value[:-1])
        else:
            try:
                return float(time_value)
            except ValueError:
                return 0.0

    def _parse_ultra_timing_function(self, timing_function: str) -> TimingFunction:
        """Parse timing function"""
        try:
            return TimingFunction(timing_function)
        except ValueError:
            return TimingFunction.EASE

    def _parse_ultra_text_shadows(self, text_shadow: str) -> List[TextShadow]:
        """Parse text-shadow property"""
        shadows = []

        # Split by comma for multiple shadows
        shadow_strings = text_shadow.split(',')

        for shadow_string in shadow_strings:
            shadow_string = shadow_string.strip()
            parts = shadow_string.split()

            if len(parts) >= 2:
                shadow = TextShadow()

                # Parse offset-x offset-y [blur-radius] [color]
                shadow.offset_x = self._parse_ultra_length(parts[0])
                shadow.offset_y = self._parse_ultra_length(parts[1])

                color_part = None
                if len(parts) >= 3:
                    # Check if third part is a length (blur) or color
                    try:
                        shadow.blur_radius = self._parse_ultra_length(parts[2])
                        if len(parts) >= 4:
                            color_part = parts[3]
                    except:
                        color_part = parts[2]

                if color_part:
                    parsed_color = self._parse_ultra_color_to_rgba(color_part)
                    if parsed_color:
                        shadow.color = parsed_color

                shadows.append(shadow)

        return shadows

    def _parse_ultra_filters(self, filter_value: str) -> List[Filter]:
        """Parse filter property"""
        filters = []

        # Parse filter functions
        filter_pattern = r'(\w+)\(([^)]+)\)'
        matches = re.finditer(filter_pattern, filter_value)

        for match in matches:
            function_name = match.group(1)
            function_args = match.group(2).strip()

            filter_obj = Filter(type=function_name)

            # Parse function arguments
            if function_name == 'blur':
                filter_obj.value = self._parse_ultra_length(function_args)
                filter_obj.unit = 'px'
            elif function_name in ['brightness', 'contrast', 'saturate', 'opacity']:
                if function_args.endswith('%'):
                    filter_obj.value = float(function_args[:-1]) / 100.0
                else:
                    filter_obj.value = float(function_args)
            elif function_name in ['hue-rotate']:
                if function_args.endswith('deg'):
                    filter_obj.value = float(function_args[:-3])
                    filter_obj.unit = 'deg'

            filters.append(filter_obj)

        return filters

    def _parse_ultra_clip_path(self, clip_path: str) -> Optional[ClipPath]:
        """Parse clip-path property"""
        if clip_path.startswith('circle('):
            # Parse circle(radius at x y)
            content = clip_path[7:-1]  # Remove 'circle(' and ')'
            clip = ClipPath(type='circle')

            # Simple parsing - full implementation would be more robust
            if 'at' in content:
                radius_part, position_part = content.split(' at ')
                clip.values = [self._parse_ultra_length(radius_part.strip())]
            else:
                clip.values = [self._parse_ultra_length(content.strip())]

            return clip

        elif clip_path.startswith('polygon('):
            # Parse polygon(x1 y1, x2 y2, ...)
            content = clip_path[8:-1]  # Remove 'polygon(' and ')'
            clip = ClipPath(type='polygon')

            points = []
            for point in content.split(','):
                coords = point.strip().split()
                if len(coords) >= 2:
                    points.extend([self._parse_ultra_length(coords[0]), self._parse_ultra_length(coords[1])])

            clip.values = points
            return clip

        return None

    def _parse_ultra_color_to_rgb(self, color: str) -> Optional[Tuple[int, int, int]]:
        """Parse color to RGB tuple"""
        rgba = self._parse_ultra_color_to_rgba(color)
        if rgba:
            return rgba[:3]
        return None

    def _parse_ultra_color_to_rgba(self, color: str) -> Optional[Tuple[int, int, int, int]]:
        """Parse color to RGBA tuple"""
        if color.startswith('#'):
            if len(color) == 7:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                return (r, g, b, 255)

        elif color.startswith('rgb'):
            match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9.]+))?\s*\)', color)
            if match:
                r, g, b = map(int, match.groups()[:3])
                a = int(float(match.group(4)) * 255) if match.group(4) else 255
                return (r, g, b, a)

        # Named colors
        named_colors = {
            'black': (0, 0, 0, 255), 'white': (255, 255, 255, 255),
            'red': (255, 0, 0, 255), 'green': (0, 128, 0, 255), 'blue': (0, 0, 255, 255),
            'yellow': (255, 255, 0, 255), 'cyan': (0, 255, 255, 255), 'magenta': (255, 0, 255, 255),
            'gray': (128, 128, 128, 255), 'grey': (128, 128, 128, 255)
        }

        return named_colors.get(color.lower())

    def _parse_ultra_length(self, value: str, container_size: float = 0) -> float:
        """Parse CSS length value with ultra support"""
        if not value or value == 'auto':
            return 0

        try:
            if value.endswith('px'):
                return float(value[:-2])
            elif value.endswith('%'):
                return container_size * (float(value[:-1]) / 100)
            elif value.endswith('em'):
                return float(value[:-2]) * 16
            elif value.endswith('rem'):
                return float(value[:-3]) * 16
            else:
                return float(value)
        except (ValueError, TypeError):
            return 0


class UltraEnhancedLayoutEngine(EnhancedLayoutEngine):
    """Ultra-enhanced layout engine extending Enhanced with animation-aware layout"""

    def __init__(self, viewport_width: int = 1200, viewport_height: int = 800):
        super().__init__(viewport_width, viewport_height)  # Get ALL Enhanced functionality
        self.animation_affected_elements: List[HTMLElement] = []

    def layout(self, element: HTMLElement, container_width: float = None,
               container_height: float = None, is_root: bool = True,
               parent_x: float = 0, parent_y: float = 0):
        """Ultra-enhanced layout extending Enhanced with animation considerations"""

        # Call enhanced layout first (which includes all base functionality)
        super().layout(element, container_width, container_height, is_root, parent_x, parent_y)

        # Apply ultra-specific layout considerations
        self._apply_ultra_layout_properties(element)

        # Handle animation-affected layout
        self._handle_ultra_animation_layout(element)

    def _apply_ultra_layout_properties(self, element: HTMLElement):
        """Apply ultra-specific layout properties"""
        if not isinstance(element.layout_box, UltraEnhancedLayoutBox):
            return

        box = element.layout_box
        style = element.computed_style

        # Handle aspect ratio
        if hasattr(box, 'aspect_ratio') and box.aspect_ratio:
            if style.get('width', 'auto') != 'auto' and style.get('height', 'auto') == 'auto':
                box.height = box.width / box.aspect_ratio
            elif style.get('height', 'auto') != 'auto' and style.get('width', 'auto') == 'auto':
                box.width = box.height * box.aspect_ratio

        # Handle content visibility
        if hasattr(box, 'content_visibility') and box.content_visibility == 'hidden':
            box.width = 0
            box.height = 0

    def _handle_ultra_animation_layout(self, element: HTMLElement):
        """Handle layout for animated elements"""
        if not isinstance(element.layout_box, UltraEnhancedLayoutBox):
            return

        box = element.layout_box

        # Check if element has animations that affect layout
        if hasattr(box, 'will_change') and box.will_change:
            layout_affecting_props = ['width', 'height', 'margin', 'padding', 'transform']
            if any(prop in box.will_change for prop in layout_affecting_props):
                self.animation_affected_elements.append(element)
                # Pre-allocate space for transforms if needed
                if 'transform' in box.will_change:
                    # Add some buffer space for transform effects
                    box.width = int(box.width * 1.2)  # 20% buffer
                    box.height = int(box.height * 1.2)


class UltraEnhancedMarkupRenderer(EnhancedMarkupRenderer):
    """Ultra-enhanced renderer extending Enhanced with animation and advanced effects"""

    def __init__(self):
        super().__init__()  # Get ALL Enhanced functionality + base functionality
        self.ultra_filter_cache = {}
        self.ultra_shadow_cache = {}
        self.animation_surfaces = {}  # Cache for animated surfaces

        # Initialize blend mode mapping
        self.blend_modes = {
            BlendMode.MULTIPLY: pygame.BLEND_MULT,
            BlendMode.SCREEN: pygame.BLEND_ALPHA_SDL2,  # Closest available
            BlendMode.OVERLAY: pygame.BLEND_ALPHA_SDL2,
            BlendMode.DARKEN: pygame.BLEND_SUB,
            BlendMode.LIGHTEN: pygame.BLEND_ADD,
        }

    def render_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Ultra-enhanced rendering extending Enhanced functionality"""
        if not element.layout_box:
            return

        # Check ultra-specific visibility rules
        if isinstance(element.layout_box, UltraEnhancedLayoutBox):
            box = element.layout_box
            if hasattr(box, 'content_visibility') and box.content_visibility == 'hidden':
                return

            # Check pointer events
            if hasattr(box, 'pointer_events') and box.pointer_events == 'none':
                # Still render but mark as non-interactive
                pass

        # Check for ultra-specific effects
        has_ultra_effects = self._has_ultra_effects(element)

        if has_ultra_effects:
            # Use ultra rendering for advanced effects
            self._render_ultra_element(element, target_surface)
        else:
            # Use enhanced rendering for standard effects (which includes base)
            super().render_element(element, target_surface)

    def _has_ultra_effects(self, element: HTMLElement) -> bool:
        """Check if element has ultra-specific effects"""
        if not isinstance(element.layout_box, UltraEnhancedLayoutBox):
            return False

        box = element.layout_box

        return (hasattr(box, 'filters') and box.filters or
                hasattr(box, 'text_shadows') and box.text_shadows or
                hasattr(box, 'clip_path') and box.clip_path or
                hasattr(box, 'mix_blend_mode') and box.mix_blend_mode != BlendMode.NORMAL or
                hasattr(box, 'backdrop_filters') and box.backdrop_filters)

    def _render_ultra_element(self, element: HTMLElement, target_surface: pygame.Surface):
        """Render element with ultra-enhanced effects"""
        if not element.layout_box:
            return

        box = element.layout_box
        if box.width <= 0 or box.height <= 0:
            return

        # Create element surface
        elem_surface = pygame.Surface((int(box.width), int(box.height)), pygame.SRCALPHA)

        # Render element content with ultra typography
        self._render_ultra_element_content(element, elem_surface)

        # Apply ultra visual effects
        processed_surface = self._apply_ultra_visual_effects(elem_surface, box)

        # Apply ultra transforms and positioning
        self._blit_ultra_element_to_target(processed_surface, target_surface, box)

        # Render children
        for child in element.children:
            self.render_element(child, target_surface)

    def _render_ultra_element_content(self, element: HTMLElement, surface: pygame.Surface):
        """Render element content with ultra-enhanced features"""

        # Use enhanced background and border rendering (inherited)
        self._render_enhanced_background(surface, element)
        self._render_enhanced_border(surface, element)

        # Ultra-enhanced text rendering
        if element.text_content and element.text_content.strip():
            self._render_ultra_advanced_text(surface, element)

    def _render_ultra_advanced_text(self, surface: pygame.Surface, element: HTMLElement):
        """Render text with ultra-advanced typography effects"""
        style = element.computed_style
        box = element.layout_box
        text = element.text_content.strip()

        if not text:
            return

        # Apply text transformations (enhanced from base)
        text = self._apply_ultra_text_transforms(text, style)

        # Get font
        font = self.get_enhanced_font(style)  # Use inherited enhanced font method
        color = self._parse_color(style.get('color', '#000000'))

        if not font or not color:
            return

        # Handle ultra text overflow and wrapping
        processed_text = self._process_ultra_text_overflow(text, font, surface.get_width(), box)

        # Create text surface
        text_surface = font.render(processed_text, True, color)

        # Apply ultra text shadows
        if hasattr(box, 'text_shadows') and box.text_shadows:
            text_surface = self._apply_ultra_text_shadows(text_surface, box.text_shadows, font, processed_text)

        # Position text with ultra alignment
        x, y = self._calculate_ultra_text_position(surface, text_surface, style, box)

        # Apply ultra text effects
        if hasattr(box, 'font_variant') and box.font_variant == 'small-caps':
            text_surface = self._apply_ultra_small_caps(processed_text, font, color)

        surface.blit(text_surface, (x, y))

    def _apply_ultra_text_transforms(self, text: str, style: Dict[str, str]) -> str:
        """Apply ultra text transform properties"""
        text_transform = style.get('text-transform', 'none')

        if text_transform == 'uppercase':
            return text.upper()
        elif text_transform == 'lowercase':
            return text.lower()
        elif text_transform == 'capitalize':
            return text.title()

        return text

    def _process_ultra_text_overflow(self, text: str, font: pygame.font.Font,
                                     max_width: float, box: UltraEnhancedLayoutBox) -> str:
        """Handle ultra text overflow and word breaking"""
        if not hasattr(box, 'text_overflow'):
            return text

        text_width = font.size(text)[0]

        if text_width <= max_width:
            return text

        if box.text_overflow == 'ellipsis':
            # Truncate text and add ellipsis
            ellipsis = '...'
            ellipsis_width = font.size(ellipsis)[0]
            available_width = max_width - ellipsis_width

            if available_width > 0:
                # Binary search for maximum fitting text
                left, right = 0, len(text)
                while left < right:
                    mid = (left + right + 1) // 2
                    if font.size(text[:mid])[0] <= available_width:
                        left = mid
                    else:
                        right = mid - 1

                return text[:left] + ellipsis

        elif hasattr(box, 'word_break') and box.word_break == 'break-all':
            # Break anywhere
            chars = []
            width = 0
            for char in text:
                char_width = font.size(char)[0]
                if width + char_width > max_width:
                    break
                chars.append(char)
                width += char_width
            return ''.join(chars)

        return text

    def _apply_ultra_text_shadows(self, text_surface: pygame.Surface, shadows: List[TextShadow],
                                  font: pygame.font.Font, text: str) -> pygame.Surface:
        """Apply ultra text shadows"""
        if not shadows:
            return text_surface

        # Calculate total bounds needed for shadows
        max_offset_x = max(shadow.offset_x for shadow in shadows)
        min_offset_x = min(shadow.offset_x for shadow in shadows)
        max_offset_y = max(shadow.offset_y for shadow in shadows)
        min_offset_y = min(shadow.offset_y for shadow in shadows)
        max_blur = max(shadow.blur_radius for shadow in shadows)

        # Create larger surface to accommodate shadows
        extra_width = int(abs(max_offset_x - min_offset_x) + max_blur * 2)
        extra_height = int(abs(max_offset_y - min_offset_y) + max_blur * 2)

        shadow_surface = pygame.Surface(
            (text_surface.get_width() + extra_width, text_surface.get_height() + extra_height),
            pygame.SRCALPHA
        )

        # Render shadows (back to front)
        for shadow in reversed(shadows):
            shadow_color = shadow.color[:3]  # RGB only for rendering
            shadow_text = font.render(text, True, shadow_color)

            # Apply blur if needed (simplified)
            if shadow.blur_radius > 0:
                shadow_text = self._apply_ultra_blur_effect(shadow_text, shadow.blur_radius)

            # Position shadow
            shadow_x = int(max_blur + max(0, -min_offset_x) + shadow.offset_x)
            shadow_y = int(max_blur + max(0, -min_offset_y) + shadow.offset_y)

            shadow_surface.blit(shadow_text, (shadow_x, shadow_y))

        # Render main text on top
        text_x = int(max_blur + max(0, -min_offset_x))
        text_y = int(max_blur + max(0, -min_offset_y))
        shadow_surface.blit(text_surface, (text_x, text_y))

        return shadow_surface

    def _apply_ultra_blur_effect(self, surface: pygame.Surface, blur_radius: float) -> pygame.Surface:
        """Apply ultra blur effect to surface (simplified)"""
        if blur_radius <= 0:
            return surface

        # Create multiple copies with slight offsets for blur effect
        blurred = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        blur_steps = max(1, int(blur_radius))

        for i in range(blur_steps):
            offset_x = (i % 3) - 1
            offset_y = (i // 3) - 1
            alpha = 255 // blur_steps

            temp_surface = surface.copy()
            temp_surface.set_alpha(alpha)
            blurred.blit(temp_surface, (offset_x, offset_y))

        return blurred

    def _apply_ultra_small_caps(self, text: str, font: pygame.font.Font,
                                color: Tuple[int, int, int]) -> pygame.Surface:
        """Apply ultra small caps effect"""
        # Simplified implementation - real small caps would use actual small cap fonts
        return font.render(text.upper(), True, color)

    def _calculate_ultra_text_position(self, surface: pygame.Surface, text_surface: pygame.Surface,
                                       style: Dict[str, str], box: UltraEnhancedLayoutBox) -> Tuple[int, int]:
        """Calculate ultra text position with alignment and indentation"""

        # Get text alignment
        text_align = style.get('text-align', 'left')

        # Calculate x position
        x = 0
        if text_align == 'center':
            x = (surface.get_width() - text_surface.get_width()) // 2
        elif text_align == 'right':
            x = surface.get_width() - text_surface.get_width()

        # Apply ultra text indent
        if hasattr(box, 'text_indent'):
            x += int(box.text_indent)

        # Apply padding
        padding_left = getattr(box, 'padding_left', 0)
        padding_top = getattr(box, 'padding_top', 0)

        x = max(x, padding_left)

        # Calculate y position (center vertically)
        available_height = surface.get_height() - padding_top * 2
        if available_height > text_surface.get_height():
            y = padding_top + (available_height - text_surface.get_height()) // 2
        else:
            y = padding_top

        return (int(x), int(y))

    def _apply_ultra_visual_effects(self, surface: pygame.Surface,
                                    box: UltraEnhancedLayoutBox) -> pygame.Surface:
        """Apply all ultra visual effects to the surface"""
        result_surface = surface

        # Apply ultra filters
        if hasattr(box, 'filters') and box.filters:
            result_surface = self._apply_ultra_filters(result_surface, box.filters)

        # Apply ultra clipping
        if hasattr(box, 'clip_path') and box.clip_path:
            result_surface = self._apply_ultra_clip_path(result_surface, box.clip_path)

        # Apply opacity (inherited from enhanced)
        if hasattr(box, 'opacity') and box.opacity < 1.0:
            self._apply_opacity(result_surface, box.opacity)

        return result_surface

    def _apply_ultra_filters(self, surface: pygame.Surface, filters: List[Filter]) -> pygame.Surface:
        """Apply ultra CSS filters"""
        result_surface = surface.copy()

        for filter_obj in filters:
            if filter_obj.type == 'blur':
                result_surface = self._apply_ultra_blur_effect(result_surface, filter_obj.value)

            elif filter_obj.type == 'brightness':
                result_surface = self._apply_ultra_brightness(result_surface, filter_obj.value)

            elif filter_obj.type == 'contrast':
                result_surface = self._apply_ultra_contrast(result_surface, filter_obj.value)

            elif filter_obj.type == 'saturate':
                result_surface = self._apply_ultra_saturation(result_surface, filter_obj.value)

            elif filter_obj.type == 'opacity':
                alpha = int(filter_obj.value * 255)
                result_surface.set_alpha(alpha)

        return result_surface

    def _apply_ultra_brightness(self, surface: pygame.Surface, brightness: float) -> pygame.Surface:
        """Apply ultra brightness filter"""
        result = surface.copy()

        # Create brightness overlay
        if brightness != 1.0:
            if brightness > 1.0:
                # Brighten
                overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                alpha = int((brightness - 1.0) * 255)
                overlay.fill((255, 255, 255, alpha))
                result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            else:
                # Darken
                overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                alpha = int((1.0 - brightness) * 255)
                overlay.fill((0, 0, 0, alpha))
                result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

        return result

    def _apply_ultra_contrast(self, surface: pygame.Surface, contrast: float) -> pygame.Surface:
        """Apply ultra contrast filter (simplified)"""
        # This is a simplified contrast implementation
        # Real contrast would require pixel-level manipulation
        return surface

    def _apply_ultra_saturation(self, surface: pygame.Surface, saturation: float) -> pygame.Surface:
        """Apply ultra saturation filter (simplified)"""
        # This is a simplified saturation implementation
        return surface

    def _apply_ultra_clip_path(self, surface: pygame.Surface, clip_path: ClipPath) -> pygame.Surface:
        """Apply ultra clip-path"""
        if clip_path.type == 'circle':
            return self._clip_ultra_circle(surface, clip_path.values[
                0] if clip_path.values else surface.get_width() // 2)
        elif clip_path.type == 'polygon':
            return self._clip_ultra_polygon(surface, clip_path.values)

        return surface

    def _clip_ultra_circle(self, surface: pygame.Surface, radius: float) -> pygame.Surface:
        """Clip surface to circle with ultra precision"""
        size = surface.get_size()
        center = (size[0] // 2, size[1] // 2)

        # Create mask
        mask_surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), center, int(radius))

        # Apply mask
        result = pygame.Surface(size, pygame.SRCALPHA)
        result.blit(surface, (0, 0))
        result.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return result

    def _clip_ultra_polygon(self, surface: pygame.Surface, points: List[float]) -> pygame.Surface:
        """Clip surface to polygon with ultra precision"""
        if len(points) < 6:  # Need at least 3 points (6 coordinates)
            return surface

        size = surface.get_size()

        # Convert points to pygame format
        polygon_points = []
        for i in range(0, len(points), 2):
            if i + 1 < len(points):
                x = points[i] * size[0] if isinstance(points[i], float) and points[i] <= 1 else points[i]
                y = points[i + 1] * size[1] if isinstance(points[i + 1], float) and points[i + 1] <= 1 else \
                points[i + 1]
                polygon_points.append((int(x), int(y)))

        # Create mask
        mask_surface = pygame.Surface(size, pygame.SRCALPHA)
        if len(polygon_points) >= 3:
            pygame.draw.polygon(mask_surface, (255, 255, 255, 255), polygon_points)

        # Apply mask
        result = pygame.Surface(size, pygame.SRCALPHA)
        result.blit(surface, (0, 0))
        result.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return result

    def _blit_ultra_element_to_target(self, surface: pygame.Surface, target: pygame.Surface,
                                      box: UltraEnhancedLayoutBox):
        """Blit element surface to target with ultra positioning and blend modes"""

        # Apply ultra blend mode
        blend_flag = 0
        if hasattr(box, 'mix_blend_mode') and box.mix_blend_mode in self.blend_modes:
            blend_flag = self.blend_modes[box.mix_blend_mode]

        # Calculate position
        x, y = int(box.x), int(box.y)

        # Apply transform if needed (inherited from enhanced)
        if hasattr(box, 'transform') and self._has_transform(box.transform):
            surface = self._apply_transforms(surface, box.transform)
            # Recalculate position for transformed element
            center_x = box.x + box.width / 2
            center_y = box.y + box.height / 2
            rect = surface.get_rect()
            rect.center = (center_x, center_y)
            x, y = rect.x, rect.y

        # Blit with ultra clipping and blend modes
        if blend_flag:
            target.blit(surface, (x, y), special_flags=blend_flag)
        else:
            target.blit(surface, (x, y))

