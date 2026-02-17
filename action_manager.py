import pygame

class ActionManager:
    def __init__(self, game):
        self.game = game
        self.actions = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "attack1": False,
            "enter": False,
            "toggle_pause": False,
            "interact": False,
            "mouse_pos": (0, 0)
        }
        self.joysticks = []
        self.init_joysticks()

    def init_joysticks(self):
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for joystick in self.joysticks:
            joystick.init()
            print(f"Joystick initialized: {joystick.get_name()}")

    def update(self):
        # Update mouse position
        mouse_pos = pygame.mouse.get_pos()
        if self.game.screen.get_width() > 0 and self.game.screen.get_height() > 0:
            scale_x = self.game.game_canvas.get_width() / self.game.screen.get_width()
            scale_y = self.game.game_canvas.get_height() / self.game.screen.get_height()
            self.actions["mouse_pos"] = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # Event Loop (Triggers & System)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            
            # Toggle Pause (Edge Triggered)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.actions["toggle_pause"] = True
            elif event.type == pygame.JOYBUTTONDOWN and event.button == 7: # Start Button
                 self.actions["toggle_pause"] = True
            
            # Debug Toggle
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_PERIOD:
                self.game.debug = not self.game.debug

            # Controller Hotplugging
            elif event.type == pygame.JOYDEVICEADDED:
                self.init_joysticks()
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.init_joysticks()

        # Polling for Continuous Actions (Keyboard + Controller)
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Controller state
        joy_x, joy_y = 0.0, 0.0
        joy_attack = False
        joy_interact = False
        joy_enter = False # Start button acts as Enter too

        if self.joysticks:
            joy = self.joysticks[0]
            try:
                joy_x = joy.get_axis(0)
                joy_y = joy.get_axis(1)
                joy_interact = joy.get_button(0) # A / Cross (Interact)
                joy_attack = joy.get_button(2)   # X / Square (Attack)
                joy_enter = joy.get_button(7)    # Start (Enter)
            except pygame.error:
                pass # Joystick might have disconnected mid-frame

        deadzone = 0.2
        
        # Merge Inputs (Logical OR)
        self.actions["left"] = keys[pygame.K_a] or (joy_x < -deadzone)
        self.actions["right"] = keys[pygame.K_d] or (joy_x > deadzone)
        self.actions["up"] = keys[pygame.K_w] or (joy_y < -deadzone)
        self.actions["down"] = keys[pygame.K_s] or (joy_y > deadzone)
        
        self.actions["enter"] = keys[pygame.K_RETURN] or joy_enter
        self.actions["interact"] = keys[pygame.K_e] or joy_interact
        self.actions["attack1"] = mouse_buttons[0] or joy_attack
