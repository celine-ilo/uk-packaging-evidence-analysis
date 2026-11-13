"""Assemble the per-figure notes into one Figure Notes document.

Each figure folder holds its own notes file — the single source of truth for
that figure. This script reads them all, in figure-number order, and writes the
combined document. The combined document is generated and should never be
edited by hand: edit the per-figure file and run this again.

Either format works per folder, and they can be mixed:

    Figure 1/notes.md      markdown, renders on GitHub, diffs cleanly in git
    Figure 1/notes.docx    Word, if that is easier to write in

Folders are read in natural numeric order, so "Figure 2" sorts before
"Figure 10" even without zero padding.

Usage:
    python3 build_figure_notes.py                 # current folder
    python3 build_figure_notes.py <folder> <out.docx>
"""
import os
import re
import sys

HEADER = "_header.md"
NOTE_NAMES = ("notes.md", "notes.docx", "note.md", "note.docx")
FIGURE_DIR = re.compile(r"^figure[\s_-]*0*(\d+)", re.I)


def figure_folders(root):
    """Every folder whose name starts with 'figure', in numeric order."""
    out = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        m = FIGURE_DIR.match(name)
        if m:
            out.append((int(m.group(1)), name, path))
    out.sort()
    return out


def read_md(path):
    return open(path, encoding="utf-8").read().rstrip()


def read_docx(path):
    """Pull a Word file back to the markdown conventions this project uses."""
    from docx import Document
    doc = Document(path)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        style = (p.style.name or "").lower()
        if "heading 1" in style:
            lines.append("# " + t)
        elif "heading 2" in style:
            lines.append("## " + t)
        elif "heading 3" in style:
            lines.append("### " + t)
        else:
            lines.append(t)
    return "\n\n".join(lines)


def read_note(folder):
    for name in NOTE_NAMES:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            text = read_docx(path) if path.endswith(".docx") else read_md(path)
            return name, text
    return None, None


def main(root=".", out=None):
    root = os.path.abspath(root)
    out = out or os.path.join(root, "Figure_Notes.docx")

    parts = []
    header = os.path.join(root, HEADER)
    if os.path.exists(header):
        parts.append(read_md(header))
        print("header   %s" % HEADER)
    else:
        print("header   none found (%s) — carrying on without one" % HEADER)

    folders = figure_folders(root)
    if not folders:
        print("\nNo figure folders found in %s" % root)
        print("Expected folders named like 'Figure 1' or 'figure-01'.")
        sys.exit(1)

    missing = []
    for num, name, path in folders:
        fname, text = read_note(path)
        if text is None:
            missing.append(name)
            print("figure %-2d %-40s NO NOTES FILE" % (num, name))
            continue
        parts.append(text)
        words = len(text.split())
        print("figure %-2d %-40s %s  %4d words" % (num, name, fname, words))

    md = "\n\n".join(parts) + "\n"
    tmp = os.path.join(root, "_assembled.md")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(md)

    here = os.path.dirname(os.path.abspath(__file__))
    builder = os.path.join(here, "build_workbook.py")
    if not os.path.exists(builder):
        print("\nWrote %s" % tmp)
        print("build_workbook.py not found beside this script, so the Word "
              "file was not built. Keep the two scripts together.")
        return

    sys.path.insert(0, here)
    import build_workbook
    build_workbook.main(tmp, out)
    os.remove(tmp)

    print("\nassembled %d figure(s) into %s" % (len(folders) - len(missing), out))
    if missing:
        print("still to write: %s" % ", ".join(missing))
    print("Edit the per-figure notes files, never %s — it is overwritten "
          "each time this runs." % os.path.basename(out))


if __name__ == "__main__":
    main(*(sys.argv[1:3] or ["."]))
