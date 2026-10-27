# -*- coding: utf-8 -*-
"""Audit THAT: gen doan truyen 23 bang NhuLai2 qua VoiceService cua app (giong het bam nut UI)."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from VietVoiceOmni.backend import db
from VietVoiceOmni.backend.voice_service import VoiceService, split_sentences

TEXT = """Buổi chiều. Studio âm nhạc. NaCha đang chỉnh mixer, tai nghe lủng lẳng trên cổ tay gõ gõ nhịp trên mặt bàn cổ. Producer bên cạnh hỏi: Anh viết bài nào hôm nay? NaCha không trả lời. Chỉ nhắm mắt. Rồi bật mic, nói vào đó như đang thu âm một bài thơ:
Một hôm, Như Lai đi qua chợ. Có người chạy đến mắng Ngài. Họ la hét thật to. Nói những điều thật xấu và không thật như nói ngài giả tu giả vờ cao quý. Đệ tử giận, muốn ra tay diệt cái ác này. Nhưng Như Lai giơ tay ra hiệu dừng.
Ngài đứng yên. Nghe hết. Sau vài nén nhang Khi tiếng mắng nhỏ dần, kiệt sức chỉ còn vài tiếng thều thào, Như Lai hỏi:
Nếu tặng ngươi một món quà mà ngươi không nhận, món quà về tay ai?
Về tay người tặng.
Đúng rồi. Lời chửi của ngươi, ta không nhận. Nó về lại với ngươi."""

db.init_db()
v = db.get_voice("NhuLai2")
assert v, "NhuLai2 khong co trong DB"
print(f"Voice NhuLai2: cfg={v['cfg_value']} steps={v['timesteps']} pause={v['pause']} ref={Path(v['ref_audio']).name}")

sents = split_sentences(TEXT)
print(f"So cau tach duoc: {len(sents)}")

svc = VoiceService.get()
eta = svc.estimate_eta(len(sents))
print(f"ETA du kien: {eta:.0f}s")

prog = {"n": 0}
def cb(done, total, e):
    prog["n"] = done
    print(f"  [{done}/{total}] ETA ~{e:.0f}s", flush=True)

t0 = time.time()
res = svc.generate(
    text=TEXT, ref_audio=v["ref_audio"],
    cfg_value=v["cfg_value"], timesteps=v["timesteps"],
    pause=v["pause"], speed=1.0,
    out_name="audit_chuyen23_nhulai2", on_progress=cb,
)
gen_t = time.time() - t0

# ghi history dung kind speech (giong UI)
db.add_history("NhuLai2", TEXT, {"cfg": v["cfg_value"], "steps": v["timesteps"], "pause": v["pause"], "speed": 1.0},
               res["mp3_path"], res["duration"], res["n_sentences"], gen_t, kind="speech", title="Cau chuyen 23")

mm = int(res["duration"]//60); ss = int(res["duration"]%60)
print(f"\n=== KET QUA ===")
print(f"  MP3: {res['mp3_path']}")
print(f"  So cau gen: {res['n_sentences']}")
print(f"  Audio: {mm}:{ss:02d} ({res['duration']:.1f}s)")
print(f"  Gen time: {gen_t:.0f}s")
print(f"  File size: {Path(res['mp3_path']).stat().st_size/1024/1024:.2f}MB")
print(f"  History (kind=speech) da ghi.")
print("*** AUDIT GEN REAL: PASS ***")
