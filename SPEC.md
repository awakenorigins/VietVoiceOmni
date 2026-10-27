# VietVoiceOmni - SPEC (Mula build, giao quyen quyet dinh)

## Quyet dinh kien truc
- UI: **Reflex** (Python thuan, compile ra React dep nhu app that). Chon vi NACHA muon dep + Mula viet Python, gan thang VoxCPM2.
- Engine chinh + DEFAULT: **VoxCPM2** (openbmb/VoxCPM2, 48kHz, GPU 3090).
- Model load 1 lan, giu thuong tru trong backend service (KHONG nap lai moi request).
- DB: SQLite (history, voices, podcast hosts).
- Khong pha gi dang chay (port 3000/8000 busy -> dung 3100 frontend / 8011 backend).

## Nhan setting tieng Viet (NACHA da duyet)
| Ky thuat | Nhan TV | Y nghia |
|---|---|---|
| cfg_value | Do bieu cam | thap=phieu/bam goc, cao=on dinh/deu (default 1.3) |
| inference_timesteps | Do min | cao=min, gen cham (default 23) |
| pause_between_sentences_sec | Nghi giua cau (giay) | default 0.6 |
| atempo (ffmpeg hau ky) | Toc do doc | 0.9=cham/trang nghiem, 1.1=nhanh (default 1.0) MOI |
| master | Hau ky | RAW (default) / Clean EQ |

## Giong da clone (GIU NGUYEN - khong dung)
- NhuLaiGoc: ref voxcpm_voices\NhuLaiGoc.wav (24s), cfg1.3 steps23 pause0.6 RAW
- NhuLai2: y het NhuLaiGoc (ban moc NACHA thich)
- Preset goc: tts-deepdive\voice_presets\*.json

## Tabs / Endpoint (tat ca PHAI dung that, audit ky)
1. **Tao giong doc**: chon voice (card) -> nhap text -> slider nhan TV -> [thanh tien trinh + ETA bao lau gen xong] -> nghe/tai.
2. **Clone giong moi**: upload ref audio -> dat ten + tinh cach -> luu preset.
3. **Kho giong (Library)**: list card, nghe demo, sua, xoa, loc.
4. **Lich su (History)**: moi lan gen luu lai (text, voice, params, file, thoi gian) -> nghe lai / tai / xoa.
5. **Podcast Room** (QUAN TRONG):
   - Add host: ten + tinh cach + thoi quen noi + giong (voice).
   - Save host vao DB -> bam chon lai de dang.
   - Multi-host: viet kich ban hoi thoai -> gen lan luot tung host -> ghep thanh 1 file podcast.
   - Backend ghi nho host THAT (sqlite).
6. **Ebook/EPUB -> Audiobook**: upload epub/txt -> tach chuong -> gen tung chuong -> xuat audiobook (chuong + ghep). Lam that neu kip, khong thi de option menu san.

## Tinh nang bo sung Mula tu quyet
- **Thanh tien trinh + ETA**: uoc luong "con bao lau" dua tren toc do gen trung binh (s/cau) * so cau con lai.
- Queue: gen nhieu job xep hang.
- Dark mode.
- Export: WAV/MP3, chon bitrate.
- Nut "gui Telegram" (dung document mode cho file lon).

## Audit checklist (fixpass tung buoc)
- [ ] Moi nut bam ra ket qua that
- [ ] Gen that ra audio nghe duoc
- [ ] Save/load preset that (ghi file json)
- [ ] History ghi DB that, nghe lai duoc
- [ ] Podcast host luu DB that, chon lai duoc
- [ ] ETA hien dung
- [ ] Khong crash khi text dai / nhieu cau
