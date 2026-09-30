const fs = require('fs'); const path = require('path');
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, ImageRun, Header, Footer, PageNumber, AlignmentType, BorderStyle } = d;
const blocks = JSON.parse(fs.readFileSync(path.join(__dirname, 'idf_blocks.json'), 'utf8'));
const ROOT = path.join(__dirname, '..'); const CW = 10206;
function runs(t, size, bold0) {
  const out = []; let b = !!bold0, i = false, sub = false, mono = false;
  const re = /(<\/?(?:b|i|sub|font)[^>]*>)|([^<]+)/g; let m;
  while ((m = re.exec(t))) {
    if (m[1]) { const tag = m[1]; if (tag === '<b>') b = true; else if (tag === '</b>') b = !!bold0; else if (tag === '<i>') i = true; else if (tag === '</i>') i = false;
      else if (tag === '<sub>') sub = true; else if (tag === '</sub>') sub = false; else if (tag.startsWith('<font')) mono = true; else if (tag === '</font>') mono = false; }
    else out.push(new TextRun({ text: m[2].replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>'), bold: b, italics: i, subScript: sub, size, font: mono ? 'Courier New' : 'Arial' }));
  }
  return out;
}
const bd = { style: BorderStyle.SINGLE, size: 4, color: '999999' }; const borders = { top: bd, bottom: bd, left: bd, right: bd };
const out = [];
for (const b of blocks) {
  if (b[0] === 'p') {
    const k = b[1];
    out.push(new Paragraph({ spacing: { before: k === 'h' ? 200 : 40, after: k === 'h' ? 60 : 80 }, keepNext: k === 'h', children: runs(b[2], k === 'h' ? 22 : k === 's' ? 16 : 19, k === 'h') }));
  } else if (b[0] === 'tbl') {
    const rows = b[1], ws = b[2], tot = ws.reduce((a, c) => a + c, 0);
    const cw = ws.map(w => Math.round(w / tot * CW)); cw[cw.length - 1] += CW - cw.reduce((a, c) => a + c, 0);
    out.push(new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: cw, rows: rows.map((r, ri) => new TableRow({ tableHeader: b[3] && ri === 0, cantSplit: true,
      children: r.map((c, ci) => new TableCell({ width: { size: cw[ci], type: WidthType.DXA }, borders, margins: { top: 40, bottom: 40, left: 70, right: 70 },
        shading: b[3] && ri === 0 ? { fill: 'E8EEF5', type: ShadingType.CLEAR, color: 'auto' } : undefined,
        children: [new Paragraph({ children: runs(c, 15, b[3] && ri === 0) })] })) })) }));
    out.push(new Paragraph({ spacing: { after: 40 }, children: [] }));
  } else if (b[0] === 'img') {
    const p = b[1], wmm = b[2]; const data = fs.readFileSync(p);
    const w = data.readUInt32BE(16), h = data.readUInt32BE(20); const pw = Math.round(wmm * 3.7795);
    out.push(new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({ type: 'png', data, transformation: { width: pw, height: Math.round(pw * h / w) }, altText: { title: 'figure', description: 'experiment figure', name: path.basename(p) } })] }));
  }
}
const hdrTxt = (t, al) => new Paragraph({ alignment: al, children: [new TextRun({ text: t, size: 15, font: 'Arial' })] });
const doc = new Document({
  creator: 'Inventor(s) - to be completed', title: 'Invention Disclosure Format (IDF)-B - AmI-CC',
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1000, bottom: 850, left: 850, right: 850 } } },
    headers: { default: new Header({ children: [hdrTxt('©VIT IPR&TT CELL', AlignmentType.LEFT), hdrTxt('Invention Disclosure Format (IDF)-B', AlignmentType.CENTER), hdrTxt('Doc. No. 02-IPR-R003 | Issue No/Date 2/01.02.2024 | Amd. No/Date 0/00.00.0000', AlignmentType.RIGHT)] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ['Page ', PageNumber.CURRENT], size: 15, font: 'Arial' })] })] }) },
    children: out }] });
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(path.join(ROOT, 'Invention_Disclosure_Format_B_FILLED.docx'), buf); console.log('ok'); });
