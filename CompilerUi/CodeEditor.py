import PyQt5

from PyQt5.QtCore import QSize, QRect
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QPlainTextEdit, QWidget

# self.sourceCodePlainTextEdit.blockCountChanged['int'].connect(MainWindow.updateLineNumberAreaWidth)
#         self.sourceCodePlainTextEdit.updateRequest['QRect','int'].connect(MainWindow.updateLineNumberArea)
from PyQt5.uic.properties import QtGui


class LineNumberArea(QWidget):
    def __init__(self, editor, parent=None):
        super(LineNumberArea, self).__init__(editor)#parent 为Editor编辑器
        self.codeEditor = editor
        fonts = QFont()
        fonts.setFamily("courier")
        fonts.setBold(True)
        self.setFont(fonts)

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, QPaintEvent):
        self.codeEditor.lineNumberAreaPaintEvent(QPaintEvent) #绘制行号部分


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged['int'].connect(self.updateLineNumberAreaWidth)
        self.updateRequest['QRect', 'int'].connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0) #更新宽度，0为占位



    def lineNumberAreaWith(self):
        """
        计算行号列宽度
        :return: int 宽度
        """
        digits = 1
        maxs = max(1, self.blockCount())
        while maxs >= 10:
            maxs //= 10
            digits += 1
        space = 8 + self.fontMetrics().width('9') * digits #offset+单字符宽度×最大位数
        return space

    def updateLineNumberAreaWidth(self, int):
        self.setViewportMargins(self.lineNumberAreaWith(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, QResizeEvent):
        super(CodeEditor, self).resizeEvent(QResizeEvent)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWith(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = PyQt5.QtGui.QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("lightgray"))
        painter.setPen(QColor("darkgray"))
        block = self.firstVisibleBlock()

        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingGeometry(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isValid() and bottom >= event.rect().top():
                number = str(blockNumber + 1)

                painter.drawText(-2, top, self.lineNumberArea.width(), self.fontMetrics().height(), 0x0002, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1
