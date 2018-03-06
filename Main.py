import sys
import traceback

import time

import re
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog, qApp, QLabel, QMessageBox, QAction

from CompilerUi.Highlighter import Pl0Highlighter
from Pl0compiler import Error
from Pl0compiler.Interpreter import Interpreter
from Pl0compiler.Praser import Praser, SymbolTable
from Pl0compiler.Scanner import Scanner
from CompilerUi.about import Ui_Form
from CompilerUi.mainWindow import Ui_MainWindow
from CompilerUi.pcodeRun import Ui_runCodeForm


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.runcodeForm = RunCodeForm()
        self.about = About()

        self.setupUi(self)

        self.tableSelectHorizontalSlider.setRange(0, 2)
        self.highlighter = Pl0Highlighter(self.sourceCodePlainTextEdit.document())
        self.filePath = None
        self.compileFin = False
        self.table = []
        self.pcodeList = None
        self.permanent = QLabel()
        self.permanent.setText("line 1 col 0")
        self.statusbar.addPermanentWidget(self.permanent)
        self.tableSelectHorizontalSlider.setVisible(False)
        self.lastTag = -1

    def menubarTriggle(self, action):
        if self.actionNewFile == action:
            self.newFile()
        if self.actionOpenFile == action:
            self.openFile()
        elif self.actionSaveFile == action:
            self.saveFile()
        elif self.actionSaveAs == action:
            self.saveAs()
        elif self.actionExit == action:
            qApp.quit()
        elif self.actionAbout == action:
            self.about.show()
        elif self.actionSavePcode == action:
            self.savePcode()

    def newFile(self):
        self.filePath = None
        self.lastTag = -1
        self.compileFin = False
        self.pcodePlainTextEdit.clear()
        self.tableTextEdit.clear()
        self.setWindowTitle("Pl0文法编译器    untitled")
        self.sourceCodePlainTextEdit.clear()
        self.ErrortextBrowser.clear()

    def openFile(self):
        fileName = QFileDialog.getOpenFileName(self, "打开文件", "",
                                               "Text files(*.txt);;Pl0 files(*.pl);;Python files(*.py)")
        if fileName != ('', ''):
            try:
                with open(fileName[0], 'r', encoding="utf-8") as fp:
                    src = fp.read()
            except:
                with open(fileName[0], 'r', encoding="gbk") as fp:
                    src = fp.read()

            finally:
                self.filePath = fileName[0]
                self.lastTag = -1
                self.compileFin = False
                self.setWindowTitle("Pl0文法编译器    " + self.filePath)
                self.sourceCodePlainTextEdit.document().clear()
                self.sourceCodePlainTextEdit.setPlainText(src)
                self.ErrortextBrowser.clear()
                self.pcodePlainTextEdit.clear()
                self.tableTextEdit.clear()

    def saveFile(self):
        if self.filePath == None:
            filename = QFileDialog.getSaveFileName(self, '保存文件', "",
                                                   "Text files(*.txt);;Pl0 files(*.pl);;Python files(*.py)")
            if filename != ('', ''):
                # if filename[1][0]=="T" and filename[0][-4:-1]!=".txt": #this is for linux
                #     arg=".txt"
                # elif filename[1]=="Pl0 files(*.pl)" and filename[0][-3:-1]!=".pl":
                #     arg=".pl"
                # elif filename[1]=="Python files(*.py)" and filename[0][-3:-1]!=".py":
                #     arg=".py"
                # else:
                #     arg=""
                # self.filePath = filename[0]+arg
                self.filePath = filename[0]
                self.setWindowTitle("Pl0文法编译器    " + self.filePath)
            else:
                return
        with open(self.filePath, 'w') as f:
            my_text = self.sourceCodePlainTextEdit.toPlainText()
            f.write(my_text)
        self.statusbar.showMessage("保存成功")

    def saveAs(self):
        filename = QFileDialog.getSaveFileName(self, '保存文件', "",
                                               "Text files(*.txt);;Pl0 files(*.pl);;Python files(*.py)")
        if filename == ('', ''):
            return
        with open(filename[0], 'w') as f:
            my_text = self.sourceCodePlainTextEdit.toPlainText()
            f.write(my_text)
        self.statusbar.showMessage("保存成功")

    def updateColLine(self):
        self.permanent.setText("line " + str(self.sourceCodePlainTextEdit.textCursor().blockNumber() + 1) + " " + str(
            self.sourceCodePlainTextEdit.textCursor().columnNumber()))

    def savePcode(self):
        filename = QFileDialog.getSaveFileName(self, '保存文件', "",
                                               "Text files(*.txt);;Pcode files(*.pcode);;Python files(*.py)")
        if filename == ('', ''):
            return
        with open(filename[0], 'w') as f:
            my_text = self.pcodePlainTextEdit.toPlainText()
            f.write(my_text)
        self.statusbar.showMessage("保存成功")

    def runPcode(self):
        try:
            if not self.compileFin:
                QMessageBox.warning(self, "警告",
                                    "编译未完成，请先编译")
            else:
                self.runcodeForm.setPcodeList(self.pcodeList)
                self.runcodeForm.runInterper()
                self.runcodeForm.show()
        except:
            print(traceback.format_exc())

    def changeTable(self, pos):
        self.tableTextEdit.clear()
        self.tableTextEdit.insertHtml(self.table[pos])

    def showTable(self):
        try:
            if not self.compileFin:
                QMessageBox.warning(self, "警告",
                                    "编译未完成，请先编译")
            else:
                self.tableTextEdit.clear()
                if len(self.table) > 1:
                    self.tableSelectHorizontalSlider.setRange(0, len(self.table) - 1)
                    self.tableSelectHorizontalSlider.setVisible(True)
                    self.tableSelectHorizontalSlider.setValue(0)
                    self.tableSelectHorizontalSlider.setFocus(True)
                self.tableTextEdit.insertHtml(self.table[0])



        except:
            print(traceback.format_exc())

    def showError(self, url):
        line = int(url.fileName()[:-1])
        if self.lastTag != -1:
            self.highlightCurrentLine(self.lastTag, 0)
        self.highlightCurrentLine(line, 1)
        self.lastTag = line

    def highlightCurrentLine(self, line, status):
        try:
            selection = self.sourceCodePlainTextEdit.document().findBlockByLineNumber(line)
            cursor = self.sourceCodePlainTextEdit.textCursor()
            line = selection.text() + " "
            cursor.setPosition(selection.position())
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            formats = QTextCharFormat()
            if status:
                formats.setBackground(QColor('red'))
            cursor.removeSelectedText()
            cursor.insertText(line, formats)
        except:
            print(traceback.format_exc())

    def producePcode(self):
        ##
        self.compileFin = False
        self.ErrortextBrowser.clear()
        self.pcodePlainTextEdit.clear()
        self.tableTextEdit.clear()
        self.tableSelectHorizontalSlider.setValue(0)
        self.tableSelectHorizontalSlider.setVisible(False)
        if self.lastTag != -1:
            self.highlightCurrentLine(self.lastTag, 0)
        s = Scanner(content=WrapperQPlianText(self.sourceCodePlainTextEdit))
        praser = Praser(s, SymbolTable(), Interpreter())
        if praser.prase():
            self.statusbar.showMessage("编译成功")
            self.compileFin = True
            self.pcodeList = praser.interperter.pcodeList
            text = ""
            for i in praser.interperter.pcodeList:
                text += i.toString() + "\n"
            self.pcodePlainTextEdit.setPlainText(text)
            self.table = praser.table.tableshow
        else:
            self.statusbar.showMessage("编译中出现错误")
            self.ErrortextBrowser.insertHtml(Error.Error.errinfo)


class WrapperQPlianText:
    def __init__(self, plainText):
        self.plainText = plainText
        self.pos = 0

    def readline(self):
        eof = 0
        textCursor = self.plainText.textCursor()
        textCursor.setPosition(self.pos)
        textCursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
        endPos = textCursor.position()
        if self.pos == endPos:
            textCursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            eof = 1

        endPos = textCursor.position()
        line = textCursor.selectedText()
        self.pos = endPos
        line = line.encode(encoding='ascii', errors='ignore').decode("ascii")
        if not eof:
            line += "\n"
        elif line != "":
            line += "\n"
        return line


class InterpreterThread(QThread, Interpreter):
    updateSingnal = pyqtSignal(int, str)

    def __init__(self):
        super(InterpreterThread, self).__init__()
        self.hasInput = False
        self.inputBuffer = ""

    def setPcodeList(self, pcodeList):
        self.pcodeList = pcodeList

    def readNum(self):
        self.updateSingnal.emit(0, "请输入一个数字")
        while not self.hasInput:
            time.sleep(0.3)
        while 1:
            try:
                a = self.inputBuffer
                self.hasInput = False
                self.inputBuffer = ""
                a = int(a)
                return a
            except:
                pass

    def errorshow(self, errormsg):
        self.updateSingnal.emit(1, errormsg)

    def printInstruct(self, msg):
        self.updateSingnal.emit(0, msg)

    def printRun(self, num, status):
        if status == 1:
            self.updateSingnal.emit(0, "\n")
        else:
            self.updateSingnal.emit(0, str(num) + " ")

    def run(self):
        self.interperter(self.pcodeList)


class RunCodeForm(QWidget, Ui_runCodeForm):
    def __init__(self, parent=None):
        super(RunCodeForm, self).__init__(parent)
        self.setupUi(self)
        self.interpre = None
        exitAction = QAction(self)
        exitAction.setShortcut('ESC')
        exitAction.triggered.connect(self.close)
        self.addAction(exitAction)

    def setPcodeList(self, pcodeList):
        self.interpre = InterpreterThread()
        self.interpre.setPcodeList(pcodeList)

    def runInterper(self):
        self.errorMonitortextEdit.clear()
        self.runMonitporTextEdit.clear()
        self.inputLineEdit.setFocus(True)
        self.interpre.updateSingnal.connect(self.updateUI)

        self.interpre.start()

    def updateUI(self, status, msg):
        if status == 1:
            self.errorMonitortextEdit.append(msg)
        else:
            self.runMonitporTextEdit.append(msg)
            self.runMonitporTextEdit.moveCursor(QTextCursor.StartOfLine)
            self.runMonitporTextEdit.textCursor().deletePreviousChar()
            self.runMonitporTextEdit.moveCursor(QTextCursor.EndOfLine)

    def sendData(self):
        if self.interpre.hasInput:
            QMessageBox.warning(self, "警告",
                                "数据已发送，请稍等后重试")
        elif self.inputLineEdit.text() != "":
            self.interpre.inputBuffer = self.inputLineEdit.text()
            self.inputLineEdit.clear()
            self.interpre.hasInput = True


class About(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setupUi(self)

    def closeAbout(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
