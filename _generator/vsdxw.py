"""Минимальный генератор файлов Microsoft Visio (.vsdx).

Координаты задаются в миллиметрах, начало — левый верхний угол листа.
Каждая фигура — обычная фигура Visio (Shape) с собственной геометрией,
поэтому файл открывается и редактируется в Visio 2013+ (и в LibreOffice Draw).
"""
import os
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
NS = ("xmlns='http://schemas.microsoft.com/office/visio/2012/main' "
      "xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' "
      "xml:space='preserve'")
MM = 1 / 25.4

ARROW = {None: 0, 'filled': 4, 'open': 1, 'hollow': 16, 'dot': 10, 'none': 0}


def _c(n, v, f=None, u=None):
    s = f"<Cell N='{n}' V='{v}'"
    if f:
        s += f" F='{f}'"
    if u:
        s += f" U='{u}'"
    return s + "/>"


def _f(x):
    return f"{x:.6f}"


class Page:
    def __init__(self, name, w=297, h=210):
        self.name, self.w, self.h = name, w, h
        self.shapes = []
        self._id = 0

    # --- служебное -------------------------------------------------------
    def _nid(self):
        self._id += 1
        return self._id

    def _X(self, x):
        return x * MM

    def _Y(self, y):
        return (self.h - y) * MM

    def _shape(self, x, y, w, h, geoms, text='', *, line='#000000', lw=0.75,
               fill='#FFFFFF', dash=False, size=9, bold=False, italic=False,
               color='#000000', align='c', valign='m', font='Arial',
               end_arrow=None, begin_arrow=None, arrow_size=1, rounding=0,
               margin=0.8, name=None, nofill=False, noline=False, under=False):
        """geoms: список контуров; контур = список команд в мм страницы:
        ('M',x,y) ('L',x,y) ('E',cx,cy,rx,ry) ('R',) — прямоугольник по рамке."""
        sid = self._nid()
        w = max(w, 0.01)
        h = max(h, 0.01)
        W, H = w * MM, h * MM
        px, py = self._X(x + w / 2), self._Y(y + h / 2)
        nm = f'{name}.{sid}' if name else f'Shape.{sid}'
        out = [f"<Shape ID='{sid}' NameU='{escape(nm)}' Name='{escape(nm)}' "
               f"Type='Shape' LineStyle='3' FillStyle='3' TextStyle='3'>"]
        out += [_c('PinX', _f(px)), _c('PinY', _f(py)), _c('Width', _f(W)),
                _c('Height', _f(H)), _c('LocPinX', _f(W / 2), 'Width*0.5'),
                _c('LocPinY', _f(H / 2), 'Height*0.5'), _c('Angle', 0),
                _c('FlipX', 0), _c('FlipY', 0), _c('ResizeMode', 0)]
        out += [_c('LineWeight', _f(lw / 72), u='PT'),
                _c('LineColor', line if not noline else '#FFFFFF'),
                _c('LinePattern', 0 if noline else (2 if dash else 1)),
                _c('FillForegnd', fill or '#FFFFFF'),
                _c('FillPattern', 0 if (nofill or fill is None) else 1),
                _c('BeginArrow', ARROW[begin_arrow]), _c('EndArrow', ARROW[end_arrow]),
                _c('BeginArrowSize', arrow_size), _c('EndArrowSize', arrow_size),
                _c('Rounding', _f(rounding * MM)),
                _c('LeftMargin', _f(margin * MM)), _c('RightMargin', _f(margin * MM)),
                _c('TopMargin', _f(margin * MM)), _c('BottomMargin', _f(margin * MM)),
                _c('VerticalAlign', {'t': 0, 'm': 1, 'b': 2}[valign]),
                ]
        style = (1 if bold else 0) | (2 if italic else 0) | (4 if under else 0)
        out.append("<Section N='Character'><Row IX='0'>" + _c('Font', font) +
                   _c('Color', color) + _c('Style', style) +
                   _c('Size', _f(size / 72), u='PT') + "</Row></Section>")
        out.append("<Section N='Paragraph'><Row IX='0'>" +
                   _c('HorzAlign', {'l': 0, 'c': 1, 'r': 2}[align]) +
                   _c('SpLine', '-1.0') + "</Row></Section>")
        x0, y0 = x, y + h  # нижний левый угол в мм страницы (y вниз)

        def lx(v):
            return _f((v - x0) * MM)

        def ly(v):
            return _f((y0 - v) * MM)

        for gi, g in enumerate(geoms):
            closed = g and g[0][0] in ('E', 'R')
            nf = 1 if (nofill or fill is None or not g or g[-1] != 'Z' and not closed) else 0
            rows = []
            ix = 1
            if g and g[0][0] == 'R':
                pts = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
                for k, (a, b) in enumerate(pts):
                    t = 'RelMoveTo' if k == 0 else 'RelLineTo'
                    rows.append(f"<Row T='{t}' IX='{ix}'>{_c('X', a)}{_c('Y', b)}</Row>")
                    ix += 1
                nf = 1 if (nofill or fill is None) else 0
            else:
                for cmd in g:
                    if cmd == 'Z':
                        continue
                    if cmd[0] == 'E':
                        _, cx, cy, rx, ry = cmd
                        rows.append(f"<Row T='Ellipse' IX='{ix}'>{_c('X', lx(cx))}{_c('Y', ly(cy))}"
                                    f"{_c('A', lx(cx + rx))}{_c('B', ly(cy))}"
                                    f"{_c('C', lx(cx))}{_c('D', ly(cy - ry))}</Row>")
                        nf = 1 if (nofill or fill is None) else 0
                    elif cmd[0] == 'A':
                        rows.append(f"<Row T='ArcTo' IX='{ix}'>{_c('X', lx(cmd[1]))}{_c('Y', ly(cmd[2]))}"
                                    f"{_c('A', _f(cmd[3] * MM))}</Row>")
                    else:
                        t = 'MoveTo' if cmd[0] == 'M' else 'LineTo'
                        rows.append(f"<Row T='{t}' IX='{ix}'>{_c('X', lx(cmd[1]))}{_c('Y', ly(cmd[2]))}</Row>")
                    ix += 1
            out.append(f"<Section N='Geometry' IX='{gi}'>{_c('NoFill', nf)}"
                       f"{_c('NoLine', 1 if noline else 0)}{_c('NoShow', 0)}"
                       f"{_c('NoSnap', 0)}{_c('NoQuickDrag', 0)}" + ''.join(rows) + "</Section>")
        if text:
            out.append(f"<Text>{escape(text)}</Text>")
        out.append("</Shape>")
        self.shapes.append(''.join(out))
        return sid

    # --- примитивы ---------------------------------------------------------
    def rect(self, x, y, w, h, text='', **kw):
        return self._shape(x, y, w, h, [[('R',)]], text, **kw)

    def rrect(self, x, y, w, h, text='', r=2.5, **kw):
        """Прямоугольник со скруглёнными углами (геометрия ArcTo)."""
        b = r * 0.2929
        g = [('M', x + r, y), ('L', x + w - r, y), ('A', x + w, y + r, -b), ('L', x + w, y + h - r),
             ('A', x + w - r, y + h, -b), ('L', x + r, y + h), ('A', x, y + h - r, -b), ('L', x, y + r),
             ('A', x + r, y, -b), 'Z']
        return self._shape(x, y, w, h, [g], text, **kw)

    def text(self, x, y, w, h, text, **kw):
        kw.setdefault('noline', True)
        kw.setdefault('nofill', True)
        kw.setdefault('margin', 0.3)
        return self._shape(x, y, w, h, [[('R',)]], text, **kw)

    def ellipse(self, x, y, w, h, text='', **kw):
        return self._shape(x, y, w, h, [[('E', x + w / 2, y + h / 2, w / 2, h / 2)]], text, **kw)

    def poly(self, pts, *, closed=False, **kw):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x, y = min(xs), min(ys)
        w, h = max(xs) - x, max(ys) - y
        g = [('M',) + tuple(pts[0])] + [('L',) + tuple(p) for p in pts[1:]]
        if closed:
            g.append(('L',) + tuple(pts[0]))
            g.append('Z')
        else:
            kw['nofill'] = True
        return self._shape(x, y, w, h, [g], '', **kw)

    def line(self, x1, y1, x2, y2, **kw):
        return self.poly([(x1, y1), (x2, y2)], **kw)

    def multi(self, x, y, w, h, geoms, text='', **kw):
        return self._shape(x, y, w, h, geoms, text, **kw)


class Doc:
    def __init__(self):
        self.pages = []

    def page(self, name, w=297, h=210):
        p = Page(name, w, h)
        self.pages.append(p)
        return p

    def save(self, path):
        doc = open(os.path.join(HERE, 'visio_document_template.xml'), encoding='utf-8').read()
        doc = doc.replace("<FaceNames>",
                          "<FaceNames><FaceName NameU='Arial' UnicodeRanges='-536859905 -1073711037 9 0' "
                          "CharSets='1073742335 -65536' Panose='2 11 6 4 2 2 2 2 2 4' Flags='325'/>"
                          "<FaceName NameU='Times New Roman' UnicodeRanges='-536859905 -1073711077 9 0' "
                          "CharSets='1073742335 -65536' Panose='2 2 6 3 5 4 5 2 3 4' Flags='325'/>")
        doc = doc.replace("LangID' V='en-GB'", "LangID' V='ru-RU'")
        ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/visio/document.xml" ContentType="application/vnd.ms-visio.drawing.main+xml"/>'
              '<Override PartName="/visio/pages/pages.xml" ContentType="application/vnd.ms-visio.pages+xml"/>']
        for i in range(len(self.pages)):
            ct.append(f'<Override PartName="/visio/pages/page{i + 1}.xml" ContentType="application/vnd.ms-visio.page+xml"/>')
        ct.append('<Override PartName="/visio/windows.xml" ContentType="application/vnd.ms-visio.windows+xml"/>'
                  '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                  '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
                  '</Types>')
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/document" Target="visio/document.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
                '</Relationships>')
        drels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.microsoft.com/visio/2010/relationships/pages" Target="pages/pages.xml"/>'
                 '<Relationship Id="rId2" Type="http://schemas.microsoft.com/visio/2010/relationships/windows" Target="windows.xml"/>'
                 '</Relationships>')
        pages = [f"<?xml version='1.0' encoding='utf-8' ?><Pages {NS}>"]
        prels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
        for i, p in enumerate(self.pages):
            pw, ph = p.w * MM, p.h * MM
            pages.append(
                f"<Page ID='{i}' NameU='{escape(p.name)}' Name='{escape(p.name)}' ViewScale='-1' "
                f"ViewCenterX='{_f(pw / 2)}' ViewCenterY='{_f(ph / 2)}'>"
                f"<PageSheet LineStyle='0' FillStyle='0' TextStyle='0'>"
                f"{_c('PageWidth', _f(pw))}{_c('PageHeight', _f(ph))}"
                f"{_c('PageScale', '0.03937007874015748', u='MM')}{_c('DrawingScale', '0.03937007874015748', u='MM')}"
                f"{_c('DrawingSizeType', 3)}{_c('DrawingScaleType', 0)}{_c('InhibitSnap', 0)}"
                f"{_c('PrintPageOrientation', 2 if p.w > p.h else 1)}{_c('PaperKind', 9)}"
                f"</PageSheet><Rel r:id='rId{i + 1}'/></Page>")
            prels.append(f'<Relationship Id="rId{i + 1}" Type="http://schemas.microsoft.com/visio/2010/relationships/page" Target="page{i + 1}.xml"/>')
        pages.append("</Pages>")
        prels.append('</Relationships>')
        win = (f"<?xml version='1.0' encoding='utf-8' ?><Windows ClientWidth='1600' ClientHeight='900' {NS}>"
               "<Window ID='0' WindowType='Drawing' WindowState='1073741824' ContainerType='Page' Page='0' ViewScale='-1'>"
               "<ShowRulers>1</ShowRulers><ShowGrid>0</ShowGrid><ShowPageBreaks>0</ShowPageBreaks>"
               "<ShowGuides>1</ShowGuides><ShowConnectionPoints>1</ShowConnectionPoints></Window></Windows>")
        app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
               'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
               '<Application>Microsoft Visio</Application><AppVersion>16.0000</AppVersion></Properties>')
        core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>Тестов М. О.</dc:creator>'
                '<dc:language>ru-RU</dc:language></cp:coreProperties>')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml', ''.join(ct))
            z.writestr('_rels/.rels', rels)
            z.writestr('docProps/app.xml', app)
            z.writestr('docProps/core.xml', core)
            z.writestr('visio/document.xml', doc)
            z.writestr('visio/_rels/document.xml.rels', drels)
            z.writestr('visio/windows.xml', win)
            z.writestr('visio/pages/pages.xml', ''.join(pages))
            z.writestr('visio/pages/_rels/pages.xml.rels', ''.join(prels))
            for i, p in enumerate(self.pages):
                z.writestr(f'visio/pages/page{i + 1}.xml',
                           f"<?xml version='1.0' encoding='utf-8' ?><PageContents {NS}><Shapes>"
                           + ''.join(p.shapes) + "</Shapes></PageContents>")


def render(vsdx_path, out_dir, dpi=150, prefix=None):
    """Рендер всех листов .vsdx в PNG через LibreOffice (для вставки в отчёт)."""
    import subprocess
    import glob
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp()
    src = os.path.join(tmp, 'd.vsdx')
    shutil.copy(vsdx_path, src)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, src],
                   check=True, capture_output=True)
    prefix = prefix or os.path.splitext(os.path.basename(vsdx_path))[0]
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', os.path.join(tmp, 'd.pdf'),
                    os.path.join(tmp, 'p')], check=True)
    files = sorted(glob.glob(os.path.join(tmp, 'p-*.png')), key=lambda s: int(s.rsplit('-', 1)[1][:-4]))
    res = []
    for i, f in enumerate(files):
        dst = os.path.join(out_dir, f'{prefix}_{i + 1}.png')
        subprocess.run(['convert', f, '-trim', '-bordercolor', 'white', '-border', '20', dst], check=True)
        res.append(dst)
    shutil.rmtree(tmp)
    return res
