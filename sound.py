import array
import math
import random
import pygame


class SoundManager:
    def __init__(self) -> None:
        self.enabled = True
        self.volume = 0.65
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.initialized = False

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self._generate_all_sounds()
            self.initialized = True
        except Exception as e:
            print(f"Warning: Audio device unavailable ({e}), running in silent mode.")
            self.enabled = False

    def toggle_sound(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def play(self, sound_name: str, volume_mult: float = 1.0) -> None:
        if not self.enabled or not self.initialized:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            snd.set_volume(min(1.0, max(0.0, self.volume * volume_mult)))
            snd.play()

    def _generate_all_sounds(self) -> None:
        sample_rate = 44100

        def create_sound(samples_gen) -> pygame.mixer.Sound:
            buf = array.array("h", samples_gen)
            return pygame.mixer.Sound(buffer=buf)

        # 1. Laser Shoot (Frequency sweep 850Hz -> 200Hz)
        laser_samples = []
        dur = 0.11
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.5
            freq = 880.0 - (680.0 * (t / dur))
            val = int(14000 * env * math.sin(2 * math.pi * freq * t))
            laser_samples.append(val)
        self.sounds["laser"] = create_sound(laser_samples)

        # 2. Triple Laser (Dual harmonic chord sweep)
        triple_samples = []
        dur = 0.13
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.3
            freq1 = 1100.0 - (750.0 * (t / dur))
            freq2 = 1450.0 - (900.0 * (t / dur))
            val = int(8500 * env * (math.sin(2 * math.pi * freq1 * t) + math.sin(2 * math.pi * freq2 * t)))
            triple_samples.append(val)
        self.sounds["triple_laser"] = create_sound(triple_samples)

        # 3. Small Explosion (Snappy crunch noise)
        exp_s_samples = []
        dur = 0.16
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 2.0
            noise = random.uniform(-1.0, 1.0)
            low_tone = math.sin(2 * math.pi * 180 * t)
            val = int(16000 * env * (0.75 * noise + 0.25 * low_tone))
            exp_s_samples.append(val)
        self.sounds["explode_small"] = create_sound(exp_s_samples)

        # 4. Medium Explosion (Rumbling noise)
        exp_m_samples = []
        dur = 0.32
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.6
            noise = random.uniform(-1.0, 1.0)
            sub = math.sin(2 * math.pi * 110 * t)
            val = int(18000 * env * (0.65 * noise + 0.35 * sub))
            exp_m_samples.append(val)
        self.sounds["explode_med"] = create_sound(exp_m_samples)

        # 5. Large Explosion (Heavy bass subterranean shock)
        exp_l_samples = []
        dur = 0.55
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.2
            noise = random.uniform(-1.0, 1.0)
            sub = math.sin(2 * math.pi * 75 * t)
            val = int(22000 * env * (0.5 * noise + 0.5 * sub))
            exp_l_samples.append(val)
        self.sounds["explode_large"] = create_sound(exp_l_samples)

        # 6. Mega Nuke Boom (Deep resonant shockwave)
        nuke_samples = []
        dur = 1.2
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 0.8
            freq = 60.0 + 30.0 * math.sin(2 * math.pi * 3.0 * t)
            noise = random.uniform(-0.8, 0.8) * (1.0 - t / dur)
            val = int(24000 * env * (math.sin(2 * math.pi * freq * t) * 0.7 + noise * 0.3))
            nuke_samples.append(val)
        self.sounds["nuke"] = create_sound(nuke_samples)

        # 7. Power-Up Chime (Ascending triad arpeggio: C5 -> E5 -> G5)
        pup_samples = []
        dur = 0.28
        total_samples = int(sample_rate * dur)
        notes = [523.25, 659.25, 783.99, 1046.50]  # C, E, G, High C
        for i in range(total_samples):
            t = i / sample_rate
            note_idx = min(len(notes) - 1, int(t / (dur / len(notes))))
            freq = notes[note_idx]
            sub_t = t % (dur / len(notes))
            sub_dur = dur / len(notes)
            env = (1.0 - sub_t / sub_dur) ** 1.1
            val = int(14000 * env * math.sin(2 * math.pi * freq * t))
            pup_samples.append(val)
        self.sounds["powerup"] = create_sound(pup_samples)

        # 8. Shield Hit / Deflection (Resonant crystal ping)
        shield_samples = []
        dur = 0.22
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 2.2
            val = int(16000 * env * (math.sin(2 * math.pi * 1250 * t) + 0.5 * math.sin(2 * math.pi * 2500 * t)))
            shield_samples.append(val)
        self.sounds["shield_hit"] = create_sound(shield_samples)

        # 9. Player Hit / Damage (Harsh distress siren crunch)
        hit_samples = []
        dur = 0.40
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.4
            freq = 280.0 + 80.0 * math.sin(2 * math.pi * 24.0 * t)
            noise = random.uniform(-0.5, 0.5)
            val = int(20000 * env * (math.sin(2 * math.pi * freq * t) + noise))
            hit_samples.append(val)
        self.sounds["player_hit"] = create_sound(hit_samples)

        # 10. UI Button Hover
        hover_samples = []
        dur = 0.04
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = 1.0 - t / dur
            val = int(8000 * env * math.sin(2 * math.pi * 880 * t))
            hover_samples.append(val)
        self.sounds["ui_hover"] = create_sound(hover_samples)

        # 11. UI Button Click
        click_samples = []
        dur = 0.06
        total_samples = int(sample_rate * dur)
        for i in range(total_samples):
            t = i / sample_rate
            env = (1.0 - t / dur) ** 1.5
            freq = 600.0 + 400.0 * (t / dur)
            val = int(12000 * env * math.sin(2 * math.pi * freq * t))
            click_samples.append(val)
        self.sounds["ui_click"] = create_sound(click_samples)
