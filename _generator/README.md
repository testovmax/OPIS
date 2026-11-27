# Генератор диаграмм Visio и отчётов (ЛР 3–8)

Скрипты строят файлы Microsoft Visio (`.vsdx`) с диаграммами и отчёты `.docx`
в оформлении ЛР 1–2 (титульный лист берётся из отчёта ЛР 2).

Требуется Python 3 с `python-docx`, `Pillow`, а также LibreOffice и `pdftoppm`
(рендер листов Visio в PNG для вставки в отчёт).

```
python3 build_lab34.py   # lab3_4: IDEF0 (задачи 1–3 и вариант 8 «Парикмахерская»)
python3 build_lab5.py    # lab5:   IDEF1X «Поликлиника» + SQL-скрипт
python3 build_lab6.py    # lab6:   UML прецеденты и классы
python3 build_lab78.py   # lab7_8: UML состояния, деятельность, последовательности
```

- `vsdxw.py` — запись `.vsdx` (фигуры с собственной геометрией, без трафаретов);
- `idef0.py`, `uml.py` — элементы нотаций; `lab*.py` — содержимое диаграмм;
- `report.py` — сборка отчёта.
