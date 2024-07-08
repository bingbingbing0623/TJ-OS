class Elevator(object):
    state=1 #门状态
    floor=1 #楼层
    dir=0   #方向
    def __init__(self,id):
        self.id=id

    #上楼函数
    def up(self):
        if self.floor<20:
            self.floor+=1
        else:
            print('超过20层,无法继续上升！')

    def down(self):
        if self.floor>1:
            self.floor-=1
        else:
            print('低于1层，无法继续下降！')

    def get_floor(self):
        print(self.floor)




