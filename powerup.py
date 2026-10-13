import math
import random
import pygame
from circleshape import CircleShape
from constants import (
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PINK,
    COLOR_PURPLE,
    COLOR_YELLOW,
    POWERUP_DURATION,
    POWERUP_RADIUS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

# Power-up Type Constants
POWERUP_SHIELD = "shield"          # Cyan: Absorbs 1 hit
POWERUP_TRIPLE_SHOT = "triple"      # Pink: 3-way spread shots
POWERUP_SPEED = "speed"            # Yellow: Super speed and agility
POWERUP_NUKE = "nuke"              # Orange: Clears all on-screen asteroids
POWERUP_LIFE = "life"              # Green: +1 Life
DEBUFF_SLOW = "slow"               # Purple: Slime debuff, halves speed & fire rate

POWERUP_CONFIG = {
    POWERUP_SHIELD: {
        "name": "SHIELD",
        "color": COLOR_CYAN,
        "symbol": "S",
        "is_debuff": False,
        "duration": POWERUP_DURATION,
    },
    POWERUP_TRIPLE_SHOT: {
        "name": "TRIPLE SHOT",
        "color": COLOR_PINK,
        "symbol": "3X",
        "is_debuff": False,
        "duration": POWERUP_DURATION,
    },
    POWERUP_SPEED: {
        "name": "HYPER SPEED",
        "color": COLOR_YELLOW,
        "symbol": "SPD",
        "is_debuff": False,
        "duration": POWERUP_DURATION,
    },
    POWERUP_NUKE: {
        "name": "MEGA NUKE",
        "color": COLOR_ORANGE,
        "symbol": "BOOM",
        "is_debuff": False,
        "duration": 0.0,
    },
    POWERUP_LIFE: {
        "name": "+1 LIFE",
        "color": COLOR_GREEN,
        "symbol": "+1",
        "is_debuff": False,
        "duration": 0.0,
    },
    DEBUFF_SLOW: {
        "name": "GLITCH SLOW",
        "color": COLOR_PURPLE,
        "symbol": "SLW",
        "is_debuff": True,
        "duration": 6.0,
    },
}


class PowerUp(CircleShape):
    containers: tuple = ()

    def __init__(self, x: float, y: float, powerup_type: str | None = None) -> None:
        super().__init__(x, y, POWERUP_RADIUS)
        if powerup_type is None:
            # Random weighted choice: mostly buffs, rare debuffs
            choices = [
                POWERUP_SHIELD,
                POWERUP_TRIPLE_SHOT,
                POWERUP_SPEED,
                POWERUP_NUKE,
                POWERUP_LIFE,
                DEBUFF_SLOW,
            ]
            weights = [25, 25, 20, 10, 10, 10]
            self.powerup_type = random.choices(choices, weights=weights)[0]
        else:
            self.powerup_type = powerup_type

        self.config = POWERUP_CONFIG[self.powerup_type]
        self.lifetime = 12.0  # Disappears after 12 seconds if not collected
        self.max_lifetime = self.lifetime
        self.age = 0.0
        self.pulse_phase = random.uniform(0, math.pi * 2)

        # Gentle drift in random direction
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(15, 35)
        self.velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)

    def update(self, dt: float) -> None:
        self.age += dt
        self.lifetime -= dt
        self.pulse_phase += 4.0 * dt

        if self.lifetime <= 0:
            self.kill()
            return

        self.position += self.velocity * dt

        # Screen wrap
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    def draw(self, screen: pygame.Surface) -> None:
        # Blink when expiring
        if self.lifetime < 3.0:
            if int(self.lifetime * 8) % 2 == 0:
                return

        color = self.config["color"]
        center = (int(self.position.x), int(self.position.y))

        # Pulsing outer aura ring
        pulse = 1.0 + 0.25 * math.sin(self.pulse_phase)
        outer_radius = max(2, int(self.radius * pulse))

        # Translucent glow circle
        glow_surf = pygame.Surface((outer_radius * 2 + 4, outer_radius * 2 + 4), pygame.SRCALPHA)
        glow_color = (*color[:3], 65)
        pygame.draw.circle(glow_surf, glow_color, (outer_radius + 2, outer_radius + 2), outer_radius)
        screen.blit(glow_surf, (center[0] - outer_radius - 2, center[1] - outer_radius - 2))

        # Diamond / Hexagon shape container
        points = []
        num_points = 6 if not self.config["is_debuff"] else 8
        for i in range(num_points):
            ang = (i * 2 * math.pi / num_points) + self.age * 1.5
            px = center[0] + math.cos(ang) * self.radius
            py = center[1] + math.sin(ang) * self.radius
            points.append((px, py))

        # Fill inner polygon
        fill_color = (*[int(c * 0.35) for c in color[:3]],)
        pygame.draw.polygon(screen, fill_color, points)
        # Border
        pygame.draw.polygon(screen, color, points, 2)

        # Label text
        font = pygame.font.Font(None, 18)
        text_surf = font.render(self.config["symbol"], True, (255, 255, 255))
        rect = text_surf.get_rect(center=center)
        screen.blit(text_surf, rect)
