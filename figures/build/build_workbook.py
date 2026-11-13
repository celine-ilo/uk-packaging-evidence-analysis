"""Build the analysis workbook as a colour-coded Word document.

Body text is fully justified. Four colour-coded box types carry meaning:

  teal  established findings
  blue  data sources and outputs
  rust  problems in the data
  plum  decisions still open

Usage: python3 build_workbook.py <markdown in> <docx out>
"""
import re
import sys

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x5A, 0x5A, 0x5A)

BOX = {
    "teal": ("15605A", "E4EFEC"),
    "blue": ("1F5B8F", "E7EEF6"),
    "rust": ("A8551E", "FAEDE2"),
    "plum": ("6B3A6B", "F2EAF2"),
}
TEAL = RGBColor(0x15, 0x60, 0x5A)

MARKER = re.compile(r"^::(teal|blue|rust|plum)::\s*(.*)$")
INLINE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def shade(par, fill):
    pr = par._p.get_or_add_pPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:fill"), fill)
    pr.append(sh)


def border(par, where, colour, size=6, space=6):
    pr = par._p.get_or_add_pPr()
    bd = pr.find(qn("w:pBdr"))
    if bd is None:
        bd = OxmlElement("w:pBdr")
        pr.append(bd)
    e = OxmlElement("w:" + where)
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), str(size))
    e.set(qn("w:space"), str(space))
    e.set(qn("w:color"), colour)
    bd.append(e)


def write_runs(par, text, size=10.5, colour=INK, mono=TEAL):
    for piece in INLINE.split(text):
        if not piece:
            continue
        if piece.startswith("**") and piece.endswith("**"):
            r = par.add_run(piece[2:-2])
            r.bold = True
            r.font.size = Pt(size)
            r.font.color.rgb = colour
            r.font.name = "Calibri"
        elif piece.startswith("`") and piece.endswith("`"):
            r = par.add_run(piece[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(size - 1)
            r.font.color.rgb = mono
        else:
            r = par.add_run(piece)
            r.font.size = Pt(size)
            r.font.color.rgb = colour
            r.font.name = "Calibri"


def main(md_path, out_path):
    lines = open(md_path, encoding="utf-8").read().split("\n")
    doc = Document()

    s = doc.sections[0]
    s.top_margin = Cm(2.0)
    s.bottom_margin = Cm(2.0)
    s.left_margin = Cm(2.2)
    s.right_margin = Cm(2.2)

    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)

    state = {"title_done": False, "ordered": 0}

    for raw in lines:
        ln = raw.rstrip()
        txt = ln.strip()
        if not txt:
            continue

        m = MARKER.match(txt)
        if m:
            kind, body = m.group(1), m.group(2)
            colour, fill = BOX[kind]
            p = doc.add_paragraph()
            # Justify prose boxes, but left-align any that carry filenames in
            # code spans: justification stretches the spaces around a long
            # unbreakable token and leaves visible gaps.
            p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if "`" in body
                           else WD_ALIGN_PARAGRAPH.JUSTIFY)
            p.paragraph_format.left_indent = Cm(0.45)
            p.paragraph_format.right_indent = Cm(0.1)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.14
            shade(p, fill)
            border(p, "left", colour, size=18, space=8)
            write_runs(p, body, size=10,
                       colour=RGBColor.from_string(colour), mono=RGBColor.from_string(colour))
            continue

        if txt.startswith("# "):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(txt[2:])
            r.bold = True
            r.font.size = Pt(20)
            r.font.color.rgb = TEAL
            r.font.name = "Calibri"
            state["title_done"] = True
            continue

        if txt.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6) if state["title_done"] else Pt(18)
            p.paragraph_format.space_after = Pt(10)
            if not state["title_done"]:
                border(p, "bottom", "C8C8C0", size=6)
            r = p.add_run(txt[3:])
            r.bold = True
            if state["title_done"]:
                r.font.size = Pt(12.5)
                r.font.color.rgb = GREY
                r.italic = True
                state["title_done"] = False
            else:
                r.font.size = Pt(14)
                r.font.color.rgb = TEAL
            r.font.name = "Calibri"
            state["ordered"] = 0
            continue

        if txt.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.left_indent = Cm(0)
            r = p.add_run(txt[4:])
            r.bold = True
            r.font.size = Pt(11.5)
            r.font.color.rgb = RGBColor.from_string("A8551E")
            r.font.name = "Calibri"
            continue

        # the byline line, directly under the title block
        if "  |  " in txt and len(txt) < 120:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(12)
            border(p, "bottom", "C8C8C0", size=6)
            r = p.add_run(txt)
            r.font.size = Pt(9.5)
            r.italic = True
            r.font.color.rgb = GREY
            r.font.name = "Calibri"
            continue

        mo = re.match(r"^(\d+)\.\s+(.*)$", txt)
        if mo:
            state["ordered"] += 1
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.16
            r = p.add_run("%d.  " % state["ordered"])
            r.bold = True
            r.font.size = Pt(10.5)
            r.font.color.rgb = TEAL
            write_runs(p, mo.group(2))
            continue

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(7)
        p.paragraph_format.line_spacing = 1.18
        write_runs(p, txt)

    doc.save(out_path)

    chk = Document(out_path)
    ps = chk.paragraphs
    just = sum(1 for p in ps if p.alignment == WD_ALIGN_PARAGRAPH.JUSTIFY)
    print("saved %s" % out_path)
    print("paragraphs %d   justified %d" % (len(ps), just))
    boxes = sum(1 for p in ps
                if p._p.get_or_add_pPr().find(qn("w:shd")) is not None)
    print("colour-coded boxes %d" % boxes)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
