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
        Dialog.resize(1130, 830)
        # create Vertical Boxlayout on the Dialog and set object named "verticalLayout_2"
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        # create horizontal Boxlayout and set object name "horizontalLayout"
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Create tab style widget on Dialog named task
        self.tasks_widget = QtGui.QTabWidget(Dialog)
        # specifying tab style widget's SizePolicy it makes tap size 
        # stretch(0) make size fixxed
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tasks_widget.sizePolicy().hasHeightForWidth())
        self.tasks_widget.setSizePolicy(sizePolicy)
        # make font form and set it
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.tasks_widget.setFont(font)
        self.tasks_widget.setAcceptDrops(True) # make drag-dropable
        self.tasks_widget.setObjectName("tasks_widget")
        # add tasks_widget on "horizontalLayout"
        self.horizontalLayout.addWidget(self.tasks_widget)
        
        # Create tab style widget on Dialog named task
        self.source_widget = QtGui.QTabWidget(Dialog)
        # make font form and set it
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.source_widget.setFont(font)
        self.source_widget.resize
        self.source_widget.setObjectName("source_widget")
        # add "source_widget" on "horizontalLayout"
        # self.horizontalLayout.addWidget( self.source_widget )
        
        # create Vertical Boxlayout on the Dialog and set object named "verticalLayout_3"
        # verticalLayout_3 contains selected_file_view (upload item list)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.addWidget( self.source_widget )

        self.selected_file_widget = QtGui.QTabWidget( Dialog )      
        self.selected_file_widget.setFont(font)
        self.selected_file_widget.setObjectName("selected_file_widget")
        self.verticalLayout_3.addWidget( self.selected_file_widget )
        # self.selected_file_view = QtGui.QListView( Dialog )      
        # self.selected_file_view.setEditTriggers( QtGui.QAbstractItemView.NoEditTriggers )
        # self.selected_file_view.setObjectName( "selected_file_view" )
        # self.verticalLayout_3.addWidget( self.selected_file_view )
        self.horizontalLayout.addLayout( self.verticalLayout_3 )

        # setStretch( index, stretch ) : Sets the stretch factor at position index. to stretch.
        self.verticalLayout_3.setStretch(0, 2)
        self.verticalLayout_3.setStretch(1, 1)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)
        # add vertical layout named "verticalLayout_2" on horizontalLayout
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        # create horizontal Boxlayout and set object name "horizontalLayout_3"
        # horizontalLayout_3 contains Context and Description widget
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.context_widget = QtGui.QTabWidget(Dialog)
        self.context_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        # make font form and set it
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.context_widget.setFont(font)
        self.context_widget.setObjectName("context_widget")
        self.horizontalLayout_3.addWidget(self.context_widget)

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)


        #-------------------------------------------------#
        # self.desc_edit = QtGui.QTextEdit(Dialog)
        self.desc_widget = QtGui.QTabWidget( Dialog )
        self.desc_widget.setFont(font)
        self.desc_widget.setObjectName("desc_edit")
        self.verticalLayout.addWidget(self.desc_widget)
        #-------------------------------------------------#

        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.upload_btn = QtGui.QPushButton(Dialog)
        self.upload_btn.setObjectName("upload_btn")
        self.horizontalLayout_2.addWidget(self.upload_btn)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(0, 10)
        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(Dialog)

        self.source_widget.setCurrentIndex(-1)
        self.context_widget.setCurrentIndex(-1)
        self.selected_file_widget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "The Current Sgtk Environment", None, QtGui.QApplication.UnicodeUTF8))
        # self.label.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.upload_btn.setText(QtGui.QApplication.translate("Dialog", "Upload", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc