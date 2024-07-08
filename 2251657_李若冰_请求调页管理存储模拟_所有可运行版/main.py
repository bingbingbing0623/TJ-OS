import sys
import time
import Window
from PyQt5.QtCore import QThread, pyqtSignal, QSemaphore, QTimer, QCoreApplication, Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow
from task import Task
from managing import MyManager

run_mode_sem = QSemaphore(1)
run_mode = 0

# 重置标识
reset_flag_sem = QSemaphore(1)
reset_flag = 0


# 信号量申请
def p(sem):
    sem.acquire()


# 信号量释放
def v(sem):
    sem.release()

# 连续执行按钮的响应函数
def setContinuousMode():
    global run_mode
    p(run_mode_sem)
    run_mode = 2
    v(run_mode_sem)


# 重置按钮的响应函数
def reSet():
    global reset_flag
    p(reset_flag_sem)
    reset_flag = 1
    v(reset_flag_sem)


# 用于实现按钮颜色变化后恢复原样的效果
def buttonColorReturn(button):
    button.setStyleSheet("background-color: #e1e1e1")


# 更新界面
def update(code_num, cur_code, need_swap, old_page, code_page, memory_page, page_missing, page_size, code_amount):
    ui.label_8.setText(str(code_num))
    if need_swap:  # 发生缺页执行了换页
        ui.label_16.setText(str(page_missing))
        eval("ui.label_" + str(memory_page + 12)).setText(("第" + str(code_page).ljust(2) + "页").ljust(4))
        for i in range(1, 11):
            eval("ui.pushButton_" + str(memory_page * 10 + i+2)).setText(str(code_page * page_size + i - 1))
        # 更新缺页率文本
    ui.label_10.setText(str("{:.2f}".format(page_missing / (code_num + 1) * 100)) + "%")

    if (code_num + 1) >= code_amount:  # 任务完成则打印完成信息
        ui.label_17.setText("已完成全部指令！！！")
    # 对代表本次Task所执行的代码所在的按钮进行红色高亮标识 并恢复原样
    button = eval("ui.pushButton_" + str(memory_page * 10 + cur_code % page_size + 3))
    button.setStyleSheet("background-color: #e16060")
    QTimer.singleShot(100, lambda: buttonColorReturn(button))



# 重置界面
def clear():
    # 重置文本与按钮
    for i in range(1, 5):
        eval("ui.label_" + str(i+11)).setText("第0页")
    for j in range(0, 4):
        for i in range(1, 11):
            eval("ui.pushButton_" + str(j * 10 + i+2)).setText(" ")


# 模拟程序主体
class MyThread(QThread):
    my_trigger_update = pyqtSignal(int, int, bool, int, int, int, int, int, int)
    my_trigger_clear = pyqtSignal()

    def __init__(self):
        super(MyThread, self).__init__()
        self.tmp_reset_flag = None
        self.my_trigger_update.connect(update)
        self.my_trigger_clear.connect(clear)

    # 检查用户是否点击了重置按钮并执行重置
    def checkReset(self):
        global reset_flag
        p(reset_flag_sem)
        if reset_flag:  # 每一步开始前检查reset，确认重置则清空界面并退出当前任务
            reset_flag = 0  # 仅这个位置的reset检查会复位reset并清空界面，下方循环内的reset检查仅用于退出循环
            v(reset_flag_sem)
            self.my_trigger_clear.emit()  # 调用重置函数
            return True
        v(reset_flag_sem)
        return False


    def waitingFirstModeSet(self):
        global run_mode
        while True:  # 等待用户第一次输入执行方式以开始模拟
            p(run_mode_sem)
            if run_mode == 2:
                v(run_mode_sem)
                break
            v(run_mode_sem)

    # 模拟过程中等待用户输入运行模式
    def waitingModeSet(self):
        global run_mode
        while True:  # 当前步的运行模式检查与等待输入。如果是一次模拟级循环中的第一次执行到这里，则前面已获取用户的第一次输入
            p(run_mode_sem)
            if run_mode == 2:  # 连续执行模式则直接退出循环，执行完下方模拟回到这里后再次直接退出循环，实现连续执行
                v(run_mode_sem)
                break
            v(run_mode_sem)

            p(reset_flag_sem)
            # 当处于连续执行模式时，会直接退出循环，则连续执行模式下可以由外部任务级循环的头部来检查是否设定了重置
            if reset_flag:
                v(reset_flag_sem)
                self.tmp_reset_flag = True  # 用于退出两层循环
                break
            v(reset_flag_sem)

    def run(self):
        while True:  # 模拟级循环
            # 初始化运行模式 准备读取用户的第一次输入以启动模拟
            global run_mode
            p(run_mode_sem)
            run_mode = 0
            v(run_mode_sem)

            # 等待用户第一次输入执行方式以开始模拟
            self.waitingFirstModeSet()

            # 初始化全局变量 这部分不可以放到上面的waitingFirstModeSet的前面执行
            # 上方的waitingFirstModeSet中，在等待用户输入的同时，用户可能点击reset按钮，所以必须在这里将reset重置
            global reset_flag
            p(reset_flag_sem)
            reset_flag = 0
            v(reset_flag_sem)

            # 模拟参数初始化
            page_size = 10  # 一个页面可以存放的指令数
            code_amount = 320  # 从用户输入读取任务代码数
            page_swap_algo = ui.comboBox.currentText()  # 从用户输入读取所选算法

            # 任务初始化
            task = Task(page_size=page_size, code_amount=code_amount)
            # 管理器初始化 传入不同的算法参数 则后续调用runTask时执行不同的算法
            manager = MyManager(page_size=page_size, algo=page_swap_algo)
            # 缺页数初始化
            page_missing = 0

            # 初始化用于退出两层循环的标志
            self.tmp_reset_flag = False

            while True:  # 任务级循环
                # 检查是否设定了重置
                if self.checkReset():
                    break
                # 等待用户设定模式
                self.waitingModeSet()
                if self.tmp_reset_flag:  # 上方waitingModeSet中读取到用户设定了reset
                    self.tmp_reset_flag = False
                    # 回到任务级循环的头部 由头部进行界面清空并退出任务级循环
                    # 如果将continue改成break，则会回到模拟级循环的头部，此时reset_flag会被重新初始化成0，则任务级循环的头部无法进行界面的清空
                    continue

                # 根据设定的调页算法进行Task代码执行，并进行内存分配或页面调换，并获取Task代码执行情况与调页情况
                log_code_num, log_cur_code, log_page_missing, log_old_page, log_code_page, log_memory_page = manager.runTask(task)

                if log_page_missing:  # 发生缺页执行了换页
                    page_missing = page_missing + 1
                if log_code_num >= (code_amount - 1):  # 运行完设定的Task的所有代码
                    p(reset_flag_sem)
                    reset_flag = 1  # 设定重置，执行完下面的界面更新回到任务级循环后即由头部执行页面清空并退出任务级循环
                    v(reset_flag_sem)
                # 更新界面
                self.my_trigger_update.emit(log_code_num, log_cur_code, log_page_missing, log_old_page, log_code_page, log_memory_page, page_missing, page_size, code_amount)
                time.sleep(0.1)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 解决高分辨率屏幕显示出错的问题
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    ui = Window.Ui_MainWindow()
    ui.setupUi(main_window)

    ui.pushButton.clicked.connect(setContinuousMode)
    ui.pushButton_2.clicked.connect(reSet)

    thread = MyThread()
    thread.start()

    main_window.show()
    sys.exit(app.exec_())
