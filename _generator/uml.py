"""Элементы диаграмм UML для листов Visio (координаты в мм)."""
import math

INK = '#1F2D3D'
FILL = '#FFFFFF'
UC_FILL = '#EAF1FB'
ST_FILL = '#FFF8E6'
ACT_FILL = '#EAF6EC'
FS = 8


# ------------------------------------------------------------ наконечники
def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    return dx / L, dy / L


def head(p, frm, tip, kind, size=3.2):
    ux, uy = _unit(frm, tip)
    nx, ny = -uy, ux
    tx, ty = tip
    if kind == 'tri':      # обобщение: незакрашенный треугольник
        bx, by = tx - ux * size * 1.2, ty - uy * size * 1.2
        pts = [(tx, ty), (bx + nx * size * 0.75, by + ny * size * 0.75), (bx - nx * size * 0.75, by - ny * size * 0.75)]
        p.poly(pts, closed=True, fill=FILL, line=INK, lw=0.9)
    elif kind in ('dia', 'dia_f'):  # агрегация / композиция
        m1 = (tx - ux * size, ty - uy * size)
        e = (tx - ux * size * 2, ty - uy * size * 2)
        pts = [(tx, ty), (m1[0] + nx * size * 0.6, m1[1] + ny * size * 0.6), e,
               (m1[0] - nx * size * 0.6, m1[1] - ny * size * 0.6)]
        p.poly(pts, closed=True, fill=INK if kind == 'dia_f' else FILL, line=INK, lw=0.9)


def line(p, pts, *, dash=False, end=None, begin=None, color=INK, lw=0.9):
    """end/begin: None | 'arrow' (закрашенная) | 'open' | 'tri' | 'dia' | 'dia_f'"""
    ea = {'arrow': 'filled', 'open': 'open'}.get(end)
    ba = {'arrow': 'filled', 'open': 'open'}.get(begin)
    p.poly(pts, dash=dash, end_arrow=ea, begin_arrow=ba, line=color, lw=lw, arrow_size=2)
    if end in ('tri', 'dia', 'dia_f'):
        head(p, pts[-2], pts[-1], end)
    if begin in ('tri', 'dia', 'dia_f'):
        head(p, pts[1], pts[0], begin)


def label(p, x, y, t, size=7.5, w=None, align='l', italic=False, bold=False, color=INK):
    lines = t.split('\n')
    w = w or max(len(l) for l in lines) * size * 0.2 + 3
    h = len(lines) * size * 0.43 + 1.4
    if align == 'c':
        x -= w / 2
    elif align == 'r':
        x -= w
    p.text(x, y, w, h, t, size=size, align=align, italic=italic, bold=bold, color=color)
    return w, h


# ------------------------------------------------------------ прецеденты
def actor(p, cx, y, name, h=20):
    r = h * 0.13
    hy = y + r
    body = [[('E', cx, hy, r, r)],
            [('M', cx, y + 2 * r), ('L', cx, y + h * 0.62)],
            [('M', cx - h * 0.25, y + h * 0.38), ('L', cx + h * 0.25, y + h * 0.38)],
            [('M', cx, y + h * 0.62), ('L', cx - h * 0.22, y + h)],
            [('M', cx, y + h * 0.62), ('L', cx + h * 0.22, y + h)]]
    p.multi(cx - h * 0.25, y, h * 0.5, h, body, '', fill=FILL, line=INK, lw=1.0, name='Актёр')
    label(p, cx, y + h + 0.5, name, size=8, align='c', bold=True)
    return (cx, y + h * 0.45)


def usecase(p, cx, cy, text, w=42, h=14):
    p.ellipse(cx - w / 2, cy - h / 2, w, h, text, fill=UC_FILL, line=INK, lw=0.9, size=7.5)
    return (cx, cy, w, h)


def ell_pt(uc, toward):
    """точка на эллипсе прецедента в направлении toward"""
    cx, cy, w, h = uc
    dx, dy = toward[0] - cx, toward[1] - cy
    a, b = w / 2, h / 2
    t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2) if (dx or dy) else 0
    return (cx + dx * t, cy + dy * t)


def uc_link(p, a, b, kind='assoc', text=None):
    """a,b — прецеденты (кортеж из usecase) или точки"""
    pa = ell_pt(a, b[:2]) if len(a) == 4 else a
    pb = ell_pt(b, a[:2]) if len(b) == 4 else b
    if kind == 'assoc':
        line(p, [pa, pb])
    elif kind in ('include', 'extend'):
        line(p, [pa, pb], dash=True, end='open')
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        label(p, mx, my - 3.8, text or f'«{kind}»', size=7, align='c', italic=True)
    elif kind == 'gen':
        line(p, [pa, pb], end='tri')


def note(p, x, y, w, h, text):
    c = 3
    p.multi(x, y, w, h, [[('M', x, y), ('L', x + w - c, y), ('L', x + w, y + c), ('L', x + w, y + h),
                          ('L', x, y + h), ('L', x, y), 'Z'], [('M', x + w - c, y), ('L', x + w - c, y + c),
                                                               ('L', x + w, y + c)]],
            text, fill='#FFFDE7', line=INK, lw=0.75, size=7, align='l')


# ------------------------------------------------------------ классы
def uclass(p, x, y, w, name, attrs, ops, stereo=None, abstract=False, size=7):
    lh = size * 0.43
    hn = (2 if stereo else 1) * lh + 3
    ha = max(1, len(attrs)) * lh + 2
    ho = max(1, len(ops)) * lh + 2
    h = hn + ha + ho
    p.rect(x, y, w, h, '', fill=FILL, line=INK, lw=1.0)
    p.rect(x, y, w, hn, '', fill='#E8EEF7', line=INK, lw=1.0)
    t = (f'«{stereo}»\n' if stereo else '') + name
    p.text(x, y, w, hn, t, size=size + 0.5, bold=True, italic=abstract)
    p.line(x, y + hn + ha, x + w, y + hn + ha, line=INK, lw=0.75)
    p.text(x + 0.5, y + hn + 0.5, w - 1, ha - 1, '\n'.join(attrs), size=size, align='l', valign='t', margin=0.5)
    p.text(x + 0.5, y + hn + ha + 0.5, w - 1, ho - 1, '\n'.join(ops), size=size, align='l', valign='t', margin=0.5)
    return (x, y, w, h)


def mult(p, pt, t, dx=1.2, dy=-4.2):
    label(p, pt[0] + dx, pt[1] + dy, t, size=7)


# ------------------------------------------------------------ состояния
def state(p, x, y, w, name, actions=(), h=None, fill=ST_FILL, size=7.5):
    lh = size * 0.43
    hn = lh + 3
    ha = len(actions) * lh + (2 if actions else 0)
    h = h or (hn + ha + (0 if actions else 2))
    p.rrect(x, y, w, h, '', r=3, fill=fill, line=INK, lw=1.0)
    if actions:
        p.text(x, y, w, hn, name, size=size, bold=True)
        p.line(x, y + hn, x + w, y + hn, line=INK, lw=0.6)
        p.text(x + 1, y + hn, w - 2, ha, '\n'.join(actions), size=size - 0.5, align='l', valign='t', margin=0.5)
    else:
        p.text(x, y, w, h, name, size=size, bold=True)
    return (x, y, w, h)


def composite(p, x, y, w, h, name):
    p.rrect(x, y, w, h, '', r=4, fill='#FFFCF3', line=INK, lw=1.1)
    p.text(x + 2, y + 1, w - 4, 5, name, size=8, bold=True, align='l')
    p.line(x, y + 6.5, x + w, y + 6.5, line=INK, lw=0.6)
    return (x, y, w, h)


def initial(p, cx, cy, r=2.2):
    p.ellipse(cx - r, cy - r, 2 * r, 2 * r, '', fill=INK, line=INK)


def final(p, cx, cy, r=2.8):
    p.ellipse(cx - r, cy - r, 2 * r, 2 * r, '', fill=FILL, line=INK, lw=1.0)
    p.ellipse(cx - r * 0.6, cy - r * 0.6, 1.2 * r, 1.2 * r, '', fill=INK, line=INK)


def trans(p, pts, text=None, at=None, align='l'):
    line(p, pts, end='open', lw=0.9)
    if text:
        if at is None:
            a, b = pts[0], pts[1]
            at = ((a[0] + b[0]) / 2 + 1, (a[1] + b[1]) / 2 - 4)
        label(p, at[0], at[1], text, size=7, align=align)


# ------------------------------------------------------------ деятельность
def action(p, cx, cy, text, w=40, h=10):
    p.rrect(cx - w / 2, cy - h / 2, w, h, text, r=h / 2.2, fill=ACT_FILL, line=INK, lw=1.0, size=7.5)
    return (cx - w / 2, cy - h / 2, w, h)


def decision(p, cx, cy, s=5):
    p.poly([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], closed=True, fill=FILL, line=INK, lw=1.0)
    return (cx, cy, s)


def bar(p, cx, cy, w=40, horizontal=True):
    if horizontal:
        p.rect(cx - w / 2, cy - 0.9, w, 1.8, '', fill=INK, line=INK)
    else:
        p.rect(cx - 0.9, cy - w / 2, 1.8, w, '', fill=INK, line=INK)


def lanes(p, x, y, widths, h, names):
    cx = x
    for w, n in zip(widths, names):
        p.rect(cx, y, w, h, '', nofill=True, line=INK, lw=1.0)
        p.rect(cx, y, w, 8, n, fill='#E8EEF7', line=INK, lw=1.0, size=8.5, bold=True)
        cx += w


# ------------------------------------------------------------ последовательности
def lifeline(p, cx, y, name, y_end, w=None, is_actor=False):
    if is_actor:
        actor(p, cx, y, name, h=13)
        top = y + 18
    else:
        w = w or max(26, len(name) * 1.6 + 4)
        p.rect(cx - w / 2, y, w, 9, name, fill='#E8EEF7', line=INK, lw=1.0, size=7.5, under=True)
        top = y + 9
    p.line(cx, top, cx, y_end, dash=True, line='#6B7785', lw=0.75)
    return cx


def activation(p, cx, y1, y2, dx=0):
    p.rect(cx - 1.6 + dx, y1, 3.2, y2 - y1, '', fill=FILL, line=INK, lw=0.8)


def msg(p, x1, x2, y, text, ret=False, num=None):
    t = (f'{num}: ' if num else '') + text
    if ret:
        line(p, [(x1, y), (x2, y)], dash=True, end='open', lw=0.8)
    else:
        line(p, [(x1, y), (x2, y)], end='arrow', lw=0.9)
    lx = min(x1, x2) + (5 if x2 < x1 else 2.5)
    label(p, lx, y - 4.0, t, size=6.8)


def self_msg(p, x, y, text, num=None, dy=5):
    t = (f'{num}: ' if num else '') + text
    line(p, [(x + 1.6, y), (x + 8, y), (x + 8, y + dy), (x + 3.2, y + dy)], end='arrow', lw=0.9)
    if x > 235:
        label(p, x - 2.5, y - 4.2, t, size=6.8, align='r')
    else:
        label(p, x + 9, y - 1.5, t, size=6.8)


def fragment(p, x, y, w, h, op, guard=None, splits=()):
    if x + w > 291:
        w = 291 - x
    p.rect(x, y, w, h, '', nofill=True, line='#4A5A6A', lw=0.9)
    tw = len(op) * 1.6 + 5
    p.poly([(x, y), (x + tw, y), (x + tw, y + 3.5), (x + tw - 2, y + 5.5), (x, y + 5.5), (x, y)], closed=True,
           fill='#F2F4F7', line='#4A5A6A', lw=0.8)
    p.text(x, y, tw - 1, 5.5, op, size=7.5, bold=True)
    if guard:
        label(p, x + tw + 1, y + 0.5, guard, size=7, italic=True)
    for sy, g in splits:
        p.line(x, sy, x + w, sy, dash=True, line='#4A5A6A', lw=0.8)
        if g:
            label(p, x + 2, sy + 0.5, g, size=7, italic=True)


def title(p, t, x=10, y=4):
    label(p, x, y, t, size=9, bold=True)
