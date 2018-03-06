from .SymbolTable import *
from .Error import *
from .Pcode import *
from .Symbol import *


class Praser:
    """
    语法分析器类
    """

    def __init__(self, lex, table, interpreter):
        """
        初始化lei类
        :param lex: Scanner 此法分析器
        :param table: SymbolTable 符号表
        :param interpreter: Interpreter 解释器
        """
        self.lex = lex
        self.table = table
        self.interperter = interpreter
        # 当前token
        self.sym = None
        '''
        当前作用域的堆栈帧大小，或者说数据大小(data size)
        计算每个变量在运行栈中相对本过程基地址的偏移量，
        放在symbolTable中的address域，
        生成目标代码时再放在code中的a域
        '''
        self.dx = 0
        Error.errCount = 0
        Error.errinfo = ""
        # 表示申明开始的符号集合：声明的FIRST集合
        '''
        设置申明开始符号集
        <分程序> ::= [<常量说明部分>][<变量说明部分>][<过程说明部分>]<语句>
        <常量说明部分> ::= const<常量定义>{,<常量定义>};
        <变量说明部分>::= var<标识符>{,<标识符>};
        <过程说明部分> ::= <过程首部><分程序>;{<过程说明部分>}
        FIRST(declaration)={const var procedure null };
        '''
        self.declbegsys = {Symbol.constsym, Symbol.varsym, Symbol.procsym}
        # 表示语句开始的符号集合：语句的FIRST集合
        '''
        设置语句开始符号集
        <语句> ::=<赋值语句>|<条件语句>|<当型循环语句>|<过程调用语句>|<读语句>|<写语句>|<复合语句>|<重复语句>|<空>
        <赋值语句> ::= <标识符>:=<表达式>
        <条件语句> ::= if<条件>then<语句>[else<语句>]
        <当型循环语句> ::= while<条件>do<语句>
        <重复语句> ::= repeat<语句>{;<语句>}until<条件>
        <过程调用语句> ::= call<标识符>
        <复合语句> ::= begin<语句>{;<语句>}end 
        FIRST(statement)={begin call if while repeat null };
        '''
        self.statbegsys = {Symbol.beginsym, Symbol.callsym, Symbol.ifsym, Symbol.whilesym, Symbol.repeatsym}
        # 表示因子开始的符号集合：因子的FIRST集合
        '''
        设置因子开始符号集
        <因子> ::= <标识符>|<无符号整数>|'('<表达式>')' 
        FIRST(factor)={ident,number,( };
        '''
        self.facbegsys = {Symbol.ident, Symbol.number, Symbol.lparen}

        self.nextsym()

    def nextsym(self):
        """
        对于getsym的封装，获得下一个token
        :return: 
        """
        self.sym = self.lex.getSym()

    def test(self, s1, s2, errcode):
        """
        测试当前符号是否合法 本过程有三个参数，s1、s2为两个符号集合，n为出错代码。
        本过程的功能是：测试当前符号（即sym变量中的值）是否在s1集合中， 如果不在，就通过调用出错报告过程输出出错代码n，
        并放弃当前符号，通过词法分析过程获取一下单词， 直到这个单词出现在s1或s2集合中为止。 这个过程在实际使用中很灵活，主要有两个用法：
        在进入某个语法单位时，调用本过程， 检查当前符号是否属于该语法单位的开始符号集合。 若不属于，则滤去开始符号和后继符号集合外的所有符号。
        在语法单位分析结束时，调用本过程， 检查当前符号是否属于调用该语法单位时应有的后继符号集合。 若不属于，则滤去后继符号和开始符号集合外的所有符号。
        通过这样的机制，可以在源程序出现错误时， 及时跳过出错的部分，保证语法分析可以继续下去。
        :param s1: firstSet 需要的符号
        :param s2: followSet 不需要的符号，添加一个补救集合
        :param errcode: int  错误号
        :return: 
        """
        if self.sym.symtype not in s1:  # 未通过检测，报错
            Error.strerrno(errcode, self.lex.lineCnt, self.lex.chCount)
            s1 |= s2  # 把s2集合补充进s1集合
            while self.sym.symtype not in s1 and not self.lex.eof:
                # 当检测不通过时，不停地获取符号，直到它属于需要的集合
                self.nextsym()

    def prase(self):
        """
        <程序> ::= <分程序>. 启动语法分析过程，此前必须先调用一次nextsym() 已在构建Praser时调用
        :return: int 运行结果 1成功运行 0编译有错误
        """
        '''
         <程序> ::= <分程序>. FOLLOW(block)={ . }
         <分程序> ::= [<常量说明部分>][<变量说明部分>][<过程说明部分>]<语句>
         FIRST(declaration)={const var procedure null };
         <语句> ::= <赋值语句>|<条件语句>|<当型循环语句>|<过程调用语句>|<读语句>|<写语句>|<复合语句>|<空>
         FIRST(statement)={begin call if while repeat null };
         FIRST(block)=  {const var procedure begin call if while repeat  . }
        '''

        self.block(0, self.declbegsys | self.statbegsys | {Symbol.peroid})  # 调用语法分析器

        if self.sym.symtype != Symbol.peroid:
            Error.strerrno(9, self.lex.lineCnt, self.lex.chCount)

        if Error.errCount == 0:  # 通过总共错误数评估执行结果
            return 1
        else:
            return 0

    def block(self, lev, fsys):
        """
        分析-->分程序
        <分程序> ::= [<常量说明部分>][<变量说明部分>][<过程说明部分>]<语句>
        :param lev: int 当前分程序所在层
        :param fsys: set 当前模块的FOLLOW集合
        :return: 
        """
        dx0 = self.dx  # 记录本层之前的数据量,以便返回时恢复
        tx0 = self.table.tablePtr  # 记录本层符号表的初始位置
        cx0 = 0  # 只是为了符合PEP8 占位
        '''
        初始值置为3
        原因：每一层最开始的位置有三个空间用于存放静态链SL、动态链DL和返回地址RA
        运行时才会填充，编译时仅是留出三个空位
        '''
        self.dx = 3

        # 获取当前pcode代码的地址，即pcode代码在pcode类list里的位置
        self.table.get(self.table.tablePtr).addr = self.interperter.listPtr
        self.interperter.gen(Pcode.JMP, 0, 0)  # 生成pcode，填入0等待回填

        if lev > SymbolTable.levMax:  # 判断嵌套层数是否超过最大限制
            Error.strerrno(32, self.lex.lineCnt, self.lex.chCount)
        # 分析<说明部分>
        while 1:
            # <常量说明部分> ::= const<常量定义>{,<常量定义>};
            if self.sym.symtype == Symbol.constsym:  # const
                self.nextsym()
                self.constDeclaration(lev)  # 分析const
                while self.sym.symtype == Symbol.comma:
                    self.nextsym()
                    self.constDeclaration(lev)

                if self.sym.symtype == Symbol.semicolon:  # 分号表示const声明结束
                    self.nextsym()
                else:
                    Error.strerrno(5, self.lex.lineCnt - 1, self.lex.chCount)

            # <变量说明部分>::=var<标识符>{,<标识符>};
            if self.sym.symtype == Symbol.varsym:
                self.nextsym()
                self.varDeclaration(lev)
                while self.sym.symtype == Symbol.comma:
                    self.nextsym()
                    self.varDeclaration(lev)

                if self.sym.symtype == Symbol.semicolon:  # 分号表示var声明结束
                    self.nextsym()
                else:
                    Error.strerrno(5, self.lex.lineCnt - 1, self.lex.chCount)  # 漏逗号或分号，因为通常在句尾，此时行号会进入下一行，故减一
            '''
             <过程说明部分> ::=  procedure<标识符>; <分程序> ;
             FOLLOW(semicolon)={NULL<过程首部>}，
             需要进行test procedure a; procedure 允许嵌套，故用while
             '''
            while self.sym.symtype == Symbol.procsym:  # procedure开头
                self.nextsym()
                if self.sym.symtype == Symbol.ident:
                    if self.table.enter(self.sym, Item.procedure, lev, self.dx):  # 是标识符就填表
                        Error.strerrno(28,self.lex.lineCnt,self.lex.chCount)
                    self.nextsym()
                else:
                    Error.strerrno(4, self.lex.lineCnt, self.lex.chCount)  # 报错proc后应为标识符
                if self.sym.symtype == Symbol.semicolon:
                    self.nextsym()
                else:
                    Error.strerrno(5, self.lex.lineCnt - 1, self.lex.chCount)  # 漏逗号或分号

                self.block(lev + 1, fsys | {Symbol.semicolon})  # 嵌套+1，处理分程序

                if self.sym.symtype == Symbol.semicolon:  # 分号，说明识别成功
                    self.nextsym()
                    self.test(self.statbegsys | {Symbol.ident, Symbol.procsym}, fsys, 6)  # 测试symtype属于FIRST(statement)
                else:
                    Error.strerrno(5, self.lex.lineCnt - 1, self.lex.chCount)  # 漏逗号或分号

            '''
              FIRST(statement)={begin call if while repeat null };
              FIRST(declaration)={const var procedure null };
              一个分程序的说明部分识别结束后，下面可能是语句statement或者嵌套的procedure（first（block）={各种声明}）
             '''

            self.test(self.statbegsys | {Symbol.ident}, self.declbegsys, 7)

            if self.sym.symtype not in self.declbegsys:  # 没有声明符号为止
                break

        '''
        开始生成当前过程代码
        分程序声明部分完成后，即将进入语句的处理， 这时的代码分配指针cx的值正好指向语句的开始位置，
        这个位置正是前面的jmp指令需要跳转到的位置
         '''
        item = self.table.get(tx0)  # 获取之前JUMP的位置，用于回填
        self.interperter.pcodeList[item.addr].arg = self.interperter.listPtr  # 回填地址
        item.addr = self.interperter.listPtr  # 回填符号表中的地址
        item.size = self.dx  # 回填符号表中的proc大小
        # 声明结束，dx为当前堆栈大小
        # 生成内存分配代码
        self.interperter.gen(Pcode.INT, 0, self.dx)

        # 分析<语句>
        self.statment(fsys | {Symbol.semicolon, Symbol.endsym}, lev)
        # 生成ret指令
        self.interperter.gen(Pcode.OPR, 0, 0)

        self.test(fsys, set(), 8)  # 没有补救集合，检测后面符号正确性

        self.dx = dx0
        self.table.printTable(0)  # 记录这一层符号表
        self.table.tablePtr = tx0  # 恢复符号表指针，因为子程序已经完成

    def constDeclaration(self, lev):
        """
        分析<常量定义>
        <常量定义> ::= <标识符>=<无符号整数>
        :param lev: int 当前所在层次
        :return: 
        """
        if self.sym.symtype == Symbol.ident:
            id = self.sym.id  # 保存标识符名字用于填表
            self.nextsym()
            if self.sym.symtype == Symbol.eql or self.sym.symtype == Symbol.becomes:
                if self.sym.symtype == Symbol.becomes:  # 为：=
                    Error.strerrno(1, self.lex.lineCnt, self.lex.chCount)  # 报错，但把其当=处理
                self.nextsym()
                if self.sym.symtype == Symbol.number:  # 读取到数字
                    self.sym.id = id  # 汇入标识符名字
                    if self.table.enter(self.sym, Item.constant, lev, self.dx):  # 填表
                        Error.strerrno(28, self.lex.lineCnt, self.lex.chCount)
                    self.nextsym()
                else:
                    Error.strerrno(2, self.lex.lineCnt, self.lex.chCount)  # =后应为数字
            else:
                Error.strerrno(3, self.lex.lineCnt, self.lex.chCount)  # 常量后应为=
        else:
            Error.strerrno(4, self.lex.lineCnt, self.lex.chCount)  # const后应为标识符

    def varDeclaration(self, lev):
        """
        分析<标识符>
        <变量说明部分>::= var <标识符> { , <标识符> } ;
        :param lev: int 当前所在层次
        :return: 
        """
        if self.sym.symtype == Symbol.ident:
            if self.table.enter(self.sym, Item.variable, lev, self.dx):  # 填表
                Error.strerrno(28, self.lex.lineCnt, self.lex.chCount)
            self.dx += 1  # 地址+1
            self.nextsym()
        else:
            Error.strerrno(4, self.lex.lineCnt, self.lex.chCount)  # var后应为标识符

    def statment(self, fsys, lev):
        """
        分析<语句>
        :param fsys: set Follow集合
        :param lev: int 当前所在层次
        :return: 
        """
        symtype = self.sym.symtype  # 依据当前token属性进行分析
        if symtype == Symbol.ident:
            self.praseAssign(fsys, lev)
        elif symtype == Symbol.readsym:
            self.praseRead(fsys, lev)
        elif symtype == Symbol.writesym:
            self.praseWrite(fsys, lev)
        elif symtype == Symbol.callsym:
            self.praseCall(fsys, lev)
        elif symtype == Symbol.ifsym:
            self.praseIf(fsys, lev)
        elif symtype == Symbol.beginsym:
            self.praseBegin(fsys, lev)
        elif symtype == Symbol.whilesym:
            self.praseWhile(fsys, lev)
        elif symtype == Symbol.repeatsym:
            self.praseRepeat(fsys, lev)
        else:
            self.test(fsys, set(), 19)  # 无补救措施，检查后续正确性

    def praseAssign(self, fsys, lev):
        """
        分析:=<表达式>
        <赋值语句> ::= <标识符>:=<表达式>
        首先获取赋值号左边的标识符， 从符号表中找到它的信息， 并确认这个标识符确为变量名。 然后通过调用表达式处理过程 算得赋值号右部的表达式的值
        并生成相应的指令 保证这个值放在运行期的数据栈顶。 最后通过前面查到的左部变量的位置信息， 生成相应的sto指令， 把栈顶值存入指定的变量的空间，
        实现了赋值操作。
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        index = self.table.position(self.sym.id)  # 在符号表中查询该标识符
        if index > 0:  # 存在
            item = self.table.get(index)
            if item.type == Item.variable:  # 为变量
                self.nextsym()
                if self.sym.symtype == Symbol.becomes:  # 匹配：=
                    self.nextsym()
                else:
                    Error.strerrno(13, self.lex.lineCnt, self.lex.chCount)  # 应为：=
                self.expression(fsys, lev)  # 处理表达式
                '''
                expression将执行一系列指令，
                但最终结果将会保存在栈顶，
                执行sto命令完成赋值
                '''
                self.interperter.gen(Pcode.STO, lev - item.lev, item.addr)  # 保存到运行站=栈中变量的位置
            else:
                Error.strerrno(12, self.lex.lineCnt, self.lex.chCount)  # 不能向常量，过程名复制
        else:
            Error.strerrno(11, self.lex.lineCnt, self.lex.chCount)  # 标识符未声明

    def praseRead(self, fsys, lev):
        """
        分析'(' <标识符> { , <标识符> } ')'
         <读语句> ::= read '(' <标识符> { , <标识符> } ')' 确定read语句语法合理的前提下（否则报错）， 生成相应的指令：
         第一条是16号操作的opr指令， 实现从标准输入设备上读一个整数值，放在数据栈顶。 第二条是sto指令，
         把栈顶的值存入read语句括号中的变量所在的单元
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        self.nextsym()
        if self.sym.symtype == Symbol.lparen:
            index = 0
            while 1:
                self.nextsym()
                if self.sym.symtype == Symbol.ident:
                    index = self.table.position(self.sym.id)  # 查找标识符位置
                if index == 0:  # 未找到
                    Error.strerrno(35, self.lex.lineCnt, self.lex.chCount)  # 变量未声明
                else:
                    item = self.table.get(index)
                    if item.type != Item.variable:
                        Error.strerrno(15, self.lex.lineCnt, self.lex.chCount)  # 不可以为变量和过程
                    else:
                        self.interperter.gen(Pcode.OPR, 0, 16)  # 读操作到栈顶
                        self.interperter.gen(Pcode.STO, lev - item.lev, item.addr)  # 保存到相对偏移处
                self.nextsym()
                if self.sym.symtype != Symbol.comma:  # 循环处理至无逗号
                    break
        else:
            Error.strerrno(34, self.lex.lineCnt, self.lex.chCount)  # 应为左括号

        if self.sym.symtype == Symbol.rparen:
            self.nextsym()
        else:
            Error.strerrno(33, self.lex.lineCnt, self.lex.chCount)  # 应为右右括号
            while self.sym.symtype not in fsys:  # 不在follow集中，继续读，纠错
                self.nextsym()

    def praseWrite(self, fsys, lev):
        """
        分析'(' <表达式> { , <表达式> } ')'
        <写语句> ::= write '(' <表达式> { , <表达式> } ')' 在语法正确的前提下，生成指令： 通过循环调用表达式处理过程
        分析write语句括号中的每一个表达式， 生成相应指令 保证把表达式的值算出并放到数据栈顶 并生成14号操作的opr指令， 输出表达式的值。
        最后生成15号操作的opr指令，输出一个换行
        :param fsys: set follow集
        :param lev: int 当前所在层次
        :return: 
        """
        self.nextsym()
        if self.sym.symtype == Symbol.lparen:
            while 1:
                self.nextsym()
                self.expression(fsys | {Symbol.rparen, Symbol.comma}, lev)  # follow={，）}
                self.interperter.gen(Pcode.OPR, 0, 14)  # 输出
                if self.sym.symtype != Symbol.comma:  # 直到不为逗号
                    break
            if self.sym.symtype == Symbol.rparen:  # 解析成功
                self.nextsym()
                self.interperter.gen(Pcode.OPR, 0, 15)  # write结束，输出换行
            else:
                Error.strerrno(33, self.lex.lineCnt, self.lex.chCount)  # 应为右括号
        else:
            Error.strerrno(34, self.lex.lineCnt, self.lex.chCount)  # 应为左括号

    def praseCall(self, fsys, lev):
        """
        分析<标识符>
        <过程调用语句> ::= call<标识符>
        从符号表中找到call语句右部的标识符， 获得其所在层次和偏移地址。 然后生成相应的cal指令。 至于调用子过程所需的保护现场等工作
        是由类PCODE解释程序在解释执行cal指令时自动完成的
        :param fsys: set FOLLOW集合
        :param lev: int 当前所在层次
        :return: 
        """
        self.nextsym()
        if self.sym.symtype == Symbol.ident:
            index = self.table.position(self.sym.id)  # 查询是否声明
            if index != 0:
                item = self.table.get(index)
                if item.type == Item.procedure:
                    self.interperter.gen(Pcode.CAL, lev - item.lev, item.addr)  # 生成变量
                else:
                    Error.strerrno(15, self.lex.lineCnt - 1, self.lex.chCount)  # 应为过程
            else:
                Error.strerrno(11, self.lex.lineCnt, self.lex.chCount)  # 未找到标识符
            self.nextsym()
        else:
            Error.strerrno(14, self.lex.lineCnt, self.lex.chCount)  # 应为标识符

    def praseIf(self, fsys, lev):
        """
        分析<条件语句>
        <条件语句> ::= if <条件> then <语句>[else《语句》]
        按if语句的语法，首先调用逻辑表达式处理过程， 处理if语句的条件，把相应的真假值放到数据栈顶。
        接下去记录下代码段分配位置（即下面生成的jpc指令的位置）， 然后生成条件转移jpc指令（遇0或遇假转移）， 转移地址未知暂时填0。
        然后调用语句处理过程处理then语句后面的语句或语句块。 then后的语句处理完后， 当前代码段分配指针的位置就应该是上面的jpc指令的转移位置。
        通过前面记录下的jpc指令的位置， 把它的跳转位置改成当前的代码段指针位置。
        :param fsys: set Follow集合
        :param lev: int 当前所在层次
        :return: 
        """
        self.nextsym()
        self.condition(fsys | {Symbol.thensym, Symbol.dosym}, lev)  # 处理条件
        if self.sym.symtype == Symbol.thensym:
            self.nextsym()
        else:
            Error.strerrno(16, self.lex.lineCnt, self.lex.chCount)  # 少then
        cx1 = self.interperter.listPtr  # 保存当前地址，待回填
        self.interperter.gen(Pcode.JPC, 0, 0)
        self.statment(fsys, lev)  # 处理statement
        self.interperter.pcodeList[cx1].arg = self.interperter.listPtr  # 回填
        if self.sym.symtype == Symbol.elsesym:  # else
            self.interperter.pcodeList[cx1].arg += 1  # 有else，多跳一位
            self.nextsym()
            tmpPtr = self.interperter.listPtr  # 记录，待回填
            self.interperter.gen(Pcode.JMP, 0, 0)
            self.statment(fsys, lev)
            self.interperter.pcodeList[tmpPtr].arg = self.interperter.listPtr  # 回填

    def praseBegin(self, fsys, lev):
        """
        分析<复合语句>
        <复合语句> ::= begin<语句>{;<语句>}end 通过循环遍历begin/end语句块中的每一个语句，
        通过递归调用语句分析过程分析并生成相应代码。
        :param fsys: set Follow集合
        :param lev: int 当前所在层次
        :return: 
        """
        self.nextsym()
        self.statment(fsys | {Symbol.semicolon, Symbol.endsym}, lev)  # FOLLOW(statement)={ ; end }
        # 循环分析{;<语句>},直到下一个符号不是语句开始符号或者收到end
        while self.sym.symtype in self.statbegsys | {Symbol.semicolon}:
            if self.sym.symtype == Symbol.semicolon:
                self.nextsym()
            else:
                Error.strerrno(10, self.lex.lineCnt - 1, self.lex.chCount)  # 缺少分号
            self.statment(fsys | {Symbol.semicolon, Symbol.endsym}, lev)
        if self.sym.symtype == Symbol.endsym:
            self.nextsym()
        else:
            Error.strerrno(17, self.lex.lineCnt - 1, self.lex.chCount)  # 应为分号或end

    def praseWhile(self, fsys, lev):
        """
        分析<当型循环语句>
        <当型循环语句> ::= while<条件>do<语句>
        首先用cx1变量记下当前代码段分配位置， 作为循环的开始位置。 然后处理while语句中的条件表达式生成相应代码把结果放在数据栈顶，
        再用cx2变量记下当前位置， 生成条件转移指令， 转移位置未知，填0。 通过递归调用语句分析过程分析do语句后的语句或语句块并生成相应代码。
        最后生成一条无条件跳转指令jmp，跳转到cx1所指位置， 并把cx2所指的条件跳转指令JPC的跳转位置,改成当前代码段分配位置
        :param fsys: set Follow集合
        :param lev: int 当前所在层次
        :return: 
        """
        cx1 = self.interperter.listPtr  # 记录判断条件地址，待跳转
        self.nextsym()
        self.condition(fsys | {Symbol.dosym}, lev)  # 这里Follow{contiditon}=do
        cx2 = self.interperter.listPtr  # 记录条件结束成功跳转处的地址 待回填
        self.interperter.gen(Pcode.JPC, 0, 0)
        if self.sym.symtype == Symbol.dosym:
            self.nextsym()
        else:
            Error.strerrno(18, self.lex.lineCnt, self.lex.chCount)  # 少do
        self.statment(fsys, lev)
        # print("enter While")
        self.interperter.gen(Pcode.JMP, 0, cx1)  # 跳至while 判断处
        self.interperter.pcodeList[cx2].arg = self.interperter.listPtr  # 回填跳出位置

    def praseRepeat(self, fsys, lev):
        """
        解析<重复语句> ::= repeat<语句>{;<语句>}until<条件>
        :param fsys: set Follow集合
        :param lev: int 当前所在层次
        :return: 
        """
        cx1 = self.interperter.listPtr
        self.nextsym()
        self.statment(fsys, lev)
        while self.sym.symtype in self.statbegsys | {Symbol.semicolon}:
            if self.sym.symtype == Symbol.semicolon:
                self.nextsym()
            else:
                Error.strerrno(34, self.lex.lineCnt, self.lex.chCount)
            self.statment(fsys | {Symbol.semicolon, Symbol.untilsym}, lev)
        if self.sym.symtype == Symbol.untilsym:
            self.nextsym()
            self.condition(fsys, lev)
            self.interperter.gen(Pcode.JPC, 0, cx1)

    def expression(self, fsys, lev):
        """
        分析<表达式>
        <表达式> ::= [+|-]<项>{<加法运算符><项>} 根据PL/0语法可知，
        表达式应该是由正负号或无符号开头、由若干个项以加减号连接而成。 而项是由若干个因子以乘除号连接而成， 因子则可能是一个标识符或一个数字，
        或是一个以括号括起来的子表达式。 根据这样的结构，构造出相应的过程， 递归调用就完成了表达式的处理。
        把项和因子独立开处理解决了加减号与乘除号的优先级问题。 在这几个过程的反复调用中，始终传递fsys变量的值，
        保证可以在出错的情况下跳过出错的符号，使分析过程得以进行下去
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        if self.sym.symtype in [Symbol.plus, Symbol.minus]:
            opraterType = self.sym.symtype
            self.nextsym()
            self.term(fsys | {Symbol.plus, Symbol.minus}, lev)
            if opraterType == Symbol.minus:
                self.interperter.gen(Pcode.OPR, 0, 1)  # 取反
        else:
            self.term(fsys | {Symbol.plus, Symbol.minus}, lev)
        # 分析{<加法运算符><项>}
        while self.sym.symtype in [Symbol.plus, Symbol.minus]:
            opraterType = self.sym.symtype
            self.nextsym()
            self.term(fsys | {Symbol.plus, Symbol.minus}, lev)
            self.interperter.gen(Pcode.OPR, 0, opraterType)

    def condition(self, fsys, lev):
        """
        分析<项>
        <项> ::= <因子>{<乘法运算符><因子>}
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        if self.sym.symtype == Symbol.oddsym:  # 分析odd
            self.nextsym()
            self.expression(fsys, lev)
            self.interperter.gen(Pcode.OPR, 0, 6)
        else:
            # FOLLOW(expression)={  =  !=  <  <=  >  >= }
            self.expression(fsys | {Symbol.eql, Symbol.neq, Symbol.lss, Symbol.leq, Symbol.gtr, Symbol.geq},
                            lev)
            if self.sym.symtype in [Symbol.eql, Symbol.neq, Symbol.lss, Symbol.leq, Symbol.gtr, Symbol.geq]:
                operatorType = self.sym.symtype
                self.nextsym()
                self.expression(fsys, lev)
                self.interperter.gen(Pcode.OPR, 0, operatorType)  # symtype=eql... leq与7... 13相对应
            else:
                Error.strerrno(20, self.lex.lineCnt, self.lex.chCount)  # 应为操作符

    def term(self, fsys, lev):
        """
        分析<项>
        <项> ::= <因子>{<乘法运算符><因子>}
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        # 分析{<乘法运算符><因子>}
        self.factor(fsys | {Symbol.mul, Symbol.div}, lev)
        while self.sym.symtype in [Symbol.mul, Symbol.div]:
            operatorType = self.sym.symtype
            self.nextsym()
            self.factor(fsys | {Symbol.mul, Symbol.div}, lev)
            self.interperter.gen(Pcode.OPR, 0, operatorType)

    def factor(self, fsys, lev):
        """
        分析<因子>
     * <因子>=<标识符>|<无符号整数>|'('<表达式>')' 开始因子处理前，先检查当前token是否在facbegsys集合中。
     * 如果不是合法的token，抛24号错误，并通过fsys集恢复使语法处理可以继续进行
        :param fsys: set Follow集
        :param lev: int 当前所在层次
        :return: 
        """
        self.test(self.facbegsys, fsys, 24)

        if self.sym.symtype in self.facbegsys:
            if self.sym.symtype == Symbol.ident:
                index = self.table.position(self.sym.id)
                if index > 0:
                    item = self.table.get(index)
                    if item.type == Item.constant:
                        self.interperter.gen(Pcode.LIT, 0, item.value)  # 如果这个标识符对应的是常量，值为val，生成lit指令，把val放到栈顶
                    elif item.type == Item.variable:
                        self.interperter.gen(Pcode.LOD, lev - item.lev, item.addr)  # 把位于距离当前层level的层的偏移地址为adr的变量放到栈顶
                    elif item.type == Item.procedure:
                        Error.strerrno(21, self.lex.lineCnt, self.lex.chCount)
                else:
                    Error.strerrno(11, self.lex.lineCnt, self.lex.chCount)
                self.nextsym()
            elif self.sym.symtype == Symbol.number:
                num = self.sym.num
                # print(num)
                if num > SymbolTable.addrMax:
                    Error.strerrno(31, self.lex.lineCnt, self.lex.chCount)
                    num = 0
                self.interperter.gen(Pcode.LIT, 0, num)
                self.nextsym()
            elif self.sym.symtype == Symbol.lparen:
                self.nextsym()
                self.expression(fsys | {Symbol.rparen}, lev)
                if self.sym.symtype == Symbol.rparen:
                    self.nextsym()
                else:
                    Error.strerrno(22, self.lex.lineCnt, self.lex.chCount)
            else:
                self.test(fsys, self.facbegsys, 23)
