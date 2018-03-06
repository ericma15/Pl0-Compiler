from .Error import Error
from .Symbol import *


class Scanner:
    """
    词法分析器
    """

    def __init__(self, **kwargs):
        """#初始化，这里为了兼容命令行和Ui模式，采用kwarg传参
        :param filePath:文件路径
        :param content:UI调用传入参数，需要实现readline方法
        """

        self.lineCnt = 0
        self.__curCh = ' '
        self.__line = ""
        self.lineLength = 0
        self.chCount = 0
        self.__ssym = dict()
        self.__filebuffer = None
        self.eof = False
        for key in kwargs:
            if key == "filePath":
                try:
                    self.__filebuffer = open(kwargs[key], 'r')
                except IOError as e:
                    print(e.strerror)
                    exit(0)
            elif key == "content":
                self.__filebuffer = kwargs[key]
            else:
                print("arg not supoort")
                exit(1)

        self.__ssym['+'] = Symbol.plus
        self.__ssym['-'] = Symbol.minus
        self.__ssym['*'] = Symbol.mul
        self.__ssym['/'] = Symbol.div
        self.__ssym['('] = Symbol.lparen
        self.__ssym[')'] = Symbol.rparen
        self.__ssym['='] = Symbol.eql
        self.__ssym[','] = Symbol.comma
        self.__ssym['.'] = Symbol.peroid
        self.__ssym[';'] = Symbol.semicolon

    def __getch(self):
        """
        一次加载一行到scanner，读取一个字符
        :param self
        :return void
        """
        if self.chCount == self.lineLength:  # 相等说明当前行已读完
            try:
                tem = ""
                if tem == "":
                    tem = self.__filebuffer.readline()
                if tem == "":  # 为空说明文件已读完，添加.使分析器结束
                    tem = "."
                    if not self.eof:  # 为了防止报错多次
                        Error.strerrno(8, self.lineCnt, self.chCount)  # 分析器读到结束，而文件未设置为结束，报错
                    self.eof = True

                self.__line = tem
                self.lineCnt += 1
            except EnvironmentError as e:
                print(e.strerror)
            self.lineLength = len(self.__line)
            self.chCount = 0
        self.__curCh = self.__line[self.chCount]  # 读入字符
        self.chCount += 1

    def getSym(self):
        """
        词法分析，获区一个token
        :param self
        :return: Symbol
        """
        while self.__curCh in [" ", "\n", "\r", "\t", "\n\r", "\r\n"]:  # 忽略空行
            self.__getch()

        if self.__curCh.isalpha():  # 匹配标识符和关键字
            sym = self.__matchAlpha()
        elif self.__curCh.isdigit():  # 匹配数字
            sym = self.__matchNum()
        else:
            sym = self.__matchOperator()  # 匹配操作符
        return sym

    def __matchAlpha(self):
        """
        匹配标识符和关键字
        :param self
        :return Symbol:符号类
        """
        wd = ""
        while 1:
            wd += self.__curCh
            self.__getch()
            if not (self.__curCh.isdigit() or self.__curCh.isalpha()):  # 获取当前单词
                break
        try:
            index = Symbol.word.index(wd)  # 尝试匹配关键字
            sym = Symbol(Symbol.wsym[index])
        except:
            sym = Symbol(Symbol.ident)
            sym.id = wd
        return sym

    def __matchNum(self):
        """
        匹配数字
        :param self
        :return Symbol:符号类
        """
        wd = ""
        while 1:
            wd += self.__curCh
            self.__getch()
            if not self.__curCh.isdigit():  # 获取数字串
                break
        sym = Symbol(Symbol.number)
        sym.num = int(wd)  # 转化为数字类型
        return sym

    def __matchOperator(self):
        """
        匹配操作符
        :param self
        :return Symbol:符号类
        """
        sym = Symbol(Symbol.nul)
        if self.__curCh == ":":  # 尝试匹配多字符操作符
            self.__getch()
            if self.__curCh == "=":  # 匹配：=
                sym.symtype = Symbol.becomes
                self.__getch()
        elif self.__curCh == "<":
            self.__getch()
            if self.__curCh == "=":  # 匹配<=
                sym = Symbol(Symbol.leq)
                self.__getch()
            elif self.__curCh == ">":  # 匹配<>
                sym = Symbol(Symbol.neq)
                self.__getch()
            else:
                sym = Symbol(Symbol.lss)  # 匹配<
        elif self.__curCh == ">":
            self.__getch()
            if self.__curCh == "=":  # 匹配>=
                sym = Symbol(Symbol.geq)
                self.__getch()  # 读入字符已被匹配，继续读入
            else:
                sym = Symbol(Symbol.gtr)  # 匹配>,当前读入字符未被匹配，下一次调用将被匹配，不需继续读入
        else:
            try:
                sym = Symbol(self.__ssym[self.__curCh])  # 单字符直接尝试匹配
                self.__getch()  # 匹配成功，读入下一个
            except KeyError as e:
                Error.strerrno(27, self.lineCnt, self.chCount)  # 失败报错
                self.__getch()  # 忽略当前，读入下一个

        return sym
