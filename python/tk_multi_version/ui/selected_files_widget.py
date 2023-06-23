from tank.platform.qt import QtCore, QtGui

class Ui_SelectedFilesWidget( object ):
    def setupUi( self, selected_ui ):
        selected_ui.setObjectName( "selected_ui" )

        self.widget = QtGui.QTableWidget()      
        # self.widget.setEditTriggers( QtGui.QAbstractItemView.NoEditTriggers )
        # self.widget.horizontalHeader().setResizeMode( QtGui.QHeaderView.Stretch )
        # self.widget.resizeColumnToContents( 0 )
        self.widget.verticalHeader().hide()
        self.widget.setColumnCount( 4 )
        self.widget.setHorizontalHeaderLabels( [ 'Project', 'Version' , 'Description' , '23.976'] )
        self.widget.horizontalHeader().resizeSection( 0, 70 )
        self.widget.horizontalHeader().resizeSection( 1, 180 )
        self.widget.horizontalHeader().resizeSection( 2, 250 )
        self.widget.horizontalHeader().resizeSection( 3, 20 )
        self.widget.horizontalHeader().setResizeMode( 0, QtGui.QHeaderView.Fixed )
        self.widget.horizontalHeader().setResizeMode( 1, QtGui.QHeaderView.Fixed )
        self.widget.horizontalHeader().setResizeMode( 2, QtGui.QHeaderView.Fixed )
        # self.widget.horizontalHeader().setResizeMode( 3, QtGui.QHeaderView.Fixed )
        self.widget.horizontalHeader().setStretchLastSection( True )

        self.widget.setDragDropOverwriteMode( False )
        self.widget.setDragEnabled( False )
        # self.widget.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
        # self.widget.resizeRowsToContents( )
        # self.widget.resizeRowsToContents( )
        # self.widget.verticalHeader().hideSection()
        
        # self.table_layout = QtGui.QVBoxLayout( selected_ui )
        # self.table_layout.addWidget( self.widget )

        self.retranslateUi( selected_ui )
        QtCore.QMetaObject.connectSlotsByName(selected_ui)

        # self.widget_tab = QtGui.QWidget( selected_ui )
        # self.widget_tab.setLayout( self.table_layout) 

    def retranslateUi(self, selected_ui):
        selected_ui.setWindowTitle(QtGui.QApplication.translate("selected_ui", "Form", None, QtGui.QApplication.UnicodeUTF8))

# class Ui_DescriptionWidget( QtGui.QTextEdit ):
#     def __init__( self, parent = None ):
#         super( Ui_DescriptionWidget, self ).__init__(parent)
#         self.textChanged.connect(self.resize_height_toContents)
#     # def keyPressEvent( self, event ):
#     #     if event.key() == QtCore.Qt.Key_Return:
#     #         self.resize_height_toContents()

#     def resize_height_toContents( self ):
#         row_count  = self.document().blockCount()
#         # row_height = self.document().height()
#         print(row_count)
#         # print(row_height)
#         # self.setMinimumHeight( 20 * row_count )
#         self.setMaximumHeight( 20 * row_count )