class Symbol:
    """
    符号类，定义记录符号信息
    """
    '''
    各类符号编码
    '''
    nul = 0  # NULL
    ident = 1  # 标识符
    plus = 2  # 加号 +
    minus = 3  # 减号 -
    mul = 4  # 乘号 *
    div = 5  # 除号 /
    oddsym = 6  # odd
    number = 7  # 数字
    eql = 8  # 等于号 = (equal)
    neq = 9  # 不等于 <> (not equal)
    lss = 10  # 小于 < (less)
    geq = 11  # 大于等于 >= (greater or equal)
    gtr = 12  # 大于 > (greater)
    leq = 13  # 小于等于 <= (less or equal)
    lparen = 14  # 左括号(
    rparen = 15  # 右括号 )
    comma = 16  # 逗号,
    semicolon = 17  # 分号
    peroid = 18  # 句号.
    becomes = 19  # 赋值符号: =
    beginsym = 20  # 开始符号begin
    endsym = 21  # 结束符号end
    ifsym = 22  # if
    thensym = 23  # then
    whilesym = 24  # while
    writesym = 25  # write
    readsym = 26  # read
    dosym = 27  # do
    callsym = 28  # call
    constsym = 29  # const
    varsym = 30  # var
    procsym = 31  # procedure
    elsesym = 32
    repeatsym = 33
    untilsym = 34

    symnum = 35  # 符号码个数

    # 关键字名字，供词法分析器匹配关键字用
    word = ["begin", "call", "const", "do",
            "else", "end", "if", "odd",
            "procedure", "read", "repeat", "then",
            "until", "var", "while", "write"]
    # 符号类型，与上面一一对应
    wsym = [beginsym, callsym, constsym, dosym,
            elsesym, endsym, ifsym, oddsym,
            procsym, readsym, repeatsym, thensym,
            untilsym, varsym, whilesym, writesym]

    def __init__(self, type):
        """
        初始化函数
        :param type: 符号编码
        """
        self.symtype = type  # 符号码
        self.id = ""  # 符号名字
        self.num = 0  # 数值大小
