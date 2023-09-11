import os
import sys
from pathlib import Path
from pprint import pprint

from pypdf import PdfMerger
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QWidget

basedir = os.path.dirname(__file__)

# порядок слияния
# order1 = ["паспорт", "разметка", "лг"]
# order2 = [*[f"п{i}" for i in range(1, 9)], *[f"о{i}" for i in range(1, 9)]]


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(basedir, "./resources/main.ui"), self)

        self.btnSelectFolder.clicked.connect(self.select_folder)

    def select_folder(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Выбор папки")
        if dir_name:
            self.path = Path(dir_name)
            self.treeWidget.clear()
            self.treeWidget.setHeaderLabel(self.path.name)
            self.load_streets(self.path, self.treeWidget)

    def load_streets(self, path: Path, tree: QTreeWidgetItem):
        self.streets = []
        anchor_dir_name = None
        anchor_dir_idx = None
        anchor_dir_root = None
        for i, element in enumerate(path.iterdir()):
            if not element.is_dir():
                continue
            # начальный случай
            # TODO: лишний
            if i == 0:
                street = Street()
                road = street.add_road(element)
                self.streets.append(street)

                anchor_dir_name = element.name
                anchor_dir_idx = i
                # добавляем читабельное название улицы в дерево
                # и делаем его "якорем"
                anchor_dir_root = QTreeWidgetItem(
                    tree, [folder_to_root_name(element.name)]
                )

                # полное название внутри улицы
                item = QTreeWidgetItem(anchor_dir_root, [element.name])
                item.setBackground(0, QColor(road.color()))
                populate_problems(item, road.status)
                anchor_dir_root.setBackground(0, QColor(street.color()))
                continue
            # n-ая часть улицы (очень наивно)
            elif any(
                # 💀
                x in [anchor_dir_name, anchor_dir_name[:-1], anchor_dir_name[:-2]]
                for x in [element.name[:-2], element.name[:-1]]
            ):
                road = self.streets[anchor_dir_idx].add_road(element)

                item = QTreeWidgetItem(anchor_dir_root, [element.name])
                item.setBackground(0, QColor(road.color()))
                populate_problems(item, road.status)
                anchor_dir_root.setBackground(0, QColor(street.color()))
            # 1-ая часть улицы
            else:
                street = Street()
                road = street.add_road(element)
                self.streets.append(street)

                anchor_dir_name = element.name
                anchor_dir_idx += 1
                anchor_dir_root = QTreeWidgetItem(
                    tree, [folder_to_root_name(element.name)]
                )

                item = QTreeWidgetItem(anchor_dir_root, [element.name])
                item.setBackground(0, QColor(road.color()))
                populate_problems(item, road.status)
                anchor_dir_root.setBackground(0, QColor(street.color()))
        pprint(self.streets)
        # pprint(Road(self.street_dirs[0][1], False).status)

    def check_street(self):
        ...

def folder_to_root_name(s):
    return "".join(
        filter(lambda ch: not ch.isdigit(), " ".join(s.replace("_", " ").split()[-2:]))
    ).strip()

def populate_problems(root, status):
    for err in status["err"]:
        item = QTreeWidgetItem(root, [err])
        item.setBackground(0, QColor(status["color"]))
    for warn in status["warn"]:
        item = QTreeWidgetItem(root, [warn])
        item.setBackground(0, QColor(status["color"]))

class Street:
    def __init__(self, main_road=None):
        self.roads = []
        if main_road is not None:
            self.roads.append(Road(main_road, True))

    def add_road(self, path: Path):
        main = False
        if not self.roads:
            main = True
        road = Road(path, is_main=main)
        self.roads.append(road)
        return road

    def color(self):
        # red
        if any(r.status["color"] == "#BF616A" for r in self.roads):
            return "#BF616A"
        # yellow
        elif any(r.status["color"] == "#EBCB8B" for r in self.roads):
            return "#EBCB8B"
        # green
        else:
            return "#A3BE8C"

    def __repr__(self):
        return str(self.roads)


class Road:
    # TODO: настройка префиксов в названиях файлов
    # TODO: полные названия в ошибках (лг - Линейный график и т.д.)

    # всегда должен быть линейный график и данные прямого+обратного направления
    required = ["лг", *[f"п{i}" for i in range(1, 9)], *[f"о{i}" for i in range(1, 9)]]
    # паспорт у первой части
    conditional = ["паспорт"]
    # разметка если есть
    warn = ["разметка"]

    def __init__(self, path: Path, is_main: bool):
        self.path = path
        self.is_main = is_main
        self.pdfs = []
        for element in self.path.iterdir():
            if ".pdf" in element.name:
                self.pdfs.append(element.name)

        s = {"ok": [], "warn": [], "err": [], "color": "#A3BE8C"}
        for pref in self.warn:
            # пока что проверяем ошибки в разметке
            # if not any(pref in x for x in self.pdfs):
            if any(pref in x for x in self.pdfs):
                s["warn"].append(f"Проверить {pref}.pdf (заголовок раздельно)")
                s["color"] = "#EBCB8B"
        for pref in self.required:
            if not any(pref in x for x in self.pdfs):
                s["err"].append(f"Отсутствует {pref}.pdf")
                s["color"] = "#BF616A"
        for pref in self.conditional:
            if (not any(pref in x for x in self.pdfs)) and self.is_main:
                s["err"].append(f"Отсутствует {pref}.pdf")
                s["color"] = "#BF616A"

        # оставшиеся
        s["ok"] = self.pdfs.copy()
        self.status = s

    def color(self):
        return self.status["color"]

    def __repr__(self):
        return f"{'Main' if self.is_main else 'Secondary'} {self.path.name}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec())
