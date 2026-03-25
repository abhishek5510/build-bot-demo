from pathlib import Path
from datetime import date

PAGE_W, PAGE_H = 595, 842


def esc(text: str) -> str:
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def draw_wrapped_text(cmds, x, y, text, size=10, leading=14, max_chars=90, color=(0.12, 0.14, 0.17)):
    words = text.split()
    line = ''
    lines = []
    for w in words:
        candidate = (line + ' ' + w).strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    r, g, b = color
    for i, ln in enumerate(lines):
        yy = y - i * leading
        cmds.append(f"BT /F1 {size} Tf {r:.3f} {g:.3f} {b:.3f} rg 1 0 0 1 {x} {yy} Tm ({esc(ln)}) Tj ET")
    return y - len(lines) * leading


def make_pdf(content_commands: list[str], out_path: Path):
    stream = '\n'.join(content_commands).encode('latin-1', errors='replace')

    objs = []
    objs.append('<< /Type /Catalog /Pages 2 0 R >>')
    objs.append('<< /Type /Pages /Kids [3 0 R] /Count 1 >>')
    objs.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>')
    objs.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    objs.append('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>')
    objs.append(f'<< /Length {len(stream)} >>\nstream\n{stream.decode("latin-1")}\nendstream')

    out = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for i, obj in enumerate(objs, start=1):
        offsets.append(len(out))
        out.extend(f'{i} 0 obj\n{obj}\nendobj\n'.encode('latin-1'))

    xref_start = len(out)
    out.extend(f'xref\n0 {len(objs)+1}\n'.encode('latin-1'))
    out.extend(b'0000000000 65535 f \n')
    for off in offsets[1:]:
        out.extend(f'{off:010d} 00000 n \n'.encode('latin-1'))

    out.extend(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF'.encode('latin-1'))
    out_path.write_bytes(out)


def floor_plan_pdf(path: Path):
    cmds = []
    # Background
    cmds.append('0.960 0.973 0.980 rg 0 0 595 842 re f')
    # Header
    cmds.append('0.063 0.145 0.231 rg 0 730 595 112 re f')
    cmds.append('BT /F2 28 Tf 1 1 1 rg 1 0 0 1 36 790 Tm (Concept Floor Design Pack) Tj ET')
    cmds.append('BT /F1 12 Tf 0.76 0.84 0.94 rg 1 0 0 1 36 768 Tm (30x40 East-facing residential concept | G+2 ready) Tj ET')
    cmds.append(f'BT /F1 10 Tf 0.76 0.84 0.94 rg 1 0 0 1 36 748 Tm (Generated on {date.today().isoformat()}) Tj ET')

    # Main plan card
    cmds.append('1 1 1 rg 28 330 539 372 re f')
    cmds.append('0.88 0.91 0.95 RG 1.5 w 28 330 539 372 re S')
    cmds.append('BT /F2 16 Tf 0.08 0.11 0.18 rg 1 0 0 1 44 676 Tm (Ground Floor Layout - Approx. 1200 sq.ft) Tj ET')

    # Plan canvas
    ox, oy, w, h = 44, 370, 505, 280
    cmds.append('0.97 0.98 0.99 rg 44 370 505 280 re f')
    cmds.append('0.58 0.63 0.72 RG 1 w 44 370 505 280 re S')

    # Rooms rectangles
    rooms = [
        ('Living', ox+8, oy+170, 200, 100),
        ('Dining', ox+210, oy+170, 120, 100),
        ('Kitchen', ox+332, oy+170, 165, 100),
        ('Bed 1', ox+8, oy+58, 170, 105),
        ('Bed 2', ox+180, oy+58, 150, 105),
        ('Study', ox+332, oy+58, 90, 105),
        ('Stair', ox+424, oy+58, 73, 105),
    ]
    for name, x, y, rw, rh in rooms:
        cmds.append('0.90 0.95 0.92 rg {:.1f} {:.1f} {:.1f} {:.1f} re f'.format(x, y, rw, rh))
        cmds.append('0.24 0.47 0.34 RG 0.8 w {:.1f} {:.1f} {:.1f} {:.1f} re S'.format(x, y, rw, rh))
        cmds.append(f'BT /F2 10 Tf 0.10 0.20 0.13 rg 1 0 0 1 {x+8:.1f} {y+rh/2:.1f} Tm ({esc(name)}) Tj ET')

    cmds.append('BT /F1 11 Tf 0.18 0.22 0.29 rg 1 0 0 1 44 340 Tm (Design intent: Cross-ventilation, larger living area, and natural light from East frontage.) Tj ET')

    y = 296
    cmds.append('1 1 1 rg 28 58 539 248 re f')
    cmds.append('0.88 0.91 0.95 RG 1.5 w 28 58 539 248 re S')
    cmds.append('BT /F2 15 Tf 0.08 0.11 0.18 rg 1 0 0 1 44 274 Tm (Floor Design Notes) Tj ET')
    points = [
        'First floor repeats utility core and adds family lounge + balcony facing East.',
        'Second floor reserves terrace garden and solar-ready utility deck.',
        'Window-to-wall ratio kept balanced for thermal comfort in warm climate zones.',
        'Stair and shaft alignment kept vertical to reduce structural complexity and MEP rerouting.'
    ]
    yy = 246
    for p in points:
        cmds.append('BT /F2 10 Tf 0.10 0.20 0.13 rg 1 0 0 1 46 {:.1f} Tm (•) Tj ET'.format(yy))
        yy = draw_wrapped_text(cmds, 60, yy, p, size=10, max_chars=78, leading=13)
        yy -= 4

    make_pdf(cmds, path)


def cost_sheet_pdf(path: Path):
    cmds = []
    cmds.append('0.958 0.970 0.986 rg 0 0 595 842 re f')
    cmds.append('0.102 0.247 0.373 rg 0 726 595 116 re f')
    cmds.append('BT /F2 28 Tf 1 1 1 rg 1 0 0 1 36 788 Tm (Construction Cost Sheet) Tj ET')
    cmds.append('BT /F1 12 Tf 0.83 0.90 0.97 rg 1 0 0 1 36 766 Tm (30x40 Plot | G+2 Premium Finish | Indicative Budget) Tj ET')
    cmds.append('BT /F1 10 Tf 0.83 0.90 0.97 rg 1 0 0 1 36 746 Tm (Benchmarked using publicly available 2025-2026 India market references.) Tj ET')

    cmds.append('1 1 1 rg 28 172 539 534 re f')
    cmds.append('0.80 0.86 0.94 RG 1.4 w 28 172 539 534 re S')

    cmds.append('0.89 0.94 0.99 rg 44 650 507 34 re f')
    cmds.append('BT /F2 12 Tf 0.09 0.18 0.30 rg 1 0 0 1 56 662 Tm (Category) Tj ET')
    cmds.append('BT /F2 12 Tf 0.09 0.18 0.30 rg 1 0 0 1 390 662 Tm (Amount (INR)) Tj ET')

    rows = [
        ('Structural RCC + steel', '₹48,00,000'),
        ('Masonry + plastering', '₹14,20,000'),
        ('Flooring + tiling', '₹10,40,000'),
        ('Electrical + plumbing + MEP', '₹9,40,000'),
        ('Doors/windows + glazing', '₹8,30,000'),
        ('Interior woodwork (core)', '₹17,80,000'),
        ('Paints + waterproofing', '₹6,60,000'),
        ('Contingency (5%)', '₹5,70,000'),
    ]

    y = 626
    for i, (k, v) in enumerate(rows):
        bg = '0.98 0.99 1' if i % 2 == 0 else '0.95 0.97 0.99'
        cmds.append(f'{bg} rg 44 {y-2} 507 30 re f')
        cmds.append(f'BT /F1 11 Tf 0.11 0.15 0.22 rg 1 0 0 1 56 {y+9} Tm ({esc(k)}) Tj ET')
        cmds.append(f'BT /F2 11 Tf 0.11 0.15 0.22 rg 1 0 0 1 404 {y+9} Tm ({esc(v)}) Tj ET')
        y -= 32

    cmds.append('0.86 0.95 0.89 rg 44 338 507 42 re f')
    cmds.append('0.47 0.72 0.54 RG 1 w 44 338 507 42 re S')
    cmds.append('BT /F2 15 Tf 0.10 0.35 0.17 rg 1 0 0 1 56 356 Tm (Estimated Total: ₹1.20 Cr - ₹1.40 Cr) Tj ET')

    cmds.append('BT /F2 13 Tf 0.09 0.18 0.30 rg 1 0 0 1 44 306 Tm (Assumptions) Tj ET')
    assumptions = [
        'Built-up area assumed near 3300-3600 sq.ft across G+2 levels.',
        'Rates vary by brand choice, soil condition, and approval scope.',
        'Land cost, statutory fees, and high-end bespoke interiors excluded.'
    ]
    yy = 286
    for a in assumptions:
        cmds.append('BT /F2 10 Tf 0.12 0.18 0.25 rg 1 0 0 1 46 {:.1f} Tm (•) Tj ET'.format(yy))
        yy = draw_wrapped_text(cmds, 60, yy, a, size=10, max_chars=80, leading=13)
        yy -= 3

    cmds.append('BT /F2 13 Tf 0.09 0.18 0.30 rg 1 0 0 1 44 198 Tm (Reference Snapshot) Tj ET')
    refs = [
        'MagicBricks / Housing.com market blogs for Bangalore residential construction ranges.',
        'Nobroker and contractor benchmark articles for material and labor split trends.',
        'Architectural planning references for 30x40 room programming and circulation.'
    ]
    yy = 178
    for r in refs:
        cmds.append('BT /F2 10 Tf 0.12 0.18 0.25 rg 1 0 0 1 46 {:.1f} Tm (•) Tj ET'.format(yy))
        yy = draw_wrapped_text(cmds, 60, yy, r, size=10, max_chars=80, leading=12)
        yy -= 2

    make_pdf(cmds, path)


if __name__ == '__main__':
    assets = Path('assets')
    assets.mkdir(exist_ok=True)
    floor_plan_pdf(assets / 'floor-plan.pdf')
    cost_sheet_pdf(assets / 'construction-cost-sheet.pdf')
    print('Generated redesigned PDFs in assets/.')
