import math
import pygame
from circleshape import CircleShape
from constants import (
    COLOR_CYAN,
    COLOR_PINK,
    COLOR_PURPLE,
    COLOR_YELLOW,
    LINE_WIDTH,
    PLAYER_INVULNERABLE_TIME,
    PLAYER_MAX_LIVES,
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN_SECONDS,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    POWERUP_DURATION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from powerup import (
    DEBUFF_SLOW,
    POWERUP_LIFE,
    POWERUP_NUKE,
    POWERUP_SHIELD,
    POWERUP_SPEED,
    POWERUP_TRIPLE_SHOT,
)
from shot import Shot
from skins import Skin, get_skin


class Player(CircleShape):
    containers: tuple = ()

    def __init__(self, x: float, y: float, skin: Skin | None = None) -> None:
        super().__init__(x, y, PLAYER_RADIUS)
        self.spawn_pos = pygame.Vector2(x, y)
        self.rotation = 0.0
        self.shoot_cooldown = 0.0
        self.max_lives = PLAYER_MAX_LIVES
        self.lives = self.max_lives
        self.skin = skin or get_skin("cyan_phantom")

        # Smooth arcade inertia physics
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 520.0
        self.drag = 0.988

        # Buff & Debuff Timers
        self.shield_active = False
        self.triple_shot_timer = 0.0
        self.speed_boost_timer = 0.0
        self.slow_debuff_timer = 0.0
        self.invulnerable_timer = 0.0

        # Animation states & references
        self.shield_angle = 0.0
        self.thrusting = False
        self.braking = False
        self.particle_manager = None
        self.sound_manager = None

    def set_skin(self, skin: Skin) -> None:
        self.skin = skin

    def set_difficulty(self, diff_config: dict) -> None:
        self.max_lives = diff_config.get("lives", 3)
        self.lives = self.max_lives

    def reset(self) -> None:
        self.position = pygame.Vector2(self.spawn_pos)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0.0
        self.shoot_cooldown = 0.0
        self.shield_active = False
        self.triple_shot_timer = 0.0
        self.speed_boost_timer = 0.0
        self.slow_debuff_timer = 0.0
        self.invulnerable_timer = PLAYER_INVULNERABLE_TIME
        self.lives = self.max_lives

    def triangle(self) -> list[pygame.Vector2]:
        return self.skin.get_polygon(self.position, self.rotation, self.radius)

    def draw(self, screen: pygame.Surface) -> None:
        # Flickering during invulnerability
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 12) % 2 == 0:
                return

        # Base Ship Hull Color
        ship_color = self.skin.primary_color
        accent_color = self.skin.accent_color
        if self.slow_debuff_timer > 0:
            ship_color = (180, 100, 255)  # Purple tint when glitched
            accent_color = (220, 150, 255)
        elif self.speed_boost_timer > 0:
            ship_color = (255, 240, 100)  # Golden tint when boosted
            accent_color = (255, 255, 200)

        poly = self.triangle()

        # Fill ship body with darker hue
        fill_color = (
            max(0, int(ship_color[0] * 0.2)),
            max(0, int(ship_color[1] * 0.2)),
            max(0, int(ship_color[2] * 0.3)),
        )
        if len(poly) >= 3:
            pygame.draw.polygon(screen, fill_color, poly)
            pygame.draw.polygon(screen, ship_color, poly, LINE_WIDTH)

        # Cockpit accent
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        cockpit_pos = self.position + forward * (self.radius * 0.22)
        pygame.draw.circle(screen, accent_color, (int(cockpit_pos.x), int(cockpit_pos.y)), 3)

        # Draw Shield Sphere if active
        if self.shield_active:
            shield_r = int(self.radius * 1.55)
            shield_surf = pygame.Surface((shield_r * 2 + 4, shield_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                shield_surf,
                (0, 240, 255, 45),
                (shield_r + 2, shield_r + 2),
                shield_r,
            )
            pygame.draw.circle(
                shield_surf,
                (0, 245, 255, 180),
                (shield_r + 2, shield_r + 2),
                shield_r,
                2,
            )
            screen.blit(
                shield_surf,
                (int(self.position.x) - shield_r - 2, int(self.position.y) - shield_r - 2),
            )

            for offset_ang in [0, 120, 240]:
                ang = math.radians(self.shield_angle + offset_ang)
                nx = int(self.position.x + math.cos(ang) * shield_r)
                ny = int(self.position.y + math.sin(ang) * shield_r)
                pygame.draw.circle(screen, (150, 255, 255), (nx, ny), 3)

    def rotate(self, dt: float) -> None:
        turn_mult = 0.65 if self.slow_debuff_timer > 0 else 1.0
        if self.speed_boost_timer > 0:
            turn_mult = 1.25
        self.rotation += PLAYER_TURN_SPEED * turn_mult * dt

    def move(self, dt: float) -> None:
        speed_mult = 1.0
        if self.slow_debuff_timer > 0:
            speed_mult = 0.55
        elif self.speed_boost_timer > 0:
            speed_mult = 1.60

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        # Apply forward thruster acceleration
        self.velocity += forward * (self.acceleration * speed_mult * dt)

        # Emit thruster particles
        if self.particle_manager and self.thrusting:
            engine_pos = self.position - forward * (self.radius * 0.8)
            thrust_color = self.skin.engine_color
            if self.speed_boost_timer > 0:
                thrust_color = (0, 240, 255)
            elif self.slow_debuff_timer > 0:
                thrust_color = (180, 50, 255)
            self.particle_manager.add_thrust(engine_pos, forward, thrust_color)

    def shoot(self) -> None:
        if self.shoot_cooldown > 0:
            return

        cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        if self.slow_debuff_timer > 0:
            cooldown *= 1.6
        elif self.speed_boost_timer > 0:
            cooldown *= 0.65

        self.shoot_cooldown = cooldown

        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        spawn_pos = self.position + forward * (self.radius + 3)

        if self.triple_shot_timer > 0:
            # 3-way spread shots
            for angle_offset in (-18, 0, 18):
                shot = Shot(spawn_pos.x, spawn_pos.y, color=COLOR_PINK)
                shot_dir = forward.rotate(angle_offset)
                shot.velocity = shot_dir * (PLAYER_SHOOT_SPEED * 1.1)
            if self.particle_manager:
                self.particle_manager.add_thrust(spawn_pos, -forward, color=COLOR_PINK)
                self.particle_manager.add_muzzle_flash(spawn_pos, forward, COLOR_PINK)
            if self.sound_manager:
                self.sound_manager.play("triple_laser")
        else:
            # Standard single shot with skin's energy laser color!
            shot = Shot(spawn_pos.x, spawn_pos.y, color=self.skin.shot_color)
            shot.velocity = forward * PLAYER_SHOOT_SPEED
            if self.particle_manager:
                self.particle_manager.add_muzzle_flash(spawn_pos, forward, self.skin.shot_color)
            if self.sound_manager:
                self.sound_manager.play("laser")

    def apply_powerup(self, powerup_type: str, particle_mgr=None) -> None:
        if self.sound_manager:
            self.sound_manager.play("powerup")

        if powerup_type == POWERUP_SHIELD:
            self.shield_active = True
            if particle_mgr:
                particle_mgr.add_popup(self.position, "SHIELD CHARGED!", COLOR_CYAN)
        elif powerup_type == POWERUP_TRIPLE_SHOT:
            self.triple_shot_timer = POWERUP_DURATION
            if particle_mgr:
                particle_mgr.add_popup(self.position, "TRIPLE CANNON!", COLOR_PINK)
        elif powerup_type == POWERUP_SPEED:
            self.speed_boost_timer = POWERUP_DURATION
            if particle_mgr:
                particle_mgr.add_popup(self.position, "HYPER DRIVE!", COLOR_YELLOW)
        elif powerup_type == POWERUP_LIFE:
            self.lives = min(self.max_lives + 2, self.lives + 1)
            if particle_mgr:
                particle_mgr.add_popup(self.position, "+1 EXTRA LIFE!", (60, 255, 120))
        elif powerup_type == DEBUFF_SLOW:
            self.slow_debuff_timer = 6.0
            if particle_mgr:
                particle_mgr.add_popup(self.position, "SYSTEM GLITCH!", COLOR_PURPLE)

    def hit(self, particle_mgr=None) -> bool:
        """Returns True if player actually loses a life, False if absorbed or invulnerable."""
        if self.invulnerable_timer > 0:
            return False

        if self.shield_active:
            self.shield_active = False
            self.invulnerable_timer = 1.0
            if self.sound_manager:
                self.sound_manager.play("shield_hit")
            if particle_mgr:
                particle_mgr.add_explosion(self.position, COLOR_CYAN, count=30, speed=220.0)
                particle_mgr.add_popup(self.position, "SHIELD BROKEN!", COLOR_CYAN)
            return False

        # Lose a life
        self.lives -= 1
        if self.sound_manager:
            self.sound_manager.play("player_hit")
        if particle_mgr:
            particle_mgr.add_explosion(self.position, (255, 80, 80), count=45, speed=280.0)
            particle_mgr.add_popup(self.position, "-1 LIFE!", (255, 60, 60))

        # Reset active buffs/debuffs on respawn
        self.triple_shot_timer = 0.0
        self.speed_boost_timer = 0.0
        self.slow_debuff_timer = 0.0
        self.invulnerable_timer = PLAYER_INVULNERABLE_TIME
        self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)
        return True

    def update(self, dt: float) -> None:
        self.shoot_cooldown -= dt
        self.shield_angle += 120.0 * dt

        # Update buff and debuff timers
        if self.triple_shot_timer > 0:
            self.triple_shot_timer -= dt
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
        if self.slow_debuff_timer > 0:
            self.slow_debuff_timer -= dt
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(dt)

        self.thrusting = keys[pygame.K_w] or keys[pygame.K_UP]
        if self.thrusting:
            self.move(dt)

        # Retro-braking reverse thrusters
        self.braking = keys[pygame.K_s] or keys[pygame.K_DOWN]

        # Apply realistic space friction / damping
        drag_coeff = 0.94 if self.braking else self.drag
        drag_step = drag_coeff ** (dt * 60.0)
        self.velocity *= drag_step

        # Clamp max speed
        max_vel = 360.0 * (1.55 if self.speed_boost_timer > 0 else (0.55 if self.slow_debuff_timer > 0 else 1.0))
        if self.velocity.length() > max_vel:
            self.velocity.scale_to_length(max_vel)

        # Update position by momentum velocity
        self.position += self.velocity * dt

        if keys[pygame.K_SPACE]:
            self.shoot()

        # Screen wrapping
        pad = self.radius
        if self.position.x < -pad:
            self.position.x = SCREEN_WIDTH + pad
        elif self.position.x > SCREEN_WIDTH + pad:
            self.position.x = -pad

        if self.position.y < -pad:
            self.position.y = SCREEN_HEIGHT + pad
        elif self.position.y > SCREEN_HEIGHT + pad:
            self.position.y = -pad
