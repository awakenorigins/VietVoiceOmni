# -*- coding: utf-8 -*-
"""VietVoiceOmni - App chinh (Reflex). UI dep, dark, tieng Viet co dau."""
import reflex as rx
from .state import State

ACCENT = "violet"


# ---------- components ----------
def sidebar_item(label: str, icon: str, tab: str) -> rx.Component:
    active = State.active_tab == tab
    return rx.hstack(
        rx.icon(icon, size=20),
        rx.text(label, size="3", weight="medium"),
        on_click=lambda: State.set_tab(tab),
        width="100%", padding="0.7em 1em", border_radius="0.6em", cursor="pointer",
        align="center", spacing="3",
        background=rx.cond(active, rx.color(ACCENT, 4), "transparent"),
        color=rx.cond(active, rx.color(ACCENT, 11), rx.color("gray", 11)),
        _hover={"background": rx.color(ACCENT, 3)}, transition="all 0.15s",
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("audio-lines", size=28, color=rx.color(ACCENT, 9)),
            rx.heading("VietVoiceOmni", size="5", weight="bold"),
            align="center", spacing="2", padding_bottom="0.3em",
        ),
        rx.text("VoxCPM2 · Giọng nói & Nhân bản", size="1", color=rx.color("gray", 9)),
        rx.divider(margin_y="1em"),
        sidebar_item("Tạo giọng đọc", "mic", "create"),
        sidebar_item("Nhân bản giọng", "user-plus", "clone"),
        sidebar_item("Kho giọng", "library", "voices"),
        sidebar_item("Thư viện", "folder-open", "library"),
        sidebar_item("Phòng Podcast", "radio", "podcast"),
        sidebar_item("Sách nói (Ebook)", "book-open", "ebook"),
        sidebar_item("Cài đặt", "settings", "settings"),
        rx.spacer(),
        rx.hstack(
            rx.icon(rx.cond(State.engine_loaded, "circle-check", "circle"), size=14,
                    color=rx.cond(State.engine_loaded, "green", rx.color("gray", 8))),
            rx.text(rx.cond(State.engine_loaded, "Động cơ sẵn sàng", "Động cơ chưa nạp"),
                    size="1", color=rx.color("gray", 9)),
            align="center", spacing="2",
        ),
        rx.color_mode.button(),
        width="260px", height="100vh", padding="1.5em", spacing="1",
        border_right=f"1px solid {rx.color('gray', 4)}",
        background=rx.color("gray", 1), position="sticky", top="0",
    )


def card(*children, **kwargs) -> rx.Component:
    return rx.box(
        *children, padding="1.5em", border_radius="1em",
        border=f"1px solid {rx.color('gray', 4)}", background=rx.color("gray", 1), **kwargs,
    )


def labeled_slider(label: str, value, hint: str, minv, maxv, stepv, handler) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2", weight="medium"), rx.spacer(),
            rx.badge(value.to_string(), color_scheme=ACCENT, variant="soft"),
            width="100%", align="center",
        ),
        rx.slider(min=minv, max=maxv, step=stepv, default_value=[value],
                  on_change=handler, color_scheme=ACCENT),
        rx.text(hint, size="1", color=rx.color("gray", 9)),
        width="100%", spacing="1",
    )


# ---------- TAB: Tao giong doc ----------
def voice_card(v: rx.Var) -> rx.Component:
    selected = State.selected_voice == v["name"]
    return rx.vstack(
        rx.hstack(
            rx.icon("mic", size=18, color=rx.color(ACCENT, 9)),
            rx.text(v["name"], weight="bold", size="3"), rx.spacer(),
            rx.cond(selected, rx.icon("check", size=16, color=rx.color(ACCENT, 9)), rx.fragment()),
            width="100%", align="center",
        ),
        rx.text(v["description"], size="1", color=rx.color("gray", 10), no_of_lines=2),
        on_click=lambda: State.select_voice(v["name"]),
        width="100%", padding="0.9em", border_radius="0.7em", cursor="pointer",
        border=rx.cond(selected, f"2px solid {rx.color(ACCENT, 8)}", f"1px solid {rx.color('gray', 4)}"),
        background=rx.cond(selected, rx.color(ACCENT, 2), rx.color("gray", 1)),
        _hover={"border": f"1px solid {rx.color(ACCENT, 6)}"}, transition="all 0.15s", spacing="1",
    )


def tab_create() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading("Tạo giọng đọc", size="6"),
            rx.text("Chọn giọng, nhập văn bản, chỉnh thông số rồi bấm Tạo.", size="2", color=rx.color("gray", 10)),
            rx.text("Chọn giọng", size="2", weight="bold", margin_top="0.5em"),
            rx.grid(rx.foreach(State.voices, voice_card), columns="2", spacing="2", width="100%"),
            rx.text_area(value=State.text_input, on_change=State.set_text_input,
                         placeholder="Dán văn bản tiếng Việt có dấu đầy đủ...",
                         width="100%", height="180px", margin_top="0.5em"),
            rx.button(
                rx.cond(State.is_generating, rx.spinner(), rx.icon("play", size=18)),
                rx.cond(State.is_generating, "Đang tạo...", "Tạo giọng đọc"),
                on_click=State.generate, disabled=State.is_generating,
                size="3", color_scheme=ACCENT, width="100%",
            ),
            rx.cond(
                State.is_generating | (State.progress_total > 0),
                card(
                    rx.hstack(
                        rx.text(State.result_info, size="2"), rx.spacer(),
                        rx.text(State.eta_text, size="2", color=rx.color(ACCENT, 10), weight="bold"),
                        width="100%",
                    ),
                    rx.progress(value=State.progress_pct, color_scheme=ACCENT, margin_top="0.5em"),
                    width="100%", margin_top="0.5em",
                ),
                rx.fragment(),
            ),
            rx.cond(
                State.result_audio_url != "",
                card(
                    rx.text("Kết quả", size="2", weight="bold"),
                    rx.audio(src=State.result_audio_url, width="100%", height="54px"),
                    rx.link(rx.button("Tải MP3", rx.icon("download", size=16), variant="soft", color_scheme=ACCENT),
                            href=State.result_audio_url, is_external=True),
                    width="100%", margin_top="0.5em", spacing="2",
                ),
                rx.fragment(),
            ),
            width="62%", spacing="3", align="start",
        ),
        rx.vstack(
            rx.heading("Thông số", size="4"),
            card(
                labeled_slider("Độ biểu cảm", State.cfg_value,
                               "Thấp = phiêu/bám gốc. Cao = ổn định/đều.", 0.3, 3.0, 0.1, State.slider_cfg),
                rx.divider(margin_y="0.8em"),
                labeled_slider("Độ mịn", State.timesteps,
                               "Cao = mịn hơn nhưng tạo chậm hơn.", 8, 40, 1, State.slider_steps),
                rx.divider(margin_y="0.8em"),
                labeled_slider("Nghỉ giữa câu (giây)", State.pause,
                               "Khoảng lặng giữa các câu.", 0.0, 2.0, 0.1, State.slider_pause),
                rx.divider(margin_y="0.8em"),
                labeled_slider("Tốc độ đọc", State.speed,
                               "0.9 = chậm/trang nghiêm. 1.1 = nhanh.", 0.7, 1.3, 0.05, State.slider_speed),
                width="100%",
            ),
            width="36%", spacing="3", align="start",
        ),
        width="100%", spacing="5", align="start",
    )


# ---------- TAB: Clone ----------
def tab_clone() -> rx.Component:
    return rx.vstack(
        rx.heading("Nhân bản giọng", size="6"),
        rx.text("Tải lên một đoạn audio mẫu (3-30s, rõ tiếng), đặt tên rồi lưu.",
                size="2", color=rx.color("gray", 10)),
        card(
            rx.vstack(
                rx.input(placeholder="Tên giọng (vd: ThầyMinh)", value=State.clone_name,
                         on_change=State.set_clone_name, width="100%"),
                rx.input(placeholder="Mô tả (tùy chọn)", value=State.clone_desc,
                         on_change=State.set_clone_desc, width="100%"),
                rx.upload(
                    rx.vstack(
                        rx.icon("upload", size=28, color=rx.color(ACCENT, 9)),
                        rx.text("Kéo thả hoặc bấm chọn file audio (.wav/.mp3)", size="2"),
                        align="center", spacing="2",
                    ),
                    id="clone_upload", multiple=False,
                    accept={"audio/*": [".wav", ".mp3", ".m4a", ".flac"]},
                    on_drop=State.handle_clone_upload(rx.upload_files(upload_id="clone_upload")),
                    border=f"2px dashed {rx.color(ACCENT, 6)}", padding="2em",
                    border_radius="0.7em", width="100%",
                ),
                rx.cond(State.clone_msg != "",
                        rx.text(State.clone_msg, size="2", color="green"), rx.fragment()),
                rx.button("Lưu giọng", rx.icon("save", size=16), on_click=State.save_clone,
                          size="3", color_scheme=ACCENT, width="100%"),
                spacing="3", width="100%",
            ),
            width="100%", max_width="640px",
        ),
        width="100%", spacing="4", align="start",
    )


# ---------- TAB: Kho giong ----------
def lib_voice_row(v: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.icon("mic", size=18, color=rx.color(ACCENT, 9)),
        rx.vstack(
            rx.text(v["name"], weight="bold", size="3"),
            rx.text(v["description"], size="1", color=rx.color("gray", 10), no_of_lines=1),
            spacing="0", align="start",
        ),
        rx.spacer(),
        rx.badge(f"biểu cảm {v['cfg_value']}", variant="soft"),
        rx.badge(f"mịn {v['timesteps']}", variant="soft"),
        rx.button(rx.icon("trash-2", size=14), on_click=lambda: State.del_voice(v["name"]),
                  variant="soft", color_scheme="red", size="1"),
        width="100%", align="center", padding="0.8em",
        border=f"1px solid {rx.color('gray', 4)}", border_radius="0.7em",
    )


def tab_voices() -> rx.Component:
    return rx.vstack(
        rx.heading("Kho giọng", size="6"),
        rx.text("Tất cả giọng đã lưu. Chọn ở tab Tạo giọng để dùng.", size="2", color=rx.color("gray", 10)),
        rx.vstack(rx.foreach(State.voices, lib_voice_row), width="100%", spacing="2"),
        width="100%", spacing="4", align="start",
    )


# ---------- TAB: Thu vien (3 muc) ----------
def lib_seg_btn(label: str, kind: str, icon: str) -> rx.Component:
    active = State.lib_kind == kind
    return rx.button(
        rx.icon(icon, size=15), label,
        on_click=lambda: State.set_lib_kind(kind),
        variant=rx.cond(active, "solid", "soft"),
        color_scheme=ACCENT, size="2",
    )


def lib_item_row(h: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.hstack(
                rx.badge(h["voice_name"], color_scheme=ACCENT, variant="soft"),
                rx.text(rx.cond(h["title"] != "", h["title"], h["text"]),
                        size="2", no_of_lines=1, color=rx.color("gray", 11), weight="medium"),
                align="center", spacing="2",
            ),
            rx.text(f"{h['n_sentences']} phần · {h['duration'].to(int)}s", size="1", color=rx.color("gray", 9)),
            spacing="1", align="start", width="100%",
        ),
        rx.spacer(),
        rx.button(rx.icon("play", size=14), on_click=lambda: State.play_history(h["mp3_path"]),
                  variant="soft", color_scheme=ACCENT, size="1"),
        rx.button(rx.icon("trash-2", size=14), on_click=lambda: State.del_history(h["id"]),
                  variant="soft", color_scheme="red", size="1"),
        width="100%", align="center", padding="0.8em",
        border=f"1px solid {rx.color('gray', 4)}", border_radius="0.7em",
    )


def tab_library() -> rx.Component:
    return rx.vstack(
        rx.heading("Thư viện", size="6"),
        rx.text("Mọi bản đã tạo, phân theo loại. Bấm Play để nghe lại.", size="2", color=rx.color("gray", 10)),
        rx.hstack(
            lib_seg_btn("Bài Thoại", "speech", "mic"),
            lib_seg_btn("Podcast", "podcast", "radio"),
            lib_seg_btn("Sách nói", "audiobook", "book-open"),
            spacing="2",
        ),
        rx.cond(
            State.history.length() > 0,
            rx.vstack(rx.foreach(State.history, lib_item_row), width="100%", spacing="2", margin_top="0.5em"),
            rx.text("Chưa có mục nào.", color=rx.color("gray", 9), margin_top="1em"),
        ),
        width="100%", spacing="4", align="start",
    )


# ---------- TAB: Podcast Room ----------
def host_card(h: rx.Var) -> rx.Component:
    expanded = State.expanded_host == h["name"]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(width="14px", height="14px", border_radius="50%", background=h["color"]),
                rx.text(h["name"], weight="bold", size="3"),
                rx.badge(h["voice_name"], variant="soft"),
                rx.spacer(),
                rx.button(rx.icon("pencil", size=13), on_click=lambda: State.edit_host(h["name"]),
                          variant="ghost", size="1"),
                rx.button(rx.icon(rx.cond(expanded, "chevron-up", "chevron-down"), size=15),
                          on_click=lambda: State.toggle_expand_host(h["name"]),
                          variant="ghost", size="1"),
                rx.button(rx.icon("trash-2", size=13), on_click=lambda: State.del_host(h["name"]),
                          variant="ghost", color_scheme="red", size="1"),
                width="100%", align="center", spacing="2",
            ),
            rx.cond(
                expanded,
                rx.vstack(
                    rx.cond(h["personality"] != "",
                            rx.hstack(rx.text("Tính cách:", size="1", color=rx.color("gray", 9)),
                                      rx.text(h["personality"], size="1"), spacing="1"), rx.fragment()),
                    rx.cond(h["habits"] != "",
                            rx.hstack(rx.text("Thói quen:", size="1", color=rx.color("gray", 9)),
                                      rx.text(h["habits"], size="1"), spacing="1"), rx.fragment()),
                    rx.hstack(
                        rx.badge(f"biểu cảm {h['cfg_value']}", variant="soft", size="1"),
                        rx.badge(f"mịn {h['timesteps']}", variant="soft", size="1"),
                        rx.badge(f"nghỉ {h['pause']}s", variant="soft", size="1"),
                        rx.badge(f"tốc độ {h['speed']}", variant="soft", size="1"),
                        spacing="1", wrap="wrap",
                    ),
                    spacing="1", align="start", width="100%", margin_top="0.4em",
                ),
                rx.fragment(),
            ),
            spacing="1", width="100%",
        ),
        width="100%", padding="0.9em", border_radius="0.7em",
        border=f"1px solid {rx.color('gray', 4)}",
        border_left=f"4px solid {h['color']}", background=rx.color("gray", 1),
    )


def tab_podcast() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading("Phòng Podcast", size="6"),
            rx.text("Viết kịch bản dạng 'TênNgườiDẫn: lời thoại' mỗi dòng. Mỗi người dẫn đọc bằng giọng riêng.",
                    size="2", color=rx.color("gray", 10)),
            rx.input(placeholder="Tiêu đề podcast", value=State.podcast_title,
                     on_change=State.set_podcast_title, width="100%"),
            rx.text_area(value=State.podcast_script, on_change=State.set_podcast_script,
                         placeholder="An: Chào mọi người, hôm nay chúng ta nói về...\nBình: Đúng rồi, chủ đề rất hay...",
                         width="100%", height="240px"),
            rx.button(
                rx.cond(State.is_podcasting, rx.spinner(), rx.icon("radio", size=18)),
                rx.cond(State.is_podcasting, "Đang dựng podcast...", "Tạo Podcast"),
                on_click=State.generate_podcast, disabled=State.is_podcasting,
                size="3", color_scheme=ACCENT, width="100%",
            ),
            rx.cond(State.podcast_progress != "",
                    rx.text(State.podcast_progress, size="2", color=rx.color(ACCENT, 10)), rx.fragment()),
            rx.cond(State.podcast_msg != "",
                    rx.text(State.podcast_msg, size="2", color="green"), rx.fragment()),
            rx.cond(State.podcast_audio_url != "",
                    card(rx.audio(src=State.podcast_audio_url, width="100%", height="54px"), width="100%"),
                    rx.fragment()),
            width="56%", spacing="3", align="start",
        ),
        rx.vstack(
            rx.hstack(
                rx.heading("Người dẫn", size="4"), rx.spacer(),
                rx.badge(State.host_count_text, color_scheme=ACCENT, variant="soft"),
                width="100%", align="center",
            ),
            card(
                rx.vstack(
                    rx.input(placeholder="Tên người dẫn", value=State.host_name,
                             on_change=State.set_host_name, width="100%"),
                    rx.input(placeholder="Tính cách (vd: vui vẻ, sắc sảo)", value=State.host_personality,
                             on_change=State.set_host_personality, width="100%"),
                    rx.input(placeholder="Thói quen nói (vd: hay đặt câu hỏi)", value=State.host_habits,
                             on_change=State.set_host_habits, width="100%"),
                    # mo rong tuy chinh giong
                    rx.hstack(
                        rx.switch(checked=State.host_advanced, on_change=State.toggle_host_advanced,
                                  color_scheme=ACCENT),
                        rx.text("Tùy chỉnh chọn giọng & thông số", size="2"),
                        align="center", spacing="2", width="100%",
                    ),
                    rx.cond(
                        State.host_advanced,
                        rx.vstack(
                            rx.text("Giọng", size="1", weight="bold", color=rx.color("gray", 10)),
                            rx.select(State.voice_names, value=State.host_voice,
                                      on_change=State.set_host_voice, placeholder="Chọn giọng", width="100%"),
                            labeled_slider("Độ biểu cảm", State.host_cfg, "", 0.3, 3.0, 0.1, State.slider_host_cfg),
                            labeled_slider("Độ mịn", State.host_steps, "", 8, 40, 1, State.slider_host_steps),
                            labeled_slider("Nghỉ giữa câu", State.host_pause, "", 0.0, 1.5, 0.1, State.slider_host_pause),
                            labeled_slider("Tốc độ đọc", State.host_speed, "", 0.7, 1.3, 0.05, State.slider_host_speed),
                            spacing="2", width="100%",
                            padding="0.8em", border_radius="0.6em", background=rx.color("gray", 2),
                        ),
                        rx.fragment(),
                    ),
                    rx.button("Lưu người dẫn", rx.icon("user-plus", size=16),
                              on_click=State.save_host, color_scheme=ACCENT, width="100%",
                              disabled=~State.can_add_host & (State.host_name == "")),
                    rx.cond(State.host_msg != "", rx.text(State.host_msg, size="1", color="green"), rx.fragment()),
                    spacing="2", width="100%",
                ),
                width="100%",
            ),
            rx.vstack(rx.foreach(State.hosts, host_card), width="100%", spacing="2"),
            width="42%", spacing="3", align="start",
        ),
        width="100%", spacing="5", align="start",
    )


# ---------- TAB: Ebook ----------
def chap_row(c: rx.Var) -> rx.Component:
    return rx.hstack(
        rx.icon("file-text", size=16, color=rx.color(ACCENT, 9)),
        rx.vstack(
            rx.text(c["title"], weight="bold", size="2"),
            rx.text(c["preview"], size="1", color=rx.color("gray", 10), no_of_lines=1),
            spacing="0", align="start",
        ),
        rx.spacer(),
        rx.badge(f"{c['len']} ký tự", variant="soft"),
        width="100%", align="center", padding="0.7em",
        border=f"1px solid {rx.color('gray', 4)}", border_radius="0.6em",
    )


def tab_ebook() -> rx.Component:
    return rx.vstack(
        rx.heading("Sách nói (Ebook → Audiobook)", size="6"),
        rx.text("Tải EPUB/TXT lên, tự động tách chương rồi tạo sách nói (ghép đầy đủ).",
                size="2", color=rx.color("gray", 10)),
        rx.hstack(
            rx.upload(
                rx.vstack(
                    rx.icon("book-open", size=28, color=rx.color(ACCENT, 9)),
                    rx.text("Kéo thả EPUB / TXT", size="2"), align="center", spacing="2",
                ),
                id="ebook_upload", multiple=False,
                accept={"application/epub+zip": [".epub"], "text/plain": [".txt"]},
                on_drop=State.handle_ebook_upload(rx.upload_files(upload_id="ebook_upload")),
                border=f"2px dashed {rx.color(ACCENT, 6)}", padding="1.5em",
                border_radius="0.7em", width="50%",
            ),
            rx.vstack(
                rx.text("Giọng đọc", size="2", weight="bold"),
                rx.select(State.voice_names, value=State.ebook_voice, on_change=State.set_ebook_voice,
                          placeholder="Chọn giọng", width="100%"),
                rx.button(
                    rx.cond(State.is_ebooking, rx.spinner(), rx.icon("book-audio", size=18)),
                    rx.cond(State.is_ebooking, "Đang tạo sách nói...", "Tạo Sách Nói"),
                    on_click=State.generate_audiobook, disabled=State.is_ebooking,
                    size="3", color_scheme=ACCENT, width="100%",
                ),
                rx.cond(State.ebook_progress != "",
                        rx.text(State.ebook_progress, size="2", color=rx.color(ACCENT, 10)), rx.fragment()),
                rx.cond(State.ebook_msg != "",
                        rx.text(State.ebook_msg, size="2", color="green"), rx.fragment()),
                width="50%", spacing="2", align="start",
            ),
            width="100%", spacing="4", align="start",
        ),
        rx.cond(
            State.ebook_audio_url != "",
            card(rx.text("Sách nói", weight="bold", size="2"),
                 rx.audio(src=State.ebook_audio_url, width="100%", height="54px"), width="100%"),
            rx.fragment(),
        ),
        rx.cond(
            State.ebook_chapters.length() > 0,
            rx.vstack(
                rx.text("Danh sách chương", size="2", weight="bold", margin_top="0.5em"),
                rx.vstack(rx.foreach(State.ebook_chapters, chap_row), width="100%", spacing="2"),
                width="100%", spacing="2", align="start",
            ),
            rx.fragment(),
        ),
        width="100%", spacing="4", align="start",
    )


# ---------- TAB: Cai dat ----------
def tab_settings() -> rx.Component:
    return rx.vstack(
        rx.heading("Cài đặt", size="6"),
        rx.text("Thông số mặc định áp dụng cho mỗi lần tạo mới + chất lượng xuất file.",
                size="2", color=rx.color("gray", 10)),
        rx.hstack(
            card(
                rx.heading("Thông số mặc định", size="4"),
                labeled_slider("Độ biểu cảm", State.set_cfg_default, "", 0.3, 3.0, 0.1, State.slider_set_cfg),
                rx.divider(margin_y="0.6em"),
                labeled_slider("Độ mịn", State.set_steps_default, "", 8, 40, 1, State.slider_set_steps),
                rx.divider(margin_y="0.6em"),
                labeled_slider("Nghỉ giữa câu", State.set_pause_default, "", 0.0, 2.0, 0.1, State.slider_set_pause),
                rx.divider(margin_y="0.6em"),
                labeled_slider("Tốc độ đọc", State.set_speed_default, "", 0.7, 1.3, 0.05, State.slider_set_speed),
                width="48%", spacing="2",
            ),
            card(
                rx.heading("Chất lượng & Âm sắc", size="4"),
                rx.text("Hậu kỳ (Master)", size="2", weight="medium", margin_top="0.5em"),
                rx.select(["raw", "clean"], value=State.set_master, on_change=State.pick_master, width="100%"),
                rx.text("raw = mộc, rõ, nhiều cảm xúc · clean = EQ làm sạch nhẹ",
                        size="1", color=rx.color("gray", 9)),
                rx.text("Bitrate MP3", size="2", weight="medium", margin_top="0.8em"),
                rx.select(["128k", "192k", "256k", "320k"], value=State.set_bitrate,
                          on_change=State.pick_bitrate, width="100%"),
                rx.divider(margin_y="0.8em"),
                rx.text("Động cơ: VoxCPM2 · 48kHz · GPU RTX 3090", size="1", color=rx.color("gray", 9)),
                rx.text("Mặc định model chính: VoxCPM2", size="1", color=rx.color("gray", 9)),
                width="48%", spacing="1",
            ),
            width="100%", spacing="4", align="start",
        ),
        rx.button("Lưu cài đặt", rx.icon("save", size=16), on_click=State.save_settings,
                  size="3", color_scheme=ACCENT),
        rx.cond(State.set_msg != "", rx.text(State.set_msg, size="2", color="green"), rx.fragment()),
        width="100%", spacing="4", align="start",
    )


# ---------- main ----------
def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.match(
                State.active_tab,
                ("create", tab_create()),
                ("clone", tab_clone()),
                ("voices", tab_voices()),
                ("library", tab_library()),
                ("podcast", tab_podcast()),
                ("ebook", tab_ebook()),
                ("settings", tab_settings()),
                tab_create(),
            ),
            padding="2.5em", width="100%", height="100vh", overflow_y="auto",
        ),
        width="100%", spacing="0", align="start",
    )


app = rx.App(
    theme=rx.theme(appearance="dark", accent_color=ACCENT, radius="large", scaling="100%"),
)
app.add_page(index, on_load=State.on_load, title="VietVoiceOmni")
