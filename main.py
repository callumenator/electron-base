import os
from typing import Any, Dict

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget, QPushButton, QTextEdit, QSplitter, QLineEdit, \
    QCompleter
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QFileSystemWatcher, QRect, QAbstractItemModel, QAbstractListModel, QModelIndex, \
    QStringListModel

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QVariant

import os


class CallHandler(QObject):

    @pyqtSlot(result=QVariant)
    def test(self):
        print('call received')
        return QVariant({"abc": "def", "ab": 22})

    # take an argument from javascript - JS:  handler.test1('hello!')
    @pyqtSlot(QVariant, result=QVariant)
    def test1(self, args):
        print('i got')
        print(args)
        return "ok"


class WebView(QWebEngineView):

    def __init__(self, page=None, url=None, dev_tools=None, parent=None):
        super().__init__(parent=parent)
        self.channel = QWebChannel()
        self.handler = CallHandler()
        self.channel.registerObject('handler', self.handler)
        if page:
            self.load(QUrl.fromLocalFile(page))
        if url:
            self.load(QUrl.fromUserInput(url))
        if dev_tools:
            self.page().setDevToolsPage(dev_tools)


class CompletionModel(QAbstractListModel):

    def headerData(self, section: int, orientation, role) -> Any:
        return ['Thing']

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 4

    def data(self, index: QModelIndex, role: int):
        result = [
            'one',
            'two',
            'three',
            'four'
        ][index.row()]
        if role == Qt.EditRole:
            return result
        if role == Qt.DisplayRole:
            return result.upper()
        # if role == Qt.SizeHintRole:
        #     return QSize(100, 20)
        return QVariant()


class CustomCompleter(QCompleter):
    def splitPath(self, path: str):
        p = [path.split(' ')[-1]]
        return p


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(QRect(0, 0, 1000, 800))
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        # dev_tools = WebView()
        browser = WebView(
            page=os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html")),
            # dev_tools=dev_tools.page(),
        )
        layout.addWidget(browser)

        self.line = QLineEdit()
        self.line.setGeometry(QRect(0, 0, 100, 100))

        self.model = QStringListModel()
        completions = {
            'commands': {
                'one': {
                    'commands': {
                        'foo': {},
                        'bar': {},
                    },
                },
                'two': {
                    'commands': {
                        'baz': {},
                        'car': {},
                    },
                },
                'three': {
                    'commands': {
                        'caz': {},
                        'dar': {},
                    }
                },
                'four': {
                    'commands': {
                        'dax': {},
                        'far': {},
                    }
                },
            },
        }

        def update_completions():
            tokens = self.line.text().split(' ')
            available = completions.get('commands')
            while tokens:
                _available = available.get(tokens.pop(0), {}).get('commands', {})
                if not _available:
                    break
                available = _available

            if available:
                self.model.setStringList(list(available.keys()))

        update_completions()
        self.line.textChanged.connect(update_completions)

        self.completions = CustomCompleter()
        self.completions.setModel(self.model)
        self.line.setCompleter(self.completions)

        self.completions.setWidget(self.line)
        layout.addWidget(self.line)

        self.show()


def apply_theme():
    with open('./style.css') as w:
        QApplication.instance().setStyleSheet(w.read())


if __name__ == "__main__":
    app = QApplication([])
    watcher = QFileSystemWatcher()
    watcher.addPath('./style.css')
    watcher.fileChanged.connect(apply_theme)
    apply_theme()

    main = MainWidget()
    app.exec_()
    print('\n'.join(repr(w) for w in app.allWidgets()))
