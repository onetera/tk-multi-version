# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
import sys
import os
import traceback

from .my_tasks.my_tasks_form import MyTasksForm
from .my_tasks.my_tasks_model import MyTasksModel
from .files_widget.files_form import FilesForm
from .util import monitor_qobject_lifetime
# by importing QT from sgtk rather than directly, we ensure that
# the code will be compatible with both PySide and PyQt.
from sgtk.platform.qt import QtCore, QtGui
from .ui.dialog import Ui_Dialog
from .framework_qtwidgets import *
from .upload_shotgun import *

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
        self.ui.upload_btn.clicked.connect(self._upload)
    

    def _upload(self):
        selected_type,item = self.file_form.selected_item()
        if not item:
            return
        desc = self.ui.desc_edit.toPlainText()

        trascoding = Transcoding(item,self.context,selected_type,desc)
        version = UploadVersion(item,self.context,selected_type)
        trascoding.create_nuke_script()
        try:
            trascoding.create_mov()
            trascoding.create_mp4()
            trascoding.create_webm()
            trascoding.create_thumbnail()
            trascoding.create_thumbnail_for_image()
            version.create_version(trascoding.read_path,trascoding.mov_path,desc)
            version.upload_thumbnail(trascoding.thumbnail_file)
            version.upload_filmstrip_thumbnail(trascoding.filmstream_file)
            #version.upload_mov(trascoding.mov_path)
            version.upload_mp4(trascoding.mp4_path)
            version.upload_webm(trascoding.webm_path)
        except Exception as e:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setText("Error.")
            msg.setInformativeText(str(e))
            msg.setWindowTitle("Version Error")
            msg.exec_()
            return
        
        text = []
        text.append(self.context.entity['name'])
        text.append('<a href="{0}">{0}</a>'.format(self.context.shotgun_url))
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
        
        init_path = os.path.join(
            self.context.filesystem_locations[0],
            self.context.step['name'])

        self.file_form = FilesForm(init_path)
        self.ui.source_widget.addTab(self.file_form,"Select")
        self._context_widget.set_context(self.context)
    

    def create_context_form(self):
        self._context_widget = context_selector.ContextWidget(self)
        self._context_widget.set_up(self._task_manager)
        self._context_widget.setFixedWidth(550)
        #self._context_widget.setFixedHeight(200)
        #self._context_widget.resize(600,200)
        self._context_widget.enable_editing(True,"Select Task")
        self._context_widget.restrict_entity_types_by_link(
            "PublishedFile", "entity")
        self._context_widget.set_context(sgtk.platform.current_bundle().context)
        self.ui.context_widget.addTab(self._context_widget,"Context")

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
        # if self._facility_tasks_model:
        #     self._facility_tasks_model.async_refresh()
