# # -*- coding: utf-8 -*-

# import sgtk
# from sgtk.platform.qt import QtCore, QtGui

# from .files_form import FilesForm

class SelectedFilesForm( QtGui.QWidget ):
    def __init__(self,root_path,parent=None):
        self.root_path = root_path
        QtGui.QWidget.__init__(self, parent)

        self.dir_model = QtGui.QFileSystemModel()
        self.file_model = QtGui.QFileSystemModel()
        self.seq_model = QtGui.QStringListModel(self.sequence_list)

    def update_from_list_click( self ):
        model = self.file_form.ui.file_view.model()
        if isinstance( model, QtGui.QFileSystemModel ):
            self.add_selected_mov_refresh()
        elif isinstance( model, QtGui.QStandardItemModel ):
            self.add_selected_seq_refresh( )
        else :
            pass
        self.ui.selected_file_view.setModel( self.selected_file_model )

    def add_selected_mov_refresh( self ):
        index = self.file_form.ui.file_view.selectedIndexes( )
        if not index:
            return 
        model = self.file_form.ui.file_view.model()
        item = model.fileInfo(index[0])
        item_name = model.fileName( index[0] )
        if item.suffix() in ["mov","ogv","mp4"]:
            if not item_name in self.selected_file_dict:
                self.selected_file_model.appendRow( VideoItem( item_name ) ) # make filesystemitem -> standarditem
                self.selected_file_dict[ item_name ] = [ item, self.context ]
            else: 
                pass

    def add_selected_seq_refresh( self ):
        index = self.file_form.ui.file_view.selectedIndexes( )
        if not index:
            return 
        model = self.file_form.ui.file_view.model()
        item = model.itemFromIndex( index[0] )
        item_name = item.text()
        if not item_name in self.selected_file_dict:
            self.selected_file_model.appendRow( SeqItem( item_name ) )
            self.selected_file_dict[ item_name ] = [ item, self.context ]
        else:
            pass        

    def update_from_selected_list_click( self ):
        self.delete_selected_list_refresh()
        self.ui.selected_file_view.setModel( self.selected_file_model )

    def delete_selected_list_refresh( self ):
        model  = self.ui.selected_file_view.model()
        index  = self.ui.selected_file_view.selectedIndexes()
        if index:
            item   = model.itemFromIndex( index[0] )
            if isinstance( item, VideoItem ) and item.video_info in self.selected_file_dict:
                del self.selected_file_dict[ item.video_info ]
                self.selected_file_model.removeRow( index[0].row() )            
            elif isinstance( item, SeqItem ) and item.seq_info in self.selected_file_dict:
                del self.selected_file_dict[ item.seq_info ]
                self.selected_file_model.removeRow( index[0].row() )        

    def selected_item( self ):
        selected_item_list = []
        if not self.selected_file_dict:
            return
        for item, item_context in self.selected_file_dict.values():
            if isinstance( item, SeqItem ):
                selected_item_list.append([ "seq", item, item_context ])
            elif "*."+item.suffix().lower() in self.file_form.image_filters:
                if item.suffix() in ["mov","ogv","mp4"]:
                    selected_item_list.append([ "mov", item, item_context ])
                else:
                    selected_item_list.append([ "image", item, item_context ])
        return selected_item_list

    def keyPressEvent( self, e ):
        if e.key() == QtGui.QKeySequence('Delete'):
            self.update_from_selected_list_click()
