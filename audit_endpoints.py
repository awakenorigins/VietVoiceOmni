"""Audit cac endpoint qua dung luong backend ma UI goi (khong qua browser click)."""
import sys, time, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from VietVoiceOmni.backend import db
from VietVoiceOmni.backend.voice_service import VoiceService

print("=== AUDIT 1: DB co giong seed ===")
db.init_db()
voices = db.list_voices()
print(f"  voices: {[v['name'] for v in voices]}")
assert any(v['name']=='NhuLai2' for v in voices)

print("=== AUDIT 2: Clone -> save voice moi (gia lap) ===")
REF = voices[0]['ref_audio']
db.add_voice("TestClone", REF, "giong test clone", 1.3, 23, 0.6, 1.0)
assert db.get_voice("TestClone") is not None
print("  OK luu giong moi")

print("=== AUDIT 3: Host (podcast) save/load THAT ===")
db.add_host("An", "NhuLai2", "vui ve sac sao", "hay dat cau hoi")
db.add_host("Binh", "NhuLaiGoc", "tram tinh", "phan tich sau")
hosts = db.list_hosts()
print(f"  hosts: {[(h['name'],h['voice_name']) for h in hosts]}")
assert len(hosts) >= 2

print("=== AUDIT 4: Podcast multi-host gen THAT (ghep 2 giong) ===")
svc = VoiceService.get()
import numpy as np, soundfile as sf
sr = svc.sample_rate
host_map = {h['name']: h for h in hosts}
script = "An: Chao moi nguoi, hom nay ban ve tinh khong.\nBinh: Dung vay, day la chu de rat sau."
segments = []
gap = np.zeros(int(0.4*sr), dtype=np.float32)
t0 = time.time()
for ln in script.splitlines():
    spk, txt = ln.split(":",1)
    spk, txt = spk.strip(), txt.strip()
    voice = db.get_voice(host_map[spk]['voice_name'])
    res = svc.generate(text=txt, ref_audio=voice['ref_audio'], out_name=f"audit_pod_{spk}")
    wav,_ = sf.read(res['wav_path'], dtype='float32')
    segments.append(wav); segments.append(gap)
    print(f"  {spk}: {res['duration']:.1f}s")
full = np.concatenate(segments)
outp = Path(__file__).parent / "output" / "audit_podcast.mp3"
sf.write(str(outp).replace('.mp3','.wav'), full, sr)
VoiceService._to_mp3(str(outp).replace('.mp3','.wav'), str(outp))
print(f"  Podcast ghep: {len(full)/sr:.1f}s, gen {time.time()-t0:.0f}s, file={outp.exists()}")
assert outp.exists()

print("=== AUDIT 5: ETA estimate ===")
eta = svc.estimate_eta(10)
print(f"  ETA 10 cau = {eta:.0f}s")
assert eta > 0

print("=== AUDIT 6: cleanup test data ===")
db.delete_voice("TestClone")
db.delete_host("An"); db.delete_host("Binh")
print("  cleaned")

print("\n*** AUDIT ENDPOINTS: TAT CA PASS ***")
