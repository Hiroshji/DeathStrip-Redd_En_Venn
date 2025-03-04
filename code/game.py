import pygame
import sys
from menu import Menu
import os

def start_game():
    if os.path.exists("game.py"):
        pygame.quit()
        subprocess.run([sys.executable, "game.py"])
    else:
        print("Error: game.py not found!")

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)

        # Game states
        self.current_scene = "start"

        # Clickable characters (name, x, y, width, height)
        self.characters = {
            "drink": ("Drikk", 50, 150, 200, 40),
            "no_drink": ("Ikke drikk", 50, 200, 200, 40),
            "stop_friend": ("Stoppe", 50, 150, 200, 40),
            "let_drive": ("La han kjøre", 50, 200, 200, 40),
        }

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x, y))

    def draw_scene(self):
        self.screen.fill((0, 0, 0))

        if self.current_scene == "start":
            self.draw_text("Velg om du vil drikke eller ikke:", 50, 50)
            self.draw_button("drink")
            self.draw_button("no_drink")

        elif self.current_scene == "decision_1":
            self.draw_text("Du drakk. Nå må du stoppe vennen din fra å kjøre.", 50, 50)
            self.draw_button("stop_friend")
            self.draw_button("let_drive")

        elif self.current_scene == "decision_2":
            self.draw_text("Du valgte å ikke drikke. Nå må du stoppe vennen din.", 50, 50)
            self.draw_button("stop_friend")
            self.draw_button("let_drive")

    def draw_button(self, key):
        text, x, y, w, h = self.characters[key]
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h))
        self.draw_text(text, x + 10, y + 10)

    def handle_click(self, pos):
        x, y = pos
        for key, (_, bx, by, bw, bh) in self.characters.items():
            if bx <= x <= bx + bw and by <= y <= by + bh:
                if key == "drink":
                    self.current_scene = "decision_1"
                elif key == "no_drink":
                    self.current_scene = "decision_2"
                elif key == "stop_friend":
                    print("You stopped your friend!")  # Placeholder for outcome
                elif key == "let_drive":
                    print("Your friend drives under influence...")  # Placeholder

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw_scene()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

# Start the game
pygame.init()
screen = pygame.display.set_mode((800, 600))

menu = Menu(screen)
result = menu.run()

if result == "start_game":
    game = Game(screen)
    game.run()
