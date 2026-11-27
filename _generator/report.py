"""Сборка отчётов .docx в оформлении ЛР1/ЛР2 (титульный лист берётся из отчёта ЛР2)."""
import copy
import os
import re

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'lab2', 'ОПИС_лаб2_ТЗ_Автосервис_1.docx')
INDENT = Cm(1.25)


class Report:
    def __init__(self, title_line):
        self.d = docx.Document(TEMPLATE)
        body = self.d.element.body
        paras = self.d.paragraphs
        last = None
        for p in paras:
            if p.text.strip() == '2026 г':
                last = p._p
                break
        # удалить всё после титульного листа (кроме sectPr)
        rm = False
        for el in list(body):
            if rm and el.tag != qn('w:sectPr'):
                body.remove(el)
            if el is last:
                rm = True
        for p in self.d.paragraphs:
            if 'ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ' in p.text:
                for r in p.runs[1:]:
                    r.text = ''
                p.runs[0].text = title_line
        self.fig = 0
        self.tab = 0
        self._first = True

    # ---------------------------------------------------------------- базовое
    def _p(self, text='', bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, spacing=1.5,
           after=0, size=14, italic=False, keep=False):
        p = self.d.add_paragraph()
        self._brk(p)
        pf = p.paragraph_format
        pf.alignment = align
        pf.first_line_indent = INDENT if indent else Cm(0)
        pf.line_spacing = spacing
        pf.space_after = Pt(after)
        pf.space_before = Pt(0)
        if keep:
            pf.keep_with_next = True
        if text:
            self._runs(p, text, bold, size, italic)
        return p

    def _runs(self, p, text, bold=False, size=14, italic=False):
        # **жирный** фрагмент внутри строки
        parts = re.split(r'(\*\*.+?\*\*)', text)
        for part in parts:
            if not part:
                continue
            b = bold
            if part.startswith('**') and part.endswith('**'):
                part = part[2:-2]
                b = True
            r = p.add_run(part)
            r.font.name = 'Times New Roman'
            r._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
            r.font.size = Pt(size)
            r.bold = b
            r.italic = italic

    def _brk(self, p):
        if self._first:
            p.paragraph_format.page_break_before = True
            self._first = False

    def page_break(self):
        self._first = True

    def h1(self, text, new_page=False):
        if new_page:
            self.page_break()
        return self._p(text, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, after=6, keep=True)

    h2 = h1

    def p(self, text, **kw):
        return self._p(text, **kw)

    def items(self, lines, marker='–'):
        for i, l in enumerate(lines):
            m = f'{i + 1})' if marker == '1)' else marker
            self._p(f'{m} {l}')

    def center(self, text, bold=False):
        return self._p(text, bold=bold, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

    # ---------------------------------------------------------------- рисунки
    def figure(self, path, caption, width_cm=16.5):
        self.fig += 1
        p = self.d.add_paragraph()
        self._brk(p)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(4)
        p.add_run().add_picture(path, width=Cm(width_cm))
        self._p(f'Рисунок {self.fig} – {caption}', align=WD_ALIGN_PARAGRAPH.CENTER, indent=False,
                spacing=1.0, after=10)
        return self.fig

    def landscape(self, on=True):
        sec = self.d.add_section(WD_SECTION.NEW_PAGE)
        w, h = Cm(21.0), Cm(29.7)
        if on:
            sec.orientation = WD_ORIENT.LANDSCAPE
            sec.page_width, sec.page_height = h, w
            sec.left_margin, sec.right_margin = Cm(2.0), Cm(1.5)
            sec.top_margin, sec.bottom_margin = Cm(1.5), Cm(1.2)
        else:
            sec.orientation = WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = w, h
            first = self.d.sections[0]
            sec.left_margin, sec.right_margin = first.left_margin, first.right_margin
            sec.top_margin, sec.bottom_margin = first.top_margin, first.bottom_margin
        self._first = False
        self._land_start = True

    def wide_figures(self, figs, width_cm=23.5):
        """figs: [(путь, подпись)] — каждый рисунок на отдельной альбомной странице."""
        self.landscape(True)
        from PIL import Image
        for i, (path, cap) in enumerate(figs):
            if i:
                self.page_break()
            w, h = Image.open(path).size
            self.figure(path, cap, min(width_cm, 16.2 * w / h))
        self.landscape(False)

    def next_fig(self):
        return self.fig + 1

    # ---------------------------------------------------------------- таблицы
    def table(self, header, rows, caption, widths=None, size=12):
        self.tab += 1
        self._p(f'Таблица {self.tab} – {caption}', align=WD_ALIGN_PARAGRAPH.LEFT, indent=False,
                spacing=1.0, keep=True, after=0)
        t = self.d.add_table(rows=1 + len(rows), cols=len(header))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r, row in enumerate([header] + rows):
            for c, val in enumerate(row):
                cell = t.cell(r, c)
                cell.text = ''
                par = cell.paragraphs[0]
                par.paragraph_format.first_line_indent = Cm(0)
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.space_after = Pt(0)
                if r == 0:
                    par.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                lines = str(val).split('\n')
                for li, line in enumerate(lines):
                    if li:
                        par = cell.add_paragraph()
                        par.paragraph_format.first_line_indent = Cm(0)
                        par.paragraph_format.line_spacing = 1.0
                        par.paragraph_format.space_after = Pt(0)
                    self._runs(par, line, bold=(r == 0), size=size)
        # повтор заголовка на новой странице
        trPr = t.rows[0]._tr.get_or_add_trPr()
        el = OxmlElement('w:tblHeader')
        el.set(qn('w:val'), 'true')
        trPr.append(el)
        if widths:
            t.autofit = False
            for c, w in enumerate(widths):
                t.columns[c].width = Cm(w)
            for row in t.rows:
                for c, w in enumerate(widths):
                    row.cells[c].width = Cm(w)
        self._p('', spacing=1.0)
        return t

    def save(self, path):
        self.d.save(path)
