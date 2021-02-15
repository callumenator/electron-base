import os
from typing import Any, Dict

from PyQt5 import QtGui
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget, QPushButton, QTextEdit, QSplitter, QLineEdit, \
    QCompleter, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QFileSystemWatcher, QRect, QAbstractItemModel, QAbstractListModel, QModelIndex, \
    QStringListModel

from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QVariant

import os

from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QSizePolicy


class CallHandler(QObject):

    def __init__(self, app):
        self.app = app
        super().__init__()


class WebView(QWebEngineView):

    def __init__(self, page=None, url=None, dev_tools=None, parent=None, handler=None):
        super().__init__(parent=parent)

        # Expose python callables inside the page
        if handler:
            self.channel = QWebChannel()
            self.channel.registerObject('handler', handler)
            self.page().setWebChannel(self.channel)

        if page:
            self.load(QUrl.fromLocalFile(page))
        if url:
            self.load(QUrl.fromUserInput(url))
        if dev_tools:
            self.page().setDevToolsPage(dev_tools)

        self.mouseDragStart = None
        self.mouseDragStop = None
        self.mouseDragTracking = False


class WebViewCallHandler(QObject):

    receive = pyqtSignal()

    def __init__(self, handler):
        super().__init__()
        self.handler = handler

    @pyqtSlot(QVariant, result=QVariant)
    def send(self, arg):
        return self.handler(arg)


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.webview_handler = WebViewCallHandler(self.on_webview_message)

        self.setGeometry(QRect(0, 0, 1000, 800))
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        dev_tools = WebView()
        browser = WebView(
            url='http://localhost:8080/',
            dev_tools=dev_tools.page(),
            handler=self.webview_handler,
        )
        self.webviews = [browser]

        self.splitter = QSplitter(self)
        self.splitter.setHandleWidth(1)
        self.splitter.addWidget(browser)
        self.splitter.addWidget(dev_tools)
        layout.addWidget(self.splitter)
        layout.setContentsMargins(0, 0, 0, 0)
        # layout.addWidget(browser)
        # layout.addWidget(dev_tools)

        self.show()

    def add_webview(self):
        self.webviews.append(
            WebView(
                page=os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html")),
                handler=self.webview_handler,
            )
        )
        self.splitter.addWidget(self.webviews[-1])

    def on_webview_message(self, argument: QVariant):
        self.add_webview()
        return QVariant({'response': 'hello'})

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        # NOTE: on mac, the command key produces control modifier, control key produces meta modifier
        key = event.key()
        modifiers = int(event.modifiers())
        if modifiers and modifiers & Qt.CTRL and key == Qt.Key_T:
            self.open_command_window()

    def open_command_window(self):
        dlg = QDialog(self)
        dlg.setWindowFlags(Qt.FramelessWindowHint)
        layout = QVBoxLayout()
        dlg.setLayout(layout)
        geom = self.geometry()
        modal_width = geom.width() * .8
        dlg.setGeometry(geom.width() / 2 - modal_width / 2, geom.y(), modal_width, 300)
        dlg.show()


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
