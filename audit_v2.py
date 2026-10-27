# -*- coding: utf-8 -*-
"""Audit v2: host mau + setting rieng, gioi han 13, library kind, settings."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from VietVoiceOmni.backend import db

db.init_db()
print("=== A1: 13 mau + MAX_HOSTS ===")
print(f"  MAX_HOSTS={db.MAX_HOSTS}, so mau={len(db.HOST_COLORS)}")
assert db.MAX_HOSTS == 13 and len(db.HOST_COLORS) == 13

print("=== A2: them host co mau tu dong + setting rieng ===")
for h in db.list_hosts():
    db.delete_host(h["name"])
db.add_host("An", "NhuLai2", "vui ve", "hay hoi", db.next_host_color(), 1.2, 20, 0.3, 1.05)
db.add_host("Binh", "NhuLaiGoc", "tram", "phan tich", db.next_host_color(), 1.4, 25, 0.5, 0.95)
hs = db.list_hosts()
for h in hs:
    print(f"  {h['name']}: mau={h['color']} cfg={h['cfg_value']} steps={h['timesteps']} pause={h['pause']} speed={h['speed']}")
assert hs[0]["color"] != hs[1]["color"], "mau phai khac nhau"
assert hs[0]["cfg_value"] == 1.2

print("=== A3: gioi han 13 host ===")
base = db.count_hosts()
for i in range(base, 13):
    db.add_host(f"H{i}", "NhuLai2", "", "", db.next_host_color())
print(f"  count = {db.count_hosts()} (max {db.MAX_HOSTS})")
assert db.count_hosts() == 13
# them cai thu 14 -> logic state se chan; o DB van cho nhung State.save_host check count
print("  (State.save_host se chan host thu 14 khi count>=13)")

print("=== A4: history kind speech/podcast/audiobook ===")
db.add_history("NhuLai2", "test bai thoai", {}, "x.mp3", 10, 3, 5, kind="speech", title="Bai thoai 1")
db.add_history("podcast", "kich ban", {}, "p.mp3", 60, 8, 0, kind="podcast", title="Podcast 1")
db.add_history("NhuLai2", "sach", {}, "b.mp3", 600, 12, 0, kind="audiobook", title="Sach 1")
for k in ["speech", "podcast", "audiobook"]:
    rows = db.list_history(50, kind=k)
    print(f"  kind={k}: {len(rows)} muc, vd title='{rows[0]['title'] if rows else '-'}'")
    assert len(rows) >= 1

print("=== A5: settings save/load ===")
db.set_setting("default_cfg", "1.5")
db.set_setting("master_mode", "clean")
s = db.all_settings()
print(f"  default_cfg={s['default_cfg']} master={s['master_mode']} bitrate={s['mp3_bitrate']}")
assert s["default_cfg"] == "1.5" and s["master_mode"] == "clean"
# reset
db.set_setting("default_cfg", "1.3"); db.set_setting("master_mode", "raw")

print("=== A6: cleanup test data ===")
for h in db.list_hosts():
    if h["name"] not in ("An", "Binh"):
        db.delete_host(h["name"])
# xoa history test
import sqlite3
con = sqlite3.connect(str(db.DB_PATH))
con.execute("DELETE FROM history WHERE mp3_path IN ('x.mp3','p.mp3','b.mp3')")
con.commit(); con.close()
db.delete_host("An"); db.delete_host("Binh")
print(f"  hosts con lai: {db.count_hosts()}")

print("\n*** AUDIT V2: TAT CA PASS ***")
