import pygame
import pygame._sdl2.controller as controller

class ActionManager:
    @property
    def current_mode(self):
        return getattr(self, '_current_mode', "keyboard_mouse")

    @current_mode.setter
    def current_mode(self, value):
        if getattr(self, '_current_mode', None) != value:
            self._current_mode = value
            if pygame.display.get_surface() is not None:
                if value == "controller":
                    pygame.mouse.set_visible(False)
                else:
                    pygame.mouse.set_visible(True)

    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        if not controller.get_init():
            controller.init()
            
        self.joysticks = {}
        if not pygame.joystick.get_init():
            pygame.joystick.init()
            
        for i in range(pygame.joystick.get_count()):
            if controller.is_controller(i):
                joy = controller.Controller(i)
                joy.init()
                self.joysticks[joy.as_joystick().get_instance_id()] = joy

        self.current_mode = "keyboard_mouse"
        self.actions = {
            "left": False, "right": False, "up": False, "down": False,
            "attack1": False, "attack2": False, "attack3": False, "enter": False, "back": False, "interact": False,
            "arrowUp": False, "arrowDown": False, "arrowRight": False, "arrowLeft": False,
            "toggle_pause": False, "mouse_pos": (0, 0), "aim_axis": (0.0, 0.0)
        }
        
        self.not_maintainable_keys = {
            "enter", "interact", "back", "toggle_pause"
        }

        # Input maps
        self.keyboard_map = {
            pygame.K_a: ["left", "arrowLeft"],
            pygame.K_d: ["right", "arrowRight"],
            pygame.K_w: ["up", "arrowUp"],
            pygame.K_s: ["down", "arrowDown"],
            pygame.K_RETURN: ["enter"],
            pygame.K_e: ["interact"],
            pygame.K_ESCAPE: ["back", "toggle_pause"],
            pygame.K_UP: ["arrowUp"],
            pygame.K_DOWN: ["arrowDown"], 
            pygame.K_RIGHT: ["arrowRight"],
            pygame.K_LEFT: ["arrowLeft"],
            pygame.K_SPACE: ["attack1"],
            pygame.K_f: ["attack2"],
            pygame.K_r: ["attack3"],
        }
        
        self.controller_button_map = {
            pygame.CONTROLLER_BUTTON_A: ["interact", "enter"],          # Cross / A
            pygame.CONTROLLER_BUTTON_B: ["back"],               # Circle / B
            pygame.CONTROLLER_BUTTON_X: ["attack2"],           # Square / X
            pygame.CONTROLLER_BUTTON_Y: ["attack3"],           # Triangle / Y
            pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: ["attack1"],  # R1 / RB
            pygame.CONTROLLER_BUTTON_START: ["toggle_pause"],  # Options / Start
            pygame.CONTROLLER_BUTTON_DPAD_UP: ["arrowUp"],
            pygame.CONTROLLER_BUTTON_DPAD_DOWN: ["arrowDown"],
            pygame.CONTROLLER_BUTTON_DPAD_LEFT: ["arrowLeft"],
            pygame.CONTROLLER_BUTTON_DPAD_RIGHT: ["arrowRight"]
        }

    def reset_not_maintainable_keys(self):
        for k in self.not_maintainable_keys:
            if k in self.actions:
                self.actions[k] = False

    def reset_keys(self):
        for k in self.actions:
            if k not in ["mouse_pos", "aim_axis"]:
                self.actions[k] = False

    def _set_action(self, action_data, is_down):
        """Helper to set action dict, supporting both string and list inputs."""
        if not action_data:
            return
            
        if isinstance(action_data, list):
            for act in action_data:
                self.actions[act] = is_down
        else:
            self.actions[action_data] = is_down

    def get_events(self):
        events = pygame.event.get()
        self.reset_not_maintainable_keys()

        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self._handle_keyboard(event)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                self._handle_mouse(event)
            elif event.type in (pygame.CONTROLLERDEVICEADDED, pygame.CONTROLLERDEVICEREMOVED, 
                                pygame.CONTROLLERBUTTONDOWN, pygame.CONTROLLERBUTTONUP, 
                                pygame.CONTROLLERAXISMOTION):
                self._handle_controller(event)
        
        self.actions["current_mode"] = self.current_mode
        return events

    def _handle_keyboard(self, event):
        self.current_mode = "keyboard_mouse"
        action = self.keyboard_map.get(event.key)
        self._set_action(action, event.type == pygame.KEYDOWN)

    def _handle_mouse(self, event):
        self.current_mode = "keyboard_mouse"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.actions["attack1"] = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.actions["attack1"] = False

    def _handle_controller(self, event):
        # Connection handling
        if event.type == pygame.CONTROLLERDEVICEADDED:
            try:
                if controller.is_controller(event.device_index):
                    joy = controller.Controller(event.device_index)
                    instance_id = joy.as_joystick().get_instance_id()
                    if instance_id not in self.joysticks:
                        joy.init()
                        self.joysticks[instance_id] = joy
            except Exception as e:
                print(f"Error adding joystick: {e}")
            return
        elif event.type == pygame.CONTROLLERDEVICEREMOVED:
            if event.instance_id in self.joysticks:
                self.joysticks[event.instance_id].quit()
                del self.joysticks[event.instance_id]
            return

        # Buttons handling (D-pad is handled as buttons in this API!)
        if event.type in (pygame.CONTROLLERBUTTONDOWN, pygame.CONTROLLERBUTTONUP):
            self.current_mode = "controller"
            action = self.controller_button_map.get(event.button)
            self._set_action(action, event.type == pygame.CONTROLLERBUTTONDOWN)

        # Axis handling for movement/aiming
        elif event.type == pygame.CONTROLLERAXISMOTION:
            axis = event.axis
            # Pygame controllers return an axis from -32768 to 32767
            value = event.value / 32768.0
            deadzone = 0.2

            if abs(value) >= deadzone:
                self.current_mode = "controller"

            if self.current_mode != "controller":
                return

            if abs(value) < deadzone:
                value = 0.0

            if axis == pygame.CONTROLLER_AXIS_LEFTX:
                self.actions["left"] = (value < 0)
                self.actions["right"] = (value > 0)
                
                # Also trigger arrow actions to navigate menus
                self.actions["arrowLeft"] = (value < 0)
                self.actions["arrowRight"] = (value > 0)
            
            elif axis == pygame.CONTROLLER_AXIS_LEFTY:
                self.actions["up"] = (value < 0)
                self.actions["down"] = (value > 0)
                
                # Also trigger arrow actions to navigate menus
                self.actions["arrowUp"] = (value < 0)
                self.actions["arrowDown"] = (value > 0)
                
            elif axis == pygame.CONTROLLER_AXIS_RIGHTX:
                # Store aim X
                self.actions["aim_axis"] = (value, self.actions["aim_axis"][1])
                
            elif axis == pygame.CONTROLLER_AXIS_RIGHTY:
                # Store aim Y
                self.actions["aim_axis"] = (self.actions["aim_axis"][0], value)
                
            elif axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT:
                # Basic attack using right trigger
                self.actions["attack1"] = (value > 0.5)

    def process_mouse_and_aim(self, game_canvas, screen):
        """Calculates scaled mouse pos and provides it globally, 
        regardless of if we use it or not."""
        mouse_pos = pygame.mouse.get_pos()
        if screen.get_width() != 0 and screen.get_height() != 0:
            scale_x = game_canvas.get_width() / screen.get_width()
            scale_y = game_canvas.get_height() / screen.get_height()
            scaled_mouse_pos = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)
            self.actions["mouse_pos"] = scaled_mouse_pos
        else:
            self.actions["mouse_pos"] = (0, 0)
