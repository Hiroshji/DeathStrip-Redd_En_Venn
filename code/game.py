import pygame
import sys

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame inside the class
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Deathtrip - Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)

        # Game states
        self.current_scene = "start"

        # Button dimensions
        button_width = 200
        button_height = 50

        # Dialogue box configuration
        dialogue_box_height = 100
        bottom_margin = 20
        dialogue_y = 600 - dialogue_box_height - bottom_margin  # dialogue box top y-coordinate

        # Position buttons immediately above the dialogue box with a 10px gap.
        button_y = dialogue_y - button_height - 10

        # For two buttons with a 20px gap, total width = 420. Center on 800px:
        left_x = (800 - 420) // 2  # e.g. 190
        right_x = left_x + button_width + 20  # e.g. 410

        # Clickable characters (name, x, y, width, height)
        self.characters = {
            "drink": ("Drikk", left_x, button_y, button_width, button_height),
            "no_drink": ("Ikke drikk", right_x, button_y, button_width, button_height),
            "stop_friend": ("Stoppe", left_x, button_y, button_width, button_height),
            "let_drive": ("La han kjøre", right_x, button_y, button_width, button_height),
        }

        # Store dialogue text for each scene including separate endings
        self.dialogues = {
            "start": "Velg om du vil drikke eller ikke:",
            "decision_1": "Du drakk. Nå må du stoppe vennen din fra å kjøre.",
            "decision_2": "Du valgte å ikke drikke. Nå må du stoppe vennen din.",
            "ending_stop": "Du stoppet vennen din og reddet dagen!",  # Unique ending for stop_friend
            "ending_drive": "Vennen din kjørte under påvirkning... en farlig avgjørelse!",  # Unique ending for let_drive
        }

        # Variables for typewriter dialogue effect
        self.current_dialogue_full = self.dialogues[self.current_scene]
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.dialogue_timer = 0      # Accumulates time for adding letters (in ms)
        self.dialogue_finished = False
        self.post_dialogue_timer = 0 # Timer after full dialogue is shown

    def reset_dialogue(self):
        self.current_dialogue_full = self.dialogues.get(self.current_scene, "")
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.dialogue_timer = 0
        self.dialogue_finished = False
        self.post_dialogue_timer = 0

    def update_dialogue(self, dt):
        # If dialogue is not finished, update it letter by letter (typewriter effect)
        if not self.dialogue_finished:
            if self.dialogue_index < len(self.current_dialogue_full):
                self.dialogue_timer += dt
                if self.dialogue_timer >= 50:  # 50ms per character
                    self.dialogue_progress += self.current_dialogue_full[self.dialogue_index]
                    self.dialogue_index += 1
                    self.dialogue_timer = 0
            else:
                # Dialogue fully typed; mark as finished
                self.dialogue_finished = True
                self.post_dialogue_timer = 0
        else:
            # Once finished, wait a delay then clear dialogue so that decision buttons appear.
            self.post_dialogue_timer += dt
            if self.post_dialogue_timer >= 2000:  # 2-second delay
                self.dialogue_progress = ""

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_dialogue_box(self, dialogue):
        # Define dialogue box rectangle (with 20px left/right margins)
        box_rect = pygame.Rect(20, 600 - 100 - 20, 800 - 40, 100)
        # Draw background
        pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        # Draw dialogue text inside
        self.draw_text(dialogue, box_rect.x + 10, box_rect.y + 10)

    def draw_scene(self):
        self.screen.fill((0, 0, 0))
        # Draw the dialogue box with the current dialogue progress
        self.draw_dialogue_box(self.dialogue_progress)

        # Only show buttons when dialogue_progress is cleared
        if self.dialogue_progress == "":
            if self.current_scene == "start":
                self.draw_button("drink")
                self.draw_button("no_drink")
            elif self.current_scene in ["decision_1", "decision_2"]:
                self.draw_button("stop_friend")
                self.draw_button("let_drive")
            # For ending scenes, no decision buttons are shown.

    def draw_button(self, key):
        text, x, y, w, h = self.characters[key]
        # Draw button rectangle
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h))
        # Draw button border
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, w, h), 2)
        # Draw button label
        self.draw_text(text, x + 10, y + 10)

    def handle_click(self, pos):
        # Only process clicks if dialogue box is cleared (i.e. buttons are visible)
        if self.dialogue_progress != "":
            return
        x, y = pos
        for key, (_, bx, by, bw, bh) in self.characters.items():
            if bx <= x <= bx + bw and by <= y <= by + bh:
                # For the initial choices
                if key == "drink":
                    self.current_scene = "decision_1"
                    self.reset_dialogue()
                elif key == "no_drink":
                    self.current_scene = "decision_2"
                    self.reset_dialogue()
                # For final decision options, set different endings so they don't repeat.
                elif key == "stop_friend":
                    print("You stopped your friend!")  # Placeholder outcome
                    self.current_scene = "ending_stop"
                    self.reset_dialogue()
                elif key == "let_drive":
                    print("Your friend drives under influence...")  # Placeholder outcome
                    self.current_scene = "ending_drive"
                    self.reset_dialogue()

    def run(self):
        while self.running:
            dt = self.clock.tick(60)  # Milliseconds between frames
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.update_dialogue(dt)
            self.draw_scene()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()