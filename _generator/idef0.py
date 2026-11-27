"""Построение диаграмм IDEF0 (контекстная, декомпозиция, дерево узлов) на листах Visio."""
import textwrap

COL = {'I': '#2E7D32', 'C': '#C62828', 'O': '#1565C0', 'M': '#6A1B9A'}
FONT = 7.5
FR = (6, 6, 291, 204)  # рамка листа
TOP_BAR = 14            # высота верхней полосы бланка
BOT_BAR = 12            # высота нижней полосы бланка


def wrap(t, w):
    lines = []
    for part in t.split('\n'):
        lines += textwrap.wrap(part, w) or ['']
    return '\n'.join(lines)


def text_size(t, size=FONT):
    lines = t.split('\n')
    cw = size * 0.205  # ширина символа, мм
    w = max(len(l) for l in lines) * cw + 3
    h = len(lines) * size * 0.43 + 1.6
    return w, h


def frame(p, node, title, number, author='Тестов М. О.', project='', context='', date='27.11.2026'):
    x0, y0, x1, y1 = FR
    p.rect(x0, y0, x1 - x0, y1 - y0, nofill=True, lw=1.0, name='Блок заголовка')
    # верхняя полоса
    p.line(x0, y0 + TOP_BAR, x1, y0 + TOP_BAR, lw=0.75)
    cols = [x0, x0 + 28, x0 + 120, x0 + 150, x0 + 185, x0 + 220, x0 + 250, x1]
    for c in cols[1:-1]:
        p.line(c, y0, c, y0 + TOP_BAR, lw=0.5)
    t = 6.5
    p.text(cols[0], y0, cols[1] - cols[0], TOP_BAR, 'ИСПОЛЬЗУЕТСЯ В:', size=t, align='l', valign='t')
    p.text(cols[1], y0, cols[2] - cols[1], TOP_BAR / 2, f'АВТОР: {author}', size=t, align='l', valign='t')
    p.text(cols[1], y0 + TOP_BAR / 2, cols[2] - cols[1], TOP_BAR / 2, f'ПРОЕКТ: {project}', size=t, align='l', valign='t')
    p.text(cols[2], y0, cols[3] - cols[2], TOP_BAR / 2, f'ДАТА: {date}', size=t, align='l', valign='t')
    p.text(cols[2], y0 + TOP_BAR / 2, cols[3] - cols[2], TOP_BAR / 2, 'ВЕРСИЯ: 1', size=t, align='l', valign='t')
    p.text(cols[3], y0, cols[4] - cols[3], TOP_BAR, '■ РАБОЧАЯ ВЕРСИЯ\n□ ЭСКИЗ\n□ РЕКОМЕНДОВАНО\n□ ПУБЛИКАЦИЯ',
           size=5.5, align='l', valign='t')
    p.text(cols[4], y0, cols[5] - cols[4], TOP_BAR, 'ЧИТАТЕЛЬ:', size=t, align='l', valign='t')
    p.text(cols[5], y0, cols[6] - cols[5], TOP_BAR, 'ДАТА:', size=t, align='l', valign='t')
    p.text(cols[6], y0, cols[7] - cols[6], TOP_BAR, f'КОНТЕКСТ:\n{context}', size=t, align='l', valign='t')
    # нижняя полоса
    yb = y1 - BOT_BAR
    p.line(x0, yb, x1, yb, lw=0.75)
    p.line(x0 + 40, yb, x0 + 40, y1, lw=0.5)
    p.line(x1 - 45, yb, x1 - 45, y1, lw=0.5)
    p.text(x0, yb, 40, BOT_BAR, f'УЗЕЛ: {node}', size=9, bold=True, align='l')
    p.text(x0 + 40, yb, x1 - x0 - 85, BOT_BAR, f'НАЗВАНИЕ: {title}', size=10, bold=True)
    p.text(x1 - 45, yb, 45, BOT_BAR, f'НОМЕР: {number}', size=9, bold=True, align='l')


def box(p, x, y, w, h, name, num, decomposed=False):
    p.rect(x, y, w, h, '', lw=1.25, fill='#FFFFFF', name=num)
    p.text(x + 1, y + 1, w - 2, h - 6, wrap(name, int(w / 1.75)), size=8.5, bold=True)
    p.text(x + w - 14, y + h - 5, 13.5, 4.5, num, size=8, bold=True, align='r')
    if decomposed:  # признак наличия дочерней диаграммы
        p.text(x + w - 1, y + h, 12, 4, num.replace('A', 'A') + 'D' if False else '', size=6)


LABEL_AT = {}


def label(p, x, y, t, color, align='l', width=None):
    w, h = text_size(t)
    key = t.replace('\n', ' ')
    if key in LABEL_AT:
        x, y = LABEL_AT.pop(key)
        align = 'l'
    if width:
        w = width
    if align == 'r':
        x -= w
    elif align == 'c':
        x -= w / 2
    p.text(x, y, w, h, t, size=FONT, color=color, align=align)
    return h


def arrow(p, pts, color, lw=1.25):
    p.poly(pts, end_arrow='filled', line=color, lw=lw)


# ---------------------------------------------------------------- контекст
def context(p, name, num, inputs, controls, outputs, mechs, purpose, viewpoint,
            node='A-0', title=None, project='', number=1):
    frame(p, node, title or name, number, project=project, context='ВЕРХНИЙ')
    bw = max(72, 27 * max(len(controls), len(mechs)))
    bh = max(42, 14 * max(len(inputs), len(outputs)))
    bx, by = 148.5 - bw / 2, 110 - bh / 2
    box(p, bx, by, bw, bh, name, 'A0')
    X0, Y0, X1, Y1 = FR[0], FR[1] + TOP_BAR, FR[2], FR[3] - BOT_BAR

    def slots(n, a, b):
        return [a + (b - a) * (i + 1) / (n + 1) for i in range(n)]

    for t, y in zip(inputs, slots(len(inputs), by, by + bh)):
        arrow(p, [(X0 + 2, y), (bx, y)], COL['I'])
        lab = wrap(t, 26)
        _, h = text_size(lab)
        label(p, X0 + 4, y - h - 0.5, lab, COL['I'])
    for t, x in zip(controls, slots(len(controls), bx, bx + bw)):
        arrow(p, [(x, Y0 + 2), (x, by)], COL['C'])
        lab = wrap(t, 16)
        label(p, x + 1, Y0 + 6 + (controls.index(t) % 2) * 12, lab, COL['C'])
    for t, y in zip(outputs, slots(len(outputs), by, by + bh)):
        arrow(p, [(bx + bw, y), (X1 - 2, y)], COL['O'])
        lab = wrap(t, 26)
        _, h = text_size(lab)
        label(p, X1 - 4, y - h - 0.5, lab, COL['O'], align='r')
    for t, x in zip(mechs, slots(len(mechs), bx, bx + bw)):
        arrow(p, [(x, Y1 - 2), (x, by + bh)], COL['M'])
        lab = wrap(t, 16)
        label(p, x + 1, Y1 - 22 + (mechs.index(t) % 2) * 10, lab, COL['M'])
    pv = wrap('Цель: ' + purpose, 62) + '\n' + wrap('Точка зрения: ' + viewpoint, 62)
    ph = text_size(pv, 7)[1] + 2
    p.text(X0 + 4, Y1 - ph - 3, 92, ph, pv,
           size=7, align='l', valign='m', line='#808080', noline=False, lw=0.5, margin=1)


# ------------------------------------------------------------ декомпозиция
class Decomp:
    """boxes: [(имя, номер)]; arrows: dict(t=метка, src=..., dst=...)
    src: 'I' | 'C' | 'M' (граничные) или (i, 'O') — выход блока i
    dst: 'O' (граница) или (j, 'I'|'C'|'M'), допускается список (ветвление)"""

    def __init__(self, p, node, title, boxes, arrows, number=2, project='', parent='',
                 bw=None, bh=26, left=40, right=40, top=32, bottom=26, decomposed=()):
        self.p = p
        self.boxes = boxes
        n = len(boxes)
        frame(p, node, title, number, project=project, context=parent)
        X0, Y0, X1, Y1 = FR[0], FR[1] + TOP_BAR, FR[2], FR[3] - BOT_BAR
        self.X0, self.Y0, self.X1, self.Y1 = X0, Y0, X1, Y1
        aw = X1 - X0 - left - right
        bw = bw or min(44, aw / (n + (n - 1) * 0.45))
        gx = (aw - n * bw) / (n - 1)
        ah = Y1 - Y0 - top - bottom
        gy = (ah - n * bh) / (n - 1)
        self.B = []
        for i in range(n):
            x = X0 + left + i * (bw + gx)
            y = Y0 + top + i * (bh + gy)
            self.B.append((x, y, bw, bh))
        self.gx, self.gy = gx, gy
        # нормализация стрелок
        self.A = []
        for a in arrows:
            a = dict(a)
            if not isinstance(a['dst'], list):
                a['dst'] = [a['dst']]
            if not isinstance(a.get('src'), list):
                a['src'] = [a['src']]
            self.A.append(a)
        # распределение портов
        ports = {}
        for k, a in enumerate(self.A):
            for s in a['src']:
                if isinstance(s, tuple):
                    ports.setdefault((s[0], 'O'), []).append(k)
            for d in a['dst']:
                if isinstance(d, tuple):
                    ports.setdefault(d, []).append(k)
        self.port = {}
        for (i, side), ks in ports.items():
            x, y, w, h = self.B[i]
            m = len(ks)
            for q, k in enumerate(ks):
                if side in ('I', 'O'):
                    v = y + h * (q + 1) / (m + 1)
                else:
                    v = x + w * (q + 1) / (m + 1)
                self.port[(i, side, k)] = v
        self.xl = {}  # занятые вертикальные дорожки в промежутках
        self.yl = {}
        for i, (nm, num) in enumerate(boxes):
            x, y, w, h = self.B[i]
            box(p, x, y, w, h, nm, num)
            if num in decomposed:
                p.text(x + w - 2, y + h + 0.3, 14, 4, f'{num}', size=6, align='l', italic=True)
        for k, a in enumerate(self.A):
            if 'at' in a:
                LABEL_AT[wrap(a['t'], a.get('lw', 34)).replace('\n', ' ')] = a['at']
            self._draw(k, a)

    # дорожки
    def lane_x(self, gap):  # gap = i: промежуток справа от блока i (-1 — левее первого)
        used = self.xl.setdefault(gap, 0)
        self.xl[gap] = used + 1
        if gap < 0:
            base = self.B[0][0] - 6
            return base - used * 4
        x, y, w, h = self.B[gap]
        return x + w + 5 + used * 4

    def lane_y(self, gap, above=False):  # промежуток под блоком gap
        key = (gap, above)
        used = self.yl.setdefault(key, 0)
        self.yl[key] = used + 1
        x, y, w, h = self.B[gap]
        if above:
            return y - 4 - used * 3.5
        return y + h + 4 + used * 3.5

    def _draw(self, k, a):
        p, t = self.p, a['t']
        off = a.get('lab', (0, 0))
        lw = a.get('lw', 34)
        dsts, srcs = a['dst'], a['src']
        # ---------- граничные источники
        if srcs[0] in ('I', 'C', 'M'):
            kind = srcs[0]
            col = COL[kind]
            lab = wrap(t, lw)
            if kind == 'I':
                ys = [self.port[(d[0], d[1], k)] for d in dsts]
                if len(dsts) == 1:
                    d = dsts[0]
                    y = ys[0]
                    tx = self._target_x_in(d, k)
                    self._enter(d, k, col, start=(self.X0 + 1, y))
                    _, h = text_size(lab)
                    label(p, self.X0 + 3 + off[0], y - h - 0.4 + off[1], lab, col)
                else:
                    bus = self.lane_x(-1)
                    y0 = min(ys)
                    p.line(self.X0 + 1, y0, bus, y0, line=col, lw=1.25)
                    p.line(bus, y0, bus, max(ys), line=col, lw=1.25)
                    for d, y in zip(dsts, ys):
                        self._enter(d, k, col, start=(bus, y), branch=True)
                    _, h = text_size(lab)
                    label(p, self.X0 + 3 + off[0], y0 - h - 0.4 + off[1], lab, col)
            elif kind == 'C':
                xs = [self.port[(d[0], d[1], k)] for d in dsts]
                if len(dsts) == 1:
                    x = xs[0]
                    self._enter(dsts[0], k, col, start=(x, self.Y0 + 1))
                    if a.get('side') == 'l':
                        label(p, x - 1 + off[0], self.Y0 + 2 + off[1], lab, col, align='r')
                    else:
                        label(p, x + 1 + off[0], self.Y0 + 2 + off[1], lab, col)
                else:
                    ybus = self.Y0 + a.get('bus', 10)
                    x0 = a.get('trunk', min(xs))
                    p.line(x0, self.Y0 + 1, x0, ybus, line=col, lw=1.25)
                    p.line(min(xs + [x0]), ybus, max(xs + [x0]), ybus, line=col, lw=1.25)
                    for d, x in zip(dsts, xs):
                        self._enter(d, k, col, start=(x, ybus), branch=True)
                    if a.get('side') == 'l':
                        label(p, x0 - 1 + off[0], self.Y0 + 1.5 + off[1], lab, col, align='r')
                    else:
                        label(p, x0 + 1 + off[0], self.Y0 + 1.5 + off[1], lab, col)
            else:  # M
                xs = [self.port[(d[0], d[1], k)] for d in dsts]
                if len(dsts) == 1:
                    x = xs[0]
                    self._enter(dsts[0], k, col, start=(x, self.Y1 - 1))
                    _, h = text_size(lab)
                    if a.get('side') == 'l':
                        label(p, x - 1 + off[0], self.Y1 - h - 1.5 + off[1], lab, col, align='r')
                    else:
                        label(p, x + 1 + off[0], self.Y1 - h - 1.5 + off[1], lab, col)
                else:
                    ybus = self.Y1 - a.get('bus', 9)
                    x0 = a.get('trunk', max(xs))
                    p.line(x0, self.Y1 - 1, x0, ybus, line=col, lw=1.25)
                    p.line(min(xs + [x0]), ybus, max(xs + [x0]), ybus, line=col, lw=1.25)
                    for d, x in zip(dsts, xs):
                        self._enter(d, k, col, start=(x, ybus), branch=True)
                    _, h = text_size(lab)
                    if a.get('side') == 'l':
                        label(p, x0 - 1 + off[0], self.Y1 - h - 1.5 + off[1], lab, col, align='r')
                    else:
                        label(p, x0 + 1 + off[0], self.Y1 - h - 1.5 + off[1], lab, col)
            return
        # ---------- источник — выход блока
        if dsts == ['O']:
            col = COL['O']
            ys = []
            for s in srcs:
                x, y, w, h = self.B[s[0]]
                ys.append((x + w, self.port[(s[0], 'O', k)]))
            lab = wrap(t, lw)
            if len(srcs) == 1:
                (xa, ya) = ys[0]
                arrow(p, [(xa, ya), (self.X1 - 1, ya)], col)
                _, h = text_size(lab)
                label(p, self.X1 - 3 + off[0], ya - h - 0.4 + off[1], lab, col, align='r')
            else:  # слияние
                bus = self.X1 - a.get('bus', 22)
                ymax = max(y for _, y in ys)
                for xa, ya in ys:
                    p.line(xa, ya, bus, ya, line=col, lw=1.25)
                p.line(bus, min(y for _, y in ys), bus, ymax, line=col, lw=1.25)
                arrow(p, [(bus, ymax), (self.X1 - 1, ymax)], col)
                _, h = text_size(lab)
                label(p, self.X1 - 3 + off[0], ymax - h - 0.4 + off[1], lab, col, align='r')
            return
        # ---------- внутренняя стрелка
        s = srcs[0]
        i = s[0]
        xi, yi, wi, hi = self.B[i]
        ya = self.port[(i, 'O', k)]
        start = (xi + wi, ya)
        for d in dsts:
            col = COL[d[1]]
            j, side = d
            pts = self._route(i, start, d, k)
            arrow(p, pts, col)
        lab = wrap(t, lw)
        w, h = text_size(lab)
        if dsts[0][0] <= i:  # обратная связь — подпись на петле
            (ax, ay), (bx, by) = pts[2], pts[3]
            cx = (ax + bx) / 2
            if dsts[0][1] == 'C':
                label(p, cx - w / 2 + off[0], ay - h - 0.4 + off[1], lab, COL[dsts[0][1]])
            else:
                label(p, cx - w / 2 + off[0], ay + 0.4 + off[1], lab, COL[dsts[0][1]])
            return
        label(p, start[0] + 1.5 + off[0], ya - h - 0.4 + off[1], lab, COL[dsts[0][1]])

    def _target_x_in(self, d, k):
        return self.B[d[0]][0]

    def _enter(self, d, k, col, start, branch=False):
        j, side = d
        x, y, w, h = self.B[j]
        v = self.port[(j, side, k)]
        if side == 'I':
            pts = [start, (x, v)] if abs(start[1] - v) < 0.01 else [start, (start[0], v), (x, v)]
        elif side == 'C':
            pts = [start, (v, y)] if abs(start[0] - v) < 0.01 else [start, (v, start[1]), (v, y)]
        else:
            pts = [start, (v, y + h)] if abs(start[0] - v) < 0.01 else [start, (v, start[1]), (v, y + h)]
        arrow(self.p, pts, col)

    def _route(self, i, start, d, k):
        j, side = d
        x, y, w, h = self.B[j]
        v = self.port[(j, side, k)]
        sx, sy = start
        if j > i:
            if side == 'I':
                lx = self.lane_x(i)
                return [start, (lx, sy), (lx, v), (x, v)]
            if side == 'C':
                return [start, (v, sy), (v, y)]
            # механизм
            lx = self.lane_x(i)
            ly = self.lane_y(j)
            return [start, (lx, sy), (lx, ly), (v, ly), (v, y + h)]
        # обратные связи (j <= i)
        xr = self.lane_x(i)
        if side == 'I':
            yb = self.lane_y(i)
            xl = self.lane_x(j - 1)
            if j - 1 >= 0:
                # дорожка слева от блока j: правее блока j-1
                pass
            return [start, (xr, sy), (xr, yb), (xl, yb), (xl, v), (x, v)]
        if side == 'C':
            yt = self.lane_y(j, above=True)
            return [start, (xr, sy), (xr, yt), (v, yt), (v, y)]
        yb = self.lane_y(i)
        return [start, (xr, sy), (xr, yb), (v, yb), (v, y + h)]


# ------------------------------------------------------------ дерево узлов
def node_tree(p, title, root, children, number=99, project=''):
    """root: (номер, имя); children: [(номер, имя, [(номер, имя), ...])]"""
    frame(p, 'A0', title, number, project=project, context='Дерево узлов')
    X0, Y0, X1, Y1 = FR[0], FR[1] + TOP_BAR, FR[2], FR[3] - BOT_BAR
    n = len(children)
    bw, bh = 52, 15
    rx = (X0 + X1) / 2 - bw / 2
    ry = Y0 + 8
    p.rect(rx, ry, bw, bh, f'{root[0]}\n{root[1]}', size=8, bold=True, lw=1.25)
    colw = (X1 - X0 - 10) / n
    cbw = min(52, colw - 6)
    ybus = ry + bh + 7
    xs = [X0 + 5 + colw * (q + 0.5) for q in range(n)]
    p.line(rx + bw / 2, ry + bh, rx + bw / 2, ybus, lw=1)
    p.line(xs[0], ybus, xs[-1], ybus, lw=1)
    cy = ybus + 7
    for q, (num, nm, sub) in enumerate(children):
        cx = xs[q]
        p.line(cx, ybus, cx, cy, lw=1)
        p.rect(cx - cbw / 2, cy, cbw, bh + 3, f'{num}\n{nm}', size=7.5, bold=True, lw=1.1)
        if sub:
            sx = cx - cbw / 2 + 4
            p.line(sx, cy + bh + 3, sx, cy + bh + 3 + 8 + (len(sub) - 1) * 17 + 7, lw=0.75)
            for r, (sn, snm) in enumerate(sub):
                yy = cy + bh + 3 + 8 + r * 17
                p.line(sx, yy + 7, sx + 4, yy + 7, lw=0.75)
                p.rect(sx + 4, yy, cbw - 8, 14, f'{sn}\n{snm}', size=6.8, lw=0.9)
