#some useful imports
import sys
from PyQt4 import QtGui, QtCore
from collections import OrderedDict as ODict
import copy
import os

from useful_functions import loc_to_glob, glob_to_loc

#####---------------Some small graphical objects to be built upon----------------------#####
class LineEdit(QtGui.QLineEdit):
    """
    This class inherits from QtGui.QLineEdit graphical object.
    It is written to have useful methods of getting the text and setting text.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def get_text(self):
        return self.text()
    
    def set_text(self, text):
        self.textbox_str = text;
        self.setText(self.textbox_str)
        
        
        
class horizontal_line(QtGui.QFrame):
    """
    Create a class that extends from `QtGui.QFrame` with the sole purpose of creating a horizontal 
    line to be drawn by the panels.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)
        

class Dirbox(QtGui.QHBoxLayout):
    """
    This class inherits from QtGui.QHBoxLayout and simply contains the horizontal line edit box (QtGui.QLineEdit)
    with the push button file selector. The inheritance from QtGui.QHBoxLayout allow the object to be of type QLayout
    which helps with the auto vertical alignment done by the class between `QLabel` (preceding text label) and the `QLayout` 
    object. It accepts the following input arguments with optional arguments:
    
    text_changed_func -> function handle to be called when the text in the lineedit has changed
    parent -> parent widget for this object. default to none
    dir_flag -> if the file/folder to be selected is a folder. default to true (directory not file)
    file_extension -> file extension to look for when opening file selector. default to .tex for tex files
    """
    
    def __init__(self, text_changed_func, parent=None, dir_flag = True, file_extension = 'Tex files (*.tex)'):
        super().__init__()
        
        self.parent=None
        self.file_extension = file_extension
        self.dir_flag = dir_flag
        
        #create line edit box + button
        self.edit_box = QtGui.QLineEdit()
        self.dir_button = QtGui.QPushButton("...")
        #connect the press of the button to a callback
        if self.dir_flag:
            self.dir_button.clicked.connect(self.dir_select)
        else:                
            self.dir_button.clicked.connect(self.file_select)
            
        #put the widgets into the horizontal box        
        self.addWidget(self.edit_box)
        self.addWidget(self.dir_button)
        #hbox.addStretch()
        
        #when text in text_edit change, call a function
        self.edit_box.textChanged.connect(text_changed_func)
        
    def file_select(self):
        self.set_text(QtGui.QFileDialog.getOpenFileName(self.parent, 'Select file', os.getcwd(), self.file_extension))
        
    def dir_select(self):
        self.set_text(QtGui.QFileDialog.getExistingDirectory(self.parent, 'Select folder', os.getcwd()))
        
    def set_text(self, text):
        self.textbox_str = text;
        self.edit_box.setText(self.textbox_str)
        
    def get_text(self):
        return self.edit_box.text()
        
        
        
class ListBox(QtGui.QListWidget):
    """
    This class is a custom type that inherits QListWidget and overloads the drag and drop functions,
    such that drag and drop operations within and between lists and be achieved. It only accepts
    the optional argument stating the parent widget to this child list.
    """
    
    #create our own signal that will be emitted when drap and drop process has finished
    fin_drop_signal = QtCore.pyqtSignal()
    fin_drag_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        
        
    #first function is when the drag motion is detected
    def dragMoveEvent(self, e):
        if e.mimeData().hasFormat("text/plain"):
            e.setDropAction(QtCore.Qt.MoveAction)
            e.accept()
        else:
            e.ignore()
    
    #function to enter the drag event, this will be followed by the dragMoveEvent defined on top       
    def dragEnterEvent(self, event):
        if (event.mimeData().hasFormat("text/plain")):
            event.accept()
        else:
            event.ignore()
    
    #function to start the dragging operation (it will remove item from the list)
    def startDrag(self, supportedActions):
        item = self.currentItem()
        mimeData = QtCore.QMimeData()
        
        ba = item.text()        
        mimeData.setData("text/plain", ba)        
               
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        
        if(drag.exec() == QtCore.Qt.MoveAction):
            self.takeItem(self.row(item))
            self.fin_drag_signal.emit()

    #function during the dropping operation
    def dropEvent(self, event):
        if event.mimeData().hasFormat("text/plain"):
            event.accept()
            event.setDropAction(QtCore.Qt.MoveAction)
            
            #find index location of event
            dropIndex = self.indexAt(event.pos()).row()                        
            #create an item to be inserted
            item = QtGui.QListWidgetItem();
            name = event.mimeData().text()
            item.setText(name)
            if(dropIndex >=0):
                #insert the item
                self.insertItem(dropIndex, item)
            else:
                self.addItem(item)
                
            #emit the finished drop signal
            self.fin_drop_signal.emit()
            
        else:
            event.ignore()
            

class ListwButtons(QtGui.QWidget):
    """
    This class creates a widget with vertical alignment containing the following widgets:
        QtGui.QLabel -> for the text at the top of the list, indicating what is inside the list
        QtGui.QListWidget/ListBox -> to list items in lc_list (locally maintained version of gl_list)
                                    and may be capable of drag and drop (if it is ListBox)
        two horizontally aligned buttons -> one is retore the state of the list while the other to delete
                                    the selected item of the list
                                    
    The class takes the following arguments (some are optional):
    
    gl_list -> list of items to initially show in the list widget
    set_button_func -> function handle to be called when either the delete or restore button is pressed
    flag_allow_drag -> a flag to indicate whether the drag and drop operation is permitted. default to False
    parent -> the parenting widget of this child widget. default to none.
    """
    
    def __init__(self, gl_list, header, set_button_func, flag_allow_drag = False, parent = None):
        super().__init__(parent=parent)
        
        vbox = QtGui.QVBoxLayout()
        
        #store some stuff
        self.gl_list = copy.deepcopy(gl_list)
        self.lc_list = copy.deepcopy(gl_list)
        
        #add the header to the layout
        vbox.addWidget(QtGui.QLabel(header))
        
        #create a list widget
        if flag_allow_drag:
            self.list = ListBox(self)
            self.list.fin_drag_signal.connect(self.update_list)
            self.list.fin_drop_signal.connect(self.update_list)
        else:
            self.list = QtGui.QListWidget(self)
            
        self.list.addItems(gl_list)
        
        vbox.addWidget(self.list)
        
        #create two buttons, to restore and delete
        self.button_restore = QtGui.QPushButton("Restore")
        self.button_delete = QtGui.QPushButton("Delete")
        
        self.button_restore.clicked.connect(self.items_restore)        
        self.button_restore.clicked.connect(lambda: set_button_func(True))
        self.button_delete.clicked.connect(self.item_delete)        
        self.button_delete.clicked.connect(lambda: set_button_func(True))
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.button_restore)
        hbox.addWidget(self.button_delete)
        
        vbox.addLayout(hbox)
        
        self.setLayout(vbox)
        
    def items_restore(self):
        self.list.clear()
        self.lc_list = copy.deepcopy(self.gl_list)
        self.list.addItems(self.lc_list)
        
    def item_delete(self):
        #self.list.removeItemWidget(self.list.currentItem())
        item = self.list.takeItem(self.list.currentRow())
        if item:
            self.lc_list.remove(item.text())
        
    def move_item_up(self):
        c_index = self.list.currentRow()
        if c_index >=0 and c_index-1>=0:
            item = self.list.takeItem(c_index)
            self.list.insertItem(c_index-1, item)
            self.list.setCurrentRow(c_index-1)
            
            temp = self.lc_list[c_index-1]
            self.lc_list[c_index-1] = self.lc_list[c_index]
            self.lc_list[c_index] = temp

    def move_item_down(self):
        c_index = self.list.currentRow()
        if c_index >=0 and c_index + 1 < self.list.count():
            item = self.list.takeItem(c_index)
            self.list.insertItem(c_index+1, item)
            self.list.setCurrentRow(c_index+1)
            
            temp = self.lc_list[c_index+1]
            self.lc_list[c_index+1] = self.lc_list[c_index]
            self.lc_list[c_index] = temp
            
    def get_current_list(self):
        return self.lc_list
    
    def add_new_list(self,gl_list):
        self.list.clear()
        self.gl_list = copy.deepcopy(gl_list)
        self.lc_list = copy.deepcopy(gl_list)
        self.list.addItems(self.gl_list)
        
    def update_list(self):
        self.lc_list = []
        for row in range(self.list.count()):
            self.lc_list.append(self.list.item(row).text())
        
class AdjustableLists(QtGui.QWidget):
    """
    Further building on top of ListwButtons to create two of them, horizontally aligned
    on the left and right with three vertically buttons in the middle. The two lists are 
    meant to show the dictionary key on the left and the value (which is a list) on the right.
    The graphic on the right will be QStackedWidget containing ListwButtons for different items 
    in the left list. The class implements showing the corresponding ListwButtons on the right 
    from QStackedWidget based on the item selected on the left. The three buttons in the middle are:
        move up -> to move item in either the right or the left list up
        generate save point -> to generate the new restore point based on the current state of the lists
        move down -> to move item in either the right or the left list down
        
    The class accepts the following input arguments:
        gl_dict -> dictionary of item to be viewed using two lists (left and right)
        header -> text on top of ListwButtons. the left list will have 'sub-' infront of the header
        parent -> optionally tell which is the parent of this child widget. default is none.
    """
    
    def __init__(self, gl_dict, header, parent=None):
        super().__init__(parent=parent)
        
        #store some variables
        self.gl_dict = gl_dict
        self.header = header
        
        #horizontal layout
        self.hbox = QtGui.QHBoxLayout()
                
        #create the left panel
        self.left_list = ListwButtons(list(gl_dict.keys()), header, self.set_apply_button, flag_allow_drag=True, parent=self)
        self.left_list.list.currentRowChanged.connect(self.sub_display)
        self.left_list.list.fin_drop_signal.connect(lambda: self.set_apply_button(True))
        self.left_list.list.itemClicked.connect(lambda: setattr(self, 'flag', False))
        
        self.hbox.addWidget(self.left_list)
        
        
        #add the move up and down buttons
        self.button_up = QtGui.QPushButton("Move Up")
        self.button_down = QtGui.QPushButton("Move Down")
        self.button_new_restore = QtGui.QPushButton("Generate New Restore\n (Apply Changes)")
        self.button_new_restore.setEnabled(False)
        
        self.button_up.clicked.connect(self.move_item_up)
        self.button_down.clicked.connect(self.move_item_down)
        

        #add buttons to vbox and then to hbox
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.button_up)
        vbox.addWidget(self.button_new_restore)
        vbox.addWidget(self.button_down)
        
        self.hbox.addLayout(vbox)
        
        
        #add a stacked widget to the right
        self.stack = QtGui.QStackedWidget(self)
        self.create_right_stack()
        
        self.hbox.addWidget(self.stack)
        
        self.setLayout(self.hbox)
    
    def create_right_stack(self):
        self.stack_widgets = {}
        for key in self.gl_dict.keys():
            self.stack_widgets[key] = ListwButtons(self.gl_dict[key], "sub-"+self.header, self.set_apply_button,
                                                   flag_allow_drag=True,parent=self)
            self.stack_widgets[key].list.itemClicked.connect(lambda: setattr(self, 'flag', True))            
            self.stack_widgets[key].list.fin_drop_signal.connect(lambda: self.set_apply_button(True))
            self.stack.addWidget(self.stack_widgets[key])
        
        #create a blank one
        self.stack_widgets['blank'] = ListwButtons([], "sub-"+self.header, self.set_apply_button, self)
        self.stack.addWidget(self.stack_widgets['blank'])
        self.stack.setCurrentWidget(self.stack_widgets['blank'])
        
    def sub_display(self):
        if self.left_list.list.currentRow() >= 0:
            self.stack.setCurrentWidget(self.stack_widgets[self.left_list.list.currentItem().text()])
        else:
            self.stack.setCurrentWidget(self.stack_widgets['blank'])
        
    def move_item_up(self):
        if not self.flag:
            self.left_list.move_item_up()
        else:
            self.stack.currentWidget().move_item_up()
        
        self.button_new_restore.setEnabled(True)
        
    def move_item_down(self):
        if not self.flag:
            self.left_list.move_item_down()
        else:
            self.stack.currentWidget().move_item_down()
        
        self.button_new_restore.setEnabled(True)
        
    def set_panel_dict(self,gl_dict):
        
        self.gl_dict = gl_dict
        
        #modify the left list
        self.left_list.add_new_list(list(self.gl_dict.keys()))
        
        #remove stack from the horizontal layout
        self.hbox.removeWidget(self.stack)
        
        #create new right list
        self.create_right_stack()
        
        #add the widget to the horizontal stack
        self.hbox.addWidget(self.stack)
        
    def get_panel_dict(self):
        self.gl_dict = ODict()
        keys = self.left_list.get_current_list()
        
        for key in keys:
            self.gl_dict[key] = self.stack_widgets[key].get_current_list()
            
        return self.gl_dict
    
    def set_apply_button(self, On=True):
        self.button_new_restore.setEnabled(On)




        
#####---------------The following are major widgets developed for the application, specifically for different panels of the main application----------------------#####
class Settings(QtGui.QWidget):
    """
    This creates the setting panel for the main application. It has capability of both
    extracting the information + loading the information from elsewhere, Ex: setting file
    
    Input arguments:
        parent -> the parent window (main window of the application)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        #create a vertical alignment
        self.layout = QtGui.QFormLayout()
        
        #Create first row -> Latex directory
        self.latex_dir = Dirbox(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Latex Dir"),self.latex_dir) 
        self.layout.addRow(horizontal_line())
        
        #create second row -> appendix folder
        self.append_folder = Dirbox(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Appendix Folder"), self.append_folder)
        
        #create third row -> prelim folder
        self.prelim_folder = Dirbox(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Prelim Folder"), self.prelim_folder)
        self.layout.addRow(horizontal_line())
        
        #create fourth row -> refs file
        self.refs_file = Dirbox(self.text_changed,dir_flag=False, file_extension='Bib files (*.bib)')
        self.layout.addRow(QtGui.QLabel("Refs File"), self.refs_file)

        #create 5th row -> for storing temporary files and settings file
        self.storage = Dirbox(self.text_changed)
        self.ifstore = QtGui.QCheckBox("Allow storage")
        hbox = QtGui.QHBoxLayout()
        hbox.addLayout(self.storage)
        hbox.addWidget(self.ifstore)
        self.layout.addRow(QtGui.QLabel("Temp folder"), hbox)
        self.layout.addRow(horizontal_line())

        
        #create 6th row -> master filename
        self.master_file = LineEdit()
        self.master_file.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Master File"), self.master_file)
        
        #create 7th row -> class file
        self.class_file = LineEdit()        
        self.class_file.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Class File"), self.class_file)
        self.layout.addRow(horizontal_line())
        
        #create 8th row -> latex subdirec
        self.latex_sub = LineEdit()
        self.latex_sub.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Latex Subdir"), self.latex_sub)
        
        #create 9th row -> img subdirec
        self.img_sub = LineEdit()
        self.img_sub.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Img Subdir"), self.img_sub)
        self.layout.addRow(horizontal_line())
               
        
        #create 10th row -> for storing tags information
        self.label_tag = LineEdit()
        self.label_tag.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Label tag"), self.label_tag)
        
        #create 11th row -> for storing tags information
        self.ref_tag = LineEdit()
        self.ref_tag.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("Ref tag"), self.ref_tag)
                
        #create 12th row -> for storing tags information
        self.app_tag = LineEdit()
        self.app_tag.textChanged.connect(self.text_changed)
        self.layout.addRow(QtGui.QLabel("App tag"), self.app_tag)
        
        #create a radio button and two push buttons (apply settings and save setting {to file})
        hbox = self.radio_loc_glob()
        self.apply_button = QtGui.QPushButton('Apply Changes')
        self.apply_button.setEnabled(False)
        self.save_setting_button = QtGui.QPushButton('Save Settings (to file)')
        self.save_setting_button.setEnabled(False)
        
        hbox_n = QtGui.QHBoxLayout()
        hbox_n.addLayout(hbox)
        hbox_n.addWidget(self.apply_button)
        hbox_n.addWidget(self.save_setting_button)
        
        self.layout.addRow(hbox_n)
        
        #add the whole layout
        self.setLayout(self.layout)
        
        #create a list of fields to be extracted when all settings information are required
        self.useful_fields = ['latex_dir', 'append_folder', 'prelim_folder', 'refs_file', 'master_file',
                             'latex_sub', 'img_sub', 'storage', 'label_tag', 'ref_tag', 'app_tag', 'class_file']
        self.to_be_validated = ['latex_dir', 'append_folder', 'prelim_folder', 'refs_file', 'storage']
        self.is_file = ['refs_file']
        
        #initially valid setting is false
        self.valid_setting = False
    
    def text_changed(self):
        self.apply_button.setEnabled(True)
    
        
    def radio_loc_glob(self):
        r1 = QtGui.QRadioButton('local')
        r2 = QtGui.QRadioButton('global')
        
        r1.toggled.connect(lambda: self.radio_toggle(r1))        
        r2.toggled.connect(lambda: self.radio_toggle(r2))
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(r1)
        hbox.addWidget(r2)
        return hbox
    
    def radio_toggle(self, button):
        #if local is on 
        if(button.text() == 'global' and button.isChecked()):
            #iterate through all things that can be local
            for field in self.to_be_validated:
                self.loc_to_glob(field, field in self.is_file)            
            
        #if global is on
        elif(button.text() == 'local' and button.isChecked()):
            #iterate through all things that can be global
            for field in self.to_be_validated:
                self.glob_to_loc(field)
                        
    
    def loc_to_glob(self, field, is_file=False):
        field_to_change = getattr(self, field)
        c_text = field_to_change.get_text()
        #call the function
        c_text = loc_to_glob(self.latex_dir.get_text(), c_text, is_file)
        #change the text accordingly
        field_to_change.set_text(c_text)

    
    def glob_to_loc(self, field):
        field_to_change = getattr(self, field)
        #call the global function to return the altered fname
        c_text = glob_to_loc(self.latex_dir.get_text(), field_to_change.get_text())
        
        field_to_change.set_text(c_text)
    
    def validate_setting(self):
        #store invalids in a list to return
        invalid_dirs = []
        
        for field in self.to_be_validated:
            c_text = getattr(self, field).get_text()
            c_text = loc_to_glob(self.latex_dir.get_text(), c_text, field in self.is_file)
            if c_text:
                if not os.path.exists(c_text):
                    invalid_dirs.append(field)
            else:
                invalid_dirs.append(field)
        
        if(len(invalid_dirs) > 0):
            self.valid_setting = False
        else:
            self.valid_setting = True
            
        return invalid_dirs
            
    def get_setting_dict(self):
        
        #put things into dictionary and return
        d = {field:getattr(self, field).get_text() for field in self.useful_fields}
        
        for field in self.to_be_validated:
            d[field] = glob_to_loc(self.latex_dir.get_text(), getattr(self, field).get_text())
            
        return d
    
    def set_setting(self, setting_dict):
        for key in setting_dict.keys():
            if key in self.useful_fields:
                getattr(self, key).set_text(setting_dict[key])
        

class SettingDialog(QtGui.QMessageBox):
    """
    This class extends from QtGui.QMessageBox to show error message for invalid settings in setting panel.
    The class takes the following arguments(/optional):
    
    accepted_func -> which function to execute if the user press the 'Yes' button
    parent -> the parent of this child object. default is none
    text -> the text to display when the user press 'show more details'. default is none
    
    """
    
    def __init__(self, accepted_func, parent=None, text=None):
        super().__init__(parent=parent)
        
        self.text = None
        
        #set the icon to indicate that an error has occured
        self.setIcon(self.Critical)
        
        #set the title of error message box
        self.setWindowTitle('Settting Error~!')
        
        #set the main message of the box
        self.setText("There are some invalid settings.")
        
        #displays additional information regarding the error
        self.setInformativeText("Some input directories do not exist!\n Do you want to reset the invalid directories?")
        
        #set standard buttons
        self.setStandardButtons(self.Yes | self.No)
        
        #set detailed text
        self.setDetailedText(self.text)
        
        #set the function to be called later
        self.func_exec = accepted_func
        
    def execute(self):
        button = self.exec_()
        if button == self.Yes:
            self.func_exec()
        
    def set_details(self, invalid_dirs):
        text = "The following directories do not exist: \n"
        for invalid_dir in invalid_dirs:
            text += invalid_dir + "\n"
            
        
        self.text = text
        self.setDetailedText(self.text)
    

class AppendixLists(QtGui.QWidget):
    """
    Similarly to the Settings class, this creates the appendix selection panel.
    The class takes the following input arguments: 
    
    gl_list -> the list of items to be visually shown in ListwButtons
    header -> used to set the text label in ListwButtons
    parent -> the parent of this child object. default is none
    """
    
    def __init__(self, gl_list, header, parent=None):
        super().__init__(parent=parent)
        
        #store some variables
        self.gl_list = gl_list
        self.header = header
        
        #horizontal layout
        self.hbox = QtGui.QHBoxLayout()
                
        #create the left panel
        self.left_list = ListwButtons(gl_list, header, self.set_apply_button, flag_allow_drag=True, parent=self)
        self.left_list.list.fin_drop_signal.connect(lambda: self.set_apply_button(True))
        
        self.hbox.addWidget(self.left_list)
        
        
        #add the move up and down buttons
        self.button_up = QtGui.QPushButton("Move Up")
        self.button_down = QtGui.QPushButton("Move Down")
        self.button_new_restore = QtGui.QPushButton("Generate New Restore\n (Apply Changes)")
        self.button_new_restore.setEnabled(False)
        self.button_regen = QtGui.QPushButton("Regenerate from Chapters List")
        
        
        self.button_up.clicked.connect(self.move_item_up)
        self.button_down.clicked.connect(self.move_item_down)
        

        #add buttons to vbox and then to hbox
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.button_up)
        vbox.addWidget(self.button_new_restore)
        vbox.addWidget(self.button_regen)
        vbox.addWidget(self.button_down)
        
        self.hbox.addLayout(vbox)
        
        
        self.setLayout(self.hbox)
    
        
    def move_item_up(self):
        self.left_list.move_item_up()        
        self.button_new_restore.setEnabled(True)
        
    def move_item_down(self):
        self.left_list.move_item_down()
        self.button_new_restore.setEnabled(True)
        
    def set_panel_dict(self,gl_list):
        
        self.gl_list = gl_list
        
        #modify the left list
        self.left_list.add_new_list(self.gl_list)
                
    def get_panel_dict(self):
        self.gl_list = self.left_list.get_current_list()
        
        return self.gl_list
    
    def set_apply_button(self, On=True):
        self.button_new_restore.setEnabled(On)
        
        

class PrelimLists(QtGui.QWidget):
    """
    Similarly to Settings and AppendixLists, this class creates a panel for selecting preliminary files.
    Unlike AdjustableLists, this creates two lists vertically aligned (top and bottom) of ListwButtons with
    horizontally  aligned three-vertically-aligned buttons (move up, regenerate restore point and move up identical 
    to AdjustableLists). It accepts the following input arguments:
    
    lists -> tuple of two lists. One for top and the other for bottom ListwButtons
    parent -> the parent of this child object. default is none
    
    """
    
    def __init__(self, lists, parent=None):
        super().__init__(parent)
        
        list1, list2 = lists
        #store locally some stuff
        self.list1 = copy.deepcopy(list1)
        self.list2 = copy.deepcopy(list2)
        
        #set up the overlaying horizontal alignment of widgets
        hbox = QtGui.QHBoxLayout()
        
        #set up a vertical alignment of widgets
        vbox = QtGui.QVBoxLayout()
        
        #create the first list based on list1
        self.upper_list = ListwButtons(list1, 'Before begin', self.set_apply_button, flag_allow_drag=True, parent=self)
        self.upper_list.list.itemClicked.connect(lambda: setattr(self, 'flag', False))
        self.upper_list.list.fin_drag_signal.connect(lambda: self.set_apply_button(True) )
        
        vbox.addWidget(self.upper_list)
        
        #create the second list based on list2
        self.lower_list = ListwButtons(list2, 'After begin', self.set_apply_button,flag_allow_drag=True, parent=self)
        self.lower_list.list.itemClicked.connect(lambda: setattr(self, 'flag', True))
        self.lower_list.list.fin_drag_signal.connect(lambda: self.set_apply_button(True) )
        
        vbox.addWidget(self.lower_list)
        
        hbox.addLayout(vbox)
        
        #create buttons to move up and down and save changes
        vbox = QtGui.QVBoxLayout()       
        self.button_up = QtGui.QPushButton("Move Up")
        self.button_down = QtGui.QPushButton("Move Down")   
        self.button_save_changes = QtGui.QPushButton("Save Changes")
        self.button_save_changes.setEnabled(False)
        
        self.button_up.clicked.connect(self.move_item_up)
        self.button_down.clicked.connect(self.move_item_down)
        
        vbox.addWidget(self.button_up)
        vbox.addWidget(self.button_save_changes)
        vbox.addWidget(self.button_down)
        
        hbox.addLayout(vbox)
        
        self.setLayout(hbox)
    
    def set_panel_dict(self,gl_lists):
        
        list1, list2 = gl_lists
        self.list1 = copy.deepcopy(list1)
        self.list2 = copy.deepcopy(list2)
        
        #modify the upper list
        self.upper_list.add_new_list(self.list1)
        
        #modify the bottom list
        self.lower_list.add_new_list(self.list2)
        
    def move_item_up(self):
        if not self.flag:
            self.upper_list.move_item_up()
        else:
            self.lower_list.move_item_up()
        
        self.button_save_changes.setEnabled(True)
        
    def move_item_down(self):
        if not self.flag:
            self.upper_list.move_item_down()
        else:
            self.lower_list.move_item_down()
        
        self.button_save_changes.setEnabled(True)
                
    def get_panel_dict(self):
        self.list1 = self.upper_list.get_current_list()        
        self.list2 = self.lower_list.get_current_list()
        return (self.list1, self.list2)
    
    def set_apply_button(self, On=True):
        self.button_save_changes.setEnabled(On)