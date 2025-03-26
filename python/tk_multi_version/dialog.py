# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from pprint import pprint
import sgtk
import sys
import os
import traceback

from .my_tasks.my_tasks_form import MyTasksForm
from .my_tasks.my_tasks_model import MyTasksModel
from .files_widget.files_form import FilesForm, SeqItem
from .util import monitor_qobject_lifetime
from .ui.selected_files_widget import Ui_SelectedFilesWidget
# from .ui.selected_files_widget import Ui_SelectedFilesWidget
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
# from sgtk.platform.qt import QCheckBox
from .ui.dialog import Ui_Dialog
from .framework_qtwidgets import *
from .upload_shotgun import *

MOV_COLORSPACE = [
    "NONE",
    "linear",
    "rec709",
    "sRGB",
    "raw"
]

SEQ_COLORSPACE =[
    "NONE",
    "linear",
    "rec709",
    "Cineon",
    "raw"
]


# There are two loggers
# logger is shotgun logger
# _logger is a independet logger
logger = sgtk.platform.get_logger(__name__)


class AppDialog(QtGui.QWidget):
    """
    Main application dialog window
    """

    def __init__(self):
        """
        Constructor
        """
        # get app bundle
        self._app = sgtk.platform.current_bundle()
        # call the base class and let it do its thing.
        QtGui.QWidget.__init__(self)

        # # Set up our own logger (other than shotgun logger) for storing timestamp
        # self.set_logger(logging.INFO)
        # now load in the UI that was created in the UI designer
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # create a background task manager
        self._task_manager = task_manager.BackgroundTaskManager(
            self,
            start_processing=True,
            max_threads=4
        )
        monitor_qobject_lifetime(self._task_manager, "Main task manager")
        self._task_manager.start_processing()

        self.selected_file_dict  = {}

        # lastly, set up our very basic UI
        self.user = sgtk.util.get_current_user(self._app.sgtk)
        # self.ui.textBrowser.setText("Hello, %s!" % self.user['firstname'])
        # create my tasks form and my time form:
        self.createTasksForm()
        # time summary labels

        # add refresh action with appropriate keyboard shortcut:
        refresh_action = QtGui.QAction("Refresh", self)
        refresh_action.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Refresh))
        refresh_action.triggered.connect(self._on_refresh_triggered)
        self.addAction(refresh_action)
        # on OSX, also add support for F5 (the default for OSX is Cmd+R)
        if sys.platform == "darwin":
            osx_f5_refresh_action = QtGui.QAction("Refresh (F5)", self)
            osx_f5_refresh_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))
            osx_f5_refresh_action.triggered.connect(self._on_refresh_triggered)
            self.addAction(osx_f5_refresh_action)
        
        self.create_context_form()
        self.create_status_form()
        self.create_selected_ui()
        self.status_init = 0
        self.ui.delete_btn.clicked.connect(self.delete_selected_item)
        self.ui.upload_btn.clicked.connect(self._upload)
        self.selected_ui.widget.clicked.connect( self.update_from_selected_ui_click )

    def _upload(self):
        selected_item_list = self.get_selected_item_list()
        if not selected_item_list:
            return

        for selected_type, item, context, seq_colorspace ,desc, mov_colorspace, fps_is_checked in selected_item_list:
            if not item:
                return
            print(seq_colorspace)
            print(mov_colorspace)
            # desc = self.ui.desc_widget.toPlainText()
            qc_bool = True if self.qc_chk.isChecked() else False

            trascoding = Transcoding(item,context,selected_type,seq_colorspace, desc,mov_colorspace,fps_is_checked)
            version = UploadVersion(item,context,selected_type)
            # trascoding = Transcoding(item,self.context,selected_type,desc)
            # version = UploadVersion(item,self.context,selected_type)
            trascoding.create_nuke_script()
            #try:
            trascoding.create_mov()
            trascoding.create_hdr_mov()
            trascoding.create_mp4()
            trascoding.create_webm()
            trascoding.create_thumbnail()
            trascoding.create_thumbnail_for_image()

            if qc_bool:
                trascoding.create_nuke_script( qc = qc_bool )
                trascoding.create_mov( qc = qc_bool )
                trascoding.create_hdr_mov( qc = qc_bool )
                trascoding.create_mp4( qc = qc_bool )
                trascoding.create_webm( qc = qc_bool )
                trascoding.create_thumbnail( qc = qc_bool )
                trascoding.create_thumbnail_for_image( qc = qc_bool )

                version.create_version(trascoding.read_path,trascoding.qc_mov_path,desc,trascoding.qc_hdr_path, qc = qc_bool )
                version.upload_thumbnail(trascoding.qc_thumbnail_file)
                version.upload_filmstrip_thumbnail(trascoding.qc_filmstream_file)
                version.upload_mp4(trascoding.qc_mp4_path)
                version.upload_webm(trascoding.qc_webm_path,trascoding.qc_mov_webm_path)

            version.create_version(trascoding.read_path,trascoding.mov_path,desc,trascoding.hdr_path)
            version.upload_thumbnail(trascoding.thumbnail_file)
            version.upload_filmstrip_thumbnail(trascoding.filmstream_file)
            version.upload_mp4(trascoding.mp4_path)
            version.upload_webm(trascoding.webm_path,trascoding.mov_webm_path)

#            except Exception as e:
#                msg = QtGui.QMessageBox()
#                msg.setIcon(QtGui.QMessageBox.Critical)
#                msg.setText("Error.")
#                msg.setInformativeText(str(e))
#                msg.setWindowTitle("Version Error")
#                msg.exec_()
#                return
            
        text = []
        if len(selected_item_list) == 1:
            text.append(context.entity['name'])
            text.append('<a href="{0}">{0}</a>'.format(context.shotgun_url))
        else :
            text.append('Upload completed')
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setText("\n".join(text))
        #msg.setInformativeText("\n".join(text))
        msg.setWindowTitle("Done")
        msg.exec_()
        
    def create_file_form(self,selection_detail,breadcrumb_trail):
        count = self.ui.source_widget.count()
        for index in range(0,count):
            widget = self.ui.source_widget.widget(index)
            widget.close()
            self.ui.source_widget.removeTab(index)

        self.context = self._app.sgtk.context_from_entity_dictionary(selection_detail['entity'])
        # pprint(self.context)
        root_path = [x for x in self.context.filesystem_locations if x.find("_3d") == -1 ]
        print('root_path', root_path)
        # print(root_path)
        init_path = " "
        if not root_path:
            entity_type = "Task"
            entity_query = [['entity','is',self.context.entity],
                            ['id','is',self.context.task['id']]]
            fields = sorted(self._app.shotgun.schema_field_read(entity_type).keys())
            # entity = self._app.shotgun.find_one(entity_type, entity_query, fields=fields) 
            entity = self._app.shotgun.find_one(entity_type, entity_query, ['entity']) 
            if self.context.entity['type'] == 'Asset':
                entity_type = 'Asset'
                entity_query = [['code','is',self.context.entity['name']],
                                ['id','is',self.context.entity['id']]]
                # print(entity_query) # [['code', 'is', 'audiR8'], ['id', 'is', 8462]]
                asset = self._app.shotgun.find_one( entity_type , entity_query, ['sg_asset_type','code'] ) 
                # print(asset) # {'sg_asset_type': 'vehicle', 'type': 'Asset', 'id': 8462}
                init_path = os.path.join(
                    self._app.sgtk.project_path,
                    "assets",
                    asset['sg_asset_type'],
                    asset['code']
                )
            else :
                entity_type = 'Shot'
                entity_query = [['code','is',self.context.entity['name']],
                                ['id','is',self.context.entity['id']]]
                shot = self._app.shotgun.find_one( entity_type , entity_query, ['sg_sequence','code'] ) 
                init_path = os.path.join(
                    self._app.sgtk.project_path,
                    "seq",
                    shot['sg_sequence']['name'],
                    shot['code']
                )
        else:
            init_path = os.path.join(
                # self.context.filesystem_locations[0],
                root_path[0],
                self.context.step['name']
                )
            print(init_path)
        self.file_form = FilesForm(init_path)
        self.ui.source_widget.addTab(self.file_form,"Select")
        self._context_widget.set_context(self.context)
        self.file_form.ui.file_view.doubleClicked.connect( self.update_from_list_click )
        self.get_task_status()
        self.get_comp_task4qc()

    def create_context_form(self):
        self._context_widget = context_selector.ContextWidget(self)
        self._context_widget.set_up(self._task_manager)
        self._context_widget.setFixedWidth(450)
        self._context_widget.enable_editing(True,"Select Task")
        self._context_widget.restrict_entity_types_by_link(
            "PublishedFile", "entity")
        self._context_widget.set_context(sgtk.platform.current_bundle().context)
        self.context_layout = QtGui.QVBoxLayout()
        self.context_layout.setSpacing(4)
        self.context_layout.setContentsMargins(0, 0, 0, 0)
        self.context_layout.addWidget(self._context_widget)
        self.context_tab = QtGui.QWidget()
        self.context_tab.setLayout(self.context_layout)
        self.ui.context_widget.addTab(self.context_tab,"Context")

    def create_selected_ui( self ):
        self.selected_ui = Ui_SelectedFilesWidget()
        self.selected_ui.setupUi( self )
        self.ui.selected_file_widget.addTab( self.selected_ui.widget, "Upload Lists" )


    def create_status_form(self):
        self._fields_manager = shotgun_fields.ShotgunFieldManager(
            self,
            bg_task_manager=self._task_manager)
        form_layout = QtGui.QGridLayout()
        form_layout.setSpacing(4)
        entity_type = "Task"
        #entity_query = [["entity",'is',self.context.entity],
        #                ['id','is',self.context.task['id']]]
        field = 'sg_status_list'
        #entities = self._app.shotgun.find(entity_type, entity_query, fields=fields)
        #entity = self._app.shotgun.find_one(entity_type, entity_query, fields=fields)
        self.qc_chk = QtGui.QCheckBox( 'QC check')
        self.qc_chk.setChecked( False )
        self.qc_chk.setHidden( True )
        sp = QtGui.QSpacerItem( 200, 10 )
        qc_lay = QtGui.QHBoxLayout()
        qc_lay.addWidget( self.qc_chk )
        qc_lay.addSpacerItem( sp )

        try:
            field_display_name = shotgun_globals.get_field_display_name(
                entity_type, field )
            self.editable_field_widget = self._fields_manager.create_widget(
                entity_type, field, entity=None, parent=self
                        )
            self.editable_field_widget.value_changed.connect(self.update_status)

            lbl = QtGui.QLabel("%s:" % (field_display_name,))
            form_layout.addWidget(lbl,0,0,QtCore.Qt.AlignLeft)
            form_layout.addWidget(self.editable_field_widget,0,1,QtCore.Qt.AlignRight)
            self.context_layout.addLayout(form_layout)
            self.context_layout.addLayout( qc_lay ) 
            bottom_sp = QtGui.QSpacerItem( 10,50 )
            self.context_layout.addSpacerItem( bottom_sp )

        except :
            pass
    
    def update_status(self):
        if not self.context:
            return
        status = self.editable_field_widget.get_value()
        data = {'sg_status_list': status}
        self._app.shotgun.update('Task',self.context.task['id'],data)

    def get_comp_task4qc( self ):
        if self.context.step and self.context.step['name'] == 'comp':
            self.qc_chk.setHidden( False )
        else:
            self.qc_chk.setChecked( False )
            self.qc_chk.setHidden( True )

    def get_task_status(self):
        entity_type = "Task"
        entity_query = [["entity",'is',self.context.entity],
                        ['id','is',self.context.task['id']]]
        fields = sorted(self._app.shotgun.schema_field_read(entity_type).keys())
        #entities = self._app.shotgun.find(entity_type, entity_query, fields=fields)
        entity = self._app.shotgun.find_one(entity_type, entity_query, fields=fields)
        self.editable_field_widget.set_value(entity['sg_status_list'])

    def closeEvent(self, event):
        """
        Executed when the main dialog is closed.
        All worker threads and other things which need a proper shutdown
        need to be called here.
        """
        logger.debug("CloseEvent Received. Begin shutting down UI.")
        # register the data fetcher with the global schema manager
        shotgun_globals.unregister_bg_task_manager(self._task_manager)
        try:
            if self._my_tasks_model:
                self._my_tasks_model.destroy()
            self._task_manager.shut_down()
        except Exception as e:
            logger.exception("Error running Shotgun Panel App closeEvent() %s" % e)


    def createTasksForm(self):
        """
        Create my task form and facility task form icluding model and view.
        :param UI_filter_action: QAction contains shotgun filter selected in UI
        """
        try:
            self._my_tasks_model = self._build_my_tasks_model(
                self._app.context.project)
            self._my_tasks_form = MyTasksForm(self._my_tasks_model,
                                              allow_task_creation=False,
                                              parent=self)
            # refresh tab
            self.ui.tasks_widget.addTab(self._my_tasks_form, "My Tasks")
            self._my_tasks_form.entity_selected.connect(self.create_file_form)
            
        except Exception as e:
            logger.exception("Failed to Load my tasks, because %s \n %s"
                             % (e, traceback.format_exc()))


    def _build_my_tasks_model(self, project):
        """
        Get settings from config file and append those settings default
        Then create task model
        :param project: dict
                        sg project context
        :UI_filter action: QAction contains shotgun filter selected in UI
        """
        if not self.user:
            # can't show my tasks if we don't know who 'my' is!
            logger.debug("There is no tasks because user is not defined")
            return None
        # get any extra display fields we'll need to retrieve:
        extra_display_fields = self._app.get_setting("my_tasks_extra_display_fields")
        # get the my task filters from the config.
        my_tasks_filters = self._app.get_setting("my_tasks_filters")
        model = MyTasksModel(project,
                             self.user,
                             extra_display_fields,
                             my_tasks_filters,
                             parent=self,
                             bg_task_manager=self._task_manager)
        monitor_qobject_lifetime(model, "My Tasks Model")
        model.async_refresh()
        logger.debug("Tasks Model Build Finished")
        return model

    def _on_refresh_triggered(self):
        """
        Slot triggered when a refresh is requested via the refresh keyboard shortcut
        """
        self._app.log_debug("Synchronizing remote path cache...")
        self._app.sgtk.synchronize_filesystem_structure()
        self._app.log_debug("Path cache up to date!")
        if self._my_tasks_model:
            self._my_tasks_model.async_refresh()

    def _init_combobox(self, combobox):
        for color in MOV_COLORSPACE:
            combobox.addItem(color)

    def _init_combobox_seq_color(self, combobox):
        for color in SEQ_COLORSPACE:
            combobox.addItem(color)

    def update_from_list_click( self ):
        print("update_from_list_click")
        model = self.file_form.ui.file_view.model()
        if isinstance( model, QtGui.QFileSystemModel ):
            item_name = self.add_selected_mov_refresh()
        elif isinstance( model, QtGui.QStandardItemModel ):
            item = self.add_selected_seq_refresh( )
            item_name = item.text()
        else :
            return
        if not item_name:
            return
        row_count = self.selected_ui.widget.rowCount()
        # print(row_count)
        self.selected_ui.widget.insertRow( row_count )
        checkbox = QtGui.QCheckBox("23.976")
        combobox = QtGui.QComboBox()
        self._init_combobox(combobox)
        seq_color_combobox = QtGui.QComboBox()
        self._init_combobox_seq_color(seq_color_combobox)
        print(self._init_combobox_seq_color)
        # combobox.addItem(COLORSPACE)
        self.selected_ui.widget.setItem( row_count, 0, QtGui.QTableWidgetItem( self.context.entity['name'] ) )
        self.selected_ui.widget.setItem( row_count, 1, QtGui.QTableWidgetItem( item_name ) )
        self.selected_ui.widget.setCellWidget(row_count, 2, seq_color_combobox)
        self.selected_ui.widget.setCellWidget(row_count, 4, combobox)
        self.selected_ui.widget.setCellWidget(row_count, 5, checkbox)
        # self.selected_ui.widget.cellWidget(row_count, 5).setAlignment(QtGui.QWidget.Qt.AlignCenter)
        # self.selected_ui.widget.resizeRowsToContents( )
        desc_editor = QtGui.QPlainTextEdit()
        # desc_editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        desc_editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # desc_editor.clear()
        desc_editor.setFrameStyle( QtGui.QFrame.NoFrame )
        self.resize_height_toContents(desc_editor)
        self.selected_ui.widget.setCellWidget( row_count, 3, desc_editor )
        self.selected_ui.widget.resizeColumnToContents( 0 )
        self.selected_ui.widget.resizeColumnToContents( 1 )
        desc_editor.textChanged.connect( lambda : self.resize_height_toContents(desc_editor) )

        
        checkbox.stateChanged.connect(lambda state, r=row_count: self.checkbox_callback(state, r))


    def checkbox_callback(self, state, row):
        print("Checkbox state changed for row {}: {}".format(row, state))

    def update_from_selected_ui_click( self ):
        row = self.selected_ui.widget.currentIndex().row()
        column = self.selected_ui.widget.currentIndex().column()
        # print( row, column )
        
        item = self.selected_ui.widget.selectedItems()
        if not item :
            return
        # print(item[0])
        if column != 2:
            item[0].setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
            self.selected_ui.widget.selectRow( row )


    def add_selected_mov_refresh( self ):
        index = self.file_form.ui.file_view.selectedIndexes( )
        if not index:
            return 
        model = self.file_form.ui.file_view.model()
        item = model.fileInfo(index[0])
        item_name = model.fileName( index[0] )
        if not item_name in self.selected_file_dict:
            if "*."+item.suffix().lower() in self.file_form.image_filters:
                if item.suffix() in ["mov","ogv","mp4"]:
                    self.selected_file_dict[ item_name ] = [ item, self.context ]
                else: 
                    self.selected_file_dict[ item_name ] = [ item, self.context ]
                return item_name
        return None

    def add_selected_seq_refresh( self ):
        index = self.file_form.ui.file_view.selectedIndexes( )
        if not index:
            return 
        model = self.file_form.ui.file_view.model()
        item = model.itemFromIndex( index[0] )
        item_name = item.text()
        if not item_name in self.selected_file_dict:
            seq_item = SeqItem( item.seq_info )
            self.selected_file_dict[ item_name ] = [ seq_item, self.context ]      
            return seq_item
        return None

    def delete_selected_item( self ):
        item_list = self.selected_ui.widget.selectedItems()
        for item in item_list:
            if item.column() == 1:
                print(item.text())
                del self.selected_file_dict[ item.text() ]
                # print('*'*100)
                # print(self.selected_file_dict.keys())
                # print('*'*100)
                self.selected_ui.widget.removeRow( item.row() )


    def get_selected_item_list( self ):
        selected_item_list = []
        desc=""
        if not self.selected_file_dict:
            return
        # print(self.selected_file_dict.keys())
        for item, item_context in self.selected_file_dict.values():
            # selected_item = self.selected_ui.widget.findItems(item.fileName(), QtCore.Qt.MatchExactly)
            # row = selected_item[0].row()
            # desc = self.selected_ui.widget.cellWidget( row, 2 ).toPlainText()
            if isinstance( item, SeqItem ):
                print(item.text())
                selected_item = self.selected_ui.widget.findItems(item.text(), QtCore.Qt.MatchExactly)
                row = selected_item[0].row()
                seq_colorspace = self.selected_ui.widget.cellWidget(row, 2).currentText()
                desc = self.selected_ui.widget.cellWidget( row, 3 ).toPlainText()
                mov_colorspace = self.selected_ui.widget.cellWidget(row, 4).currentText()
                fps_checkbox = self.selected_ui.widget.cellWidget(row, 5)
                fps_is_checked = fps_checkbox.isChecked()
                selected_item_list.append([ "seq", item, item_context, seq_colorspace,desc, mov_colorspace,fps_is_checked ])
            elif "*."+item.suffix().lower() in self.file_form.image_filters:
                selected_item = self.selected_ui.widget.findItems(item.fileName(), QtCore.Qt.MatchExactly)
                row = selected_item[0].row()
                seq_colorspace = self.selected_ui.widget.cellWidget(row, 2).currentText()
                desc = self.selected_ui.widget.cellWidget( row, 3 ).toPlainText()
                mov_colorspace = self.selected_ui.widget.cellWidget(row, 4).currentText()
                fps_checkbox = self.selected_ui.widget.cellWidget(row, 5)
                fps_is_checked = fps_checkbox.isChecked()
                if item.suffix() in ["mov","ogv","mp4"]:
                    selected_item_list.append([ "mov", item, item_context, seq_colorspace,desc ,mov_colorspace,fps_is_checked ])
                else:
                    selected_item_list.append([ "image", item, item_context, seq_colorspace,desc ,mov_colorspace,fps_is_checked ])
                
        return selected_item_list


    def resize_height_toContents( self, desc_editor ):
        row_count  = desc_editor.blockCount()
        font = QtGui.QFontMetrics(desc_editor.font())
        height = font.height()
        desc_editor.setFixedHeight( row_count * height + 8 )
        self.selected_ui.widget.resizeRowsToContents( )
