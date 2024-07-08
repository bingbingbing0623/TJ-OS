import sys
import threading
import time
from elevator import Elevator
from PyQt5.QtWidgets import (QApplication)
from example import floor_send,opendoor_send,closedoor_send,Example,exitFlag,MsgQueue


TOP = 20
BOTTOM = 1
STATE = {0: "门停开着", 1: "门停关着", 2: "电梯上升", 3: "电梯下降"}
DIR = {0: "向下", 1: "向上"}

lock = threading.Lock()#线程锁

#创建五个电梯，放在列表里面
elevators=[]
for i in range(5):
    elevators.append(Elevator(i))

def closed(state, cur, d,id):

    if d == 1:
        if startup(cur,d,id):
            state = 2
        else:
            d = 0
            if startup(cur,d,id):
                state = 3
            else:
                return state,cur,d
    else:
        if startup(cur,d,id):
            state = 3
        else:
            d = 1
            if startup(cur,d,id):
                state = 2
            else:
                return state,cur,d
    return state,cur,d


def up(state,cur,d,id):
    while True:
        state = state
        if stop(cur,d,id):
            state = 1
            print("电梯当前状态:%s,楼层:%d,方向：%s" % (STATE[state], cur, DIR[d]))
            break
        cur +=1
        print("正在前往第%d层" % cur)
        floor_send.sendMsg.emit(str(id)+str(cur))
        time.sleep(2)
    return state,cur,d


def down(state, cur, d, id):
    while True:
        state = state
        if stop(cur, d, id):  # 检查是否应该停止
            state = 1
            print("电梯当前状态:%s,楼层:%d,方向：%s" % (STATE[state], cur, DIR[d]))
            break
        cur -= 1  # 向下移动
        print("正在前往第%d层" % cur)
        floor_send.sendMsg.emit(str(id) + str(cur))
        time.sleep(2)
    return state, cur, d


def startup(cur, d, id):
    global MsgQueue
    for m in MsgQueue[id]:
        if m.type in {1, 2, 3} and m.value > cur and d == 1:
            return True
        if m.type in {1, 2, 3} and m.value < cur and d == 0:
            return True
    return False


def stop(cur, d, id):
    global MsgQueue
    tmp = False
    tmplist = MsgQueue[id][:]
    if d == 1:  # 向上运行时的停止条件
        if cur == TOP:
            tmp = True
        for m in MsgQueue[id]:
            if m.type in {1, 2, 3} and m.value == cur:
                tmp = True
                tmplist.remove(m)
    elif d == 0:  # 向下运行时的停止条件
        if cur == BOTTOM:
            tmp = True
        for m in MsgQueue[id]:
            if m.type in {1, 2, 3} and m.value == cur:
                tmp = True
                tmplist.remove(m)
    MsgQueue[id] = tmplist[:]
    return tmp

def closeThread(arg):
    global exitFlag
    print("正在关门...")
    if exitFlag[arg] != [1]:
        print("关门终止")
    time.sleep(1)
    print("已关门")
def closedoor(id):

    t = threading.Thread(target=closeThread,args=(id,))
    t.start()
    t.join()

def openThread(arg):
    global exitFlag
    print("正在开门...")
    if exitFlag[arg] != [1]:
       print("开门终止")
    time.sleep(1)
    print("已开门")
def opendoor(id):

    t = threading.Thread(target=openThread,args=(id,))
    t.start()
    t.join()

def statemachine(id):
    global MsgQueue, exitFlag
    print(id)
    while True:
        time.sleep(0.3)
        print("电梯当前状态:%s,楼层:%d,方向：%s" % (elevators[id].state, elevators[id].floor, DIR[elevators[id].dir]))
        if MsgQueue[id] == [] and elevators[id].state == 1:
            continue
        if exitFlag[id] != []:
            tmplist = MsgQueue[id][:]
            for m in tmplist:
                if m.type == 0 and m.value == 0:  # 关门
                    if elevators[id].state == 0:
                        elevators[id].state = 1
                        closedoor(id)
                        closedoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
                if m.type == 0 and m.value == 1:  # 开门
                    if elevators[id].state == 1 or elevators[id].state == 0:
                        elevators[id].state = 0
                        opendoor(id)
                        opendoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
                if m.type == 0 and m.value == 2:  # 进门并关闭门
                    if elevators[id].state == 1:
                        elevators[id].state = 0
                        opendoor(id)
                        opendoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
            MsgQueue[id] = tmplist[:]
            continue

        if elevators[id].state == 0:  # 门停开着
            counter = 2
            while counter:
                if exitFlag[id] != []:
                    print("超时终止")
                    break
                time.sleep(1)
                counter -= 1
            if counter == 0:
                print("超时")
                exitFlag[id].append(1)
                closedoor(id)
                closedoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 1
            continue
        if elevators[id].state == 1:  # 门停关着
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir = closed(elevators[id].state,
                                                                                   elevators[id].floor,
                                                                                   elevators[id].dir, id)
            continue
        if elevators[id].state == 2:  # 电梯上升
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir = up(elevators[id].state,
                                                                               elevators[id].floor,
                                                                               elevators[id].dir, id)
            if elevators[id].state == 1:
                exitFlag[id].append(1)
                opendoor(id)
                opendoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 0
            continue
        if elevators[id].state == 3:  # 电梯下降
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir = down(elevators[id].state,
                                                                                 elevators[id].floor,
                                                                                 elevators[id].dir, id)
            if elevators[id].state == 1:
                exitFlag[id].append(1)
                opendoor(id)
                opendoor_send.sendMsg.emit(str(id) + str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 0
            continue


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    for i in range(5):
        thread1 = threading.Thread(target=statemachine,args=(i,))
        thread1.start()
    sys.exit(app.exec_())