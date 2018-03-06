


class Item:
    """
    符号表单项类
    """
    '''
    定义三种特殊符号类型
    '''
    constant = 0
    variable = 1
    procedure = 2
    typeName = ["constant", "variable", "procedure"]

    def __init__(self, name, type):
        """
        初始化符号表的一项，用于填表以及打印
        :param name: Symbol.id 符号名字
        :param type: Item定义的三种类型
        """
        self.name = name
        self.type = type
        self.value = 0
        self.lev = 0
        self.addr = 0
        self.size = 0

    def printItem(self):
        """
        在终端输出当前符号表项
        :return: 
        """
        print(self.name + "\t" + Item.typeName[self.type] + "\t" + str(self.value) + "\t" + str(self.lev) + "\t" + str(self.addr) + "\t" + str(self.size))

    def showItem(self):
        """
        返回当前符号表当前表项
        :return: str-html table
        """

        return "<tr><td>" + self.name + "</td> <td>" + Item.typeName[self.type] + "</td> <td>" + str(
        self.value) + "</td> <td>" + str(self.lev) + "</td> <td>" + str(self.addr) + "</td> <td>" + str(
        self.size) + "</td></tr>"


class SymbolTable:
    """
    符号表类

    """

    tableMax = 500  # 符号表的大小
    symMax = 10  # 符号的最大长度
    addrMax = 1000000  # 最大允许的数值
    levMax = 3  # 最大允许过程嵌套声明层数[0, levmax]
    numMax = 14  # number的最大位数
    tableswitch = True  # 显示名字表与否，仅在命令行模式生效

    def __init__(self):
        """
        初始化符号表，填入用于占位的第0项
        """
        self.table = [Item("", 0)]
        self.tableshow = []  # 用于记录Ui模式需要返回的html 表格
        self.tablePtr = 0  # 当前符号表项指针

    def get(self, i):
        """
        获取符号表某一项内容
        :param i: 符号表中的位置
        :return: Item 符号表中第i项符号表项
        """
        if i > SymbolTable.tableMax:  # 由于python特性，这里仅提示，不禁止
            print("warning:符号表过大")
        return self.table[i]

    def enter(self, sym, type, lev, dx):
        """
        将一个符号填入符号表中，从第1项开始填
        :param sym: Symbol 填入的符号
        :param type: 填入符号类型，定义在Item类中
        :param lev: 符号所在层次
        :param dx: 当前应分配的变量的相对地址
        :return: 
        """
        if self.findDuplicateName(sym.id,lev):
            return 1
        self.tablePtr += 1
        item = Item(sym.id, type)
        item.name = sym.id
        item.type = type
        if type == Item.constant:
            item.value = sym.num
        elif type == Item.variable:
            item.lev = lev
            item.addr = dx
        elif type == Item.procedure:
            item.lev = lev
        if self.tablePtr < len(self.table):  # 指针不在末尾，直接填入，在末尾则需要扩充符号表大小
            self.table[self.tablePtr] = item
        else:
            self.table.append(item)
        return 0
    def findDuplicateName(self,name,lev):
        for i in self.table[1:self.tablePtr+1][::-1]:
            if i.lev<lev:
                return 0
            if i.name==name and i.lev==lev:
                return 1
    def position(self, name):
        """
        在符号表中查找一个符号名字位置，返回其下标，从后向前查
        :param name: Symbol.id str 要查找的名字
        :return: int 符号项下表，不存在返回0
        """
        for index, i in enumerate(self.table[1:self.tablePtr + 1][::-1]):  # 通过切片操作获得符号表当前有效项，并反序
            if i.name == name:
                return self.tablePtr - index  # 计算下标位置
        return 0  # w未找到，返回0

    def printTable(self, start):
        """
        填充符号表
        :param start: 符号表起始下标，打印全部即设为0
        :return: 
        """
        if not self.tableswitch:
            return
        table = "<table border='1' cellpadding='10' width='100%'><tr>   <td>标识符名称</td>   <td>类型</td>   <td>值</td>    <td>层次</td>   <td>地址</td> <td>大小</td></tr>"
        if start > self.tablePtr:
            pass
        for i in self.table[start + 1:self.tablePtr + 1]:
            table += i.showItem()
        table += "</table>"
        self.tableshow += [table]
