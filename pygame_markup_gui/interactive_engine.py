import pygame
from typing import Callable, List, Optional, Dict
from enum import Enum
from dataclasses import dataclass
from .html_engine import HTMLElement


class EventPhase(Enum):
    CAPTURING = 1
    AT_TARGET = 2
    BUBBLING = 3


@dataclass
class InteractiveEvent:
    """Custom event object similar to DOM events"""
    type: str
    target: HTMLElement
    current_target: HTMLElement = None
    phase: EventPhase = EventPhase.BUBBLING
    bubbles: bool = True
    cancelable: bool = True
    stopped: bool = False
    stopped_immediate: bool = False

    # Mouse/keyboard specific data
    pos: tuple = (0, 0)
    button: int = 0
    key: int = 0
    unicode: str = ""

    def stop_propagation(self):
        """Stop event from bubbling further"""
        self.stopped = True

    def stop_immediate_propagation(self):
        """Stop event and prevent other handlers on current element"""
        self.stopped_immediate = True
        self.stopped = True


class ElementState:
    """Track visual/interaction state of elements"""

    def __init__(self):
        self.hovered = False
        self.focused = False
        self.active = False
        self.disabled = False
        self.pressed = False


class InteractionManager:
    """Central manager for all HTML element interactions"""

    def __init__(self, root_element: HTMLElement):
        self.root_element = root_element
        self.focused_element: Optional[HTMLElement] = None
        self.hovered_element: Optional[HTMLElement] = None
        self.active_element: Optional[HTMLElement] = None

        # Element states
        self.element_states: Dict[HTMLElement, ElementState] = {}

        # Event listeners: element -> event_type -> list of handlers
        self.event_listeners: Dict[HTMLElement, Dict[str, List[Callable]]] = {}

        # Focusable elements cache
        self.focusable_elements: List[HTMLElement] = []
        self.focus_index = 0

        # Dragging state
        self.dragging_element: Optional[HTMLElement] = None
        self.drag_offset = (0, 0)

        # Initialize
        self._update_focusable_elements()
        self._initialize_element_states()

    def add_event_listener(self, element: HTMLElement, event_type: str,
                           handler: Callable, use_capture: bool = False):
        """Add event listener to element (DOM-like addEventListener)"""
        if element not in self.event_listeners:
            self.event_listeners[element] = {}
        if event_type not in self.event_listeners[element]:
            self.event_listeners[element][event_type] = []

        # Store handler with capture flag
        self.event_listeners[element][event_type].append({
            'handler': handler,
            'capture': use_capture
        })

    def remove_event_listener(self, element: HTMLElement, event_type: str, handler: Callable):
        """Remove event listener from element"""
        if (element in self.event_listeners and
                event_type in self.event_listeners[element]):
            self.event_listeners[element][event_type] = [
                h for h in self.event_listeners[element][event_type]
                if h['handler'] != handler
            ]

    def dispatch_event(self, event: InteractiveEvent):
        """Dispatch event with proper bubbling/capturing phases"""
        # Build path from root to target
        path = []
        current = event.target
        while current:
            path.append(current)
            current = current.parent
        path.reverse()  # Root to target

        # Capturing phase
        event.phase = EventPhase.CAPTURING
        for element in path[:-1]:  # Exclude target
            if event.stopped:
                break
            event.current_target = element
            self._call_event_handlers(element, event, capture_phase=True)

        # Target phase
        if not event.stopped:
            event.phase = EventPhase.AT_TARGET
            event.current_target = event.target
            self._call_event_handlers(event.target, event, capture_phase=False)

        # Bubbling phase
        if event.bubbles and not event.stopped:
            event.phase = EventPhase.BUBBLING
            for element in reversed(path[:-1]):  # Target to root
                if event.stopped:
                    break
                event.current_target = element
                self._call_event_handlers(element, event, capture_phase=False)

    def _call_event_handlers(self, element: HTMLElement, event: InteractiveEvent,
                             capture_phase: bool):
        """Call appropriate event handlers for element"""
        if element not in self.event_listeners:
            return

        event_type = event.type
        if event_type not in self.event_listeners[element]:
            return

        for handler_info in self.event_listeners[element][event_type]:
            if event.stopped_immediate:
                break

            # Check if handler should be called in this phase
            if handler_info['capture'] == capture_phase:
                try:
                    handler_info['handler'](event)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def handle_mouse_motion(self, pos: tuple) -> bool:
        """Handle mouse motion events"""
        # Find element under mouse
        hit_element = self._get_element_at_position(pos)

        # Handle hover state changes
        if hit_element != self.hovered_element:
            # Mouse leave previous element
            if self.hovered_element:
                self._set_element_state(self.hovered_element, 'hovered', False)
                leave_event = InteractiveEvent(
                    type='mouseleave',
                    target=self.hovered_element,
                    pos=pos,
                    bubbles=False
                )
                self.dispatch_event(leave_event)

            # Mouse enter new element
            if hit_element:
                self._set_element_state(hit_element, 'hovered', True)
                enter_event = InteractiveEvent(
                    type='mouseenter',
                    target=hit_element,
                    pos=pos,
                    bubbles=False
                )
                self.dispatch_event(enter_event)

            self.hovered_element = hit_element

        # Handle dragging
        if self.dragging_element and self.dragging_element.layout_box:
            new_x = pos[0] - self.drag_offset[0]
            new_y = pos[1] - self.drag_offset[1]
            self.dragging_element.layout_box.x = new_x
            self.dragging_element.layout_box.y = new_y

            drag_event = InteractiveEvent(
                type='drag',
                target=self.dragging_element,
                pos=pos
            )
            self.dispatch_event(drag_event)
            return True

        # General mouse move event
        if hit_element:
            move_event = InteractiveEvent(
                type='mousemove',
                target=hit_element,
                pos=pos
            )
            self.dispatch_event(move_event)

        return hit_element is not None

    def handle_mouse_down(self, pos: tuple, button: int) -> bool:
        """Handle mouse button down events"""
        hit_element = self._get_element_at_position(pos)

        if hit_element:
            # Set focus to clicked element if focusable
            if self._is_focusable(hit_element):
                self.set_focus(hit_element)

            # Set active state
            self.active_element = hit_element
            self._set_element_state(hit_element, 'active', True)

            # Check if element is draggable
            if self._is_draggable(hit_element):
                self.dragging_element = hit_element
                box = hit_element.layout_box
                self.drag_offset = (pos[0] - box.x, pos[1] - box.y)

            # Dispatch mouse down event
            mouse_event = InteractiveEvent(
                type='mousedown',
                target=hit_element,
                pos=pos,
                button=button
            )
            self.dispatch_event(mouse_event)

            return True

        # Click outside any element - clear focus
        if self.focused_element:
            self.set_focus(None)

        return False

    def handle_mouse_up(self, pos: tuple, button: int) -> bool:
        """Handle mouse button up events"""
        hit_element = self._get_element_at_position(pos)

        # Clear active state
        if self.active_element:
            self._set_element_state(self.active_element, 'active', False)
            self.active_element = None

        # Handle drag end
        if self.dragging_element:
            # Check for drop targets
            drop_target = None
            if hit_element and hit_element != self.dragging_element:
                if self._is_droppable(hit_element):
                    drop_target = hit_element

            # Dispatch drag end and drop events
            drag_end_event = InteractiveEvent(
                type='dragend',
                target=self.dragging_element,
                pos=pos
            )
            self.dispatch_event(drag_end_event)

            if drop_target:
                drop_event = InteractiveEvent(
                    type='drop',
                    target=drop_target,
                    pos=pos
                )
                self.dispatch_event(drop_event)

            self.dragging_element = None
            self.drag_offset = (0, 0)

        # Dispatch mouse up event
        if hit_element:
            mouse_event = InteractiveEvent(
                type='mouseup',
                target=hit_element,
                pos=pos,
                button=button
            )
            self.dispatch_event(mouse_event)

            # Dispatch click event if mouse was pressed and released on same element
            if hit_element == self.hovered_element:
                click_event = InteractiveEvent(
                    type='click',
                    target=hit_element,
                    pos=pos,
                    button=button
                )
                self.dispatch_event(click_event)

        return hit_element is not None

    def handle_key_down(self, key: int, unicode: str = "") -> bool:
        """Handle keyboard events"""
        # Tab navigation
        if key == pygame.K_TAB:
            shift_pressed = pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
            self._navigate_focus(-1 if shift_pressed else 1)
            return True

        # Enter/Space on focused element
        if key in [pygame.K_RETURN, pygame.K_SPACE]:
            if self.focused_element:
                # Simulate click on focused element
                if self.focused_element.layout_box:
                    center_x = self.focused_element.layout_box.x + self.focused_element.layout_box.width // 2
                    center_y = self.focused_element.layout_box.y + self.focused_element.layout_box.height // 2

                    click_event = InteractiveEvent(
                        type='click',
                        target=self.focused_element,
                        pos=(center_x, center_y)
                    )
                    self.dispatch_event(click_event)
                return True

        # Arrow key navigation for certain elements
        if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            if self.focused_element:
                arrow_event = InteractiveEvent(
                    type='keydown',
                    target=self.focused_element,
                    key=key,
                    unicode=unicode
                )
                self.dispatch_event(arrow_event)
                return True

        # Dispatch to focused element
        if self.focused_element:
            key_event = InteractiveEvent(
                type='keydown',
                target=self.focused_element,
                key=key,
                unicode=unicode
            )
            self.dispatch_event(key_event)
            return True

        return False

    def handle_mouse_wheel(self, delta: int, pos: tuple) -> bool:
        """Handle mouse wheel events"""
        hit_element = self._get_element_at_position(pos)

        if hit_element:
            # Find scrollable container
            scrollable = self._find_scrollable_parent(hit_element)
            if scrollable:
                wheel_event = InteractiveEvent(
                    type='wheel',
                    target=scrollable,
                    pos=pos
                )
                # Add scroll delta as custom property
                wheel_event.delta = delta
                self.dispatch_event(wheel_event)
                return True

        return False

    def set_focus(self, element: Optional[HTMLElement]):
        """Set focus to specific element"""
        if self.focused_element == element:
            return

        # Blur previous element
        if self.focused_element:
            self._set_element_state(self.focused_element, 'focused', False)
            blur_event = InteractiveEvent(
                type='blur',
                target=self.focused_element,
                bubbles=False
            )
            self.dispatch_event(blur_event)

        # Focus new element
        self.focused_element = element
        if element:
            self._set_element_state(element, 'focused', True)
            # Update focus index
            if element in self.focusable_elements:
                self.focus_index = self.focusable_elements.index(element)

            focus_event = InteractiveEvent(
                type='focus',
                target=element,
                bubbles=False
            )
            self.dispatch_event(focus_event)

    def get_element_state(self, element: HTMLElement) -> ElementState:
        """Get current state of element"""
        if element not in self.element_states:
            self.element_states[element] = ElementState()
        return self.element_states[element]

    def _set_element_state(self, element: HTMLElement, state_name: str, value: bool):
        """Set element state and trigger visual updates"""
        state = self.get_element_state(element)
        setattr(state, state_name, value)

        # Apply visual state changes to computed style
        self._apply_state_styles(element, state)

    def _apply_state_styles(self, element: HTMLElement, state: ElementState):
        """Apply CSS-like state styles (hover, focus, active)"""
        # This could be expanded to support CSS pseudo-classes
        # For now, just modify some basic properties

        if state.hovered and element.tag == 'button':
            # Brighten button on hover
            element.computed_style['background-color'] = '#0088ff'
        elif element.tag == 'button':
            # Default button color
            element.computed_style['background-color'] = '#007acc'

        if state.focused:
            # Add focus outline
            element.computed_style['border-color'] = '#ff6600'
            element.computed_style['border-width'] = '2px'

        if state.active:
            # Pressed appearance
            if element.tag == 'button':
                element.computed_style['background-color'] = '#005580'

    def _get_element_at_position(self, pos: tuple) -> Optional[HTMLElement]:
        """Find the topmost element at given position"""
        return self._find_element_recursive(self.root_element, pos)

    def _find_element_recursive(self, element: HTMLElement, pos: tuple) -> Optional[HTMLElement]:
        """Recursively find element at position (depth-first for topmost)"""
        if not element.layout_box:
            return None

        # Check if position is within element bounds
        box = element.layout_box
        if (pos[0] >= box.x and pos[0] < box.x + box.width and
                pos[1] >= box.y and pos[1] < box.y + box.height):

            # Check children first (they're on top)
            for child in reversed(element.children):  # Reverse for z-order
                hit_child = self._find_element_recursive(child, pos)
                if hit_child:
                    return hit_child

            # No child hit, return this element if it's interactive
            if self._is_interactive(element):
                return element

        return None

    def _is_interactive(self, element: HTMLElement) -> bool:
        """Check if element should receive mouse events"""
        # All elements can receive events, but text nodes are usually skipped
        return element.tag != 'text'

    def _is_focusable(self, element: HTMLElement) -> bool:
        """Check if element can receive keyboard focus"""
        focusable_tags = {'button', 'input', 'select', 'textarea', 'a'}

        # Check tag type
        if element.tag.lower() in focusable_tags:
            return True

        # Check for tabindex attribute
        tabindex = element.attributes.get('tabindex')
        if tabindex is not None:
            try:
                return int(tabindex) >= 0
            except ValueError:
                pass

        return False

    def _is_draggable(self, element: HTMLElement) -> bool:
        """Check if element is draggable"""
        # Check draggable attribute
        draggable = element.attributes.get('draggable', '').lower()
        if draggable == 'true':
            return True

        # Some elements are draggable by default
        return element.tag.lower() in {'img'}

    def _is_droppable(self, element: HTMLElement) -> bool:
        """Check if element can be a drop target"""
        # For now, consider div and container elements as droppable
        return element.tag.lower() in {'div', 'section', 'main', 'article'}

    def _find_scrollable_parent(self, element: HTMLElement) -> Optional[HTMLElement]:
        """Find nearest scrollable parent element"""
        current = element
        while current:
            style = current.computed_style
            overflow = style.get('overflow', 'visible')
            if overflow in ['scroll', 'auto']:
                return current
            current = current.parent
        return None

    def _update_focusable_elements(self):
        """Update list of focusable elements in tab order"""
        self.focusable_elements = []
        self._collect_focusable_recursive(self.root_element)

    def _collect_focusable_recursive(self, element: HTMLElement):
        """Recursively collect focusable elements"""
        if self._is_focusable(element):
            self.focusable_elements.append(element)

        for child in element.children:
            self._collect_focusable_recursive(child)

    def _navigate_focus(self, direction: int):
        """Navigate focus in tab order"""
        if not self.focusable_elements:
            return

        if self.focused_element is None:
            # No current focus, focus first element
            self.set_focus(self.focusable_elements[0])
            self.focus_index = 0
        else:
            # Move focus
            self.focus_index = (self.focus_index + direction) % len(self.focusable_elements)
            self.set_focus(self.focusable_elements[self.focus_index])

    def _initialize_element_states(self):
        """Initialize states for all elements"""
        self._initialize_recursive(self.root_element)

    def _initialize_recursive(self, element: HTMLElement):
        """Recursively initialize element states"""
        self.element_states[element] = ElementState()
        for child in element.children:
            self._initialize_recursive(child)


# Convenience classes for specific behaviors
class FormHandler:
    """Handle form-specific interactions"""

    def __init__(self, interaction_manager: InteractionManager):
        self.manager = interaction_manager

    def setup_button(self, button_element: HTMLElement, on_click: Callable = None):
        """Setup button with click handler"""

        def handle_click(event):
            print(f"Button '{button_element.text_content}' clicked!")
            if on_click:
                on_click(event)

        self.manager.add_event_listener(button_element, 'click', handle_click)

    def setup_input(self, input_element: HTMLElement, on_change: Callable = None):
        """Setup input field with change handler"""

        def handle_key(event):
            if event.key == pygame.K_RETURN and on_change:
                on_change(event)

        self.manager.add_event_listener(input_element, 'keydown', handle_key)


class ScrollableContainer:
    """Enhanced scrolling behavior"""

    def __init__(self, element: HTMLElement, interaction_manager: InteractionManager):
        self.element = element
        self.manager = interaction_manager
        self.scroll_y = 0
        self.max_scroll = 0

        # Add wheel event listener
        self.manager.add_event_listener(element, 'wheel', self.handle_wheel)

    def handle_wheel(self, event):
        """Handle mouse wheel scrolling"""
        delta = getattr(event, 'delta', 0)
        scroll_step = 30

        self.scroll_y += delta * scroll_step
        self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))

        # Apply scroll offset to children
        self._apply_scroll_offset()

    def _apply_scroll_offset(self):
        """Apply scroll offset to child elements"""
        for child in self.element.children:
            if child.layout_box:
                # This is a simplified version - in reality you'd want to
                # store original positions and apply scroll transform
                pass


class AccessibilityHelper:
    """Accessibility features"""

    def __init__(self, interaction_manager: InteractionManager):
        self.manager = interaction_manager

    @staticmethod
    def announce_focus_change(element: HTMLElement):
        """Announce focus changes for screen readers"""
        if element:
            text = element.text_content or f"{element.tag} element"
            print(f"Screen reader: {text}")

    @staticmethod
    def get_element_description(element: HTMLElement) -> str:
        """Get accessible description of element"""
        # Check for aria-label, title, etc.
        aria_label = element.attributes.get('aria-label')
        if aria_label:
            return aria_label

        title = element.attributes.get('title')
        if title:
            return title

        return element.text_content or f"{element.tag} element"
