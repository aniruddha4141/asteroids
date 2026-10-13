import pygame
from circleshape import CircleShape
from constants import COLOR_CYAN, LINE_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SHOT_RADIUS


class Shot(CircleShape):
    containers: tuple = ()

    def __init__(self, x: float, y: float, color: tuple[int, int, int] = COLOR_CYAN) -> None:
        super().__init__(x, y, SHOT_RADIUS)
        self.color = color
        self.lifetime = 1.4  # bullets expire after 1.4 seconds

    def draw(self, screen: pygame.Surface) -> None:
        pos_int = (int(self.position.x), int(self.position.y))
        # Draw soft outer glow
        glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        glow_color = (*self.color[:3], 80)
        pygame.draw.circle(glow_surf, glow_color, (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow_surf, (pos_int[0] - self.radius * 2, pos_int[1] - self.radius * 2))

        # Core bullet
        pygame.draw.circle(screen, (255, 255, 255), pos_int, self.radius - 1)
        pygame.draw.circle(screen, self.color, pos_int, self.radius, 1)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.lifetime -= dt

        # Wrap around screen
        if self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.x > SCREEN_WIDTH:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0

        if self.lifetime <= 0:
            self.kill()
