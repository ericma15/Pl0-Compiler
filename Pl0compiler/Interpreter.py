from .Pcode import Pcode


class Interpreter:
    """
    解释器类，包括生成函数和解释函数
    """
    stackSize = 1000  # 运行栈上限
    listswitch = True  # 显示Pcode与否，仅在命令行模式生效

    def __init__(self):
        self.pcodeList = []
        self.listPtr = 0  # 虚拟机代码指针初始为栈底

    def gen(self, f, l, a):
        """
        生成虚拟机代码
        :param f: Pcode.fun
        :param l: Pcode.lev
        :param a: Pcode.arg
        :return: 
        """
        self.pcodeList.append(Pcode(f, l, a))
        self.listPtr += 1

    def listcode(self, start):
        """
        输出Pcode
        :param start: int 起始位置
        :return: 
        """
        if Interpreter.listswitch:
            i = start
            while i < self.listPtr:
                print(str(i) + " " + self.pcodeList[i].toString())
                i += 1

    def interperter(self, pcodeList):
        """
        运行Pcode虚拟机，这里写了两个，一个运行栈有限，一个运行栈无限，默认调有限
        :param pcodeList: 代码list code list 
        :return: 
        """
        try:
            self.interperter3(pcodeList)
            # self.interperter2(pcodeList)
        except:
            self.errorshow("stack overflow!")

    def interperter3(self, pcodeList):
        """
        这个过程模拟了一台可以运行类PCODE指令的栈式计算机。 它拥有一个栈式数据段用于存放运行期数据, 拥有一个代码段用于存放类PCODE程序代码。
        同时还拥用数据段分配指针、指令指针、指令寄存器、局部段基址指针等寄存器。
        :param pcodeList: 
        :return: 
        """
        pc = 0  # pc:指令指针，
        bp = 0  # bp:指令基址，
        sp = 0  # sp:栈指针
        runtimeStack = [0 for i in range(Interpreter.stackSize)]
        while 1:
            command = pcodeList[pc]
            pc += 1

            fun = command.fun
            arg = command.arg
            if fun == Pcode.LIT:
                runtimeStack[sp] = arg
                sp += 1
            elif fun == Pcode.OPR:
                if arg == 0:
                    sp = bp
                    pc = runtimeStack[sp + 2]
                    bp = runtimeStack[sp + 1]
                elif arg == 1:
                    runtimeStack[sp - 1] = -runtimeStack[sp - 1]
                elif arg == 2:
                    sp -= 1
                    runtimeStack[sp - 1] += runtimeStack[sp]
                elif arg == 3:
                    sp -= 1
                    runtimeStack[sp - 1] -= runtimeStack[sp]
                elif arg == 4:
                    sp -= 1
                    runtimeStack[sp - 1] *= runtimeStack[sp]
                elif arg == 5:
                    sp -= 1
                    tem = runtimeStack[sp]
                    if tem == 0:
                        self.errorshow("RuntimeError: Div 0")
                        return 1
                    runtimeStack[sp - 1] //= tem
                elif arg == 6:
                    runtimeStack[sp - 1] %= 2
                elif arg == 7:
                    self.errorshow("Undefined operator,maybe youmean %")
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[sp - 1] %= tem
                elif arg == 8:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] == runtimeStack[sp] else 0
                elif arg == 9:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] != runtimeStack[sp] else 0
                elif arg == 10:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] < runtimeStack[sp] else 0
                elif arg == 11:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] >= runtimeStack[sp] else 0
                elif arg == 12:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] > runtimeStack[sp] else 0
                elif arg == 13:
                    sp -= 1
                    runtimeStack[sp - 1] = 1 if runtimeStack[sp - 1] <= runtimeStack[sp] else 0
                elif arg == 14:
                    self.printRun(runtimeStack[sp - 1], 0)
                    sp -= 1
                elif arg == 15:
                    self.printRun(0, 1)
                elif arg == 16:
                    try:
                        tem = self.readNum()
                        self.printInstruct(str(tem) + "\n\n")
                        runtimeStack[sp] = tem
                        sp += 1
                    except Exception as e:
                        print(e.args)
                        runtimeStack[sp] = 0
                        sp += 1
                else:
                    self.errorshow("不存在的参数")
            elif fun == Pcode.LOD:
                runtimeStack[sp] = runtimeStack[self.base(command.level, runtimeStack, bp) + arg]
                sp += 1
            elif fun == Pcode.STO:
                sp -= 1
                runtimeStack[self.base(command.level, runtimeStack, bp) + arg] = runtimeStack[sp]
            elif fun == Pcode.CAL:
                runtimeStack[sp] = self.base(command.level, runtimeStack, bp)
                runtimeStack[sp + 1] = bp
                runtimeStack[sp + 2] = pc
                bp = sp
                pc = arg
            elif fun == Pcode.INT:
                sp += arg
            elif fun == Pcode.JMP:
                pc = arg
            elif fun == Pcode.JPC:
                sp -= 1
                if runtimeStack[sp] == 0:
                    pc = arg
            else:
                self.errorshow("不存在的操作符")
            if pc == 0:
                self.printInstruct("运行结束")
                break

    def interperter2(self, pcodeList):
        runtimeStack = []
        pc = 0
        bp = 0
        sp = 0
        while 1:
            command = pcodeList[pc]
            pc += 1
            fun = command.fun
            arg = command.arg
            if fun == Pcode.LIT:
                runtimeStack.append(arg)
                sp += 1
            elif fun == Pcode.OPR:
                if arg == 0:
                    sp = bp
                    pc = runtimeStack[sp + 2]
                    bp = runtimeStack[sp + 1]
                    runtimeStack = runtimeStack[0:sp]
                elif arg == 1:
                    runtimeStack[-1] = -runtimeStack[-1]
                elif arg == 2:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] += tem
                elif arg == 3:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] -= tem
                elif arg == 4:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] *= tem
                elif arg == 5:
                    sp -= 1
                    tem = runtimeStack.pop()
                    if tem == 0:
                        self.errorshow("RuntimeError: Div 0")
                        return 1
                    runtimeStack[-1] //= tem
                elif arg == 6:
                    runtimeStack[-1] %= 2
                elif arg == 7:
                    self.errorshow("Undefined operator,maybe youmean %")
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] %= tem
                elif arg == 8:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] == tem else 0
                elif arg == 9:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] != tem else 0
                elif arg == 10:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] < tem else 0
                elif arg == 11:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] >= tem else 0
                elif arg == 12:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] > tem else 0
                elif arg == 13:
                    sp -= 1
                    tem = runtimeStack.pop()
                    runtimeStack[-1] = 1 if runtimeStack[-1] <= tem else 0
                elif arg == 14:
                    self.printRun(runtimeStack[-1], 0)
                    runtimeStack.pop()
                    sp -= 1
                elif arg == 15:
                    self.printRun(0, 1)
                elif arg == 16:
                    try:
                        tem = self.readNum()
                        self.printInstruct(str(tem) + "\n\n")
                        runtimeStack.append(tem)
                        sp += 1
                    except Exception as e:
                        print(e.args)
                        runtimeStack.append(0)
                        sp += 1
                else:
                    self.errorshow("不存在的参数")
            elif fun == Pcode.LOD:
                tem = runtimeStack[self.base(command.level, runtimeStack, bp) + arg]
                runtimeStack.append(tem)
                sp += 1
            elif fun == Pcode.STO:

                runtimeStack[self.base(command.level, runtimeStack, bp) + arg] = runtimeStack[-1]
                runtimeStack.pop()
                sp -= 1
            elif fun == Pcode.CAL:
                runtimeStack.append(self.base(command.level, runtimeStack, bp))
                runtimeStack.append(bp)
                runtimeStack.append(pc)
                bp = sp
                pc = arg
            elif fun == Pcode.INT:
                sp += arg
                runtimeStack.extend([0] * (sp - len(runtimeStack)))
            elif fun == Pcode.JMP:
                pc = arg
            elif fun == Pcode.JPC:
                sp -= 1
                if runtimeStack.pop() == 0:
                    pc = arg
            else:
                self.errorshow("不存在的操作符")
            if pc == 0:
                self.printInstruct("运行结束")
                break

    def readNum(self):
        while 1:
            try:
                return int(input("请输入一个整数"))
            except:
                pass

    def errorshow(self, errormsg):
        print(errormsg)

    def printInstruct(self, msg):
        print(msg, end="")

    def printRun(self, num, status):
        if status == 1:
            print("")
        else:
            print(num, end="")

    def base(self, level, runtimeStack, bp):
        """
        通过给定的层次差来获得该层的堆栈帧基址
        :param level: 目标层次与当前层次的层次差
        :param runtimeStack: runtimeStack 运行栈
        :param bp: 当前层堆栈帧基地址
        :return: 目标层次的堆栈帧基地址
        """
        while level > 0:
            bp = runtimeStack[bp]
            level -= 1
        return bp
