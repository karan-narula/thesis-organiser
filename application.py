#some useful imports
import sys
from PyQt4 import QtGui, QtCore
import os
from graphics_objs import*
from useful_functions import*

#####---------------The main application class----------------------#####
class Application(QtGui.QMainWindow):
    """
    This class inherits from QtGui.QMainWindow since it is an instant of
    the main window class
    """
    
    def __init__(self):
        super().__init__()
        self.setGeometry(800,500,200,0)
        self.setWindowTitle('Thesis Compiler')
        #self.setWindowIcon(QtGui.QIcon('latex_logo.png'))
        
        #initialise member non-inherited member data which will be in use during the application
        self.variables_init()
        
        #create dockable window area
        self.create_dockable()

        #----------------Following is the creation of different panels and the associated variables---------------
        #create setting panel                 
        self.setting = Settings()
        self.setting.apply_button.clicked.connect(self.apply_changes)
        self.setting.save_setting_button.clicked.connect(self.save_setting)
        self.setting.ifstore.stateChanged.connect(self.allow_store)
        
        #create dialog box specific to setting_panel
        self.setting_error = SettingDialog(accepted_func=self.setting_dialog_accept, parent=self.dockable_panel)
        
        #create the chapters-list panel
        self.chapters_selection = AdjustableLists(self.chapter_dict, "Chapters")
        self.chapters_selection.button_new_restore.clicked.connect(lambda: self.reset_restore('chapters_selection',
                                                                                              'chapter_dict'))
        
        #create the appendix-list panel
        self.appendices_selection = AppendixLists(self.appendix_list, "Appendices")
        self.appendices_selection.button_new_restore.clicked.connect(lambda: self.reset_restore('appendices_selection',
                                                                                                'appendix_list'))
        self.appendices_selection.button_regen.clicked.connect(self.get_appendix_list)
        
        #create the prelims-list panel
        self.prelims_selection = PrelimLists(self.prelims_lists)
        self.prelims_selection.button_save_changes.clicked.connect(lambda: self.reset_restore('prelims_selection',
                                                                                                'prelims_lists'))
        
        #create the editable text object for loading, saving and editing the template
        self.template_format = QtGui.QTextEdit()
        
        #----------------Following is for the menu bar--------------------
        #create some actions for the file menu
        fileAction_quit = QtGui.QAction("&Quit", self)
        fileAction_quit.setShortcut("Ctrl+Shift+Q")
        fileAction_quit.triggered.connect(self.close_application)
        
        fileAction_loadTemplate = QtGui.QAction("&Load Template", self)
        fileAction_loadTemplate.setShortcut("Ctrl+L")
        fileAction_loadTemplate.triggered.connect(self.load_template)
        
        self.fileAction_saveTemplate = QtGui.QAction("&Save Template", self)
        self.fileAction_saveTemplate.setShortcut("Ctrl+S")
        self.fileAction_saveTemplate.setEnabled(False)
        self.fileAction_saveTemplate.triggered.connect(self.save_template)
        
        fileAction_loadSetting = QtGui.QAction("&Load Setting", self)
        fileAction_loadSetting.setShortcut("Ctrl+Shift+L")
        fileAction_loadSetting.triggered.connect(self.load_setting)
        
        fileAction_saveSetting = QtGui.QAction("&Save Settings", self)
        fileAction_saveSetting.setShortcut("Ctrl+Shift+S")
        fileAction_saveSetting.triggered.connect(self.save_setting)
        
        #attach action to the file menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(fileAction_loadSetting)
        fileMenu.addAction(fileAction_saveSetting)
        fileMenu.addAction(fileAction_loadTemplate)
        fileMenu.addAction(self.fileAction_saveTemplate)        
        fileMenu.addAction(fileAction_quit) 
        
        #create some actions for the edit menu
        editAction_templates = QtGui.QAction('&Template', self)
        editAction_templates.setShortcut("Ctrl+Shift+E")
        editAction_templates.triggered.connect(self.editor)
        
        editAction_chapters = QtGui.QAction('&Chapters List', self)
        editAction_chapters.setShortcut("Ctrl+C")
        editAction_chapters.triggered.connect(self.toggle_chapter_panel)
        
        editAction_append = QtGui.QAction('&Appendices List', self)
        editAction_append.setShortcut("Ctrl+A")
        editAction_append.triggered.connect(self.toggle_appendix_panel)
        
        editAction_prelims = QtGui.QAction('&Prelims List', self)
        editAction_prelims.setShortcut("Ctrl+p")
        editAction_prelims.triggered.connect(self.toggle_prelims_panel)
        
        editAction_settings = QtGui.QAction('&Settings', self)
        editAction_settings.setShortcut("Ctrl+F5")
        editAction_settings.triggered.connect(self.toggle_setting_panel)
        
        #create some actions for the view menu
        viewAction_master = QtGui.QAction('&'+self.setting_dict['master_file'],self)
        viewAction_master.setShortcut("Ctrl+m")
        #editAction_settings.triggered.connect(self.toggle_setting_panel)
        
        #attach action to the edit menu
        editMenu = mainMenu.addMenu('&Edit')
        editMenu.addAction(editAction_templates)
        editMenu.addAction(editAction_chapters)
        editMenu.addAction(editAction_append)
        editMenu.addAction(editAction_prelims)
        editMenu.addAction(editAction_settings)
        
        #create some actions for the tex menu
        texMenu = mainMenu.addMenu('&Tex')
        texAction_genMaster = QtGui.QAction("&Generate master file", self)
        texAction_genMaster.setShortcut("Ctrl+Shift+G")
        texAction_genMaster.triggered.connect(self.gen_master_tex)
        
        texAction_compile = QtGui.QAction("&Compile", self)
        texAction_compile.setShortcut("Ctrl+Shift+C")
        texAction_compile.triggered.connect(self.tex_compile)
        
        #attach action to the tex menu
        texMenu.addAction(texAction_genMaster)
        texMenu.addAction(texAction_compile)
           
        
        self.show()
        
    def variables_init(self):
        #create a dictionary to be filled
        self.setting_dict = {}
        #fill the default values according to the convention in setting object
        self.setting_dict['latex_dir'] = os.getcwd()
        self.setting_dict['latex_sub'] = 'tex'
        self.setting_dict['img_sub'] = 'figs'
        self.setting_dict['append_folder'] = r'\append'
        self.setting_dict['refs_file'] = r'\refs\references.bib'
        self.setting_dict['prelim_folder'] = r'\prelims'
        self.setting_dict['storage'] = r'\app_temp'
        self.setting_dict['label_tag'] = '\label'
        self.setting_dict['ref_tag'] = r'\cref'
        self.setting_dict['app_tag'] = r'app:'
        self.setting_dict['master_file'] = 'master.tex'
        self.setting_dict['class_file'] = 'dmathesis.cls'
        
        
        #self.setting_dict[] = ['begin', 'end', 'appendix']
        
        #some useful variables
        self.appendix_search = self.setting_dict['label_tag'] + '{' + self.setting_dict['app_tag']
        self.chapter_search = self.setting_dict['ref_tag'] + '{' + self.setting_dict['app_tag']
        
        #setting file default name and location
        self.setting_filename = os.path.normpath('/app_settings.txt')
        #master file name, default -> master.tex
        
        
        #write the default beginning, body and end templates to the template folder (this is for the current thesis, 
        #otherwise modify)
        self.template_set()
        
        #create a chapter dictionary
        self.chapter_dict = chapter_dict(self.setting_dict['latex_dir'], 
                                         self.setting_dict['latex_sub'], self.setting_dict['img_sub'])
        
        self.get_appendix_list()
        
        self.prelims_lists = (get_prelim_files(self.setting_dict['latex_dir'], self.setting_dict['prelim_folder']), [])
                
    def get_appendix_list(self):
        #create an appendix list
        appendix_list = get_appendix_list(self.setting_dict['latex_dir'], self.setting_dict['append_folder'],
                                               self.appendix_search, self.setting_dict['ref_tag'], 
                                               self.chapter_dict, self.setting_dict['latex_sub'])
        self.appendix_list = [glob_to_loc(self.setting_dict['latex_dir'] + self.setting_dict['append_folder'], 
                                          fname)[1:] for fname in appendix_list]
        
        if(hasattr(self, 'appendices_selection')):
            self.appendices_selection.button_new_restore.setEnabled(True)
            self.appendices_selection.set_panel_dict(self.appendix_list)
        
    
    def save_setting(self):
        #save all the settings to a file, prompt user for the setting file
        temp = [self.setting_dict, self.chapter_dict, self.appendix_list]
        
        self.setting_file = QtGui.QFileDialog.getSaveFileName(self, 'Save file', os.getcwd(), 'Text files (*.txt)')
        self.save_file()
        
    def load_setting(self):
        self.setting_file = QtGui.QFileDialog.getOpenFileName(self, 'Select file', os.getcwd(), 'Text files (*.txt)')
        self.setting_dict, self.chapter_dict, self.appendix_list, self.prelims_lists = load_setting(self.setting_file)
        self.toggle_setting_panel()
   
    def save_template(self):
        self.template_file = QtGui.QFileDialog.getSaveFileName(self, 'Save file', os.getcwd(), 'Text files (*.txt)')
        with open(self.template_file, 'w') as f: f.writelines(self.template_text)
            
    def load_template(self):
        self.template_file = QtGui.QFileDialog.getOpenFileName(self, 'Select file', os.getcwd(), 'Text files (*.txt)')
        if self.template_file:
            with open(self.template_file, 'r') as f: 
                self.template_text = "".join([line for line in f])
        
            self.editor()
        
    def save_file(self):
        #set save button back to invisible
        self.setting.save_setting_button.setEnabled(False)
        
        #save the file according to the stored filename
        save_setting((self.setting_dict, self.chapter_dict, self.appendix_list, self.prelims_lists), self.setting_file)
        
    
    def allow_store(self):
        #if checkerbox is checked, posiibly enable the save button if current dictionary is valid
        if self.setting.ifstore.isChecked():        
            #if dictionary is valid, enable the save setting button
            if self.setting.valid_setting:
                self.setting.save_setting_button.setEnabled(True)
            else:
                self.setting.save_setting_button.setEnabled(False)
        
        else:
            self.setting.save_setting_button.setEnabled(False)
        
    def reset_restore(self, parent_attr, var_attr):
        getattr(self, parent_attr).set_apply_button(False)
        setattr(self, var_attr, getattr(self, parent_attr).get_panel_dict())
        getattr(self, parent_attr).set_panel_dict(getattr(self, var_attr))
        
        
    def template_set(self):
        sep = "%% --------------------------------------------------------------" \
            +"-------------------------------------------------------- %%"
        self.template_text = "%% DO NOT MODIFY LINES WITH PERCENT SIGN %%\n\n" + sep\
                + "\n%% PUT COMMANDS OR TEXTS BEFORE INCLUDING THE FIRST CHAPTER VIA " \
                +"\\include{} %%\n\n\\cleardoublepage\n\\ifodd\\value{page}\\else\n\t\\newpage\n" \
                +"\\fi\n\\pagenumbering{arabic}\n\n\\setcounter{page}{1}\n\n\\setcounter{chapter}{0}\n\n" \
                + sep + "\n\n\n\n\n" + sep +"\n%% PUT COMMANDS OR TEXTS BEFORE \\bibliography{} section %%" \
                + "\n\n\\bibliographystyle{unsrt}\n\\cleardoublepage\n\\phantomsection\n" \
                + "\\addcontentsline{toc}{chapter}{\\numberline{}References}\n\n" + sep + "\n\n\n\n\n" \
                + sep + "\n%% PUT COMMANDS OR TEXT BEFORE INCLUDING THE APPENDICES, COMMANDS SHOULD START " \
                + "APPENDIX SECTION WITH \\begin{appendices} %%\n\n" + "\\begin{appendices}\n" \
                + "\\setcounter{chapter}{0}\n" + "\\renewcommand\\chaptername{Appendix}\n" \
                + "\\renewcommand{\\theequation}{\\Alph{chapter}.\\arabic{equation}}\n\\crefalias{chapter}{appsec}\n\n" \
                + sep + "\n"
         
        self.template_file = ''
    
    def create_dockable(self):
        self.dockable_panel = QtGui.QDockWidget("General Purpose", self)
        self.dockable_panel.setFeatures(QtGui.QDockWidget.DockWidgetClosable | QtGui.QDockWidget.DockWidgetFloatable)
        self.dockable_panel.setWindowModality(QtCore.Qt.NonModal)
        self.dockable_panel.setFloating(False)        
        self.dockable_panel.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.dockable_panel)        
        self.dockable_panel.visibilityChanged.connect(self.redock)
            
    def redock(self, visibility):
        #retrieve the changed chapter list in the panel
        #self.chapter_dict = self.chapters_selection.get_panel_dict()
        pass
        
    def apply_changes(self):
        #set apply button to invisible
        self.setting.apply_button.setEnabled(False)
        
        #check validitiy of directories
        self.invalid_dirs = self.setting.validate_setting()
        
        #get the dictionary of the settings
        self.setting_dict = self.setting.get_setting_dict()
        
        #change the absolute path for the save_setting file according to the setting
        self.setting_file = self.setting_dict['latex_dir'] + self.setting_dict['storage'] +   self.setting_filename
        
        #check the storage (if enabled and path is valid then open the button)
        self.allow_store()
        
        #if directorie/s is/are not valid, raise the dialog box
        if not self.setting.valid_setting:
            self.setting_error.set_details(self.invalid_dirs)
            self.setting_error.execute()
        
        #create new chapter and appendix dictionary
        self.chapter_dict = chapter_dict(self.setting_dict['latex_dir'], 
                                         self.setting_dict['latex_sub'], self.setting_dict['img_sub'])
        self.get_appendix_list()
        self.prelims_lists = (get_prelim_files(self.setting_dict['latex_dir'], self.setting_dict['prelim_folder']), [])
    
    def toggle_setting_panel(self):
        #if setting_panel is a widget object, then you can simply set the central widget of the main window to be
        #setting panel
        #self.setGeometry(800,500,200,500)
        #self.setCentralWidget(self.setting_panel)
        
        #if setting_panel is a dockable widget, then the following docks it on the main window
        self.dockable_panel.setWindowTitle('Settings')
        self.dockable_panel.setWidget(self.setting)
        self.dockable_panel.setFloating(False)
        self.dockable_panel.show()
        
        #set the setting panel with the dictionary (either read in or default)
        self.setting.set_setting(self.setting_dict)
        
                
    def setting_dialog_accept(self):
        #will set all the texts of boxes that are invalids to blanks
        for field in self.invalid_dirs:
            getattr(self.setting, field).set_text('')
            
    
    def toggle_chapter_panel(self):
        #modify the chapter selection panel based on the new chapter dict
        self.chapters_selection.set_panel_dict(self.chapter_dict)
        
        #set the dockable panel
        self.dockable_panel.setWindowTitle("Chapter Selection")
        self.dockable_panel.setWidget(self.chapters_selection)
        self.dockable_panel.setFloating(False)
        self.dockable_panel.show()
        
        #disable the save operation
        self.fileAction_saveTemplate.setEnabled(False)
        
    def toggle_appendix_panel(self):
        #modify the chapter selection panel based on the new chapter dict
        self.appendices_selection.set_panel_dict(self.appendix_list)
        
        #set the dockable panel
        self.dockable_panel.setWindowTitle("Appendices Selection")
        self.dockable_panel.setWidget(self.appendices_selection)
        self.dockable_panel.setFloating(False)
        self.dockable_panel.show()
        
        #disable the save operation
        self.fileAction_saveTemplate.setEnabled(False)
        
    def toggle_prelims_panel(self):
        self.prelims_selection.set_panel_dict(self.prelims_lists)
        
        #set the dockable panel
        self.dockable_panel.setWindowTitle("Prelims Selection")
        self.dockable_panel.setWidget(self.prelims_selection)
        self.dockable_panel.setFloating(False)
        self.dockable_panel.show()
        
        #disable the save operation
        self.fileAction_saveTemplate.setEnabled(False)
        
    def tex_compile(self):
        self.dockable_panel.setWidget()
    
    def gen_master_tex(self):        
        gen_master_file(self.setting_dict, '/app_temp/format.txt',
                       self.chapter_dict, self.appendix_list, self.prelims_lists)
    
    def editor(self):
        self.template_format.setText(self.template_text)
        
        #set the dockable panel
        self.dockable_panel.setWindowTitle("Format Template")
        self.dockable_panel.setWidget(self.template_format)
        self.dockable_panel.setFloating(False)
        self.dockable_panel.show()
        
        #enable the save operation
        self.fileAction_saveTemplate.setEnabled(True)
        
        
    def close_application(self):
        sys.exit()
        
        
        
        
#run the application if this is the main file being run
def run():
    app = QtGui.QApplication(sys.argv)
    GUI = Application()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    run()