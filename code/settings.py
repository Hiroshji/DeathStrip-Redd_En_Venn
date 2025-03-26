import pygame
import sys
import os
from menu import do_fade_transition, run_menu

pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1088, 612
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Settings")

# Colors and font
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
font = pygame.font.Font(None, 36)

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

def update_config(new_value):
    config_path = "config.txt"
    with open(config_path, "w") as f:
        f.write("volume=" + str(new_value))

# Load the button click sound from the "sound" folder using try/except
try:
    button_click_sound = pygame.mixer.Sound("sound/button_click.wav")  # Adjust file name/extension if necessary.
    # Set volume using the config value (scaled to 0.0-1.0)
    config_volume = read_config()
    button_click_sound.set_volume(min(config_volume / 5.0, 1.0))
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

# Animated button that moves down/up on click and plays sound
class AnimatedButton:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.action = action
        self.hovered = False
        self.pressed = False
        self.press_offset = 5  # How many pixels to move down when pressed

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

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

# Simple horizontal slider to control the button click sound volume
# Slider range is 0.0 to 5.0 even though effective volume is scaled to 0.0–1.0.
class Slider:
    def __init__(self, x, y, width, height, min_val=0.0, max_val=5.0, initial=1.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial
        self.handle_radius = height // 2
        self.handle_x = x + int((self.value - self.min_val) / (self.max_val - self.min_val) * width)
        self.dragging = False

    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, WHITE, self.rect, 2)
        # Draw the handle
        handle_center = (self.handle_x, self.rect.centery)
        pygame.draw.circle(surface, DARK_GRAY, handle_center, self.handle_radius)

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            handle_rect = pygame.Rect(
                self.handle_x - self.handle_radius,
                self.rect.centery - self.handle_radius,
                self.handle_radius * 2,
                self.handle_radius * 2,
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (self.handle_x - self.rect.x) / self.rect.width
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            # Scale the slider value to effective volume (0.0–1.0); update sound volume
            if button_click_sound:
                button_click_sound.set_volume(min(self.value / self.max_val, 1.0))
            # Update the config file with the new slider value
            update_config(self.value)

def settings_screen():
    clock = pygame.time.Clock()
    running = True

    # Read volume from config file and use that as the slider's initial value.
    initial_volume = read_config()
    
    # Use the same background as the chapters screen.
    background_img = pygame.image.load("images/background_chapter.png").convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Create UI elements.
    sample_button = AnimatedButton("Test Button", 100, 100, 200, 50,
                                   lambda: print("Button action executed"))
    slider = Slider(100, 200, 300, 20, min_val=0.0, max_val=5.0, initial=initial_volume)
    
    # Define a callback that triggers the fade transition and then goes to the menu.
    def return_to_menu():
        do_fade_transition(lambda: run_menu())
        nonlocal running
        running = False

    # Create the "Tilbake" (Return) button.
    return_button = AnimatedButton("Tilbake", 20, SCREEN_HEIGHT - 60, 150, 50, return_to_menu)

    # Main loop.
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            sample_button.handle_event(event)
            slider.update(event)
            return_button.handle_event(event)

        sample_button.update()
        return_button.update()

        # Blit the chapter background.
        screen.blit(background_img, (0, 0))
        sample_button.draw(screen)
        slider.draw(screen)
        return_button.draw(screen)

        # Display the current volume level.
        volume_text = font.render(f"Volume: {slider.value:.2f}", True, WHITE)
        screen.blit(volume_text, (100, 240))

        pygame.display.flip()

    # After the loop ends, transition back to the menu.
    import menu
    menu.run_menu()

if __name__ == "__main__":
    settings_screen()