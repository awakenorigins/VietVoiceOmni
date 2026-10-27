"""
VietVoiceOmni - Voice Service
Wrapper quanh VoxCPM2 engine. Giu model thuong tru (load 1 lan).
Gen tach cau + pause + atempo (toc do doc) + callback progress/ETA.
"""
import os
import re
import sys
import time
import threading
import subprocess
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import soundfile as sf

# --- Paths ---
# Goc chua engine VoxCPM2 + voxcpm_engine.py. Uu tien bien moi truong VOXCPM_ROOT,
# fallback ve 2 cap tren thu muc repo (vi du khi dat canh thu muc VietVoice/ va VoxCPM/).
_env_root = os.environ.get("VOXCPM_ROOT")
if _env_root:
    TTS_ROOT = Path(_env_root)
else:
    TTS_ROOT = Path(__file__).resolve().parents[3]
APPS_DIR = TTS_ROOT / "VietVoice" / "apps"
VOXCPM_SRC = TTS_ROOT / "VoxCPM" / "src"
OUT_DIR = Path(__file__).resolve().parents[2] / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# offline -> load nhanh
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

for p in (str(APPS_DIR), str(VOXCPM_SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)


def split_sentences(text: str) -> list[str]:
    """Tach text thanh tung cau theo dau cau, giu cau goi gon."""
    text = text.strip()
    # tach theo . ! ? ; va xuong dong
    parts = re.split(r"(?<=[.!?;])\s+|\n+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        out.append(p)
    return out


class VoiceService:
    """Singleton giu engine VoxCPM2 thuong tru."""

    _instance: Optional["VoiceService"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._engine = None
        self._engine_lock = threading.Lock()
        self._last_speeds: list[float] = []  # s/cau gan day -> ETA

    @classmethod
    def get(cls) -> "VoiceService":
        with cls._lock:
            if cls._instance is None:
                cls._instance = VoiceService()
            return cls._instance

    @property
    def loaded(self) -> bool:
        return self._engine is not None

    def ensure_engine(self, cfg_value=1.3, timesteps=23):
        with self._engine_lock:
            if self._engine is None:
                from voxcpm_engine import VoxCPMEngine, _enable_offline_if_cached
                _enable_offline_if_cached("openbmb/VoxCPM2")
                self._engine = VoxCPMEngine(
                    cfg_value=cfg_value, inference_timesteps=timesteps
                )
            return self._engine

    @property
    def sample_rate(self) -> int:
        eng = self.ensure_engine()
        return getattr(eng, "sample_rate", 48000)

    def estimate_eta(self, n_sentences: int) -> float:
        """Uoc luong giay con lai dua tren toc do gen trung binh."""
        if not self._last_speeds:
            return n_sentences * 12.0  # default ~12s/cau
        avg = sum(self._last_speeds) / len(self._last_speeds)
        return n_sentences * avg

    def generate(
        self,
        text: str,
        ref_audio: str,
        cfg_value: float = 1.3,
        timesteps: int = 23,
        pause: float = 0.6,
        speed: float = 1.0,
        out_name: str = "omni",
        on_progress: Optional[Callable[[int, int, float], None]] = None,
    ) -> dict:
        """
        Gen audio. on_progress(done, total, eta_sec) goi sau moi cau.
        Tra dict: {wav_path, duration, total_time, n_sentences}
        """
        eng = self.ensure_engine(cfg_value, timesteps)
        sr = self.sample_rate
        sentences = split_sentences(text)
        total = len(sentences)
        if total == 0:
            raise ValueError("Text rong")

        pause_samples = int(pause * sr)
        silence = np.zeros(pause_samples, dtype=np.float32)
        chunks = []
        t_start = time.time()
        speeds = []

        for i, sent in enumerate(sentences):
            t0 = time.time()
            wav = eng.infer(
                text=sent,
                ref_audio=ref_audio,
                cfg_value=cfg_value,
                inference_timesteps=timesteps,
                normalize=True,
            )
            wav = np.asarray(wav, dtype=np.float32)
            chunks.append(wav)
            if i < total - 1:
                chunks.append(silence)
            dt = time.time() - t0
            speeds.append(dt)
            # cap nhat toc do trung binh (giu 20 gan nhat)
            self._last_speeds.append(dt)
            self._last_speeds = self._last_speeds[-20:]
            remaining = total - (i + 1)
            avg = sum(speeds) / len(speeds)
            eta = remaining * avg
            if on_progress:
                on_progress(i + 1, total, eta)

        full = np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)

        # toc do doc (atempo) - chi khi != 1.0
        raw_path = OUT_DIR / f"{out_name}_raw.wav"
        sf.write(str(raw_path), full, sr)
        final_path = raw_path
        if abs(speed - 1.0) > 0.01:
            tempo_path = OUT_DIR / f"{out_name}_tempo.wav"
            self._apply_tempo(str(raw_path), str(tempo_path), speed)
            final_path = tempo_path

        # luon xuat mp3 de nghe/tai
        mp3_path = OUT_DIR / f"{out_name}.mp3"
        self._to_mp3(str(final_path), str(mp3_path))

        info = sf.info(str(final_path))
        return {
            "wav_path": str(final_path),
            "mp3_path": str(mp3_path),
            "duration": info.duration,
            "total_time": time.time() - t_start,
            "n_sentences": total,
        }

    @staticmethod
    def _apply_tempo(src: str, dst: str, speed: float):
        # atempo giu cao do, doi toc do. atempo nhan 0.5-2.0
        s = max(0.5, min(2.0, speed))
        subprocess.run(
            ["ffmpeg", "-y", "-i", src, "-filter:a", f"atempo={s}", dst],
            check=True, capture_output=True,
        )

    @staticmethod
    def _to_mp3(src: str, dst: str, bitrate: str = "192k"):
        subprocess.run(
            ["ffmpeg", "-y", "-i", src, "-codec:a", "libmp3lame", "-b:a", bitrate, dst],
            check=True, capture_output=True,
        )
