# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'files_widget.ui'
#
# Created: Mon Oct  7 17:08:01 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_FilesWidget(object):
    def setupUi(self, FilesWidget):
        FilesWidget.setObjectName("FilesWidget")
        FilesWidget.resize(710, 290)
        self.verticalLayout = QtGui.QVBoxLayout(FilesWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text_edit = QtGui.QLineEdit(FilesWidget)
        self.text_edit.setObjectName("text_edit")
        self.verticalLayout.addWidget(self.text_edit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dir_view = QtGui.QTreeView(FilesWidget)
        self.dir_view.setObjectName("dir_view")
        self.horizontalLayout.addWidget(self.dir_view)
        self.file_view = QtGui.QListView(FilesWidget)
        self.file_view.setObjectName("file_view")
        self.horizontalLayout.addWidget(self.file_view)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FilesWidget)
        QtCore.QMetaObject.connectSlotsByName(FilesWidget)

    def retranslateUi(self, FilesWidget):
        FilesWidget.setWindowTitle(QtGui.QApplication.translate("FilesWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

