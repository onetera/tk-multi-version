# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created: Mon Oct  7 17:08:01 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from tank.platform.qt import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):

        Dialog.setObjectName("Dialog")
        Dialog.resize(1180, 820)

        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout_2 = QtGui.QVBoxLayout()
        
        # make font form and set it
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)

        # Create tab style widget on Dialog named task
        # specifying tab style widget's SizePolicy it makes tap size 
        # stretch(0) make size fixxed
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.tasks_widget = QtGui.QTabWidget()
        self.tasks_widget.setSizePolicy(sizePolicy)
        self.tasks_widget.setFont(font)
        self.tasks_widget.setAcceptDrops(True) # make drag-dropable
        self.tasks_widget.setObjectName("tasks_widget")
        sizePolicy.setHeightForWidth(self.tasks_widget.sizePolicy().hasHeightForWidth())

        self.context_widget = QtGui.QTabWidget()
        self.context_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.context_widget.setFont(font)
        self.context_widget.setObjectName("context_widget")

        self.verticalLayout_2.addWidget( self.tasks_widget )
        self.verticalLayout_2.addWidget( self.context_widget )
        self.verticalLayout_2.setStretch( 0, 3 )
        self.verticalLayout_2.setStretch( 1, 1.2 )
        self.horizontalLayout.addLayout( self.verticalLayout_2 )


        self.source_widget = QtGui.QTabWidget()
        self.source_widget.setFont(font)
        self.source_widget.resize
        self.source_widget.setObjectName("source_widget")

        self.selected_file_widget = QtGui.QTabWidget()
        self.selected_file_widget.setFont(font)
        self.selected_file_widget.resize
        self.selected_file_widget.setObjectName("selected_file_widget")

        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.addWidget( self.source_widget )
        self.verticalLayout_3.addWidget( self.selected_file_widget )
        self.horizontalLayout.addLayout( self.verticalLayout_3 )

        self.horizontalLayout.setStretch( 0, 1 )
        self.horizontalLayout.setStretch( 1, 3 )

        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

        self.delete_btn = QtGui.QPushButton()
        self.delete_btn.setObjectName("delete_btn")

        self.upload_btn = QtGui.QPushButton()
        self.upload_btn.setObjectName("upload_btn")
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout_2.addWidget(self.delete_btn)
        self.horizontalLayout_2.addWidget(self.upload_btn)

        self.verticalLayout.addLayout( self.horizontalLayout )
        self.verticalLayout.addLayout( self.horizontalLayout_2 )
        self.verticalLayout.setStretch(0, 10)
        self.verticalLayout.setStretch(1, 1)
        
        self.retranslateUi(Dialog)
        
        self.source_widget.setCurrentIndex(-1)
        self.context_widget.setCurrentIndex(-1)
        # self.selected_file_widget.setCurrentIndex(-1)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "The Current Sgtk Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_btn.setText(QtGui.QApplication.translate("Dialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.upload_btn.setText(QtGui.QApplication.translate("Dialog", "Upload", None, QtGui.QApplication.UnicodeUTF8))


from . import resources_rc
