import math
import random
import pygame
from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_PINK,
    COLOR_WHITE,
    LINE_WIDTH,
    POWERUP_DROP_CHANCE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from logger import log_event
from powerup import PowerUp


class Asteroid(CircleShape):
    containers: tuple = ()

    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-45, 45)

        # Generate unique jagged rock vertices
        num_vertices = random.randint(9, 14)
        self.vertex_offsets: list[tuple[float, float]] = []
        for i in range(num_vertices):
            angle = (i * 2 * math.pi / num_vertices)
            # Vary radius slightly between 0.75x and 1.25x
            dist = self.radius * random.uniform(0.75, 1.25)
            self.vertex_offsets.append((math.cos(angle) * dist, math.sin(angle) * dist))

        # Assign aesthetic tint based on size
        if self.radius >= 40:
            self.color = (200, 215, 230)
            self.score_value = 20
        elif self.radius >= 25:
            self.color = (220, 200, 240)
            self.score_value = 50
        else:
            self.color = (255, 180, 220)
            self.score_value = 100

    def draw(self, screen: pygame.Surface) -> None:
        # Compute rotated screen positions for vertices
        rad = math.radians(self.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        pts = []
        for ox, oy in self.vertex_offsets:
            rx = ox * cos_a - oy * sin_a + self.position.x
            ry = ox * sin_a + oy * cos_a + self.position.y
            pts.append((rx, ry))

        # Fill with semi-dark tone
        fill_color = (
            max(0, int(self.color[0] * 0.12)),
            max(0, int(self.color[1] * 0.12)),
            max(0, int(self.color[2] * 0.15)),
        )
        if len(pts) >= 3:
            pygame.draw.polygon(screen, fill_color, pts)
            pygame.draw.polygon(screen, self.color, pts, LINE_WIDTH)

            # Draw a subtle inner crater line for extra detail
            p1 = pts[0]
            p2 = pts[len(pts) // 2]
            p_mid = (self.position.x, self.position.y)
            pygame.draw.line(screen, fill_color, p1, p_mid, 1)

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.rotation += self.rot_speed * dt

        # Screen wrapping
        pad = self.radius * 1.5
        if self.position.x < -pad:
            self.position.x = SCREEN_WIDTH + pad
        elif self.position.x > SCREEN_WIDTH + pad:
            self.position.x = -pad

        if self.position.y < -pad:
            self.position.y = SCREEN_HEIGHT + pad
        elif self.position.y > SCREEN_HEIGHT + pad:
            self.position.y = -pad

    def split(self, particle_manager=None, drop_chance: float | None = None, sound_manager=None) -> int:
        self.kill()
        awarded_points = self.score_value

        if sound_manager:
            if self.radius >= 40:
                sound_manager.play("explode_large")
            elif self.radius >= 25:
                sound_manager.play("explode_med")
            else:
                sound_manager.play("explode_small")

        # Spawn particle explosion
        if particle_manager:
            particle_manager.add_explosion(self.position, self.color, count=int(self.radius * 0.8))
            particle_manager.add_popup(
                self.position,
                f"+{awarded_points}",
                self.color,
            )

        # Chance to drop a Power-up or De-buff
        chance = drop_chance if drop_chance is not None else POWERUP_DROP_CHANCE
        if random.random() < chance:
            PowerUp(self.position.x, self.position.y)
            if particle_manager:
                particle_manager.add_popup(
                    self.position,
                    "DROP!",
                    (255, 255, 100),
                )

        if self.radius <= ASTEROID_MIN_RADIUS:
            return awarded_points

        log_event("asteroid_split")
        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle)
        v2 = self.velocity.rotate(-random_angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS
        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = v1 * 1.2
        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2.velocity = v2 * 1.2

        return awarded_points
