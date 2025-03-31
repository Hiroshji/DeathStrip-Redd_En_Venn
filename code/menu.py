import pygame
import sys
import os
from transition import FadeTransition  # Import the transition class

pygame.init()

# --- Config file functions ---
def read_config():
    # Check if config.txt exists; if not create one with default volume=1.0.
    config_path = "config.txt"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            line = f.readline().strip()
            try:
                vol = float(line.split("=")[1])
            except Exception as e:
                vol = 1.0
            return vol
    else:
        with open(config_path, "w") as f:
            f.write("volume=1.0")
        return 1.0

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1088, 612
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deathtrip - Menu")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Define your target size for the logo display.
target_width, target_height = 400, 200

# Load the full square logo image.
orig_logo = pygame.image.load("images/logo.png").convert_alpha()

# Use the entire image rather than cropping.
logo_content = orig_logo

# Compute a scale factor so that the full image fits inside the target area.
scale_factor = min(target_width / logo_content.get_width(), target_height / logo_content.get_height())
scaled_width = int(logo_content.get_width() * scale_factor)
scaled_height = int(logo_content.get_height() * scale_factor)

# Scale the full logo while preserving the image.
scaled_logo = pygame.transform.smoothscale(logo_content, (scaled_width, scaled_height))

# Create a new surface with the target dimensions and a transparent background.
logo_img = pygame.Surface((target_width, target_height), pygame.SRCALPHA)

# Center the scaled logo on the new surface.
x_offset = (target_width - scaled_width) // 2
y_offset = (target_height - scaled_height) // 2
logo_img.blit(scaled_logo, (x_offset, y_offset))

# Load images
button_box_img = pygame.image.load("images/button_box.png").convert_alpha()
background_menu_img = pygame.image.load("images/background_menu.png").convert()
background_menu_img = pygame.transform.scale(background_menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Read volume from config file
config_volume = read_config()

# Load button click sound and set volume (slider range is 0.0–5.0; scaled to 0.0–1.0)
try:
    button_click_sound = pygame.mixer.Sound(os.path.join("sound", "button_click.wav"))
    button_click_sound.set_volume(min(config_volume / 5.0, 1.0))
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

# AnimatedButton class that moves down/up and plays a sound effect
class AnimatedButton:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.action = action
        self.hovered = False
        self.pressed = False
        self.press_offset = 5

    def draw(self, screen):
        scaled_img = pygame.transform.scale(button_box_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_img, (self.rect.x, self.rect.y))
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self):
        if self.pressed:
            self.rect.y = self.base_rect.y + self.press_offset
        else:
            self.rect.y = self.base_rect.y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                if button_click_sound:
                    button_click_sound.play()
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos):
                    self.action()

# Helper function to perform a wipe transition before executing an action.
def do_fade_transition(action):
    fade_effect = FadeTransition(screen, speed=10, color=BLACK)
    fade_effect.start()
    clock = pygame.time.Clock()
    triggered_action = False
    while not fade_effect.done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # Show current background during fade in phase
        if fade_effect.phase == "fade_in":
            screen.blit(background_menu_img, (0, 0))
        # When fade reaches black, trigger the new scene
        if not triggered_action and fade_effect.phase == "fade_out":
            action()  # Setup the new scene
            triggered_action = True
        fade_effect.update()
        fade_effect.draw()
        pygame.display.flip()
        clock.tick(60)

# Button actions using the transition helper
def start_game():
    import game
    do_fade_transition(lambda: game.Game().run())

def open_settings():
    import settings
    do_fade_transition(lambda: settings.settings_screen())

# New function: Select Scene (Chapter)
def select_scene():
    # Define available scenes.
    scenes = [
        ("start", "Kapittel 1"),
        ("scene_2", "Kapittel 2"),
        ("scene_3", "Kapittel 3"),
        ("scene_4", "Kapittel 4")
    ]
    running_scene = True

    # Create a button to go back to the main menu.
    def go_back():
        nonlocal running_scene
        running_scene = False

    back_button = AnimatedButton("Tilbake", 20, SCREEN_HEIGHT - 60, 150, 50, go_back)

    buttons = []
    btn_width = 200
    btn_height = 70
    gap = 20
    total_width = len(scenes) * btn_width + (len(scenes) - 1) * gap
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = SCREEN_HEIGHT // 2 - btn_height // 2
    for i, (scene_key, label) in enumerate(scenes):
        btn_x = start_x + i * (btn_width + gap)
        # On click: start game with chosen scene.
        def make_action(key=scene_key):
            return lambda: do_fade_transition(lambda: __import__("game").Game(start_scene=key).run())
        buttons.append(AnimatedButton(label, btn_x, y, btn_width, btn_height, make_action()))

    while running_scene:
        screen.blit(background_menu_img, (0, 0))
        for btn in buttons:
            btn.update()
            btn.draw(screen)
        back_button.update()
        back_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_scene = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                for btn in buttons:
                    btn.handle_event(event)
                back_button.handle_event(event)
        pygame.display.flip()
    do_fade_transition(run_menu)

# Create main menu buttons.
buttons = [
    AnimatedButton("Start Spill", 20, SCREEN_HEIGHT - 220, 250, 70, start_game),
    # Replace "Kapitel" button action with the new select_scene menu:
    AnimatedButton("Kapittel", 40, SCREEN_HEIGHT - 150, 250, 70, lambda: do_fade_transition(select_scene)),
    AnimatedButton("Innstillinger", 60, SCREEN_HEIGHT - 80, 250, 70, open_settings)
]

def run_menu():
    running = True
    while running:
        screen.blit(background_menu_img, (0, 0))
        logo_x = -35
        logo_y = 20
        screen.blit(logo_img, (logo_x, logo_y))
        
        for button in buttons:
            button.update()
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                for button in buttons:
                    button.handle_event(event)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_menu()