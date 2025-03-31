import pygame
import sys
import os

pygame.init()

# Set video mode
screen = pygame.display.set_mode((1088, 612))
pygame.display.set_caption("Deathtrip - Game")

# --- Config file functions ---
def read_config():
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

# Load assets
button_box_img = pygame.image.load("images/button_box.png").convert_alpha()
try:
    button_click_sound = pygame.mixer.Sound(os.path.join("sound", "button_click.wav"))
    config_volume = read_config()
    button_click_sound.set_volume(min(config_volume / 5.0, 1.0))
except Exception as e:
    print("Error loading sound:", e)
    button_click_sound = None

font = pygame.font.SysFont("Arial", 24)
WHITE = (255, 255, 255)
DARK_GRAY = (150, 150, 150)

# AnimatedButton class for decisions (with sound and animation)
class AnimatedButton:
    def __init__(self, text, x, y, width, height, action):
        self.text = text
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.action = action
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

class Game:
    # Modified __init__ to accept an optional start_scene parameter.
    def __init__(self, start_scene="start"):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 24)

        # Set the starting scene based on the parameter.
        self.current_scene = start_scene

        # Preload chapter backgrounds.
        self.backgrounds = {
            "start": pygame.transform.scale(pygame.image.load("images/chapter1.jpg").convert(), (1088, 612)),
            "decision_drink": pygame.transform.scale(pygame.image.load("images/chapter2.jpg").convert(), (1088, 612)),
            "decision_no_drink": pygame.transform.scale(pygame.image.load("images/chapter2.jpg").convert(), (1088, 612)),
            "scene_2": pygame.transform.scale(pygame.image.load("images/chapter3.jpg").convert(), (1088, 612)),
            "decision_exit": pygame.transform.scale(pygame.image.load("images/chapter3.jpg").convert(), (1088, 612)),
            "scene_3": pygame.transform.scale(pygame.image.load("images/chapter4.jpg").convert(), (1088, 612)),
            "decision_try_stop": pygame.transform.scale(pygame.image.load("images/chapter4.jpg").convert(), (1088, 612)),
            "scene_4": pygame.transform.scale(pygame.image.load("images/chapter5.jpg").convert(), (1088, 612)),
            "decision_seat": pygame.transform.scale(pygame.image.load("images/chapter5.jpg").convert(), (1088, 612)),
            "ending_stop": pygame.transform.scale(pygame.image.load("images/chapter5.jpg").convert(), (1088, 612)),
            "ending_drive": pygame.transform.scale(pygame.image.load("images/chapter5.jpg").convert(), (1088, 612))
        }

        # Game state and dialogues (script based on your story)
        self.dialogues = {
            "start": [
                "Venn: Hei, kom og ta en shot med oss!",
                "Du: Jeg vet ikke, jeg skal tidlig opp i morgen.",
                "Venn: Slapp av, én drink skader ikke! Vi skal jo bare ha det gøy."
            ],
            "scene_2": [
                "Du: Hva gjør du?",
                "Vennen: Jeg skal hjem. Det går fint, jeg har kontroll.",
                "Du: Er du sikker? Kanskje det er bedre å vente litt eller få noen til å kjøre deg?",
                "Vennen: Slapp av, jeg føler meg helt fin. Det er ingen problem.",
                "Du: Det handler ikke bare om deg. Hva om noe skjer?",
                "Vennen: Det skjer ikke noe, jeg har full kontroll. Slutt å bekymre deg."
            ],
            "scene_3": [
                "Du: Vent litt, kanskje vi heller kan bestille en taxi?",
                "Vennen: Nei, nei, jeg er helt fin. Dette går bra.",
                "Du: Men tenk om noe skjer? Det er ikke verdt risikoen.",
                "Vennen: Jeg sier det går fint. Hvorfor lager du så mye drama?"
            ],
            "scene_4": [
                "Vennen: Kom igjen, bare hopp inn, vi kommer oss kjapt hjem!",
                "Du: Jeg vet ikke... Jeg føler meg ikke trygg.",
                "Vennen: Slutt å overtenke, det går bra! Vil du hjem eller ikke?"
            ],
            "ending_stop": [
                "Du stoppet vennen din."
            ],
            "ending_drive": [
                "Vennen din kjørte under påvirkning..."
            ],
            # Wrong decision info dialogues:
            "info_drink": [
                "lorem: Drinking and driving is dangerous.",
            ],
            "info_exit_A": [
                "lorem: Intervening that way may cause more harm.",
            ],
            "info_try_stop_A": [
                "lorem: Forcing the issue isn’t safe.",
            ],
            "info_seat_B": [
                "lorem: Getting in the car in that situation is risky.",
            ]
        }
        self.current_dialogue_full = self.dialogues[self.current_scene]
        self.dialogue_progress = ""
        self.dialogue_index = 0
        self.current_line_index = 0   # Track which dialogue line you're on.
        self.dialogue_timer = 0       # Timer for typewriter effect (ms)
        self.dialogue_finished = False
        self.post_dialogue_timer = 0  # Delay after full dialogue is shown

        # Button layout (for decision buttons)
        self.button_width = 200
        self.button_height = 50
        dialogue_box_height = 100
        bottom_margin = 20
        dialogue_y = 612 - dialogue_box_height - bottom_margin
        self.button_y = dialogue_y - self.button_height - 10
        total_buttons_width = self.button_width * 2 + 20  # two buttons with 20px gap
        self.left_x = (1088 - total_buttons_width) // 2
        self.right_x = self.left_x + self.button_width + 20

        # Decision buttons (will be created when dialogue is finished)
        self.decision_buttons = {}

        self.info_mode = False
        self.info_text = ""
        
    def reset_dialogue(self):
        # Now current_dialogue_full will be the list of lines for the current scene.
        self.current_dialogue_full = self.dialogues.get(self.current_scene, [])
        self.current_line_index = 0         # Which dialogue line we're on.
        self.dialogue_progress = ""         # The current text being typewritten.
        self.dialogue_timer = 0             # Timer for typewriter effect.
        self.dialogue_finished = False      # True when the current line is fully displayed.
        self.post_dialogue_timer = 0        # Delay after finished before advancing.
        self.decision_buttons = {}          # Clear decision buttons.

    def update_dialogue(self, dt):
        # If there are still lines to show.
        if self.current_line_index < len(self.current_dialogue_full):
            # If the current line is not finished, do the typewriter effect.
            if not self.dialogue_finished:
                if self.dialogue_index < len(self.current_dialogue_full[self.current_line_index]):
                    self.dialogue_timer += dt
                    if self.dialogue_timer >= 30:  # adjust speed here
                        self.dialogue_progress += self.current_dialogue_full[self.current_line_index][self.dialogue_index]
                        self.dialogue_index += 1
                        self.dialogue_timer = 0
                else:
                    self.dialogue_finished = True
                    self.post_dialogue_timer = 0
            else:
                self.post_dialogue_timer += dt
                # If the current scene is one of the info (wrong decision) scenes,
                # auto-transition after a brief delay.
                if self.current_scene in {"info_drink", "info_exit_A", "info_try_stop_A", "info_seat_B"}:
                    if self.post_dialogue_timer >= 1000:
                        self.auto_transition()
                else:
                    # For narrative/dialogue scenes that require continuation, allow space press or delay.
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE] or self.post_dialogue_timer >= 1000:
                        self.current_line_index += 1
                        self.dialogue_progress = ""
                        self.dialogue_index = 0
                        self.dialogue_timer = 0
                        self.dialogue_finished = False
        else:
            # All dialogue lines are done.
            self.dialogue_progress = ""

    def auto_transition(self):
        # Mapping for info scenes to the next scene in the story.
        auto_mapping = {
            "info_drink": "scene_2",
            "info_exit_A": "scene_3",
            "info_try_stop_A": "scene_4",
            "info_seat_B": "ending_drive"
        }
        if self.current_scene in auto_mapping:
            self.current_scene = auto_mapping[self.current_scene]
            self.reset_dialogue()

    def draw_text(self, text, x, y, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_dialogue_box(self, dialogue):
        box_rect = pygame.Rect(20, 612 - 100 - 20, 1088 - 40, 100)
        pygame.draw.rect(self.screen, (50, 50, 50), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        self.draw_text(dialogue, box_rect.x + 10, box_rect.y + 10)

    def create_decision_buttons(self):
        # Create decision buttons based on the current scene.
        if self.current_scene == "start":
            self.decision_buttons = {
                "drink": AnimatedButton("Ja", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("drink")),
                "no_drink": AnimatedButton("Nei", self.right_x, self.button_y, self.button_width, self.button_height,
                                           lambda: self.handle_decision("no_drink"))
            }
        elif self.current_scene == "scene_2":
            self.decision_buttons = {
                "exit_A": AnimatedButton("A: Ja", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("exit_decision_A")),
                "exit_B": AnimatedButton("B: Nei", self.right_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("exit_decision_B"))
            }
        elif self.current_scene == "scene_3":
            self.decision_buttons = {
                "try_A": AnimatedButton("A: Ja", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("try_stop_A")),
                "try_B": AnimatedButton("B: Nei", self.right_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("try_stop_B"))
            }
        elif self.current_scene == "scene_4":
            self.decision_buttons = {
                "seat_A": AnimatedButton("A: Nei", self.left_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("seat_A")),
                "seat_B": AnimatedButton("B: Ja", self.right_x, self.button_y, self.button_width, self.button_height,
                                          lambda: self.handle_decision("seat_B"))
            }
        # No decision buttons are created for ending scenes.

    def handle_decision(self, decision):
        # Map decision keys to the next scene.
        if decision == "drink":
            self.current_scene = "info_drink"      # wrong decision; show info dialogue
        elif decision == "no_drink":
            self.current_scene = "scene_2"          # correct decision
        elif decision == "exit_decision_A":
            self.current_scene = "info_exit_A"      # wrong choice
        elif decision == "exit_decision_B":
            self.current_scene = "scene_3"          # correct choice
        elif decision == "try_stop_A":
            self.current_scene = "info_try_stop_A"  # wrong choice
        elif decision == "try_stop_B":
            self.current_scene = "scene_4"          # correct choice
        elif decision == "seat_A":
            self.current_scene = "ending_stop"      # correct ending
        elif decision == "seat_B":
            self.current_scene = "info_seat_B"        # wrong choice
        self.reset_dialogue()

    def draw_scene(self):
        # Draw the background corresponding to the current scene.
        bg = self.backgrounds.get(self.current_scene)
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        # Draw dialogue or decision buttons.
        if self.current_line_index < len(self.current_dialogue_full):
            self.draw_dialogue_box(self.dialogue_progress)
        else:
            if not self.decision_buttons:
                self.create_decision_buttons()
            for btn in self.decision_buttons.values():
                btn.update()
                btn.draw(self.screen)

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.dialogue_progress == "" and self.decision_buttons:
                    for btn in self.decision_buttons.values():
                        btn.handle_event(event)
            self.update_dialogue(dt)
            self.draw_scene()
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()  # Defaults to "start" scene.
    game.run()