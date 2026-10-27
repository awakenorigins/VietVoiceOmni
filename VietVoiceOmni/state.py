"""VietVoiceOmni - Reflex State (toan bo logic nghiep vu). UI text co dau day du."""
import asyncio
import time
from pathlib import Path

import reflex as rx

from .backend import db
from .backend.voice_service import VoiceService, split_sentences

ASSETS = Path(__file__).resolve().parents[1] / "assets"
OUT_DIR = Path(__file__).resolve().parents[1] / "output"


def _public_url(mp3_path: str) -> str:
    try:
        src = Path(mp3_path)
        if not src.exists():
            return ""
        dst_dir = ASSETS / "audio"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / src.name
        if str(src.resolve()) != str(dst.resolve()):
            import shutil
            shutil.copy2(src, dst)
        return f"/audio/{src.name}"
    except Exception:
        return ""


class State(rx.State):
    # ----- chung -----
    active_tab: str = "create"
    engine_loaded: bool = False

    # ----- Tao giong doc -----
    voices: list[dict] = []
    selected_voice: str = ""
    text_input: str = ""
    cfg_value: float = 1.3
    timesteps: int = 23
    pause: float = 0.6
    speed: float = 1.0
    is_generating: bool = False
    progress_done: int = 0
    progress_total: int = 0
    eta_sec: float = 0.0
    result_audio_url: str = ""
    result_info: str = ""

    # ----- Clone -----
    clone_name: str = ""
    clone_desc: str = ""
    clone_ref_path: str = ""
    clone_msg: str = ""

    # ----- Library / History -----
    lib_kind: str = "speech"  # speech | podcast | audiobook
    history: list[dict] = []

    # ----- Podcast / Hosts -----
    hosts: list[dict] = []
    host_name: str = ""
    host_voice: str = ""
    host_personality: str = ""
    host_habits: str = ""
    host_cfg: float = 1.3
    host_steps: int = 23
    host_pause: float = 0.4
    host_speed: float = 1.0
    host_advanced: bool = False  # mo rong tuy chinh giong
    host_msg: str = ""
    expanded_host: str = ""      # host dang mo rong xem
    podcast_script: str = ""
    podcast_title: str = ""
    podcast_audio_url: str = ""
    podcast_msg: str = ""
    is_podcasting: bool = False
    podcast_progress: str = ""

    # ----- Ebook -----
    ebook_path: str = ""
    ebook_chapters: list[dict] = []
    ebook_voice: str = ""
    ebook_msg: str = ""
    is_ebooking: bool = False
    ebook_progress: str = ""
    ebook_audio_url: str = ""

    # ----- Settings -----
    set_cfg_default: float = 1.3
    set_steps_default: int = 23
    set_pause_default: float = 0.6
    set_speed_default: float = 1.0
    set_master: str = "raw"
    set_bitrate: str = "192k"
    set_msg: str = ""

    # ===== lifecycle =====
    def on_load(self):
        db.init_db()
        self._refresh_voices()
        self._refresh_history()
        self._refresh_hosts()
        self._load_settings()
        self.engine_loaded = VoiceService.get().loaded

    def set_tab(self, tab: str):
        self.active_tab = tab

    # ===== simple setters (Reflex 0.9 khong tu sinh) =====
    def set_text_input(self, v: str): self.text_input = v
    def set_clone_name(self, v: str): self.clone_name = v
    def set_clone_desc(self, v: str): self.clone_desc = v
    def set_host_name(self, v: str): self.host_name = v
    def set_host_voice(self, v: str): self.host_voice = v
    def set_host_personality(self, v: str): self.host_personality = v
    def set_host_habits(self, v: str): self.host_habits = v
    def set_podcast_title(self, v: str): self.podcast_title = v
    def set_podcast_script(self, v: str): self.podcast_script = v
    def set_ebook_voice(self, v: str): self.ebook_voice = v
    def set_lib_kind(self, v: str): self.lib_kind = v; self._refresh_history()

    # slider setters
    def slider_cfg(self, v: list): self.cfg_value = float(v[0])
    def slider_steps(self, v: list): self.timesteps = int(v[0])
    def slider_pause(self, v: list): self.pause = float(v[0])
    def slider_speed(self, v: list): self.speed = float(v[0])
    def slider_host_cfg(self, v: list): self.host_cfg = float(v[0])
    def slider_host_steps(self, v: list): self.host_steps = int(v[0])
    def slider_host_pause(self, v: list): self.host_pause = float(v[0])
    def slider_host_speed(self, v: list): self.host_speed = float(v[0])
    def toggle_host_advanced(self, v: bool): self.host_advanced = v

    # ===== voices =====
    def _refresh_voices(self):
        self.voices = db.list_voices()
        names = [v["name"] for v in self.voices]
        if not self.selected_voice and names:
            self.selected_voice = names[0]
        if not self.host_voice and names:
            self.host_voice = names[0]
        if not self.ebook_voice and names:
            self.ebook_voice = names[0]

    def select_voice(self, name: str):
        self.selected_voice = name
        v = db.get_voice(name)
        if v:
            self.cfg_value = v["cfg_value"]
            self.timesteps = v["timesteps"]
            self.pause = v["pause"]
            self.speed = v["speed"]

    # ===== GEN giong doc =====
    @rx.event(background=True)
    async def generate(self):
        async with self:
            if self.is_generating:
                return
            if not self.text_input.strip():
                self.result_info = "Chưa nhập văn bản"
                return
            if not self.selected_voice:
                self.result_info = "Chưa chọn giọng"
                return
            self.is_generating = True
            self.result_audio_url = ""
            self.result_info = "Đang chuẩn bị..."
            self.progress_done = 0
            sents = split_sentences(self.text_input)
            self.progress_total = len(sents)
            voice = db.get_voice(self.selected_voice)
            cfg, steps, pause, speed = self.cfg_value, self.timesteps, self.pause, self.speed
            text, vname, ref = self.text_input, self.selected_voice, voice["ref_audio"]

        svc = VoiceService.get()
        async with self:
            self.eta_sec = svc.estimate_eta(self.progress_total)

        prog_box = {"done": 0, "total": self.progress_total, "eta": 0.0}

        def on_prog(done, total, eta):
            prog_box["done"] = done
            prog_box["total"] = total
            prog_box["eta"] = eta

        out_name = f"omni_{int(time.time())}"
        loop = asyncio.get_event_loop()
        fut = loop.run_in_executor(
            None,
            lambda: svc.generate(
                text=text, ref_audio=ref, cfg_value=cfg, timesteps=steps,
                pause=pause, speed=speed, out_name=out_name, on_progress=on_prog,
            ),
        )
        while not fut.done():
            await asyncio.sleep(0.4)
            async with self:
                self.progress_done = prog_box["done"]
                self.eta_sec = prog_box["eta"]
                self.result_info = f"Đang đọc câu {prog_box['done']}/{prog_box['total']}..."
        res = await fut

        url = _public_url(res["mp3_path"])
        db.add_history(
            vname, text,
            {"cfg": cfg, "steps": steps, "pause": pause, "speed": speed},
            res["mp3_path"], res["duration"], res["n_sentences"], res["total_time"],
            kind="speech", title=text[:40],
        )
        async with self:
            self.is_generating = False
            self.result_audio_url = url
            self.engine_loaded = True
            self.progress_done = self.progress_total
            self.eta_sec = 0.0
            mm = int(res["duration"] // 60); ss = int(res["duration"] % 60)
            self.result_info = f"Xong! {res['n_sentences']} câu, audio {mm}:{ss:02d}, tạo trong {res['total_time']:.0f}s"
            self._refresh_history()

    # ===== history / library =====
    def _refresh_history(self):
        self.history = db.list_history(80, kind=self.lib_kind)

    def del_history(self, hid: int):
        db.delete_history(hid)
        self._refresh_history()

    def play_history(self, mp3_path: str):
        self.result_audio_url = _public_url(mp3_path)
        self.active_tab = "create"

    # ===== clone =====
    async def handle_clone_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        f = files[0]
        data = await f.read()
        dest_dir = OUT_DIR / "refs"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f.filename
        with open(dest, "wb") as out:
            out.write(data)
        self.clone_ref_path = str(dest)
        self.clone_msg = f"Đã nhận mẫu: {f.filename}"

    def save_clone(self):
        if not self.clone_name.strip():
            self.clone_msg = "Chưa đặt tên giọng"
            return
        if not self.clone_ref_path:
            self.clone_msg = "Chưa tải lên audio mẫu"
            return
        db.add_voice(self.clone_name.strip(), self.clone_ref_path, self.clone_desc, 1.3, 23, 0.6, 1.0)
        self.clone_msg = f"Đã lưu giọng '{self.clone_name}'"
        self.clone_name = ""; self.clone_desc = ""; self.clone_ref_path = ""
        self._refresh_voices()

    def del_voice(self, name: str):
        db.delete_voice(name)
        self._refresh_voices()

    # ===== podcast hosts =====
    def _refresh_hosts(self):
        self.hosts = db.list_hosts()

    def save_host(self):
        if not self.host_name.strip():
            self.host_msg = "Chưa đặt tên người dẫn"
            return
        if not self.host_voice:
            self.host_msg = "Chưa chọn giọng cho người dẫn"
            return
        existing = db.get_host(self.host_name.strip())
        if not existing and db.count_hosts() >= db.MAX_HOSTS:
            self.host_msg = f"Đã đạt giới hạn {db.MAX_HOSTS} người dẫn"
            return
        color = existing["color"] if existing else db.next_host_color()
        db.add_host(
            self.host_name.strip(), self.host_voice, self.host_personality, self.host_habits,
            color, self.host_cfg, self.host_steps, self.host_pause, self.host_speed,
        )
        self.host_msg = f"Đã lưu người dẫn '{self.host_name}'"
        self.host_name = ""; self.host_personality = ""; self.host_habits = ""
        self.host_advanced = False
        self.host_cfg = 1.3; self.host_steps = 23; self.host_pause = 0.4; self.host_speed = 1.0
        self._refresh_hosts()

    def edit_host(self, name: str):
        """Nap host vao form de sua."""
        h = db.get_host(name)
        if not h:
            return
        self.host_name = h["name"]; self.host_voice = h["voice_name"]
        self.host_personality = h["personality"]; self.host_habits = h["habits"]
        self.host_cfg = h["cfg_value"]; self.host_steps = h["timesteps"]
        self.host_pause = h["pause"]; self.host_speed = h["speed"]
        self.host_advanced = True

    def toggle_expand_host(self, name: str):
        self.expanded_host = "" if self.expanded_host == name else name

    def del_host(self, name: str):
        db.delete_host(name)
        self._refresh_hosts()

    @rx.event(background=True)
    async def generate_podcast(self):
        async with self:
            if self.is_podcasting:
                return
            if not self.podcast_script.strip():
                self.podcast_msg = "Chưa có kịch bản"
                return
            self.is_podcasting = True
            self.podcast_audio_url = ""
            self.podcast_msg = "Đang phân tích kịch bản..."
            script = self.podcast_script
            title = self.podcast_title or f"podcast_{int(time.time())}"

        host_map = {h["name"]: h for h in db.list_hosts()}
        lines = []
        for ln in script.splitlines():
            ln = ln.strip()
            if not ln or ":" not in ln:
                continue
            spk, txt = ln.split(":", 1)
            spk, txt = spk.strip(), txt.strip()
            if txt:
                lines.append((spk, txt))

        if not lines:
            async with self:
                self.is_podcasting = False
                self.podcast_msg = "Kịch bản sai định dạng. Mỗi dòng: TênNgườiDẫn: lời thoại"
            return

        svc = VoiceService.get()
        import numpy as np, soundfile as sf
        sr = svc.sample_rate
        gap = np.zeros(int(0.5 * sr), dtype=np.float32)
        segments = []
        loop = asyncio.get_event_loop()
        default_voice = self.selected_voice or (db.list_voices()[0]["name"] if db.list_voices() else "")

        for idx, (spk, txt) in enumerate(lines):
            host = host_map.get(spk)
            if host:
                voice = db.get_voice(host["voice_name"])
                hcfg, hsteps, hpause, hspeed = host["cfg_value"], host["timesteps"], host["pause"], host["speed"]
            else:
                voice = db.get_voice(default_voice)
                hcfg, hsteps, hpause, hspeed = 1.3, 23, 0.4, 1.0
            if not voice:
                continue
            async with self:
                self.podcast_progress = f"Dòng {idx+1}/{len(lines)} — {spk}"
            ref = voice["ref_audio"]
            res = await loop.run_in_executor(
                None,
                lambda t=txt, r=ref, cf=hcfg, st=hsteps, pa=hpause, sp=hspeed: svc.generate(
                    text=t, ref_audio=r, cfg_value=cf, timesteps=st,
                    pause=pa, speed=sp, out_name=f"pod_{int(time.time()*1000)}",
                ),
            )
            wav, _sr = sf.read(res["wav_path"], dtype="float32")
            segments.append(wav)
            segments.append(gap)

        full = np.concatenate(segments) if segments else np.zeros(1, dtype=np.float32)
        out_wav = OUT_DIR / f"{title}.wav"
        sf.write(str(out_wav), full, sr)
        out_mp3 = OUT_DIR / f"{title}.mp3"
        VoiceService._to_mp3(str(out_wav), str(out_mp3))
        dur = len(full) / sr
        speakers = list({s for s, _ in lines})
        db.add_podcast(title, script, speakers, str(out_mp3), dur)
        db.add_history("podcast", script, {"hosts": speakers}, str(out_mp3), dur,
                       len(lines), 0, kind="podcast", title=title)

        url = _public_url(str(out_mp3))
        async with self:
            self.is_podcasting = False
            self.podcast_audio_url = url
            mm = int(dur // 60); ss = int(dur % 60)
            self.podcast_msg = f"Xong podcast! {len(lines)} lượt thoại, {mm}:{ss:02d}"
            self.podcast_progress = ""
            self._refresh_history()

    # ===== EBOOK =====
    async def handle_ebook_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        from .backend import ebook as ebk
        f = files[0]
        data = await f.read()
        dest_dir = OUT_DIR / "books"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f.filename
        with open(dest, "wb") as out:
            out.write(data)
        self.ebook_path = str(dest)
        try:
            chs = ebk.parse_book(str(dest))
            self.ebook_chapters = [
                {"title": c["title"], "preview": c["text"][:160], "text": c["text"], "len": len(c["text"])}
                for c in chs
            ]
            self.ebook_msg = f"Đã đọc {len(chs)} chương từ '{f.filename}'"
        except Exception as e:
            self.ebook_msg = f"Lỗi đọc sách: {e}"

    @rx.event(background=True)
    async def generate_audiobook(self):
        async with self:
            if self.is_ebooking:
                return
            chs = list(self.ebook_chapters)
            if not chs:
                self.ebook_msg = "Chưa có sách"
                return
            if not self.ebook_voice:
                self.ebook_msg = "Chưa chọn giọng đọc"
                return
            self.is_ebooking = True
            self.ebook_audio_url = ""
            voice = db.get_voice(self.ebook_voice)
            ref = voice["ref_audio"]
            chapters = chs
            book_name = Path(self.ebook_path).stem

        svc = VoiceService.get()
        import numpy as np, soundfile as sf
        sr = svc.sample_rate
        loop = asyncio.get_event_loop()
        all_seg = []
        chap_gap = np.zeros(int(1.2 * sr), dtype=np.float32)
        for ci, ch in enumerate(chapters):
            async with self:
                self.ebook_progress = f"Chương {ci+1}/{len(chapters)} — {ch['title']}"
            res = await loop.run_in_executor(
                None,
                lambda t=ch["text"]: svc.generate(
                    text=t, ref_audio=ref, cfg_value=1.3, timesteps=23,
                    pause=0.6, speed=1.0, out_name=f"chap_{ci}_{int(time.time())}",
                ),
            )
            wav, _ = sf.read(res["wav_path"], dtype="float32")
            all_seg.append(wav)
            all_seg.append(chap_gap)
        full = np.concatenate(all_seg) if all_seg else np.zeros(1, dtype=np.float32)
        out_wav = OUT_DIR / f"audiobook_{book_name}.wav"
        sf.write(str(out_wav), full, sr)
        out_mp3 = OUT_DIR / f"audiobook_{book_name}.mp3"
        VoiceService._to_mp3(str(out_wav), str(out_mp3))
        dur = len(full) / sr
        db.add_history(self.ebook_voice, book_name, {"chapters": len(chapters)},
                       str(out_mp3), dur, len(chapters), 0, kind="audiobook", title=book_name)
        url = _public_url(str(out_mp3))
        async with self:
            self.is_ebooking = False
            self.ebook_audio_url = url
            mm = int(dur // 60); ss = int(dur % 60)
            self.ebook_msg = f"Xong sách nói! {len(chapters)} chương, {mm}:{ss:02d}"
            self.ebook_progress = ""
            self._refresh_history()

    # ===== SETTINGS =====
    def _load_settings(self):
        s = db.all_settings()
        self.set_cfg_default = float(s["default_cfg"])
        self.set_steps_default = int(s["default_steps"])
        self.set_pause_default = float(s["default_pause"])
        self.set_speed_default = float(s["default_speed"])
        self.set_master = s["master_mode"]
        self.set_bitrate = s["mp3_bitrate"]

    def slider_set_cfg(self, v: list): self.set_cfg_default = float(v[0])
    def slider_set_steps(self, v: list): self.set_steps_default = int(v[0])
    def slider_set_pause(self, v: list): self.set_pause_default = float(v[0])
    def slider_set_speed(self, v: list): self.set_speed_default = float(v[0])
    def pick_master(self, v: str): self.set_master = v
    def pick_bitrate(self, v: str): self.set_bitrate = v

    def save_settings(self):
        db.set_setting("default_cfg", self.set_cfg_default)
        db.set_setting("default_steps", self.set_steps_default)
        db.set_setting("default_pause", self.set_pause_default)
        db.set_setting("default_speed", self.set_speed_default)
        db.set_setting("master_mode", self.set_master)
        db.set_setting("mp3_bitrate", self.set_bitrate)
        # ap dung lam mac dinh cho tab tao giong
        self.cfg_value = self.set_cfg_default
        self.timesteps = self.set_steps_default
        self.pause = self.set_pause_default
        self.speed = self.set_speed_default
        self.set_msg = "Đã lưu cài đặt và áp dụng mặc định"

    # ===== computed =====
    @rx.var
    def progress_pct(self) -> int:
        if self.progress_total == 0:
            return 0
        return int(self.progress_done / self.progress_total * 100)

    @rx.var
    def eta_text(self) -> str:
        if self.eta_sec <= 0:
            return ""
        s = int(self.eta_sec)
        if s < 60:
            return f"~{s}s còn lại"
        return f"~{s//60}m{s%60:02d}s còn lại"

    @rx.var
    def voice_names(self) -> list[str]:
        return [v["name"] for v in self.voices]

    @rx.var
    def host_count_text(self) -> str:
        return f"{len(self.hosts)}/{db.MAX_HOSTS} người dẫn"

    @rx.var
    def can_add_host(self) -> bool:
        return len(self.hosts) < db.MAX_HOSTS
