"""Ebook/EPUB -> tach chuong. Tra list (tieu_de, noi_dung)."""
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path


class _HTMLText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
        if tag in ("p", "br", "div", "h1", "h2", "h3", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)

    def text(self):
        t = "".join(self.parts)
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r"\n\s*\n+", "\n\n", t)
        return t.strip()


def _html_to_text(html: str) -> str:
    p = _HTMLText()
    try:
        p.feed(html)
    except Exception:
        pass
    return p.text()


def parse_epub(path: str) -> list[dict]:
    """Tra list chuong: [{title, text}]. Doc theo spine order neu co."""
    chapters = []
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        # tim cac file html/xhtml
        html_files = [n for n in names if n.lower().endswith((".xhtml", ".html", ".htm"))]
        # uu tien thu tu opf spine
        opf = next((n for n in names if n.lower().endswith(".opf")), None)
        order = html_files
        if opf:
            try:
                opf_data = z.read(opf).decode("utf-8", "ignore")
                ids = re.findall(r'idref="([^"]+)"', opf_data)
                hrefs = dict(re.findall(r'id="([^"]+)"[^>]*href="([^"]+)"', opf_data))
                base = str(Path(opf).parent)
                ordered = []
                for i in ids:
                    h = hrefs.get(i)
                    if not h:
                        continue
                    full = (Path(base) / h).as_posix().lstrip("/")
                    match = next((n for n in html_files if n.endswith(h) or n == full), None)
                    if match:
                        ordered.append(match)
                if ordered:
                    order = ordered
            except Exception:
                pass
        for idx, n in enumerate(order):
            try:
                raw = z.read(n).decode("utf-8", "ignore")
            except Exception:
                continue
            txt = _html_to_text(raw)
            if len(txt) < 30:
                continue
            # tieu de = dong dau khong rong
            first = next((l.strip() for l in txt.splitlines() if l.strip()), f"Chuong {idx+1}")
            title = first[:60]
            chapters.append({"title": title, "text": txt})
    return chapters


def parse_txt(path: str) -> list[dict]:
    """TXT: tach chuong theo dong 'Chuong N' hoac chia khoi lon."""
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    # tach theo 'Chuong' / 'Chapter'
    pat = re.compile(r"(?im)^\s*(chuong|chapter|ch\u01b0\u01a1ng)\s+[\dIVXLC]+.*$")
    matches = list(pat.finditer(text))
    if len(matches) >= 2:
        chapters = []
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            title = m.group(0).strip()[:60]
            chapters.append({"title": title, "text": body})
        return chapters
    # khong co marker -> chia khoi ~3000 ky tu
    chunks = []
    buf = ""
    for para in text.split("\n\n"):
        buf += para + "\n\n"
        if len(buf) > 3000:
            chunks.append(buf.strip()); buf = ""
    if buf.strip():
        chunks.append(buf.strip())
    return [{"title": f"Phan {i+1}", "text": c} for i, c in enumerate(chunks)]


def parse_book(path: str) -> list[dict]:
    p = path.lower()
    if p.endswith(".epub"):
        return parse_epub(path)
    return parse_txt(path)
