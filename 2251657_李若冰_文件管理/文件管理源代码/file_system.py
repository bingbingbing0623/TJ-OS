from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QMainWindow, QTreeWidget, QTreeWidgetItem, QDialog, QMenu, QLabel, QHBoxLayout, \
    QSpacerItem, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt
from file_system_ui import Ui_MainWindow
from file_system_core import FileSystem as FS, File, Directory, load_from_disk
from editor import TextEditor
from dialog import NewItemDialog
import os


class FileSystem_ui(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        if os.path.exists("fs.pickle"):
            self.fs = load_from_disk("fs.pickle")
        else:
            self.fs = FS()
        self.files = []  # 用于存储当前目录下的文件
        self.dirs = []  # 用于存储当前目录下的文件夹
        self.text_editor = TextEditor()
        self.text_editor.text_saved.connect(self.save_file)
        self.treeWidget.doubleClicked.connect(self.on_double_clicked)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.show_menu)

        self.new_dir_button.clicked.connect(self.new_directory_dialog)
        self.new_file_button.clicked.connect(self.new_file_dialog)
        self.return_button.clicked.connect(self.back_to_parent)
        self.return_root_button.clicked.connect(self.back_to_root)

        self.format_button.clicked.connect(self.fformat)

        self.treeWidget.setHeaderLabels(["名称", "修改日期", "类型", "大小"])
        self.list()
        self.path_label.setText(self.fs.current_directory.name)
        if self.fs.current_directory.name == "/":
            self.return_button.setEnabled(False)
            self.return_root_button.setEnabled(False)

    def show_menu(self, pos):
        # 创建右键菜单
        menu = QMenu(self)

        # 添加菜单项
        createMenu = QMenu(menu)
        createMenu.setTitle('新建')
        new_file_action = createMenu.addAction("新建文件")
        file_icon_path = r"img\file.png"
        new_file_action.setIcon(QIcon(file_icon_path))
        new_directory_action = createMenu.addAction("新建文件夹")
        directory_icon_path = r"img\folder.png"
        new_directory_action.setIcon(QIcon(directory_icon_path))
        new_action = menu.addMenu(createMenu)
        delete_action = menu.addAction("删除")
        delete_icon_path = r"img\delete.png"
        delete_action.setIcon(QIcon(delete_icon_path))

        rename_action = menu.addAction("重命名")
        rename_icon_path = r"img\rename.png"
        rename_action.setIcon(QIcon(rename_icon_path))

        # 显示菜单，并等待用户选择
        action = menu.exec_(self.treeWidget.mapToGlobal(pos))

        # 根据用户选择执行相应操作
        if action == new_file_action:
            self.new_file_dialog()
        elif action == new_directory_action:
            self.new_directory_dialog()
        elif action == delete_action:
            self.delete()
        elif action == rename_action:
            self.rename()

    def new_directory_dialog(self):
        original_name = "新建文件夹"
        name = original_name
        count = 1

        # 检查文件夹是否存在，如果存在则自动重命名
        while not self.fs.create_directory(name):
            name = f"{original_name}_({count})"
            count += 1

        self.list()

    def new_file_dialog(self):
        original_name = "新建文件"
        name = original_name
        count = 1
        # 检查文件夹是否存在，如果存在则自动重命名
        while not self.fs.create_file(name):
            name = f"{original_name}_({count})"
            count += 1

        self.list()

    def back_to_parent(self):
        self.fs.change_directory(self.fs.current_directory.parent.name)
        self.list()
        self.path_label.setText(self.fs.get_current_path())
        if self.fs.current_directory.name == "/":
            self.return_button.setEnabled(False)
            self.return_root_button.setEnabled(False)

    def back_to_root(self):
        self.fs.change_directory(self.fs.root.name)
        self.list()
        self.path_label.setText("/")
        if self.fs.current_directory.name == "/":
            self.return_button.setEnabled(False)
            self.return_root_button.setEnabled(False)

    def list(self):
        """
        列出当前目录下的文件和文件夹
        """
        self.treeWidget.clear()
        for file in self.fs.current_directory.files:
            item = QTreeWidgetItem()
            item.setText(0, file.name)
            icon_path = r"img\file.png"
            item.setIcon(0, QIcon(icon_path))
            item.setText(1, self.fs.get_file_mtime(file).strftime("%Y-%m-%d %H:%M:%S"))
            item.setText(2, "文件")
            item.setText(3, self.format_size(self.fs.get_file_size(file)))
            self.treeWidget.addTopLevelItem(item)
            self.files.append(file)

        for directory in self.fs.current_directory.subdirectories:
            item = QTreeWidgetItem()
            item.setText(0, directory.name + "/")
            # 设置图标
            icon_path = r"img\folder.png"
            item.setIcon(0, QIcon(icon_path))
            item.setText(1, self.fs.get_directory_time(directory).strftime("%Y-%m-%d %H:%M:%S"))
            item.setText(2, "文件夹")
            item.setText(3, str(self.fs.get_dir_item_nums(directory)) + "项")
            self.treeWidget.addTopLevelItem(item)
            self.dirs.append(directory)

        total, used = self.fs.get_total_and_used_space_size()
        self.size_label.setText(
            "已使用空间：" + self.format_size(used) + " / " + self.format_size(total))

        self.treeWidget.repaint()
        self.size_label.repaint()

    def on_double_clicked(self, index):
        item = self.treeWidget.itemFromIndex(index)
        name = item.text(0)
        for file in self.files:
            if file.name == name:
                self.open_file(name)
                return

        for directory in self.dirs:
            if directory.name == name.rstrip("/"):
                self.open_directory(name)
                return

    def open_file(self, name):
        data = self.fs.read_file(name)
        self.text_editor.setWindowTitle(name)
        self.text_editor.file_name = name
        self.text_editor.open_file(data.decode("utf-8"))
        self.text_editor.show()

    def save_file(self, text):
        if self.fs.write_file(self.text_editor.file_name,
                              bytearray(text, "utf-8")):
            self.list()
        else:
            QtWidgets.QMessageBox.warning(self, "错误", "保存失败,空间不足")

    def open_directory(self, name):
        self.return_button.setEnabled(True)
        self.return_root_button.setEnabled(True)
        self.files.clear()
        self.dirs.clear()
        self.fs.change_directory(name.rstrip("/"))
        self.list()
        self.path_label.setText(self.fs.get_current_path())

    def delete(self):
        current_items = [item.text(0) for item in
                         self.treeWidget.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)]
        if not current_items:
            QMessageBox.warning(self, "错误", "当前目录下没有可以删除的文件或文件夹")
            return

        item = self.treeWidget.currentItem()
        if item is None:
            QMessageBox.warning(self, "错误", "请选择要删除的文件或文件夹")
            return

        name = item.text(0)
        if name.endswith("/"):
            self.delete_dir(name.rstrip("/"))
        else:
            self.delete_file(name)

    def delete_file(self, name):
        self.fs.delete_file(name)
        self.list()

    def delete_dir(self, name):
        self.fs.remove_directory(name)
        self.list()

    def format_size(self, size):
        # 格式化文件大小
        if size < 1024:
            return str(size) + " B"
        elif size < 1024 * 1024:
            return "{:.1f} KB".format(size / 1024)
        elif size < 1024 * 1024 * 1024:
            return "{:.1f} MB".format(size / (1024 * 1024))
        else:
            return "{:.1f} GB".format(size / (1024 * 1024 * 1024))

    def rename(self):
        item = self.treeWidget.currentItem()
        if not item:
            QMessageBox.warning(self, "错误", "当前目录下没有文件或文件夹可重命名")
            return

        old_name = item.text(0).rstrip("/")
        dialog = NewItemDialog(self)
        dialog.setWindowTitle("重命名")

        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.get_input_text()

            # 如果新名字和旧名字相同，则不做任何改变
            if new_name == old_name:
                return

            # 检查新文件名是否与已有文件名冲突
            existing_names = [item.text(0).rstrip("/") for item in
                              self.treeWidget.findItems("", QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)]
            old_name = item.text(0)
            if old_name.endswith("/"):
                # 处理文件夹重命名
                if new_name:
                    while new_name in [dir.name for dir in self.fs.current_directory.subdirectories]:
                        new_name += "-(副本)"
                    result, err = self.fs.rename_directory(old_name.rstrip("/"), new_name)
                    if result:
                        self.list()
                    else:
                        if err == 1:
                            self.show_error_message(1, is_directory=True)
                else:
                    self.show_error_message(1, is_directory=True)
            else:
                # 处理文件重命名
                if new_name:
                    while new_name in existing_names:
                        new_name += "-(副本)"
                    result, err = self.fs.rename_file(old_name, new_name)
                    if result:
                        self.list()
                    else:
                        if err == 1:
                            self.show_error_message(1, is_directory=False)
                        else:
                            self.show_error_message(err, is_directory=False)
                else:
                    self.show_error_message(1, is_directory=False)
        else:
            dialog.close()

    def show_error_message(self, err_code, is_directory):
        if is_directory:
            error_messages = {
                1: "文件夹名不能为空。",
            }
        else:
            error_messages = {
                1: "文件名不能为空。"
            }

        error_message = error_messages.get(err_code, "未知错误。")
        QtWidgets.QMessageBox.warning(self, "重命名错误", error_message)

    def fformat(self):
        self.fs.fformat()
        self.list()


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = FileSystem_ui()
    ui.list()
    ui.show()
    flag = app.exec_()
    ui.fs.save_to_disk("fs.pickle")
    sys.exit(flag)


if __name__ == '__main__':
    main()
