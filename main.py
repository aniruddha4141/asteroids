import json
import os
import sys
import pygame
from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import (
    COLOR_CYAN,
    COLOR_PINK,
    DIFF_NORMAL,
    DIFFICULTIES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STATE_GAME_OVER,
    STATE_HANGAR,
    STATE_MENU,
    STATE_OPTIONS,
    STATE_PAUSED,
    STATE_PLAYING,
)
from logger import log_event, log_state
from particles import ParticleManager
from player import Player
from powerup import POWERUP_NUKE, PowerUp
from shot import Shot
from skins import ALL_SKINS, get_skin
from sound import SoundManager
from ui import Button, UIManager

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.txt")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


def load_high_score() -> int:
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
    except Exception:
        pass
    return 0


def save_high_score(score: int) -> None:
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass


def load_settings() -> dict:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"skin_id": "cyan_phantom", "difficulty": DIFF_NORMAL}


def save_settings(settings: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def main():
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ASTEROIDS - Cyberpunk Arcade Edition")
    clock = pygame.time.Clock()
    dt = 0.0

    # Procedural Audio Synthesizer
    sounds = SoundManager()
    Button.sound_manager = sounds

    # Load persistent settings
    user_settings = load_settings()
    current_skin_id = user_settings.get("skin_id", "cyan_phantom")
    current_skin = get_skin(current_skin_id)
    current_diff_key = user_settings.get("difficulty", DIFF_NORMAL)
    if current_diff_key not in DIFFICULTIES:
        current_diff_key = DIFF_NORMAL
    current_diff = DIFFICULTIES[current_diff_key]

    # Particle system & starfield
    particles = ParticleManager()

    # Sprite Groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Assign containers
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = updatable
    Shot.containers = (shots, updatable, drawable)
    PowerUp.containers = (powerups, updatable, drawable)

    # Game State Variables
    current_state = STATE_MENU
    score = 0
    high_score = load_high_score()
    combo = 1
    combo_timer = 0.0
    asteroids_destroyed = 0
    is_new_high = False

    # Create Player & Asteroid Field
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, skin=current_skin)
    player.particle_manager = particles
    player.sound_manager = sounds
    player.set_difficulty(current_diff)

    asteroid_field = AsteroidField()
    asteroid_field.set_difficulty(current_diff["spawn_rate"], current_diff["speed_mult"])

    # State transition callbacks
    def start_game():
        nonlocal current_state, score, combo, combo_timer, asteroids_destroyed, is_new_high
        score = 0
        combo = 1
        combo_timer = 0.0
        asteroids_destroyed = 0
        is_new_high = False

        for a in list(asteroids):
            a.kill()
        for s in list(shots):
            s.kill()
        for p in list(powerups):
            p.kill()

        player.set_difficulty(current_diff)
        player.reset()
        asteroid_field.set_difficulty(current_diff["spawn_rate"], current_diff["speed_mult"])
        current_state = STATE_PLAYING

    def resume_game():
        nonlocal current_state
        current_state = STATE_PLAYING

    def restart_game():
        start_game()

    def open_options():
        nonlocal current_state
        current_state = STATE_OPTIONS

    def open_hangar():
        nonlocal current_state
        current_state = STATE_HANGAR

    def open_menu():
        nonlocal current_state
        current_state = STATE_MENU

    def quit_game():
        if score > high_score:
            save_high_score(score)
        save_settings({"skin_id": current_skin.skin_id, "difficulty": current_diff_key})
        pygame.quit()
        sys.exit()

    def on_skin_change(new_skin):
        nonlocal current_skin
        current_skin = new_skin
        player.set_skin(new_skin)
        save_settings({"skin_id": current_skin.skin_id, "difficulty": current_diff_key})

    def on_diff_change(new_diff_key):
        nonlocal current_diff_key, current_diff
        current_diff_key = new_diff_key
        current_diff = DIFFICULTIES[new_diff_key]
        player.set_difficulty(current_diff)
        asteroid_field.set_difficulty(current_diff["spawn_rate"], current_diff["speed_mult"])
        save_settings({"skin_id": current_skin.skin_id, "difficulty": current_diff_key})

    ui_manager = UIManager(
        on_start=start_game,
        on_resume=resume_game,
        on_restart=restart_game,
        on_options=open_options,
        on_hangar=open_hangar,
        on_menu=open_menu,
        on_quit=quit_game,
        on_skin_change=on_skin_change,
        on_difficulty_change=on_diff_change,
        on_toggle_sound=sounds.toggle_sound,
    )

    # Sync UI selection indices
    for idx, s in enumerate(ALL_SKINS):
        if s.skin_id == current_skin_id:
            ui_manager.selected_skin_idx = idx
            break

    for idx, dk in enumerate(ui_manager.diff_keys):
        if dk == current_diff_key:
            ui_manager._select_diff(idx)
            break

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == STATE_PLAYING:
                        current_state = STATE_PAUSED
                    elif current_state == STATE_PAUSED:
                        current_state = STATE_PLAYING
                    elif current_state in (STATE_OPTIONS, STATE_HANGAR):
                        current_state = STATE_MENU

                elif event.key == pygame.K_m:
                    sounds.toggle_sound()

            ui_manager.handle_event(event, current_state)

        # Update Phase
        particles.update(dt)
        ui_manager.update(dt, current_state)

        if current_state == STATE_PLAYING:
            log_state()
            updatable.update(dt)

            # Update Combo
            if combo_timer > 0:
                combo_timer -= dt
                if combo_timer <= 0:
                    combo = 1

            # Check Asteroid Collisions
            for asteroid in list(asteroids):
                # Asteroid vs Player
                if asteroid.collides_with(player):
                    log_event("player_hit")
                    lost_life = player.hit(particles)
                    if lost_life:
                        if player.lives <= 0:
                            current_state = STATE_GAME_OVER
                            if score > high_score:
                                high_score = score
                                is_new_high = True
                                save_high_score(high_score)
                            break

                # Asteroid vs Shots
                for shot in list(shots):
                    if asteroid.collides_with(shot):
                        log_event("asteroid_shot")
                        shot.kill()
                        # Laser impact sparks
                        particles.add_impact_sparks(
                            shot.position,
                            shot.velocity.normalize(),
                            shot.color,
                        )
                        awarded = asteroid.split(
                            particle_manager=particles,
                            drop_chance=current_diff["drop_chance"],
                            sound_manager=sounds,
                        )
                        combo_mult = max(1, combo)
                        final_awarded = int(awarded * combo_mult * current_diff["score_mult"])
                        score += final_awarded
                        asteroids_destroyed += 1
                        combo = min(8, combo + 1)
                        combo_timer = 2.5
                        break

            # Check Power-up Collisions
            for p in list(powerups):
                if p.collides_with(player):
                    if p.powerup_type == POWERUP_NUKE:
                        sounds.play("nuke")
                        particles.add_nuke(player.position)
                        particles.add_popup(player.position, "MEGA NUKE DETONATED!", (255, 140, 20))
                        for ast in list(asteroids):
                            pts = ast.split(
                                particle_manager=particles,
                                drop_chance=current_diff["drop_chance"],
                                sound_manager=sounds,
                            )
                            score += int(pts * current_diff["score_mult"])
                            asteroids_destroyed += 1
                    else:
                        player.apply_powerup(p.powerup_type, particle_mgr=particles)
                    p.kill()

        elif current_state == STATE_MENU:
            for a in asteroids:
                a.update(dt * 0.4)
            for p in powerups:
                p.update(dt * 0.4)

        # Drawing Phase onto world render surface
        particles.draw_background(render_surf)

        if current_state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER):
            for obj in drawable:
                obj.draw(render_surf)

        particles.draw_effects(render_surf)

        # In-game HUD with threat radar
        if current_state in (STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER):
            ui_manager.hud.draw(
                render_surf,
                score=score,
                high_score=high_score,
                combo=combo,
                combo_timer=combo_timer,
                player=player,
                diff_name=current_diff["name"],
                diff_color=current_diff["color"],
                diff_score_mult=current_diff["score_mult"],
                sound_enabled=sounds.enabled,
                asteroids=asteroids,
            )

        # Apply Screen Shake Offset in PLAYING state
        shake_offset = particles.shake.get_offset() if current_state == STATE_PLAYING else (0, 0)
        screen.fill((0, 0, 0))
        screen.blit(render_surf, shake_offset)

        # UI Overlays (drawn directly on screen without camera shake)
        if current_state == STATE_MENU:
            ui_manager.draw_menu(screen, high_score, sound_enabled=sounds.enabled)
        elif current_state == STATE_HANGAR:
            ui_manager.draw_hangar(screen)
        elif current_state == STATE_OPTIONS:
            ui_manager.draw_options(screen)
        elif current_state == STATE_PAUSED:
            ui_manager.draw_paused(screen)
        elif current_state == STATE_GAME_OVER:
            ui_manager.draw_game_over(
                screen,
                final_score=score,
                high_score=high_score,
                asteroids_destroyed=asteroids_destroyed,
                is_new_high=is_new_high,
            )

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()
