#some useful imports
import os
from collections import OrderedDict as ODict
import re
from glob import glob
import ntpath
import json


#####---------------Some functions for converting directories between global and local path----------------------#####
def loc_to_glob(base_path, fname, is_file=False):
    """
    converts local to global coordinate. Accepts the following arguments:
    
    base_path -> base directory of the local path/filename
    fname -> local path/filename
    is_file -> is this a filename? (True/False)
    """
    
    c_text = os.path.normpath(fname)
    #if it is a file use another function
    if is_file:
        is_exist = os.path.isfile
    else:
        is_exist = os.path.isdir
        
    if os.path.isabs(c_text):
        if not is_exist(c_text):
            c_text  = os.path.normpath(base_path) + c_text

        #if new path is invalid, ask set to empty and ask user to specify
        #print(c_text, is_exist(c_text))
        if not is_exist(c_text):
            #raise dialog box
            c_text  = ''
    else:
        c_text  = ''
        
    return c_text
    
def glob_to_loc(base_path, fname):
    """
    converts global directory to relative path (local one). Accepts the following arguments:
    
    base_path -> base directory of the local path/filename
    fname -> local path/filename
    """
    
    glob_dir = os.path.normpath(base_path)
    c_text = os.path.normpath(fname)
    if glob_dir and c_text:
        if glob_dir in c_text and glob_dir != c_text:
            start = c_text.find(glob_dir)                                  
            c_text = c_text[start+len(glob_dir):]
            
    c_text = os.path.normpath(c_text)
    return c_text    

    
    
    
    
#####---------------Some functions for making directory, listing folders and listing files ----------------------#####
#safely create directory if it does not exist
def make_dir(base, sub_dir):
    c_dir = base + "/" + sub_dir
    if not os.path.isdir(c_dir):
        os.makedirs(c_dir)

#get list of folders in current directory
def list_folders(mypath):
    return [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

#get list of files in the given directory
def list_files(mypath):
    return [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    



    
#####---------------Some functions for generating/filtering various lists for chapter, appendices and preliminary files ----------------------#####
def filter_chapters(chapters_list, abs_path, tex_sub, img_sub):
    """
    Function to filter the chapter list to contain only folders that contains tex_sub directory and .tex files within that.
    The function will also generate an img_sub if the chapter doesn't already contain one. It takes the following arguments:
    
    chapters_list -> original chapter list
    abs_path -> absolute path to where the chapters reside
    tex_sub -> the subdirectory in the chapter folder in which the .tex files reside
    img_sub -> the subdirectory in the chapter folder in which the images files included in the chapter reside
    
    The function returns the revised chapter list. 
    """
    revised_list = []    
    for chapter in chapters_list:
        #get sub directories now
        sub_path = abs_path + "/" + chapter
        sub_folders = list_folders(sub_path)
        if tex_sub in sub_folders:
            #get all files and check against extension            
            if len(glob(sub_path + "/" + tex_sub + '/*.tex')) > 0:
                revised_list.append(chapter)
                #if image subfolder is not created then create it
                if img_sub not in sub_folders:
                    #create image subfolder
                    os.makedirs(sub_path + "/" + img_sub)
                    
    return revised_list
    
    
def chapter_dict(thesis_directory, tex_sub, img_sub):
    """
    The function generates an ordered chapter dictionary with the chapters being the keys and the sub-chapters
    or included .tex files as values. It takes in the following arguments:
    
    thesis_directory -> the base directory in which all the chapter folders reside
    tex_sub -> the subdirectory in the chapter folder in which the .tex files reside
    img_sub -> the subdirectory in the chapter folder in which the images files included in the chapter reside
    
    The function returns an ordered chapter dictionary for use in the GUI.
    """
    chapter_folders = list_folders(thesis_directory)
    filtered_chapters = filter_chapters(chapter_folders, thesis_directory, tex_sub, img_sub)
    d = ODict()
    for filtered_chapter in filtered_chapters:
        chapter_files_list = glob(thesis_directory + "/" + filtered_chapter + "/" + tex_sub + "/*.tex")
        d[filtered_chapter] = [ntpath.split(path)[-1] for path in chapter_files_list]
        
    return d
    
    
def get_appendix_tags(thesis_directory, append_folder, appendix_search, ref_tag):
    """
    The function generates an appendix tag dictionary containing the appendix tag as the key and appendix file as value.
    Appendix tag are searched in the appendix files to be used to compared for cross-references in the main .tex files.
    The following are the input arguments to the function:
    
    thesis_directory -> the base directory in which all the chapter folders reside
    append_folder -> the local directory (within thesis_directory) where the appendix files (.tex) reside
    appendix_search -> an indication of what to search for when finding appendix tag. Ex: \label{app:
    ref_tag -> the tag used during the cross references in the chapter .tex files; Ex: \cref{} or \ref{}
    
    The function returns a dictionary of appendix tags and keys and appendix files as value
    """
    #list all files in appendix folder
    appendix_files = glob(thesis_directory  + append_folder + "/" + "*.tex")

    appendix_tags = []
    #iterate through all file and find the tag
    for appendix_file in appendix_files:
        with open(appendix_file, 'r') as f:
            for line in f:
                if appendix_search in line:
                    break
        
            l_index = line.find(appendix_search)
            start = line.find('{',l_index)
            end = line.find('}', l_index)
            appendix_tags.append(ref_tag+line[start:end])
            
    return {appendix_tag: appendix_file for appendix_tag, appendix_file in zip(appendix_tags,appendix_files)}, appendix_tags
    
    
def get_appendix_list(thesis_directory, append_folder, appendix_search, ref_tag, chapter_dict, tex_sub):
    """
    This functions returns the list of appendix files that are currently being cross-referenced by the chapters 
    in the chapters' list. The function takes the following input arguments:
    
    thesis_directory -> the base directory in which all the chapter folders and append_folder reside
    append_folder -> the local directory (within thesis_directory) where the appendix files (.tex) reside
    appendix_search -> an indication of what to search for when finding appendix tag. Ex: \label{app:
    ref_tag -> the tag used during the cross references in the chapter .tex files; Ex: \cref{} or \ref{}
    chapter_dict -> chapter_dict is a dictionary with chapter keys and sub-chapter values. It can be generated, for example, from chapter_dict function
    tex_sub -> the subdirectory in the chapter folder in which the .tex files reside
    
    The function returns the list of appendices.
    """
    
    #get appendix tag dictionary
    appendix_dict, appendix_tags = get_appendix_tags(thesis_directory, append_folder, appendix_search, ref_tag)
    
    #go through each .tex file in chapter_dict
    progs = [re.compile(re.escape(appendix_tags[i])) for i in range(len(appendix_tags))]
    user_appendices = []
    
    for chapter, files in chapter_dict.items():
        for file in files:
            chapter_dir = thesis_directory + "/" + chapter + "/" + tex_sub + "/" + file
            
            #open the tex file
            with open(chapter_dir, 'r') as f:
                for line in f:
                    for prog,tag in zip(progs, appendix_tags):
                        if prog.search(line):
                            if appendix_dict[tag] not in user_appendices:
                                user_appendices.append(appendix_dict[tag])
                                
    return user_appendices
    
    
def get_prelim_files(thesis_directory, prelim_folder):
    """
    The function returns the list of preliminary files to be included either before \begin{document} or
    immediately after but must before the inclusion of the chapters. The function takes the following input arguments:
    
    thesis_directory -> the base directory in which all the chapter folders and prelim_folder reside
    prelim_folder -> the folder in thesis_directory in which all the .tex preliminary files exist
    
    """
    
    pathname = thesis_directory + prelim_folder + "/"
    #extensions = ["*.tex", "*.cls"]
    extensions = ["*.tex"]
    prelim_files = []
    [prelim_files.extend(glob(pathname+extension)) for extension in extensions]
    
    return [glob_to_loc(thesis_directory + prelim_folder, prelim_file)[1:] for prelim_file in prelim_files] 
    

    
    


#####---------------Some functions for saving and loading different save configurations from a setting file (.txt) ----------------------#####
def save_setting(setting_dict, file_name):
    """
    The function writes the dictionary of setting to the specified file name. 
    The function takes the following input arguments:
    
    setting_dict -> the dictionary/ordered dictionary/tuple/list of all the settings
    file_name -> the name of the file (absolute path) for the setting to be saved to
    """
    
    with open(file_name, 'w') as file:
        file.write(json.dumps(setting_dict))

        
def load_setting(file_name):
    """
    The function to load the settings/configurations from a file.
    The function takes the following input arguments:
    
    file_name -> the name of the file (absolute path) for the configuration to be loaded. This includes the following:
        setting_dict -> dictionary of settings on the setting panel in the GUI
        chapter_dict -> chapter_dict is a dictionary with chapter keys and sub-chapter values.
        appendix_list -> list of appendix files to be included
        prelims_lists -> list of preliminary files to be included
    
    The function returns all the tuple of all the lists/dictionary mentioned above
    """
    
    with open(file_name, 'r') as file:
        setting_dict, chapter_dict, appendix_list, prelims_lists = json.loads(file.read() , object_pairs_hook=ODict)
        
    return setting_dict, chapter_dict, appendix_list,  prelims_lists
    
    

    
    
#####---------------Function to generate the main master tex file which will be used for compiling ----------------------#####
def gen_master_file(setting_dict, format_file, chapter_dict, appendix_list, prelims_lists):
    """
    The function generates a compilable master file based on the chapter, appendix and preliminary dictionaries/lists.
    It also takes into account the format which is specified in the modifiable format_file.
    The function takes the following input arguments:
    setting_dict -> dictionary of settings on the setting panel in the GUI
    format_file -> the file name (given in relative path) of the format file which will be read and used to generate the master .tex file.
    chapter_dict -> chapter_dict is a dictionary with chapter keys and sub-chapter values.
    appendix_list -> list of appendix files to be included
    prelims_lists -> list of preliminary files to be included
    
    """
    
    #extract two lists from prelims_lists
    before_doc_list, after_doc_list = prelims_lists
    
    #some tags to look for
    sep_tag = "% -----"
    before_doc_tags = [r"BEFORE \begin{document}", r"AFTER \begin{document}", r"VIA \include{}", r"\bibliography{}", 
                       r"\begin{appendices}", "\n\n"]
    
    start_section = False
    counter = 0
    
    #first open up the master file to write
    with open(setting_dict['latex_dir']+"/"+setting_dict['master_file'], 'w') as fout, open (setting_dict['latex_dir']+format_file, 'r') as fin:
        #document class and stuff here that are before docs
        text = ''
        text += '\documentclass{' + setting_dict['class_file'].split(".cls")[0] + '}\n'
        for t in before_doc_list:
            text += r'\input{' + setting_dict['prelim_folder'][1:] + "/" + t.split(".tex")[0] + '}\n' 
        fout.writelines(text)
        
        #iterate through the format
        for line in fin:
            if sep_tag in line:
                start_section = False
            
            if before_doc_tags[counter].lower() in line.lower():
                start_section = True
                text = ''
                if counter == 1: #immediately before begin document, write a \begin{document}
                    text = r"\begin{document}"+"\n\n"
                elif counter == 2: #before including the chapters just write include the preliminary
                    for t in after_doc_list:
                        text += r'\input{' + setting_dict['prelim_folder'][1:] + "/"  + t  + "}\n"
                elif counter == 3: #here put the chapers and subchapters in
                    for chapter, sub_chapters in chapter_dict.items():
                        for sub_chapter in sub_chapters:
                            text += r'\include{' + chapter + "/" + setting_dict['latex_sub'] + "/" + sub_chapter.split(".tex")[0] + "}\n"
                            
                        text += "\n"
                    
                elif counter == 4: #here write the bibliography 
                    text = r'\bibliography{' + setting_dict['refs_file'].replace("\\", "/")[1:].split(".bib")[0] + '}\n'
                
                fout.writelines(text)
                counter += 1

            elif start_section:
                fout.writelines(line)
        
        
        #put in the appendices and the end the document
        text = ''
        for appendix in appendix_list:
            text += r'\include{' + setting_dict['append_folder'][1:] + "/"  + appendix.split(".tex")[0] + "}\n"
        
        text += r"\end{appendices}" + "\n" + r"\end{document}" + "\n"
        fout.writelines(text)