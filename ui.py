import math
import pygame
from constants import (
    COLOR_CYAN,
    COLOR_GRAY,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PINK,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    DIFF_EASY,
    DIFF_EXTREME,
    DIFF_HARD,
    DIFF_NORMAL,
    DIFFICULTIES,
    LINE_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STATE_HANGAR,
)
from powerup import POWERUP_CONFIG
from skins import ALL_SKINS, Skin


class Button:
    sound_manager = None

    def __init__(
        self,
        rect: tuple[int, int, int, int] | pygame.Rect,
        text: str,
        callback,
        font: pygame.font.Font,
        base_color: tuple[int, int, int] = (25, 30, 50),
        hover_color: tuple[int, int, int] = (40, 50, 85),
        border_color: tuple[int, int, int] = COLOR_CYAN,
        text_color: tuple[int, int, int] = COLOR_WHITE,
        selected: bool = False,
    ) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.is_hovered = False
        self.selected = selected
        self.click_animation = 0.0

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            new_hover = self.rect.collidepoint(event.pos)
            if new_hover and not self.is_hovered:
                if Button.sound_manager:
                    Button.sound_manager.play("ui_hover", 0.35)
            self.is_hovered = new_hover
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.click_animation = 0.15
                if Button.sound_manager:
                    Button.sound_manager.play("ui_click", 0.65)
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, dt: float) -> None:
        if self.click_animation > 0:
            self.click_animation = max(0.0, self.click_animation - dt)

    def draw(self, screen: pygame.Surface) -> None:
        draw_rect = self.rect.copy()
        if self.click_animation > 0:
            draw_rect.y += 2

        # Background color
        if self.selected:
            current_bg = (int(self.border_color[0] * 0.35), int(self.border_color[1] * 0.35), int(self.border_color[2] * 0.35))
        elif self.is_hovered:
            current_bg = self.hover_color
        else:
            current_bg = self.base_color

        bg_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        bg_surf.fill((*current_bg, 220))
        screen.blit(bg_surf, draw_rect.topleft)

        # Border & glow
        if self.selected:
            border_c = (255, 255, 255)
            border_w = 3
        elif self.is_hovered:
            border_c = (255, 255, 255)
            border_w = 3
        else:
            border_c = self.border_color
            border_w = 2

        pygame.draw.rect(screen, border_c, draw_rect, border_w, border_radius=6)

        if self.is_hovered or self.selected:
            corner_len = 8
            accent = COLOR_PINK if not self.selected else self.border_color
            pygame.draw.line(screen, accent, draw_rect.topleft, (draw_rect.left + corner_len, draw_rect.top), 3)
            pygame.draw.line(screen, accent, draw_rect.topleft, (draw_rect.left, draw_rect.top + corner_len), 3)
            pygame.draw.line(screen, accent, draw_rect.bottomright, (draw_rect.right - corner_len, draw_rect.bottom), 3)
            pygame.draw.line(screen, accent, draw_rect.bottomright, (draw_rect.right, draw_rect.bottom - corner_len), 3)

        txt_c = (255, 255, 255) if (self.is_hovered or self.selected) else self.text_color
        txt_surf = self.font.render(self.text, True, txt_c)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        screen.blit(txt_surf, txt_rect)


class HUD:
    def __init__(self) -> None:
        self.font_large = pygame.font.Font(None, 42)
        self.font_medium = pygame.font.Font(None, 26)
        self.font_small = pygame.font.Font(None, 20)

    def draw(
        self,
        screen: pygame.Surface,
        score: int,
        high_score: int,
        combo: int,
        combo_timer: float,
        player,
        diff_name: str = "NORMAL",
        diff_color: tuple[int, int, int] = COLOR_CYAN,
        diff_score_mult: float = 1.0,
        sound_enabled: bool = True,
        asteroids: pygame.sprite.Group | None = None,
    ) -> None:
        # 1. Top-Left: Score, Difficulty Tag, and Combo
        score_label = self.font_small.render("SCORE", True, COLOR_GRAY)
        screen.blit(score_label, (25, 16))
        score_val = self.font_large.render(f"{score:06d}", True, COLOR_CYAN)
        screen.blit(score_val, (25, 32))

        diff_tag = f"[{diff_name} x{diff_score_mult:.2f}]"
        diff_surf = self.font_small.render(diff_tag, True, diff_color)
        screen.blit(diff_surf, (155, 16))

        if combo > 1:
            combo_text = f"COMBO x{combo}"
            combo_surf = self.font_medium.render(combo_text, True, COLOR_ORANGE)
            screen.blit(combo_surf, (190, 38))
            bar_w = int(max(0.0, (combo_timer / 2.5)) * 90)
            if bar_w > 0:
                pygame.draw.rect(screen, COLOR_ORANGE, (190, 62, bar_w, 4), border_radius=2)

        # 2. Top-Right: High Score & Sound Status
        high_label = self.font_small.render("HIGH SCORE", True, COLOR_GRAY)
        high_label_rect = high_label.get_rect(topright=(SCREEN_WIDTH - 25, 16))
        screen.blit(high_label, high_label_rect)

        high_val = self.font_large.render(f"{high_score:06d}", True, COLOR_YELLOW)
        high_val_rect = high_val.get_rect(topright=(SCREEN_WIDTH - 25, 32))
        screen.blit(high_val, high_val_rect)

        # Audio Toggle Badge
        snd_txt = "[M] AUDIO: ON" if sound_enabled else "[M] AUDIO: MUTED"
        snd_col = (130, 160, 190) if sound_enabled else COLOR_RED
        snd_surf = self.font_small.render(snd_txt, True, snd_col)
        snd_rect = snd_surf.get_rect(bottomright=(SCREEN_WIDTH - 25, SCREEN_HEIGHT - 18))
        screen.blit(snd_surf, snd_rect)

        # 3. Bottom-Left: Player Lives Icons
        lives_y = SCREEN_HEIGHT - 35
        lives_label = self.font_small.render("HULL INTEGRITY", True, COLOR_GRAY)
        screen.blit(lives_label, (25, lives_y - 20))

        for i in range(max(0, player.lives)):
            lx = 35 + i * 26
            ly = lives_y
            mini_pos = pygame.Vector2(lx, ly)
            pts = player.skin.get_polygon(mini_pos, 0, 9.0)
            pygame.draw.polygon(screen, player.skin.primary_color, pts, 2)

        # 4. Top-Center: Active Buffs & Debuffs Badges
        badges = []
        if player.shield_active:
            badges.append(("SHIELD", COLOR_CYAN, 1.0, "ACTIVE"))
        if player.triple_shot_timer > 0:
            ratio = player.triple_shot_timer / 8.5
            badges.append(("TRIPLE SHOT", COLOR_PINK, ratio, f"{player.triple_shot_timer:.1f}s"))
        if player.speed_boost_timer > 0:
            ratio = player.speed_boost_timer / 8.5
            badges.append(("HYPER SPEED", COLOR_YELLOW, ratio, f"{player.speed_boost_timer:.1f}s"))
        if player.slow_debuff_timer > 0:
            ratio = player.slow_debuff_timer / 6.0
            badges.append(("GLITCH SLOW", COLOR_PURPLE, ratio, f"{player.slow_debuff_timer:.1f}s"))

        if badges:
            total_w = len(badges) * 140 - 10
            start_x = (SCREEN_WIDTH - total_w) // 2
            for idx, (b_name, b_col, b_ratio, b_time) in enumerate(badges):
                bx = start_x + idx * 140
                by = 18
                bw, bh = 130, 36

                pill_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
                pill_surf.fill((20, 24, 38, 200))
                screen.blit(pill_surf, (bx, by))
                pygame.draw.rect(screen, b_col, (bx, by, bw, bh), 1, border_radius=4)

                lbl = self.font_small.render(f"{b_name} {b_time}", True, b_col)
                lbl_rect = lbl.get_rect(center=(bx + bw // 2, by + bh // 2 - 4))
                screen.blit(lbl, lbl_rect)

                meter_w = int(max(0.0, min(1.0, b_ratio)) * (bw - 10))
                pygame.draw.rect(screen, b_col, (bx + 5, by + bh - 7, meter_w, 3), border_radius=1)

        # 5. Off-screen Threat Radar Arrows
        if asteroids:
            margin = 20
            for ast in asteroids:
                if ast.radius >= 35:
                    is_outside = (
                        ast.position.x < 0
                        or ast.position.x > SCREEN_WIDTH
                        or ast.position.y < 0
                        or ast.position.y > SCREEN_HEIGHT
                    )
                    if is_outside:
                        cx = max(margin, min(SCREEN_WIDTH - margin, int(ast.position.x)))
                        cy = max(margin, min(SCREEN_HEIGHT - margin, int(ast.position.y)))
                        to_ast = (ast.position - pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                        if to_ast.length() > 0:
                            fwd = to_ast.normalize()
                            p1 = pygame.Vector2(cx, cy) + fwd * 7
                            p2 = pygame.Vector2(cx, cy) - fwd.rotate(90) * 5 - fwd * 5
                            p3 = pygame.Vector2(cx, cy) + fwd.rotate(90) * 5 - fwd * 5
                            pygame.draw.polygon(screen, COLOR_RED, [p1, p2, p3])


class UIManager:
    def __init__(
        self,
        on_start,
        on_resume,
        on_restart,
        on_options,
        on_hangar,
        on_menu,
        on_quit,
        on_skin_change,
        on_difficulty_change,
        on_toggle_sound=None,
    ) -> None:
        self.font_title = pygame.font.Font(None, 78)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 34)
        self.font_subtitle = pygame.font.Font(None, 28)
        self.font_btn = pygame.font.Font(None, 30)
        self.font_body = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        self.hud = HUD()
        self.time_elapsed = 0.0

        # State tracking for Skins & Difficulties
        self.selected_skin_idx = 0
        self.on_skin_change = on_skin_change
        self.diff_keys = [DIFF_EASY, DIFF_NORMAL, DIFF_HARD, DIFF_EXTREME]
        self.selected_diff_idx = 1  # Default NORMAL
        self.on_difficulty_change = on_difficulty_change
        self.on_toggle_sound = on_toggle_sound

        # Menu Buttons
        btn_w, btn_h = 270, 50
        cx = (SCREEN_WIDTH - btn_w) // 2
        cy = 310

        self.menu_buttons = [
            Button((cx, cy, btn_w, btn_h), "START MISSION", on_start, self.font_btn, border_color=COLOR_CYAN),
            Button((cx, cy + 60, btn_w, btn_h), "HANGAR & DIFFICULTY", on_hangar, self.font_btn, border_color=COLOR_GREEN),
            Button((cx, cy + 120, btn_w, btn_h), "INTEL & CONTROLS", on_options, self.font_btn, border_color=COLOR_YELLOW),
            Button((cx, cy + 180, btn_w, btn_h), "QUIT GAME", on_quit, self.font_btn, border_color=COLOR_PINK),
        ]

        # Options Buttons
        self.options_buttons = [
            Button((cx, SCREEN_HEIGHT - 85, btn_w, btn_h), "BACK TO MENU", on_menu, self.font_btn, border_color=COLOR_CYAN),
        ]

        # Pause Buttons
        p_cy = SCREEN_HEIGHT // 2
        self.pause_buttons = [
            Button((cx, p_cy - 30, btn_w, btn_h), "RESUME", on_resume, self.font_btn, border_color=COLOR_GREEN),
            Button((cx, p_cy + 35, btn_w, btn_h), "RESTART", on_restart, self.font_btn, border_color=COLOR_YELLOW),
            Button((cx, p_cy + 100, btn_w, btn_h), "MAIN MENU", on_menu, self.font_btn, border_color=COLOR_PINK),
        ]

        # Game Over Buttons
        self.game_over_buttons = [
            Button((cx, p_cy + 40, btn_w, btn_h), "PLAY AGAIN", on_restart, self.font_btn, border_color=COLOR_GREEN),
            Button((cx, p_cy + 105, btn_w, btn_h), "MAIN MENU", on_menu, self.font_btn, border_color=COLOR_CYAN),
            Button((cx, p_cy + 170, btn_w, btn_h), "QUIT GAME", on_quit, self.font_btn, border_color=COLOR_PINK),
        ]

        # Hangar Navigation Buttons
        self.btn_prev_skin = Button(
            (80, 420, 150, 44),
            "< PREV SHIP",
            self._prev_skin,
            self.font_btn,
            border_color=COLOR_CYAN,
        )
        self.btn_next_skin = Button(
            (410, 420, 150, 44),
            "NEXT SHIP >",
            self._next_skin,
            self.font_btn,
            border_color=COLOR_CYAN,
        )

        diff_start_x = 680
        diff_btn_w = 125
        diff_btn_h = 44
        self.diff_buttons = []
        for i, dk in enumerate(self.diff_keys):
            cfg = DIFFICULTIES[dk]
            bx = diff_start_x + i * (diff_btn_w + 10)
            btn = Button(
                (bx, 190, diff_btn_w, diff_btn_h),
                cfg["name"],
                lambda idx=i: self._select_diff(idx),
                self.font_btn,
                border_color=cfg["color"],
                selected=(i == self.selected_diff_idx),
            )
            self.diff_buttons.append(btn)

        self.btn_hangar_back = Button(
            (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 85, 260, 50),
            "CONFIRM & RETURN",
            on_menu,
            self.font_btn,
            border_color=COLOR_CYAN,
        )

        self.hangar_buttons = [
            self.btn_prev_skin,
            self.btn_next_skin,
            *self.diff_buttons,
            self.btn_hangar_back,
        ]

    def _prev_skin(self) -> None:
        self.selected_skin_idx = (self.selected_skin_idx - 1) % len(ALL_SKINS)
        skin = ALL_SKINS[self.selected_skin_idx]
        if self.on_skin_change:
            self.on_skin_change(skin)

    def _next_skin(self) -> None:
        self.selected_skin_idx = (self.selected_skin_idx + 1) % len(ALL_SKINS)
        skin = ALL_SKINS[self.selected_skin_idx]
        if self.on_skin_change:
            self.on_skin_change(skin)

    def _select_diff(self, idx: int) -> None:
        self.selected_diff_idx = idx
        for i, btn in enumerate(self.diff_buttons):
            btn.selected = (i == idx)
        diff_key = self.diff_keys[idx]
        if self.on_difficulty_change:
            self.on_difficulty_change(diff_key)

    def get_current_skin(self) -> Skin:
        return ALL_SKINS[self.selected_skin_idx]

    def get_current_diff_key(self) -> str:
        return self.diff_keys[self.selected_diff_idx]

    def update(self, dt: float, state: str) -> None:
        self.time_elapsed += dt
        buttons = self._get_buttons_for_state(state)
        for btn in buttons:
            btn.update(dt)

    def handle_event(self, event: pygame.event.Event, state: str) -> bool:
        buttons = self._get_buttons_for_state(state)
        for btn in buttons:
            if btn.handle_event(event):
                return True
        return False

    def _get_buttons_for_state(self, state: str) -> list[Button]:
        if state == "menu":
            return self.menu_buttons
        elif state == "options":
            return self.options_buttons
        elif state == STATE_HANGAR:
            return self.hangar_buttons
        elif state == "paused":
            return self.pause_buttons
        elif state == "game_over":
            return self.game_over_buttons
        return []

    def draw_menu(self, screen: pygame.Surface, high_score: int, sound_enabled: bool = True) -> None:
        title_text = "ASTEROIDS"
        pulse = 0.5 + 0.5 * math.sin(self.time_elapsed * 3.0)

        t_glow = self.font_title.render(title_text, True, (0, int(150 + 90 * pulse), 255))
        glow_rect = t_glow.get_rect(center=(SCREEN_WIDTH // 2, 130))
        screen.blit(t_glow, glow_rect)

        t_core = self.font_title.render(title_text, True, COLOR_WHITE)
        core_rect = t_core.get_rect(center=(SCREEN_WIDTH // 2, 128))
        screen.blit(t_core, core_rect)

        sub = self.font_subtitle.render("CYBERPUNK ARCADE OVERDRIVE", True, COLOR_PINK)
        sub_rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 180))
        screen.blit(sub, sub_rect)

        hs = self.font_body.render(f"TOP RECORD: {high_score:06d} PTS", True, COLOR_YELLOW)
        screen.blit(hs, hs.get_rect(center=(SCREEN_WIDTH // 2, 220)))

        cur_skin = self.get_current_skin()
        cur_diff = DIFFICULTIES[self.get_current_diff_key()]
        cfg_str = f"VESSEL: {cur_skin.name}  |  DIFFICULTY: {cur_diff['name']} (x{cur_diff['score_mult']:.2f})"
        cfg_surf = self.font_small.render(cfg_str, True, cur_diff["color"])
        screen.blit(cfg_surf, cfg_surf.get_rect(center=(SCREEN_WIDTH // 2, 252)))

        for btn in self.menu_buttons:
            btn.draw(screen)

        hint = self.font_body.render(
            "WASD / ARROWS : Move & Thrusters  |  SPACE : Shoot  |  M : Audio  |  ESC : Pause",
            True,
            COLOR_GRAY,
        )
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 28)))

    def draw_hangar(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 26, 235))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render("HANGAR & PROTOCOLS", True, COLOR_CYAN)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 70)))

        # LEFT PANEL
        panel1_rect = pygame.Rect(60, 130, 520, 480)
        pygame.draw.rect(screen, (18, 24, 40), panel1_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_CYAN, panel1_rect, 1, border_radius=8)

        head1 = self.font_medium.render("VESSEL SELECTION", True, COLOR_CYAN)
        screen.blit(head1, (85, 148))

        skin = self.get_current_skin()

        preview_center = pygame.Vector2(320, 290)
        preview_box = pygame.Rect(180, 200, 280, 180)
        pygame.draw.rect(screen, (10, 15, 28), preview_box, border_radius=6)
        pygame.draw.rect(screen, (40, 55, 90), preview_box, 1, border_radius=6)

        rot_angle = (self.time_elapsed * 55.0) % 360
        ship_poly = skin.get_polygon(preview_center, rot_angle, radius=48.0)

        fill_c = (
            max(0, int(skin.primary_color[0] * 0.25)),
            max(0, int(skin.primary_color[1] * 0.25)),
            max(0, int(skin.primary_color[2] * 0.35)),
        )
        if len(ship_poly) >= 3:
            pygame.draw.polygon(screen, fill_c, ship_poly)
            pygame.draw.polygon(screen, skin.primary_color, ship_poly, LINE_WIDTH + 1)

        fwd = pygame.Vector2(0, 1).rotate(rot_angle)
        cockpit_pos = preview_center + fwd * (48.0 * 0.22)
        pygame.draw.circle(screen, skin.accent_color, (int(cockpit_pos.x), int(cockpit_pos.y)), 4)

        rear_pos = preview_center - fwd * (48.0 * 0.75)
        flame_len = 12.0 + 6.0 * math.sin(self.time_elapsed * 18.0)
        flame_tip = rear_pos - fwd * flame_len
        pygame.draw.line(screen, skin.engine_color, rear_pos, flame_tip, 3)

        v_name = self.font_large.render(skin.name, True, skin.primary_color)
        screen.blit(v_name, v_name.get_rect(center=(320, 485)))

        v_tag = self.font_small.render(skin.tagline, True, (200, 215, 235))
        screen.blit(v_tag, v_tag.get_rect(center=(320, 518)))

        specs_y = 545
        specs = [
            ("HULL", skin.primary_color),
            ("ACCENT", skin.accent_color),
            ("THRUSTER", skin.engine_color),
            ("LASER", skin.shot_color),
        ]
        badge_w = 90
        for i, (s_name, s_col) in enumerate(specs):
            bx = 100 + i * (badge_w + 14)
            pygame.draw.rect(screen, (25, 32, 52), (bx, specs_y, badge_w, 28), border_radius=4)
            pygame.draw.rect(screen, s_col, (bx, specs_y, badge_w, 28), 1, border_radius=4)
            pygame.draw.circle(screen, s_col, (bx + 14, specs_y + 14), 5)
            s_lbl = self.font_small.render(s_name, True, COLOR_WHITE)
            screen.blit(s_lbl, (bx + 26, specs_y + 7))

        # RIGHT PANEL
        panel2_rect = pygame.Rect(640, 130, 580, 480)
        pygame.draw.rect(screen, (18, 24, 40), panel2_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_GREEN, panel2_rect, 1, border_radius=8)

        head2 = self.font_medium.render("MISSION DIFFICULTY", True, COLOR_GREEN)
        screen.blit(head2, (665, 148))

        diff_cfg = DIFFICULTIES[self.get_current_diff_key()]

        card_rect = pygame.Rect(665, 255, 530, 245)
        pygame.draw.rect(screen, (12, 16, 30), card_rect, border_radius=6)
        pygame.draw.rect(screen, diff_cfg["color"], card_rect, 1, border_radius=6)

        d_title = self.font_large.render(f"PROTOCOL: {diff_cfg['name']}", True, diff_cfg["color"])
        screen.blit(d_title, (685, 275))

        d_desc = self.font_body.render(diff_cfg["desc"], True, COLOR_WHITE)
        screen.blit(d_desc, (685, 318))

        stats_y = 365
        stats_data = [
            ("Asteroid Spawn Interval", f"{diff_cfg['spawn_rate']:.2f}s"),
            ("Meteor Velocity Factor", f"{diff_cfg['speed_mult']:.2f}x"),
            ("Initial Ship Hull Lives", f"{diff_cfg['lives']} Lives"),
            ("Power-Up Drop Frequency", f"{int(diff_cfg['drop_chance'] * 100)}%"),
            ("Score Multiplier Bonus", f"+{int((diff_cfg['score_mult'] - 1.0) * 100)}% (x{diff_cfg['score_mult']:.2f})"),
        ]

        for idx, (label, val) in enumerate(stats_data):
            row_y = stats_y + idx * 24
            l_surf = self.font_small.render(f"•  {label}:", True, (170, 185, 210))
            v_surf = self.font_small.render(val, True, diff_cfg["color"])
            screen.blit(l_surf, (690, row_y))
            screen.blit(v_surf, (940, row_y))

        for btn in self.hangar_buttons:
            btn.draw(screen)

    def draw_options(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 14, 25, 235))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render("INTEL & POWER-UPS", True, COLOR_CYAN)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 85)))

        card_w, card_h = 360, 68
        col1_x = SCREEN_WIDTH // 2 - card_w - 20
        col2_x = SCREEN_WIDTH // 2 + 20
        start_y = 145

        items = [
            ("[S] ENERGY SHIELD", "Absorbs 1 collision without taking ship damage.", COLOR_CYAN),
            ("[3X] TRIPLE CANNON", "Fires a 3-way spread pattern with high speed.", COLOR_PINK),
            ("[SPD] HYPER DRIVE", "Boosts thruster acceleration & agile turning.", COLOR_YELLOW),
            ("[BOOM] MEGA NUKE", "Detonates all visible asteroids on screen.", COLOR_ORANGE),
            ("[+1] SHIP RESTORE", "Awards +1 extra ship hull life.", COLOR_GREEN),
            ("[SLW] GLITCH HAZARD", "De-buff: Reduces thrusters and rate of fire.", COLOR_PURPLE),
        ]

        for i, (head, desc, col) in enumerate(items):
            cx = col1_x if i % 2 == 0 else col2_x
            cy = start_y + (i // 2) * (card_h + 16)

            pygame.draw.rect(screen, (20, 26, 44), (cx, cy, card_w, card_h), border_radius=6)
            pygame.draw.rect(screen, col, (cx, cy, card_w, card_h), 1, border_radius=6)

            h_surf = self.font_body.render(head, True, col)
            screen.blit(h_surf, (cx + 14, cy + 12))

            d_surf = self.font_small.render(desc, True, (210, 220, 235))
            screen.blit(d_surf, (cx + 14, cy + 38))

        score_info = self.font_body.render(
            "SCORING: Large = 20 pts  |  Medium = 50 pts  |  Small = 100 pts  |  Combos multiply score up to 8x!",
            True,
            COLOR_WHITE,
        )
        screen.blit(score_info, score_info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 130)))

        for btn in self.options_buttons:
            btn.draw(screen)

    def draw_paused(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 22, 190))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render("SYSTEM PAUSED", True, COLOR_CYAN)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))

        for btn in self.pause_buttons:
            btn.draw(screen)

    def draw_game_over(
        self,
        screen: pygame.Surface,
        final_score: int,
        high_score: int,
        asteroids_destroyed: int,
        is_new_high: bool,
    ) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 8, 18, 220))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render("MISSION FAILED", True, COLOR_RED)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))

        if is_new_high:
            nh = self.font_medium.render("★ NEW RECORD HIGH SCORE! ★", True, COLOR_YELLOW)
            screen.blit(nh, nh.get_rect(center=(SCREEN_WIDTH // 2, 195)))

        score_txt = self.font_large.render(f"FINAL SCORE: {final_score:06d}", True, COLOR_WHITE)
        screen.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH // 2, 240)))

        stats_txt = self.font_body.render(
            f"Asteroids Obliterated: {asteroids_destroyed}  |  Personal Best: {high_score:06d}",
            True,
            COLOR_GRAY,
        )
        screen.blit(stats_txt, stats_txt.get_rect(center=(SCREEN_WIDTH // 2, 280)))

        for btn in self.game_over_buttons:
            btn.draw(screen)
