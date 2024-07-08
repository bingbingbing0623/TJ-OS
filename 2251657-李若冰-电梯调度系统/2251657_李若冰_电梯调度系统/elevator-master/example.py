from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QLCDNumber, QPushButton, QApplication
)
from PyQt5.QtCore import pyqtSignal, QObject

# 信号机制
class Msg:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# 继承自 QObject 类，用于连接到 Qt 框架的信号槽机制
class Linktoqt(QObject):
    sendMsg = pyqtSignal(str)  # 发送字符串类型信号

    def __init__(self):
        super().__init__()

floor_send = Linktoqt()  # 楼层消息，传递给lcd显示屏
opendoor_send = Linktoqt()  # 开门信息，传递button信息
closedoor_send = Linktoqt()  # 关门信息，传递button信息

# 信息队列
exitFlag_1 = []
exitFlag_2 = []
exitFlag_3 = []
exitFlag_4 = []
exitFlag_5 = []
exitFlag = [exitFlag_1, exitFlag_2, exitFlag_3, exitFlag_4, exitFlag_5]
MsgQueue_1 = []
MsgQueue_2 = []
MsgQueue_3 = []
MsgQueue_4 = []
MsgQueue_5 = []
MsgQueue = [MsgQueue_1, MsgQueue_2, MsgQueue_3, MsgQueue_4, MsgQueue_5]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.lcd = []  # 有五个显示屏
        self.element_button = []  # 先实现一部电梯的按钮
        self.initUI()

    def initUI(self):
        global MsgQueue, exitFlag
        grid = QGridLayout()
        self.setLayout(grid)

        # 整体布局
        positions = [(i, j) for i in range(1, 23) for j in range(1, 9)]
        lift_pos = [(i, j) for i in range(1, 21) for j in range(4, 9)]
        open_pos = [(i, j) for i in range(21, 23) for j in range(4, 9)]

        # 增加lcd显示屏
        for i in range(5):
            self.lcd.append(QLCDNumber(self))
            self.lcd[i].setDigitCount(2)
            self.lcd[i].display(1)
            grid.addWidget(self.lcd[i], *(23, i + 4))
            self.lcd[i].setStyleSheet(
                "color: black; background-color: white; border: 2px solid black;")

        floor_send.sendMsg.connect(self.slot_hand)

        # 创建一系列按钮
        left_names = ['', '20\/',
                     '19/\\', '19\/',
                     '18/\\', '18\/',
                     '17/\\', '17\/',
                     '16/\\', '16\/',
                     '15/\\', '15\/',
                     '14/\\', '14\/',
                     '13/\\', '13\/',
                     '12/\\', '12\/',
                     '11/\\', '11\/',
                     '10/\\', '10\/',
                     '09/\\', '09\/',
                     '08/\\', '08\/',
                     '07/\\', '07\/',
                     '06/\\', '06\/',
                     '05/\\', '05\/',
                     '04/\\', '04\/',
                     '03/\\', '03\/',
                     '02/\\', '02\/',
                     '01/\\', '',
                     ]
        cmd_names = ['open_1', 'close_1',
                     'open_2', 'close_2',
                     'open_3', 'close_3',
                     'open_4', 'close_4',
                     'open_5', 'close_5',
                     ]

        for position in positions:
            if position[1] < 3 and position[0] < 21:
                pos = position[1] - 1 + (position[0] - 1) * 2
                button = QPushButton()
                button.setText(left_names[pos])
                button.setStyleSheet(
                    "color: white; background-color: #4CAF50; border: 2px solid #4CAF50; border-radius: 4px;")
                button.clicked.connect(self.up_down_button_clicked)
                grid.addWidget(button, *position)

            if position[1] == 3:
                continue

            if position[1] > 3 and position[0] < 21:
                floor_button = QPushButton()
                floor_button.setText(str(21 - position[0]))
                floor_button.setStyleSheet(
                    "color: white; background-color: #2196F3; border: 2px solid #2196F3; border-radius: 4px;")
                floor_button.clicked.connect(self.floor_clicked)
                self.element_button.append(floor_button)
                grid.addWidget(floor_button, *position)

            if position in open_pos:
                o_pos = (position[1] - 4) * 2 + position[0] - 21
                btn = QPushButton()
                btn.setText(cmd_names[o_pos])
                btn.setStyleSheet(
                    "color: white; background-color: #f44336; border: 2px solid #f44336; border-radius: 4px;")
                btn.clicked.connect(self.open_close_button_clicked)
                grid.addWidget(btn, *position)

        opendoor_send.sendMsg.connect(self.opendoor)  # 接收开门信息
        closedoor_send.sendMsg.connect(self.closedoor)  # 接收关门信息

        self.move(300, 150)
        self.setWindowTitle('Elevator')
        self.show()

    def opendoor(self, msg):  # 开门，将按钮设为绿色
        id = int(msg[0])
        floor_value = int(msg[1:])
        floor_num = (20 - floor_value) * 5 + id
        self.element_button[floor_num].setStyleSheet(
            "color: white; background-color: green; border: 2px solid green; border-radius: 4px;")

    def closedoor(self, msg):  # 关门，将按钮设为原来颜色
        id = int(msg[0])
        floor_value = int(msg[1:])
        floor_num = (20 - floor_value) * 5 + id
        self.element_button[floor_num].setStyleSheet(
            "color: white; background-color: #2196F3; border: 2px solid #2196F3; border-radius: 4px;")

    def slot_hand(self, msg):    # 回调函数，收到消息之后将显示屏上的值更改
        id = int(msg[0])
        floor_value = 1
        if int(msg) < 100:
            floor_value = int(msg) % 10
        else:
            floor_value = int(msg) % 100

        self.lcd[id].display(floor_value)

    def up_down_button_clicked(self):   # 上下楼按钮槽函数
        sender = self.sender()
        txt = sender.text()
        # 如果在20层按上/1层按下，都是不被允许的
        if txt == '':
            print('不被允许！！')
            return
        type = 0
        value = 0
        if txt.endswith('\\'):
            type = 2
            value = int(txt[0] + txt[1])
        elif txt.endswith('/'):
            type = 3
            value = int(txt[0] + txt[1])
        m = Msg(type, value)
        for i in range(5):
            MsgQueue[i].append(m)

    def floor_clicked(self):
        try:
            sender = self.sender()
            txt = sender.text()
            idx = self.layout().indexOf(sender)  # 获取按钮在布局中的索引
            position = self.layout().getItemPosition(idx)
            id = int(position[1] - 4)
            value = int(txt)
            m = Msg(1, value)
            MsgQueue[id].append(m)
        except Exception as e:
            print("发生错误，电梯号:", id)
            print(e)
    def open_close_button_clicked(self):
        sender = self.sender()
        txt = sender.text()
        idx = self.layout().indexOf(sender)  # 获取按钮在布局中的索引
        position = self.layout().getItemPosition(idx)
        id = int(position[1] - 4)
        value = 0
        if txt.startswith('o'):
            value = int(txt.split('_')[1]) 
            m = Msg(0, value)
        elif txt.startswith('c'):
            value = int(txt.split('_')[1])
            m = Msg(1, value)  
        for i in range(5):
            MsgQueue[id].append(m)




