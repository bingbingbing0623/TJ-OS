# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1030, 716)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.path_label = QtWidgets.QLabel(self.centralwidget)
        self.path_label.setObjectName("path_label")
        self.horizontalLayout_3.addWidget(self.path_label)
        self.horizontalSpacer_2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                        QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)
        self.size_label = QtWidgets.QLabel(self.centralwidget)
        self.size_label.setObjectName("size_label")
        self.horizontalLayout_3.addWidget(self.size_label)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.new_file_button = QtWidgets.QPushButton(self.centralwidget)
        self.new_file_button.setMaximumSize(QtCore.QSize(116, 45))
        self.new_file_button.setObjectName("new_file_button")
        self.horizontalLayout.addWidget(self.new_file_button)
        self.new_dir_button = QtWidgets.QPushButton(self.centralwidget)
        self.new_dir_button.setMaximumSize(QtCore.QSize(116, 45))
        self.new_dir_button.setObjectName("new_dir_button")
        self.horizontalLayout.addWidget(self.new_dir_button)
        self.format_button = QtWidgets.QPushButton(self.centralwidget)
        self.format_button.setObjectName("format_button")
        self.horizontalLayout.addWidget(self.format_button)
        self.horizontalSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                      QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.return_button = QtWidgets.QPushButton(self.centralwidget)
        self.return_button.setMaximumSize(QtCore.QSize(116, 45))
        self.return_button.setObjectName("return_button")
        self.horizontalLayout.addWidget(self.return_button)
        self.return_root_button = QtWidgets.QPushButton(self.centralwidget)
        self.return_root_button.setMaximumSize(QtCore.QSize(116, 45))
        self.return_root_button.setObjectName("return_root_button")
        self.horizontalLayout.addWidget(self.return_root_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # 使用 QTreeWidget 替换 QListWidget
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setHeaderLabels(["名称", "修改日期", "类型", "大小"])  # 添加表头

        # 设置表头各列均匀分布
        header = self.treeWidget.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        self.horizontalLayout_2.addWidget(self.treeWidget)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "文件系统"))
        self.path_label.setText(_translate("MainWindow", "/"))
        self.size_label.setText(_translate("MainWindow", "已使用：剩余空间："))
        self.new_file_button.setText(_translate("MainWindow", "新建文件"))
        self.new_dir_button.setText(_translate("MainWindow", "新建文件夹"))
        self.format_button.setText(_translate("MainWindow", "格式化"))
        self.return_button.setText(_translate("MainWindow", "返回上一级"))
        self.return_root_button.setText(_translate("MainWindow", "返回根目录"))



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
