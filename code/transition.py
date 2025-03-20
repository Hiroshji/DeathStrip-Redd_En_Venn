import pygame

class FadeTransition:
    """
    A fade transition effect that fades to black then reveals the new scene.
    """
    def __init__(self, screen, speed=5, color=(0, 0, 0)):
        """
        :param screen: The Pygame display surface.
        :param speed: The change in alpha per frame.
        :param color: The color of the fade (default is black).
        """
        self.screen = screen
        self.speed = speed
        self.color = color
        self.overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        self.overlay.fill(self.color)
        self.alpha = 0
        self.overlay.set_alpha(self.alpha)
        self.phase = "fade_in"  # "fade_in" means fading from clear to black, then "fade_out" reveals new scene.
        self.done = False

    def start(self):
        """Resets the transition."""
        self.alpha = 0
        self.overlay.set_alpha(self.alpha)
        self.phase = "fade_in"
        self.done = False

    def update(self):
        if self.phase == "fade_in":
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                self.phase = "fade_out"
        elif self.phase == "fade_out":
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.done = True
        self.overlay.set_alpha(self.alpha)

    def draw(self):
        """Draws the fade overlay."""
        self.screen.blit(self.overlay, (0, 0))