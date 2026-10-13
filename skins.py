import math
import pygame
from constants import (
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_ORANGE,
    COLOR_PINK,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
)


class Skin:
    def __init__(
        self,
        skin_id: str,
        name: str,
        tagline: str,
        primary_color: tuple[int, int, int],
        accent_color: tuple[int, int, int],
        engine_color: tuple[int, int, int],
        shot_color: tuple[int, int, int],
        shape_type: str,
    ) -> None:
        self.skin_id = skin_id
        self.name = name
        self.tagline = tagline
        self.primary_color = primary_color
        self.accent_color = accent_color
        self.engine_color = engine_color
        self.shot_color = shot_color
        self.shape_type = shape_type

    def get_polygon(self, position: pygame.Vector2, rotation: float, radius: float) -> list[pygame.Vector2]:
        forward = pygame.Vector2(0, 1).rotate(rotation)
        right = pygame.Vector2(0, 1).rotate(rotation + 90)

        if self.shape_type == "classic":
            # Classic Interceptor with notched engine bay
            a = position + forward * radius
            b = position - forward * radius - right * (radius / 1.4)
            c = position - forward * (radius * 0.5)
            d = position - forward * radius + right * (radius / 1.4)
            return [a, b, c, d]

        elif self.shape_type == "crimson":
            # Forward-swept razor fighter
            nose = position + forward * (radius * 1.15)
            wing_r = position - forward * (radius * 0.3) + right * (radius * 1.1)
            wing_r_tip = position + forward * (radius * 0.5) + right * (radius * 1.1)
            back_r = position - forward * (radius * 0.8) + right * (radius * 0.4)
            engine = position - forward * (radius * 0.5)
            back_l = position - forward * (radius * 0.8) - right * (radius * 0.4)
            wing_l_tip = position + forward * (radius * 0.5) - right * (radius * 1.1)
            wing_l = position - forward * (radius * 0.3) - right * (radius * 1.1)
            return [nose, wing_r_tip, wing_r, back_r, engine, back_l, wing_l, wing_l_tip]

        elif self.shape_type == "sovereign":
            # Heavy Delta Cruiser with dual rear engine pylons
            nose = position + forward * (radius * 1.1)
            shoulder_r = position + forward * (radius * 0.2) + right * (radius * 0.6)
            wing_r = position - forward * (radius * 0.9) + right * (radius * 0.95)
            pylon_r = position - forward * (radius * 1.0) + right * (radius * 0.4)
            pylon_l = position - forward * (radius * 1.0) - right * (radius * 0.4)
            wing_l = position - forward * (radius * 0.9) - right * (radius * 0.95)
            shoulder_l = position + forward * (radius * 0.2) - right * (radius * 0.6)
            return [nose, shoulder_r, wing_r, pylon_r, pylon_l, wing_l, shoulder_l]

        elif self.shape_type == "viper":
            # Twin fuselage needle dart
            tip_r = position + forward * (radius * 1.2) + right * (radius * 0.25)
            inner_notch = position + forward * (radius * 0.4)
            tip_l = position + forward * (radius * 1.2) - right * (radius * 0.25)
            fin_l = position - forward * (radius * 0.9) - right * (radius * 0.85)
            engine_mid = position - forward * (radius * 0.6)
            fin_r = position - forward * (radius * 0.9) + right * (radius * 0.85)
            return [inner_notch, tip_r, fin_r, engine_mid, fin_l, tip_l]

        elif self.shape_type == "spectre":
            # Shuriken stealth scout
            front = position + forward * (radius * 1.25)
            cut_r = position + forward * (radius * 0.1) + right * (radius * 0.4)
            flare_r = position - forward * (radius * 0.7) + right * (radius * 1.15)
            notch = position - forward * (radius * 0.4)
            flare_l = position - forward * (radius * 0.7) - right * (radius * 1.15)
            cut_l = position + forward * (radius * 0.1) - right * (radius * 0.4)
            return [front, cut_r, flare_r, notch, flare_l, cut_l]

        # Fallback classic
        return [
            position + forward * radius,
            position - forward * radius - right * (radius / 1.4),
            position - forward * radius + right * (radius / 1.4),
        ]


ALL_SKINS: list[Skin] = [
    Skin(
        skin_id="cyan_phantom",
        name="CYBER PHANTOM",
        tagline="Standard Issue Precision Interceptor",
        primary_color=(0, 245, 255),
        accent_color=(255, 255, 255),
        engine_color=(255, 140, 20),
        shot_color=(0, 245, 255),
        shape_type="classic",
    ),
    Skin(
        skin_id="crimson_blade",
        name="CRIMSON BLADE",
        tagline="Aggressive Swept-Wing Assault Fighter",
        primary_color=(255, 55, 80),
        accent_color=(255, 180, 200),
        engine_color=(255, 20, 140),
        shot_color=(255, 60, 90),
        shape_type="crimson",
    ),
    Skin(
        skin_id="golden_sovereign",
        name="GOLDEN TITAN",
        tagline="Armored Delta Cruiser with Ion Thrusters",
        primary_color=(255, 215, 30),
        accent_color=(255, 245, 180),
        engine_color=(0, 220, 255),
        shot_color=(255, 225, 60),
        shape_type="sovereign",
    ),
    Skin(
        skin_id="emerald_viper",
        name="EMERALD VIPER",
        tagline="Twin-Fuselage Needle-Dart Stealth Ship",
        primary_color=(50, 255, 130),
        accent_color=(180, 255, 220),
        engine_color=(70, 255, 90),
        shot_color=(50, 255, 130),
        shape_type="viper",
    ),
    Skin(
        skin_id="void_spectre",
        name="VOID SPECTRE",
        tagline="Dark Astral Shuriken Scout",
        primary_color=(190, 80, 255),
        accent_color=(240, 200, 255),
        engine_color=(220, 60, 255),
        shot_color=(200, 80, 255),
        shape_type="spectre",
    ),
]

SKIN_MAP = {s.skin_id: s for s in ALL_SKINS}


def get_skin(skin_id: str) -> Skin:
    return SKIN_MAP.get(skin_id, ALL_SKINS[0])
