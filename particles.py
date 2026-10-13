import math
import random
import pygame
from constants import COLOR_BG, SCREEN_HEIGHT, SCREEN_WIDTH


class Star:
    def __init__(self) -> None:
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.speed = random.uniform(5, 25)
        self.size = random.choice([1, 1, 1, 2, 2, 3])
        brightness = random.randint(140, 255)
        self.color = (brightness, brightness, min(255, brightness + 20))
        self.twinkle_speed = random.uniform(1.5, 4.0)
        self.twinkle_phase = random.uniform(0, math.pi * 2)

    def update(self, dt: float) -> None:
        self.y = (self.y + self.speed * dt) % SCREEN_HEIGHT
        self.twinkle_phase += self.twinkle_speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        alpha = int(180 + 75 * math.sin(self.twinkle_phase))
        color = (
            min(255, int(self.color[0] * (alpha / 255))),
            min(255, int(self.color[1] * (alpha / 255))),
            min(255, int(self.color[2] * (alpha / 255))),
        )
        if self.size == 1:
            screen.set_at((int(self.x), int(self.y)), color)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Particle:
    def __init__(
        self,
        pos: pygame.Vector2,
        velocity: pygame.Vector2,
        color: tuple[int, int, int],
        lifetime: float,
        size: float = 3.0,
    ) -> None:
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.position += self.velocity * dt
        self.velocity *= 0.96  # friction
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.lifetime <= 0:
            return
        factor = max(0.0, self.lifetime / self.max_lifetime)
        current_size = max(1.0, self.size * factor)
        alpha = int(255 * factor)
        c = (
            min(255, int(self.color[0] * (alpha / 255))),
            min(255, int(self.color[1] * (alpha / 255))),
            min(255, int(self.color[2] * (alpha / 255))),
        )
        pygame.draw.circle(screen, c, (int(self.position.x), int(self.position.y)), int(current_size))


class Shockwave:
    def __init__(self, pos: pygame.Vector2, color: tuple[int, int, int], max_radius: float = 180.0, speed: float = 400.0) -> None:
        self.position = pygame.Vector2(pos)
        self.color = color
        self.radius = 5.0
        self.max_radius = max_radius
        self.speed = speed

    def update(self, dt: float) -> bool:
        self.radius += self.speed * dt
        return self.radius < self.max_radius

    def draw(self, screen: pygame.Surface) -> None:
        factor = 1.0 - (self.radius / self.max_radius)
        if factor <= 0:
            return
        width = max(1, int(3 * factor))
        c = (
            int(self.color[0] * factor),
            int(self.color[1] * factor),
            int(self.color[2] * factor),
        )
        pygame.draw.circle(screen, c, (int(self.position.x), int(self.position.y)), int(self.radius), width)


class FloatingText:
    def __init__(self, pos: pygame.Vector2, text: str, color: tuple[int, int, int], font: pygame.font.Font, duration: float = 1.2) -> None:
        self.position = pygame.Vector2(pos)
        self.text = text
        self.color = color
        self.font = font
        self.lifetime = duration
        self.max_lifetime = duration

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.position.y -= 35 * dt  # float upward
        return self.lifetime > 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.lifetime <= 0:
            return
        factor = max(0.0, self.lifetime / self.max_lifetime)
        text_surf = self.font.render(self.text, True, self.color)
        alpha = int(255 * factor)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(int(self.position.x), int(self.position.y)))
        screen.blit(text_surf, rect)


class ScreenShake:
    def __init__(self) -> None:
        self.trauma = 0.0

    def add_trauma(self, amount: float) -> None:
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt: float) -> None:
        if self.trauma > 0:
            self.trauma = max(0.0, self.trauma - dt * 2.2)

    def get_offset(self) -> tuple[int, int]:
        if self.trauma <= 0:
            return (0, 0)
        shake = self.trauma * self.trauma
        max_disp = 14.0 * shake
        return (
            int(random.uniform(-max_disp, max_disp)),
            int(random.uniform(-max_disp, max_disp)),
        )


class ParticleManager:
    def __init__(self) -> None:
        self.stars = [Star() for _ in range(120)]
        self.particles: list[Particle] = []
        self.shockwaves: list[Shockwave] = []
        self.popups: list[FloatingText] = []
        self.shake = ScreenShake()
        self.font = pygame.font.Font(None, 24)

    def update(self, dt: float) -> None:
        for s in self.stars:
            s.update(dt)
        self.shake.update(dt)
        self.particles = [p for p in self.particles if p.update(dt)]
        self.shockwaves = [w for w in self.shockwaves if w.update(dt)]
        self.popups = [t for t in self.popups if t.update(dt)]

    def draw_background(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BG)
        for s in self.stars:
            s.draw(screen)

    def draw_effects(self, screen: pygame.Surface) -> None:
        for w in self.shockwaves:
            w.draw(screen)
        for p in self.particles:
            p.draw(screen)
        for t in self.popups:
            t.draw(screen)

    def add_explosion(self, pos: pygame.Vector2, color: tuple[int, int, int], count: int = 24, speed: float = 160.0) -> None:
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(20, speed)
            vel = pygame.Vector2(math.cos(angle) * spd, math.sin(angle) * spd)
            life = random.uniform(0.3, 0.85)
            size = random.uniform(2.0, 4.5)
            self.particles.append(Particle(pos, vel, color, life, size))
        self.shockwaves.append(Shockwave(pos, color, max_radius=60.0, speed=250.0))
        self.shake.add_trauma(0.22 if count < 25 else 0.42)

    def add_impact_sparks(self, pos: pygame.Vector2, normal: pygame.Vector2, color: tuple[int, int, int], count: int = 10) -> None:
        for _ in range(count):
            angle = math.atan2(normal.y, normal.x) + random.uniform(-1.0, 1.0)
            spd = random.uniform(100, 320)
            vel = pygame.Vector2(math.cos(angle) * spd, math.sin(angle) * spd)
            self.particles.append(Particle(pos, vel, color, random.uniform(0.15, 0.35), size=2.5))

    def add_muzzle_flash(self, pos: pygame.Vector2, forward: pygame.Vector2, color: tuple[int, int, int]) -> None:
        for _ in range(5):
            spread = random.uniform(-0.4, 0.4)
            vel = forward.rotate(math.degrees(spread)) * random.uniform(80, 200)
            self.particles.append(Particle(pos, vel, (255, 255, 255), random.uniform(0.08, 0.18), size=2.0))

    def add_thrust(self, pos: pygame.Vector2, forward: pygame.Vector2, color: tuple[int, int, int] = (255, 120, 20)) -> None:
        spread = random.uniform(-0.35, 0.35)
        plume_dir = -forward.rotate(math.degrees(spread))
        speed = random.uniform(120, 260)
        vel = plume_dir * speed
        life = random.uniform(0.12, 0.30)
        size = random.uniform(2.5, 4.5)
        self.particles.append(Particle(pos, vel, color, life, size))

    def add_nuke(self, pos: pygame.Vector2) -> None:
        self.shockwaves.append(Shockwave(pos, (255, 240, 100), max_radius=SCREEN_WIDTH * 0.9, speed=750.0))
        self.shockwaves.append(Shockwave(pos, (0, 240, 255), max_radius=SCREEN_WIDTH * 0.7, speed=500.0))
        for _ in range(60):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(80, 450)
            vel = pygame.Vector2(math.cos(angle) * spd, math.sin(angle) * spd)
            self.particles.append(Particle(pos, vel, (255, 200, 80), random.uniform(0.5, 1.2), random.uniform(3, 6)))
        self.shake.add_trauma(1.0)

    def add_popup(self, pos: pygame.Vector2, text: str, color: tuple[int, int, int]) -> None:
        self.popups.append(FloatingText(pos, text, color, self.font))
