# -*- coding: utf-8 -*-
# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import re
import sgtk
from sgtk.platform.qt import QtCore, QtGui
from pprint import pprint

from ..ui.files_widget import Ui_FilesWidget
from ..ext_packages import pyseq

# exr 과 같은 seq가 들어왔을 때 SeqItem의 인스턴스 생성
class SeqItem(QtGui.QStandardItem):
    
    def __init__(self,seq_info, context_name = None, parent=None):

        QtGui.QStandardItem.__init__(self,parent)
        self.seq_info = seq_info
<<<<<<< HEAD
        self.setText(seq_info.format())
    
class SelItem(QtGui.QStandardItem):
    def __init__( self, sel_info, parent = None ):
        self.sel_info = sel_info
        self.setText(sel_info)

class FilesForm(QtGui.QWidget):

    def __init__(self,root_path,parent=None):
        
        self.root_path = root_path
        QtGui.QWidget.__init__(self, parent)
        self.sequence_list = []
        #---------------------------------------------------#
        self.selected_list = []
        #---------------------------------------------------#

=======
        if context_name:
            self.setText( "SHOT [" + context_name + "] - " + seq_info.format() )
        else:
            self.setText( seq_info.format() )


class VideoItem(QtGui.QStandardItem):
    def __init__( self, video_info, context_name = None, parent = None ):
        QtGui.QStandardItem.__init__(self,parent)
        self.video_info = video_info
        if context_name:
            self.setText( "SHOT [" +  context_name + "] - " + video_info )
        else:
            self.setText( context_name )



class FilesForm(QtGui.QWidget):
    def __init__(self,root_path,parent=None):
        self.root_path = root_path
        QtGui.QWidget.__init__(self, parent)
        self.sequence_list = []
>>>>>>> test
        self.image_filters = ["*.jpg",
                              "*.jpeg",
                              "*.png",
                              "*.tga",
                              "*.exr",
                              "*.tif",
                              "*.tiff",
                              "*.psd",
                              "*.hdri",
                              "*.hdr",
                              "*.cin",
                              "*.dpx",
                              "*.mov",
                              "*.ogv",
                              "*.mp4"
                              ]

        self.dir_model = QtGui.QFileSystemModel()
        self.file_model = QtGui.QFileSystemModel()
        self.seq_model = QtGui.QStringListModel(self.sequence_list)
        #---------------------------------------------------#
        # QStringListModel( [list] )
        # 그럼 select 시 list로 바꿔야함
        self.sel_model = QtGui.QStandardItemModel()
        #---------------------------------------------------#

        self.ui = Ui_FilesWidget()
        self.ui.setupUi(self)
        self.build_models()
        self.setup_connections()
        
    def build_models(self):
        """ Sets up fileSystemModels and their links to views. """
        self.dir_model.setRootPath(self.root_path)
        self.file_model.setRootPath(self.root_path)
        # self.sel_model.setRootPath(self.root_path)
        '''
        QDir.AllDirs = filter가 적용되지 않은 모든 dir
        Qdir.Dirs = filter가 적용된 dir()
        QDir.NoDotAndDotDot = .과 ..즉 상위 제외
        filter()는 디렉터리 모델에 대해 지정된 필터를 반환
        필터를 설정하지 않은 경우 기본 필터는 QDir::AllEntries | QDir:NoDotAndDotDot | QDir:AllDirs.
        QDir.AllEntries = dir, file, drive, 심볼릭 링크등 등
        '''

        # Filters.
        self.dir_model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        self.file_model.setFilter(self.file_model.filter() | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(self.image_filters)
        self.file_model.setNameFilterDisables(False)

        # Associate Views/Models.
        self.ui.dir_view.setModel(self.dir_model)
        self.ui.file_view.setModel(self.file_model)

        # Set initial indexes.
        self.ui.dir_view.setRootIndex(self.dir_model.index(self.root_path))
        self.ui.file_view.setRootIndex(self.file_model.index(self.root_path))
        # self.ui.sel_view.setRootIndex(self.sel_model.index(self.root_path))

        # Hide all but Name column.
        self.ui.dir_view.hideColumn(1)
        self.ui.dir_view.hideColumn(2)
        self.ui.dir_view.hideColumn(3)

    def setup_connections(self):
        """ Sets up input connections from different parts of the interface, to the appropriate methods. """
        self.ui.dir_view.clicked.connect(self.update_from_tree_click)
<<<<<<< HEAD
        # self.ui.file_view.clicked.connect(self.update_from_list_click)
        # self.ui.file_view.doubleClicked.connect(self.update_from_list_click)
=======
        # self.ui.file_view.doubleClicked.connect( self.update_from_list_click )
        # self.ui.sel_file_view.doubleClicked.connect( self.update_from_sel_list_click)
        #self.ui.file_view.clicked.connect(self.update_from_list_click)
>>>>>>> test
        #self.text_edit.editingFinished.connect(self.update_from_text_entry)
        #self.up_button.clicked.connect(self.up_directory)
        #self.seq_box.stateChanged.connect(self.sequence_toggle)

    def update_from_tree_click(self):
        self.ui.text_edit.setText(self.dir_model.filePath(self.ui.dir_view.selectedIndexes()[0]))
        # <type 'PySide.QtCore.QModelIndex'>
        # print( type( self.ui.dir_view.selectedIndexes()[0] ))
        # <type 'list'>
        # print( type( self.ui.dir_view.selectedIndexes() ))
        # [<PySide.QtCore.QModelIndex(0,0,0x2b2ff70,QFileSystemModel(0x2d4c740) )   at 0x7fc34232d830>]
        # print( self.ui.dir_view.selectedIndexes() )
        self.string_list_refresh()
        # seq_model이 있다면 file_view를 listModel로
        # 없다면 fileSystemModel로
        if self.seq_model:
            self.ui.file_view.setModel(self.seq_model)
        else:
            self.ui.file_view.setModel(self.file_model)
        try:
            self.ui.file_view.setRootIndex(self.file_model.index(self.dir_model.filePath(self.ui.dir_view.selectedIndexes()[0])))
        except:
            pass
    

<<<<<<< HEAD
    def update_from_list_click( self ):
        # 클릭한 파일의 인덱스를 받아서 반환해야하는데..
        # selected = self.ui.text_edit.setText(self.dir_model.filePath(self.ui.dir_view.selectedIndexes()[0]))
        selected = self.ui.text_edit.setText(self.dir_model.filePath(self.ui.dir_view.selectedIndexes()[0]))
        '''
        폴더 선택시
        <type 'PySide.QtCore.QModelIndex'>
        <PySide.QtCore.QModelIndex(!!!!2!!!!,0,0x39eef00,QFileSystemModel(0x3ae1f90) )   at 0x7f2564e42d40>
        파일 선택시
        <type 'PySide.QtCore.QModelIndex'>
        <PySide.QtCore.QModelIndex(0,0,0x2cb1930,QStandardItemModel(0x3c6aa10) )   at 0x7f25653d4a70>
        '''
        # print (type(selected))
        # print (selected)
        # print (dir(selected))
        # print (str(selected))

        # self.sel_model.appendRow( SeqItem( selected ) )
        # self.ui.sel_file_view.setModel( self.seq_model )


    def scan_folder_sequences(self):
=======
    def scan_folder_list(self):
>>>>>>> test

        """ Returns a list of lists. filtered is a list of only the sequences in the specified path, first_last is
         a list of individual frames of the sequence. """
        file_path = self.dir_model.filePath(self.ui.dir_view.selectedIndexes()[0])
        sequences = [x for x in pyseq.get_sequences(file_path)
                     if x.tail() in ['.jpg','.exr','.dpx','.tiff','.jpg','.jpeg','.png'] ]
        # 위 확장자만 갖는 sequence list를 만듦
        # print( sequences )
        return sequences

    # def scan_folder_mov( self ):
    #     mov_file  = [ x for x in os.listdir(file_path) if x.endwith('.mov','.mp4','.ogv')
    #     sequences.extend( mov_file )

    def string_list_refresh(self):
        """ Refresh the StringListModel. """
<<<<<<< HEAD
        # list 자료형 sequence_list
        sequence_list = self.scan_folder_sequences()
        if sequence_list : # 리스트가 있다면 seq_model에 추가
            # seq_model = QtGui.QStringListModel(self.sequence_list)
            # QstringListModel
=======
        sequence_list = self.scan_folder_list()
        if sequence_list :
>>>>>>> test
            self.seq_model = QtGui.QStandardItemModel()
            for i in sequence_list:
                print('*'* 50)
                print(type (i))
                print(type (SeqItem(i)))
                print(i.format())
                print('*'* 50)
                self.seq_model.appendRow(SeqItem(i))
        else:
            self.seq_model = None

    # def selected_item(self):
    #     index = self.ui.file_view.selectedIndexes()
    #     if not index:
    #         return 
    #     model = self.ui.file_view.model()
    #     if isinstance(model, QtGui.QFileSystemModel):
    #         item = model.fileInfo(index[0])
    #         if "*."+item.suffix().lower() in self.image_filters:
    #             if item.suffix() in ["mov","ogv","mp4"]:
    #                 return "mov",item
    #             else:
    #                 return "image",item
    #         else:
    #             return
    #     elif isinstance(model, QtGui.QStandardItemModel):
    #         return "seq",model.itemFromIndex(index[0])
