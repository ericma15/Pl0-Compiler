

class Pcode:
    """
    pcode类
    """
    #Pcode内部指令
    LIT = 0
    OPR = 1
    LOD = 2
    STO = 3
    CAL = 4
    INT = 5
    JMP = 6
    JPC = 7
    #指令名称
    PcodeNameList = ["LIT", "OPR", "LOD", "STO", "CAL", "INT", "JMP", "JPC"]

    def __init__(self, fun, level, arg):
        """
        初始化一条指令
        :param fun: int 为Pcode指令在PcodeNameList在的位置下标
        :param level: 引用层与声明层的层次差
        :param arg: 指令参数
        """
        self.fun = fun
        self.level = level
        self.arg = arg

    def toString(self):
        """
        返回当前指令
        :return: str Pcode指令
        """
        return Pcode.PcodeNameList[self.fun] + " " + str(self.level) + " " + str(self.arg)
