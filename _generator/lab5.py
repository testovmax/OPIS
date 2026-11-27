"""ЛР 5. Информационная модель IDEF1X «Поликлиника» (вариант 8)."""
from vsdxw import Doc

FS = 7.0      # размер шрифта атрибутов
LH = 3.05     # высота строки, мм
LINE = '#1F3864'

# сущность: (имя, физ. имя, зависимая?, ключи, неключевые)
# атрибут: (логическое имя, физическое имя, тип, признак) признак: '' | 'FK' | 'O' | 'FK,O' | 'AK'
E = {
    'uch': ('Участок', 'District', False,
            [('Номер участка', 'district_no', 'SMALLINT', '')],
            [('Описание территории', 'territory', 'NVARCHAR(200)', '')]),
    'spec': ('Специальность', 'Specialty', False,
             [('Код специальности', 'specialty_id', 'SMALLINT', '')],
             [('Название специальности', 'specialty_name', 'NVARCHAR(60)', '')]),
    'cab': ('Кабинет', 'Room', False,
            [('Номер кабинета', 'room_no', 'SMALLINT', '')],
            [('Этаж', 'floor', 'TINYINT', ''), ('Назначение', 'purpose', 'NVARCHAR(60)', 'O')]),
    'pac': ('Пациент', 'Patient', False,
            [('Номер медкарты', 'card_no', 'INT', '')],
            [('Номер участка', 'district_no', 'SMALLINT', 'FK'),
             ('Фамилия', 'last_name', 'NVARCHAR(40)', ''), ('Имя', 'first_name', 'NVARCHAR(40)', ''),
             ('Отчество', 'middle_name', 'NVARCHAR(40)', 'O'), ('Дата рождения', 'birth_date', 'DATE', ''),
             ('Пол', 'sex', 'CHAR(1)', ''), ('Адрес', 'address', 'NVARCHAR(200)', ''),
             ('Телефон', 'phone', 'VARCHAR(16)', 'O'), ('Номер полиса ОМС', 'oms_policy', 'CHAR(16)', 'AK'),
             ('СНИЛС', 'snils', 'CHAR(11)', 'O')]),
    'vr': ('Врач', 'Doctor', False,
           [('Табельный номер', 'doctor_id', 'INT', '')],
           [('Код специальности', 'specialty_id', 'SMALLINT', 'FK'), ('Номер кабинета', 'room_no', 'SMALLINT', 'FK'),
            ('Номер участка', 'district_no', 'SMALLINT', 'FK,O'),
            ('Фамилия', 'last_name', 'NVARCHAR(40)', ''), ('Имя', 'first_name', 'NVARCHAR(40)', ''),
            ('Отчество', 'middle_name', 'NVARCHAR(40)', 'O'), ('Категория', 'category', 'NVARCHAR(20)', 'O')]),
    'tal': ('Талон', 'Ticket', True,
            [('Табельный номер', 'doctor_id', 'INT', 'FK'), ('Дата приёма', 'visit_date', 'DATE', ''),
             ('Время приёма', 'visit_time', 'TIME(0)', '')],
            [('Номер медкарты', 'card_no', 'INT', 'FK,O'), ('Статус талона', 'status', 'NVARCHAR(15)', '')]),
    'pri': ('Приём', 'Visit', True,
            [('Табельный номер', 'doctor_id', 'INT', 'FK'), ('Дата приёма', 'visit_date', 'DATE', 'FK'),
             ('Время приёма', 'visit_time', 'TIME(0)', 'FK')],
            [('Код МКБ-10', 'icd_code', 'VARCHAR(7)', 'FK'), ('Жалобы', 'complaints', 'NVARCHAR(500)', 'O'),
             ('Рекомендации', 'recommendations', 'NVARCHAR(500)', 'O'),
             ('Больничный лист', 'sick_leave', 'BIT', '')]),
    'diag': ('Диагноз', 'Diagnosis', False,
             [('Код МКБ-10', 'icd_code', 'VARCHAR(7)', '')],
             [('Наименование диагноза', 'diagnosis_name', 'NVARCHAR(200)', '')]),
    'prep': ('Препарат', 'Medicine', False,
             [('Код препарата', 'medicine_id', 'INT', '')],
             [('Наименование препарата', 'medicine_name', 'NVARCHAR(100)', ''),
              ('Форма выпуска', 'dosage_form', 'NVARCHAR(40)', '')]),
    'rec': ('Рецепт', 'Prescription', False,
            [('Номер рецепта', 'prescription_no', 'INT', '')],
            [('Табельный номер', 'doctor_id', 'INT', 'FK'), ('Дата приёма', 'visit_date', 'DATE', 'FK'),
             ('Время приёма', 'visit_time', 'TIME(0)', 'FK'), ('Код препарата', 'medicine_id', 'INT', 'FK'),
             ('Дозировка', 'dosage', 'NVARCHAR(100)', ''), ('Дата выписки', 'issue_date', 'DATE', '')]),
}
NUM = {k: i + 1 for i, k in enumerate(['uch', 'spec', 'cab', 'pac', 'vr', 'tal', 'pri', 'diag', 'prep', 'rec'])}

# ненормализованная полная атрибутивная модель (до нормализации)
UNNORM = {
    'pac': [('Номер участка', 'FK'), ('ФИО пациента', ''), ('Дата рождения', ''), ('Пол', ''), ('Адрес', ''),
            ('Телефоны', ''), ('Номер полиса ОМС', 'AK'), ('СНИЛС', 'O')],
    'vr': [('Код специальности', 'FK'), ('Номер кабинета', 'FK'), ('Номер участка', 'FK,O'),
           ('ФИО врача', ''), ('Категория', 'O')],
    'tal': [('Номер медкарты', 'FK,O'), ('Номер кабинета', ''), ('Статус талона', '')],
    'pri': [('Код МКБ-10', 'FK'), ('Наименование диагноза', ''), ('Жалобы', 'O'), ('Рекомендации', 'O'),
            ('Больничный лист', '')],
}

POS = {'uch': (10, 14), 'spec': (88, 14), 'cab': (166, 14),
       'pac': (10, 66), 'vr': (88, 66), 'tal': (166, 66), 'prep': (236, 66),
       'diag': (88, 140), 'pri': (166, 140), 'rec': (236, 140)}
W = {'uch': 58, 'spec': 60, 'cab': 52, 'pac': 58, 'vr': 60, 'tal': 52, 'pri': 52, 'diag': 58, 'prep': 54, 'rec': 54}


def ent_box(p, k, mode, phys=False):
    """mode: 'erd' | 'kb' | 'fa' | 'unnorm'"""
    name, pname, dep, keys, attrs = E[k]
    x, y = POS[k]
    w = W[k]
    title = (pname if phys else name)
    p.text(x, y - 4.6, w, 4.4, f'{title}/{NUM[k]}' if not phys else title, size=7.5, bold=True, align='l')
    rnd = 2.5 if dep else 0
    if mode == 'erd':
        h = 9
        (p.rrect if dep else p.rect)(x, y, w, h, '', lw=1.0, line=LINE, fill='#F3F6FB')
        return (x, y, w, h)

    def fmt(a):
        nm, ph, tp, fl = a
        s = ph if phys else nm
        if phys:
            s = f'{s}: {tp}'
        tags = []
        if 'FK' in fl:
            tags.append('FK')
        if 'AK' in fl:
            tags.append('AK1')
        if tags:
            s += ' (' + ','.join(tags) + ')'
        if 'O' in fl.split(','):
            s += ' (O)'
        return s

    klines = [fmt(a) for a in keys]
    if mode == 'kb':
        alines = [fmt(a) for a in attrs if 'FK' in a[3] or 'AK' in a[3]]
    elif mode == 'unnorm' and k in UNNORM:
        alines = []
        for nm, fl in UNNORM[k]:
            s = nm + (' (FK)' if 'FK' in fl else '') + (' (AK1)' if 'AK' in fl else '') + (' (O)' if 'O' in fl.split(',') else '')
            alines.append(s)
    else:
        alines = [fmt(a) for a in attrs]
    hk = len(klines) * LH + 2
    ha = max(1, len(alines)) * LH + 2
    h = hk + ha
    (p.rrect if dep else p.rect)(x, y, w, h, '', lw=1.0, line=LINE, fill='#FFFFFF')
    p.line(x, y + hk, x + w, y + hk, lw=0.75, line=LINE)
    p.text(x + 0.5, y + 0.6, w - 1, hk - 1, '\n'.join(klines), size=FS, align='l', valign='t', margin=0.6)
    if alines:
        p.text(x + 0.5, y + hk + 0.6, w - 1, ha - 1, '\n'.join(alines), size=FS, align='l', valign='t', margin=0.6)
    return (x, y, w, h)


def diamond(p, x, y):
    p.poly([(x, y - 1.6), (x + 1.6, y), (x, y + 1.6), (x - 1.6, y)], closed=True, fill='#FFFFFF', line=LINE, lw=0.75)


def rel(p, pts, kind, card='', verb='', vat=None, opt=False, card_at=None):
    dash = kind == 'nonid'
    p.poly(pts, line=LINE, lw=1.0, dash=dash, end_arrow='dot',
           begin_arrow='dot' if kind == 'mm' else None)
    if opt:
        diamond(p, *pts[0])
    if card:
        cx, cy = card_at if card_at else (pts[-1][0] + 1.5, pts[-1][1] - 5)
        p.text(cx, cy, 5, 4, card, size=7.5, bold=True, align='l')
    if verb:
        vx, vy = vat
        p.text(vx, vy, 34, 4, verb, size=6.8, italic=True, align='l', color='#333333')


def build_page(p, mode, phys=False, title=''):
    B = {}
    for k in E:
        if mode == 'erd' and k == 'rec':
            continue
        B[k] = ent_box(p, k, mode, phys)

    def bot(k, dx=0.5):
        x, y, w, h = B[k]
        return (x + w * dx, y + h)

    def top(k, dx=0.5):
        x, y, w, h = B[k]
        return (x + w * dx, y)

    def left(k, dy=0.5):
        x, y, w, h = B[k]
        return (x, y + min(h * dy, h - 2))

    def right(k, dy=0.5):
        x, y, w, h = B[k]
        return (x + w, y + min(h * dy, h - 2))

    vb = not phys  # глагольные фразы на логическом уровне
    # Участок -> Пациент
    rel(p, [bot('uch', 0.3), top('pac', 0.3)], 'nonid', 'P', 'обслуживает' if vb else '', (bot('uch', 0.3)[0] + 1.5, B['uch'][1] + B['uch'][3] + 3))
    # Участок -> Врач (необязательная, 0 или 1)
    a = right('uch', 0.4 if mode != 'erd' else 0.5)
    rel(p, [a, (80, a[1]), (80, 58), (B['vr'][0] + 10, 58), (B['vr'][0] + 10, B['vr'][1])], 'nonid', 'Z',
        'закреплён за' if vb else '', (81, 47), opt=True, card_at=(B['vr'][0] + 11.5, B['vr'][1] - 5))
    # Специальность -> Врач
    rel(p, [bot('spec', 0.55), top('vr', 0.55)], 'nonid', '', 'имеет' if vb else '', (bot('spec', 0.55)[0] + 1.5, 46 if mode != 'erd' else 30))
    # Кабинет -> Врач
    c = bot('cab', 0.3)
    rel(p, [c, (c[0], 61), (B['vr'][0] + 50, 61), (B['vr'][0] + 50, B['vr'][1])], 'nonid', '',
        'используется' if vb else '', (c[0] + 1.5, 52 if mode != 'erd' else 30))
    # Врач -> Талон (идентифицирующая)
    s = right('vr', 0.2 if mode != 'erd' else 0.5)
    rel(p, [s, (B['tal'][0], s[1])], 'id', 'P', 'выдаёт' if vb else '', (s[0] + 0.5, s[1] - 4.5),
        card_at=(B['tal'][0] - 4.5, s[1] + 0.3))
    # Пациент -> Талон
    s = bot('pac', 0.5)
    yy = 132
    rel(p, [s, (s[0], yy), (B['tal'][0] + B['tal'][2] - 8, yy), (B['tal'][0] + B['tal'][2] - 8, B['tal'][1] + B['tal'][3])],
        'nonid', '', 'записывается по' if vb else '', (s[0] + 1.5, yy - 4), opt=True)
    # Талон -> Приём (1 : 0 или 1)
    s = bot('tal', 0.3)
    rel(p, [s, (s[0], B['pri'][1])], 'id', 'Z', 'оформляется в' if vb else '', (s[0] + 1.5, B['pri'][1] - 13 if mode != 'erd' else yy + 1),
        card_at=(s[0] + 1.5, B['pri'][1] - 4.5))
    # Диагноз -> Приём
    s = right('diag', 0.5 if mode == 'erd' else 0.3)
    rel(p, [s, (B['pri'][0], s[1])], 'nonid', '', 'ставится при' if vb else '', (s[0] + 0.5, s[1] - 4.5))
    if mode == 'erd':
        # многие-ко-многим Приём — Препарат
        s = right('pri', 0.5)
        x2 = B['prep'][0] + 20
        rel(p, [s, (x2, s[1]), (x2, B['prep'][1] + B['prep'][3])], 'mm', '', 'назначается' if vb else '', (s[0] + 1.5, s[1] - 4.5))
    else:
        s = right('pri', 0.15)
        rel(p, [s, (B['rec'][0], s[1])], 'nonid', '', 'выписывается' if vb else '', (s[0] + 0.5, s[1] - 4.5))
        s = bot('prep', 0.5)
        rel(p, [s, (s[0], B['rec'][1])], 'nonid', '', 'входит в' if vb else '', (s[0] + 1.5, s[1] + 2))
    if title:
        p.text(10, 200, 277, 6, title, size=8, italic=True, align='l', color='#555555')


def build(d):
    build_page(d.page('ERD'), 'erd')
    build_page(d.page('KB'), 'kb')
    build_page(d.page('FA (до нормализации)'), 'unnorm')
    build_page(d.page('FA (3НФ)'), 'fa')
    build_page(d.page('Физическая модель'), 'fa', phys=True)


if __name__ == '__main__':
    import sys
    import vsdxw
    d = Doc()
    build(d)
    d.save(sys.argv[1])
    print(vsdxw.render(sys.argv[1], sys.argv[2], dpi=110))
