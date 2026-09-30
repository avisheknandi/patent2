"""Export the IDF content blocks (from build_idf.py) to JSON for the .docx builder."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "build_idf.py")).read()
src = src[:src.index("SimpleDocTemplate(os.path.join(ROOT, \"Invention")]
src = src.replace("P = lambda t, st=B: Paragraph(t, st)", "P = lambda t, st=B: ('p', 'h' if st is H else 's' if st is S else 'b', t)")
src = src.replace("def tbl(rows, widths, head=True, fs=7.3):", "def tbl(rows, widths, head=True, fs=7.3):\n    return ('tbl', [[str(c) for c in r] for r in rows], [float(w/mm) for w in widths], head)\ndef _old(rows, widths, head=True, fs=7.3):")
src = src.replace("KeepTogether(", "(lambda x: ('keep', x))(").replace("Image(", "(lambda p,width,height: ('img', p, float(width/mm)))(")
src = src.replace("Spacer(1, 6)", "('sp',)").replace("Spacer(1, 10)", "('sp',)")
ns = {"__file__": os.path.join(here, "build_idf.py")}; exec(src, ns)
def flat(x):
    out = []
    for i in x:
        if isinstance(i, list): out += flat(i)
        elif i[0] == 'keep': out += flat(i[1])
        elif i[0] != 'sp': out.append(i)
    return out
json.dump(flat(ns['st']), open(os.path.join(here, "idf_blocks.json"), "w"), ensure_ascii=False)
