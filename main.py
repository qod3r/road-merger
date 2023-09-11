import os
import sys
from pathlib import Path
from pprint import pprint

from pypdf import PdfMerger
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QTreeWidgetItem, QWidget

basedir = os.path.dirname(__file__)


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
        order1 = ["паспорт", "разметка", "лг"]
        order2 = [*[f"п{i}" for i in range(1, 9)], *[f"о{i}" for i in range(1, 9)]]
        
        self.street_dirs = []
        anchor_dir_name = None
        anchor_dir_idx = None
        anchor_dir_tree = None
        for i, element in enumerate(path.iterdir()):
            if element.is_dir():
                # начальный случай
                if i == 0:
                    anchor_dir_name = element.name
                    anchor_dir_idx = i
                    anchor_dir_tree = QTreeWidgetItem(
                        tree, [folder_to_root_name(element.name)]
                    )
                    QTreeWidgetItem(anchor_dir_tree, [element.name])
                    self.street_dirs.append([element])
                    continue
                # n-ая часть улицы (очень наивно)
                if any(
                    # 💀
                    x in [anchor_dir_name, anchor_dir_name[:-1], anchor_dir_name[:-2]]
                    for x in [element.name[:-2], element.name[:-1]]
                ):
                    QTreeWidgetItem(anchor_dir_tree, [element.name])
                    self.street_dirs[anchor_dir_idx].append(element)
                # 1-ая часть улицы
                else:
                    anchor_dir_name = element.name
                    anchor_dir_idx += 1
                    anchor_dir_tree = QTreeWidgetItem(
                        tree, [folder_to_root_name(element.name)]
                    )
                    QTreeWidgetItem(anchor_dir_tree, [element.name])
                    self.street_dirs.append([element])
        pprint(self.street_dirs)


def folder_to_root_name(s):
    return "".join(
        filter(lambda ch: not ch.isdigit(), " ".join(s.replace("_", " ").split()[-2:]))
    ).strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec())
