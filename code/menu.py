import pygame
import sys
import os

# Initialize Pygame
pygame.init()

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

# Load images
button_box_img = pygame.image.load("images/button_box.png").convert_alpha()
background_menu_img = pygame.image.load("images/background_menu.png").convert()
background_menu_img = pygame.transform.scale(background_menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Button class
class Button:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.hovered = False

    def draw(self, screen):
        # Use the button image scaled to button size
        scaled_img = pygame.transform.scale(button_box_img, (self.rect.width, self.rect.height))
        screen.blit(scaled_img, (self.rect.x, self.rect.y))
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.action()

# Button actions
def start_game():
    import game
    game.Game().run()

def open_settings():
    import settings  # This will run settings.py

def show_info():
    info_screen()

# Info screen
def select_chapter():
    # Use the same background image for consistency
    background_img = background_menu_img

    def go_back():
        nonlocal running_chapter
        running_chapter = False

    back_button = Button("Tilbake", 20, SCREEN_HEIGHT - 60, 150, 50, go_back)

    # Define the chapter squares
    square_size = 150
    spacing = 20
    total_width = 4 * square_size + 3 * spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y = SCREEN_HEIGHT // 2 - square_size // 2

    # Create a list of chapter rectangles
    chapters = [
        pygame.Rect(start_x + i * (square_size + spacing), y, square_size, square_size)
        for i in range(4)
    ]

    running_chapter = True
    while running_chapter:
        screen.blit(background_img, (0, 0))
        
        # Draw the chapter squares
        for i, rect in enumerate(chapters):
            pygame.draw.rect(screen, DARK_GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            chapter_text = font.render(str(i + 1), True, WHITE)
            text_rect = chapter_text.get_rect(center=rect.center)
            screen.blit(chapter_text, text_rect)
        
        # Draw the back button
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running_chapter = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(chapters):
                    if rect.collidepoint(event.pos):
                        print(f"Chapter {i + 1} clicked. (Functionality not implemented)")
                back_button.check_click(event.pos)
        
        pygame.display.flip()

# Create buttons for main menu
buttons = [
    Button("Start Spill", 20, SCREEN_HEIGHT - 220, 250, 70, start_game),
    Button("Kapitel", 40, SCREEN_HEIGHT - 150, 250, 70, select_chapter),
    Button("Innstillinger", 60, SCREEN_HEIGHT - 80, 250, 70, open_settings)
]

def run_menu():
    running = True
    while running:
        # Use the background image for the main menu
        screen.blit(background_menu_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.check_click(event.pos)
                    
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_menu()