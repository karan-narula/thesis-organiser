# Thesis Organiser
This is an application using PyQt for organizing thesis chapters, sub-chapters and appendices. The application allows user to change different settings which will help in generating a list of possible chapter, sub-chapter, appendices and preliminary files. The user has control over the final format of the generated and compilable master tex file. Additional features include:
- Organising the list of chapters, sub-chapters, appendices and preliminary files
- Saving and loading the configurations
- Saving and loading the format file
- Generating a list of appendix files based on the cross-references in the dictionary of chapters and sub-chapters

## Some Definitions
The definitions are given to the components of 

## Installation instruction
The application can be started by running `application.py`. This relies on the following imports:
+ `sys`
+ `PyQt4`
+ `os`
+ `json`
+ `copy`
+ `glob`
+ `ntpath`
+ `collections`
+ `re`

Most of modules come with standard python installation and if necessary can use `pip` to install. The installation of `PyQt` on different operating systems are given in the following subsections. Alternately, more information can be found [here](https://www.tutorialspoint.com/pyqt/pyqt_introduction.htm).

### Windows 
You can find source packages [here](https://riverbankcomputing.com/software/pyqt/download) for linux, MAC OS and Windows. The binary packages are no longer available. Altenately, there are windows wheel packages [available](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4) for download. More information are given in this [answer](https://stackoverflow.com/questions/22640640/how-to-install-pyqt4-on-windows-using-pip), where you can essentially use `pip` to install `PyQt4`. Example is shown below:
```
C:\path\where\wheel\is\> pip install PyQt4-4.11.4-cp35-none-win_amd64.whl
```
## Linux
For Ubuntu or any other debian Linux distribution, use the following command to install PyQt
```
sudo apt-get install python-qt4
```
**or** 
```
sudo apt-get install pyqt5-dev-tools
```

## Mac OS
[PyQtX](http://sourceforge.net/projects/pyqtx/) project hosts binaries of PyQt for Mac. Use Homebrew installer as per the following command −
```
brew install pyqt
```
