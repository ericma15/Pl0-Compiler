

class Error:
    """
    错误类
    所有变量均为static
    """
    errCount = 0 #总共错误个数
    errinfo="" #错误信息 html
    errorinfo = ["", #错误具体信息
                 "1.应是=而不是:=",
                 "2.=后应为数",
                 "3.标识符后应为=",
                 "4.const,var,procedure 后应为标识符",
                 "5.漏掉逗号或分号",
                 "6.过程说明后的符号不正确",
                 "7.应为语句",
                 "8.程序体内语句后的符号不正确",
                 "9.应为句号",
                 "10.语句之间漏分号",
                 "11.标识符未说明",
                 "12.不可向常量或过程名赋值",
                 "13.应为赋值运算符:=",
                 "14.call后应为标识符",
                 "15.不可调用常量或过程",
                 "16.应为then",
                 "17.应为分号或end",
                 "18.应为do",
                 "19.语句后的符号不正确",
                 "20.应为关系运算符",
                 "21.表达式内不可有过程标识符",
                 "22.漏右括号",
                 "23.因子后不可为此符号",
                 "24.表达式不能以此符号开始",
                 "25.这个数太大",
                 "26.符号表过大",
                 "27.不存在的符号",
                 "28.同级变量或常量重名",
                 "29.Not Defined Yet",
                 "30.Not Defined Yet",
                 "31.数越界",
                 "32.嵌套层数过大",
                 "33.格式错误，应为右括号",
                 "34.格式错误，应为左括号",
                 "35.read()中的变量未声明"]

    def __init__(self):
        pass

    @staticmethod
    def strerrno(errcode, line,col):
        """
        错误输出程序，将当前错误存入errorinfo
        :param errcode: int 错误编码
        :param line: int 出现错误的行号
        :param col:  int 出现错误的位置
        :return: 
        """
        Error.errCount+=1#错误计数加1
        #由于Ui中行号计数从0开始，所以href中line-1 ，但显示仍为line
        Error.errinfo+="Complier meet a erro at line <strong><a href=" + str(line-1) +'">'+str(line)+ "</a></strong> col <strong>"+str(col)+'</strong> errorinfo:<br> <font color="#FF0000">' + Error.errorinfo[errcode]+"</font><br>"

