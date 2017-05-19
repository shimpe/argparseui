##############################################################################
#      This file is part of argparseui.                                      #
#                                                                            #
#      argparseui is free software: you can redistribute it and/or modify    #
#      it under the terms of the GNU General Public License as published by  #
#      the Free Software Foundation, either version 3 of the License, or     #
#      (at your option) any later version.                                   #
#                                                                            #
#      argparseui is distributed in the hope that it will be useful,        #
#      but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#      GNU General Public License for more details.                          #
#                                                                            #
#      You should have received a copy of the GNU General Public License     #
#      along with argparseui.  If not, see <http://www.gnu.org/licenses/>.   #
##############################################################################

import textwrap
import argparse

from PyQt5 import QtCore, QtGui, QtWidgets

__VERSION__ = "0.0.5"

def comb(str1, str2):
    return str1 + str2

import re
try:
    _find_unsafe = re.compile(r'[^\w@%+=:,./-]', re.ASCII).search
except:
    _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s
    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

SINGLE = {
    'int'     : 'an integer',
    'float'   : 'a floating point number',
    'str'     : 'a string',
    'unicode' : 'a unicode string'
    }

MULTIPLE = {
    'int'     : '%d integers',
    'float'   : '%d floating point numbers',
    'str'     : '%d strings',
    'unicode' : '%d unicode strings'
    }

_OR_MORE = {
    'int'     : ' or more integers',
    'float'   : ' or more floating point numbers',
    'str'     : ' or more strings',
    'unicode' : ' or more unicode strings'
    }

class ArgparseUi(QtWidgets.QDialog):
    def __init__(self, parser, use_scrollbars=False, remove_defaults_from_helptext=False,
                 helptext_default=' [default=%(default)s]', use_save_load_button=False, window_title="Make your choice", 
                 left_label_alignment=None, ok_button_handler=None, cancel_button_handler=None, parent=None):
        super(ArgparseUi, self).__init__(parent)
        self.setWindowTitle(window_title)
        self.parser = parser
        self.use_scrollbars = use_scrollbars
        self.remove_defaults_from_helptext = remove_defaults_from_helptext
        self.helptext_default = helptext_default
        self.use_save_load_button = use_save_load_button
        self.ok_button_handler = ok_button_handler # function that takes two options: the ArgparseUi instance and "parsed options"
        self.cancel_button_handler= cancel_button_handler # function that takes one option: the ArgparseUi instance
        self.commandLineArgumentCreators = []
        self.filename = None
        self.destToWidget = {}

        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.mainLayout)
        
        self.description = QtWidgets.QWidget(self)
        self.descriptionLayout = QtWidgets.QVBoxLayout(self.description)
        self.description.setLayout(self.descriptionLayout)
        
        self.options = QtWidgets.QWidget(self)
        self.optionsLayout = QtWidgets.QFormLayout(self.options)
        if left_label_alignment is not None:
            self.optionsLayout.setLabelAlignment(QtCore.Qt.AlignLeft if left_label_alignment else QtCore.Qt.AlignRight)
        self.options.setLayout(self.optionsLayout)

        self.buttons = QtWidgets.QWidget(self)
        self.buttonsLayout = QtWidgets.QHBoxLayout(self.buttons)
        self.buttons.setLayout(self.buttonsLayout)
        
        self.epilog = QtWidgets.QWidget(self)
        self.epilogLayout = QtWidgets.QVBoxLayout(self.epilog)
        self.epilog.setLayout(self.epilogLayout)
        
        if self.use_save_load_button:
          self.LoadButton = self.addButton("Load options")

        self.OkButton = self.addButton("Ok")
        self.CancelButton= self.addButton("Cancel")

        if self.use_save_load_button:
          self.SaveButton = self.addButton("Save options")
          self.SaveAsButton = self.addButton("Save options as")

        self.buttonsLayout.addSpacerItem(QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    
        self.OkButton.clicked.connect(self.onOk)
        self.CancelButton.clicked.connect(self.onCancel)
        if self.use_save_load_button:
          self.LoadButton.clicked.connect(self.onLoad)
          self.SaveButton.clicked.connect(self.onSave)
          self.SaveAsButton.clicked.connect(self.onSaveAs)
  
        self.create_ui()

        self.mainLayout.addWidget(self.description)
        if self.use_scrollbars:
          self.scrollableArea = QtWidgets.QScrollArea(self)
          self.scrollableArea.setWidgetResizable(True)
          self.scrollableArea.setEnabled(True)
          self.scrollableArea.setFrameShape(QtWidgets.QFrame.NoFrame)
          self.scrollableArea.setWidget(self.options)
          self.mainLayout.addWidget(self.scrollableArea)
          self.resize(self.sizeHint())
          self.update()
          self.updateGeometry()
        else:
          self.mainLayout.addWidget(self.options)
        self.mainLayout.addWidget(self.epilog)
        self.mainLayout.addWidget(self.buttons)

    def addButton(self, label):
      self.buttonsLayout.addSpacerItem(QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
      b = QtWidgets.QPushButton(label, self.buttons)
      self.buttonsLayout.addWidget(b)
      return b
    
    def sizeHint(self):
      """
      helps determining the initial size of the dialog when scrollbars are requested
      """
      return QtCore.QSize(self.options.sizeHint().width(), self.options.sizeHint().height() + self.OkButton.sizeHint().height())

    def create_ui(self):
        """
        create a dialog with the options from the parser
        and an ok and cancel button
        """
        self.addDescription()
        self.actionLookupTable = { 
                    type(argparse._HelpAction(None)) : self.makeHelpActionEntry,
                    type(argparse._VersionAction(None)) : self.makeHelpActionEntry,                   
                    type(argparse._StoreAction(None,None,None)): self.makeStoreConstEntry,
                    type(argparse._StoreConstAction(None,None,None)): self.makeStoreConstEntry,
                    type(argparse._StoreTrueAction(None, None)): self.makeStoreConstEntry,
                    type(argparse._StoreFalseAction(None, None)): self.makeStoreConstEntry,
                    type(argparse._StoreAction(None, None)) : self.makeStoreActionEntry,
                    type(argparse._CountAction(None, None)) : self.makeCountActionEntry,
                    type(argparse._AppendAction(None,None)) : self.makeAppendActionEntry,
                    type(argparse._AppendConstAction(None, None, None)) : self.makeCountActionEntry
                    }
                    
        for a in self.parser._get_optional_actions():
            try:
                self.actionLookupTable[type(a)](a, optional=True)
                #print ("Introspected type: {0}\n".format(a))
            except KeyError:
                print ("Unsupported type: {0}\n".format(a))

        for a in self.parser._get_positional_actions():
            try:
                self.actionLookupTable[type(a)](a, optional=True)
                #print ("Introspected type: {0}\n".format(a))
            except KeyError:
                print ("Unsupported type: {0}\n".format(a))

            
        #self.addEpilog()
        
    def addDescription(self):    
        """
        add a description above the ui
        """
        if self.parser.description is not None:
            descr  = self.parser.description
        else:
            descr = "<b>Choose which options to include, and define their value below</b>"
        label = QtWidgets.QLabel(descr)
        self.descriptionLayout.addWidget(label)
        
    def addEpilog(self):
        """
        add an epilog text underneath the ui
        """
        if self.parser.epilog is not None:
            descr = self.parser.epilog
        else:
            descr = "<b>This options dialog is auto-generated by argparseui {0}!</b>".format(__VERSION__)
        label = QtWidgets.QLabel(descr)
        self.epilogLayout.addWidget(label)
        
    def makeHelpString(self, a):
        """
        extract help string for argparse parser and for use in the dialog
        """
        helpstring = ""
        if a.help:
            helpstring += self.makeOptionString(a) + (" " + a.help)  
        elif a.option_strings:
            helpstring += (" " + self.makeOptionString(a))
        else:
            helpstring += "positional argument"

        if self.remove_defaults_from_helptext:
            helpstring = helpstring.replace(self.helptext_default, '')
        return '\n'.join(textwrap.wrap(helpstring, 80))
        
    def makeOptionString(self, a):
        """
        extract option strings as defined in argparse parser for use in the dialog
        """
        the_options = " ".join(a.option_strings)
        return the_options
            
    def extractTypename(self, a):
        """
        given an argparse action, find out what datatype it expects
        and return that as a string (used to create help text)
        """
        rawtypename = "{0}".format(a.type)
        if 'type' in rawtypename:
          return rawtypename[7:-2]
        elif 'class' in rawtypename:
          return rawtypename[8:-2]
        return rawtypename
        
    def makeTypeHelp(self, a):
        """
        synthesize a human-readable string to describe the expected datatype
        """
        typehelp = "programming error"
        if a.choices:
            typehelp = "" # no need to explain as options are represented in a combo box
        else:
            rawtypename = self.extractTypename(a)
            nargs = a.nargs

            if rawtypename in ['int', 'float'] and a.default is not None:
                typename = ""
            elif rawtypename == 'None':
                typename = ""
            else:
                try:
                  intargs = int(nargs)
                except ValueError:
                  intargs = -1
                except TypeError:
                  intargs = -1

                if nargs == '1':
                  typename = SINGLE.get(rawtypename, rawtypename)
                elif intargs > 0:
                  if rawtypename in MULTIPLE:
                    typename = MULTIPLE[rawtypename] % intargs
                  else:
                    typename = rawtypename
                elif nargs == "*":
                  if rawtypename in _OR_MORE:
                    typename = "0" + _OR_MORE[rawtypename]
                  else:
                    typename = rawtypename
                elif nargs == "+":
                  if rawtypename in _OR_MORE:
                    typename = "1" + _OR_MORE[rawtypename]
                  else:
                    typename = rawtypename
                elif nargs == "?":
                  typename = SINGLE.get(rawtypename, rawtypename)
                else:
                  typename = SINGLE.get(rawtypename, rawtypename)

            typehelp = " [" + typename + "]" if typename else ""
            
        return typehelp

    def getValidator(self, a):
        """
        return a validator for a QLineEdit
        """
        validator = None
        if not a.choices and a.nargs in [None, '1']:
            rawtypename = self.extractTypename(a)
            if rawtypename == 'int':
                validator = QtGui.QIntValidator
            elif rawtypename == 'float':
                validator = QtGui.QDoubleValidator
        return validator

    def disableOnClick(self, widget):
        """
        function that creates a function that can be 
        used to disable a given widget (used to generate
        clicked handlers on-the-fly)
        """
        def disable(state):
            widget.setEnabled(state)
        return disable
  
    def makeHelpActionEntry(self, a, optional=True):
        """
        do not add the help action in the dialog
        since the dialog replaces the help action
        """
        pass
      
    def registerDisplayStateInfo(self, dest, list_of_widgets):
        """
        registers backward dependency from option_string to widget;
        used to update ui state when loading files
        """
        for w in list_of_widgets:
          if dest not in self.destToWidget:
            self.destToWidget[dest] = []
          self.destToWidget[dest].append(w)

    def makeStoreConstEntry(self, a, optional=True):
        """
        make a dialog entry for a StoreTrue action
        (represented as a label)
        """
        helpstring = self.makeHelpString(a)
        rhslabel = QtWidgets.QLabel("", self.options)
        include = QtWidgets.QCheckBox(helpstring, self.options)
        if a.default:
            include.setChecked(True)
        self.optionsLayout.addRow(include, rhslabel)
        self.registerDisplayStateInfo(a.dest, [include])
        self.commandLineArgumentCreators.append(self.createFunctionToMakeStoreConstEntryCommandLine(include, a))
        self.registerDisplayStateInfo(a.dest, [include])
    
    def createFunctionToMakeStoreConstEntryCommandLine(self, include_widget, a):
        """
        function to create a function that generates a command line string,
        specialized for one given option (these functions are generated on-the-fly 
        while building the ui)
        """
        def to_command_line():
            if type(include_widget) == QtWidgets.QCheckBox:
                checked = include_widget.isChecked()
            else:
                checked = True
            if checked:            
                return ["{0}".format(a.option_strings[0])]
            else:
                return []
        return to_command_line
    
    def makeStoreActionEntry(self, a, optional=True):
        """
        make a dialog entry for a StoreAction entry
        (represented as combo box or line edit, depending on 
        choices being defined or not
        """
        helpstring = self.makeHelpString(a)
        typehelp = self.makeTypeHelp(a)
        validator = self.getValidator(a)
        if a.choices:
            combobox = QtWidgets.QComboBox(self.options)
            for c in a.choices:
                combobox.addItem("{0}".format(c))
            if a.default is not None:
                combobox.setCurrentIndex(combobox.findText("{0}".format(a.default)))
                
            if optional:
                include = QtWidgets.QCheckBox(comb(helpstring, typehelp), self.options)
                enabled = a.default is not None
                include.setChecked(enabled)
                self.disableOnClick(combobox)(enabled)                
                include.clicked.connect(self.disableOnClick(combobox))                        
                self.registerDisplayStateInfo(a.dest, [include])
            else:
                include = QtWidgets.QLabel(comb(helpstring, typehelp), self.options)

            self.registerDisplayStateInfo(a.dest, [combobox])
            self.commandLineArgumentCreators.append(self.createFunctionToMakeStoreEntryCommandLine(include, combobox, a))    
            self.optionsLayout.addRow(include, combobox)
                
        else:
            lineedit = QtWidgets.QLineEdit(self.options)
            if a.default is not None:
                lineedit.setText("{0}".format(a.default))
            if validator is not None:
                lineedit.setValidator(validator(self))
            
            if optional:
                include = QtWidgets.QCheckBox(comb(helpstring, typehelp), self.options)
                enabled = a.default is not None
                include.setChecked(enabled)
                self.disableOnClick(lineedit)(enabled)
                include.clicked.connect(self.disableOnClick(lineedit))        
                self.registerDisplayStateInfo(a.dest, [include])
            else:
                include = QtWidgets.QLabel(comb(helpstring, typehelp), self.options)
                
            self.registerDisplayStateInfo(a.dest, [lineedit])
            self.commandLineArgumentCreators.append(self.createFunctionToMakeStoreEntryCommandLine(include, lineedit, a))
            self.optionsLayout.addRow(include, lineedit)
            
    def createFunctionToMakeStoreEntryCommandLine(self, include_widget, value_widget, argument):
        """
        function to create a function that generates a command line string,
        specialized for one given option (these functions are generated on-the-fly 
        while building the ui)
        """
        def to_command_line():
            if type(include_widget) == QtWidgets.QCheckBox:
                checked = include_widget.isChecked()
            else:
                checked = True
            if checked:
                if type(value_widget) == QtWidgets.QLineEdit:
                    if argument.option_strings:
                        if argument.nargs == "1" or argument.nargs is None:
                          return ["{0}".format(argument.option_strings[0]),  
                                        "{0}".format(value_widget.text())]
                        else:
                          cmd = ["{0}".format(argument.option_strings[0])]
                          cmd.extend(["{0}".format(l) for l in "{0}".format(value_widget.text()).strip().split(" ")])
                          return cmd
                    else:
                        return ["{0}".format(value_widget.text())]
                elif type(value_widget) == QtWidgets.QComboBox:
                    if argument.option_strings:
                        return ["{0}".format(argument.option_strings[0]), 
                                     "{0}".format(value_widget.currentText())] 
                    else:
                        return ["{0}".format(value_widget.currentText())]
                else:
                    assert False # programming error
            else:
                return []
        return to_command_line
            
    def makeCountActionEntry(self, a, optional=True):
        """
        add an entry for a counting action
        (represented by a spinbox)
        """
        helpstring = self.makeHelpString(a)
        spinbox = QtWidgets.QSpinBox(self.options)
        spinbox.setRange(0, 100)
        spinbox.setValue(a.nargs)
        if optional:
            include = QtWidgets.QCheckBox(helpstring, self.options)                                
            enabled = a.default is not None
            include.setChecked(enabled)
            self.disableOnClick(spinbox)(enabled)
            include.clicked.connect(self.disableOnClick(spinbox))                
            self.registerDisplayStateInfo(a.dest, [include])
        else:
            include = QtWidgets.QLabel(helpstring, self.options)
            
        self.registerDisplayStateInfo(a.dest, [spinbox])
        self.commandLineArgumentCreators.append(self.createFunctionToMakeCountActionCommandLine(include, spinbox, a))
        self.optionsLayout.addRow(include, spinbox)
        
    def createFunctionToMakeCountActionCommandLine(self, include_widget, value_widget, argument):
        """
        function to create a function that generates a command line string,
        specialized for one given option (these functions are generated on-the-fly 
        while building the ui)
        """

        def to_command_line():
            if type(include_widget) == QtWidgets.QCheckBox:
                checked = include_widget.isChecked()
            else:
                checked = True
            if checked:
                if type(value_widget) == QtWidgets.QSpinBox:
                    if argument.option_strings:
                        return [("{0}".format(argument.option_strings[0]))]*value_widget.value()
                    else:
                        assert False # programming error
                else:
                    assert False # programming error
            else:
                return []
        return to_command_line           
            
    def cleanupEmptyTableRows(self, tablewidget):
        """
        function to create a function that cleans up the unused columns of a tablewidget,
        specialized for one given option (these functions are generated on-the-fly 
        while building the ui)
        """
        def cleanup(row, col):
            data = []
            tablewidget.blockSignals(True)
            for c in range(tablewidget.columnCount()):
                cellText = "{0}".format(tablewidget.item(0, c).text() if tablewidget.item(0, c) else "")
                if cellText:
                    data.append(cellText)
            tablewidget.setColumnCount(len(data)+1)
            for c, d in enumerate(data):
                tablewidget.setItem(0, c, QtWidgets.QTableWidgetItem(d))
            tablewidget.setItem(0, len(data), QtWidgets.QTableWidgetItem(""))
            tablewidget.blockSignals(False)
        return cleanup
    
    def makeAppendActionEntry(self, a, optional=True):
        """
        creates a table widget for appending arguments into a list
        """
        helpstring = self.makeHelpString(a)
        tablewidget = QtWidgets.QTableWidget(1, 1, self.options)      
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(tablewidget.sizePolicy().hasHeightForWidth())
        tablewidget.setSizePolicy(sizePolicy)
        tablewidget.cellChanged.connect(self.cleanupEmptyTableRows(tablewidget))
        tablewidget.verticalHeader().hide()
        tablewidget.horizontalHeader().hide()

        if a.default:
            # add enough rows to hold default data + one empty row
            cnt = tablewidget.columnCount()
            needed = len(a.default)
            if needed >= cnt:
                for i in range(needed-cnt+1):
                    tablewidget.insertColumn(tablewidget.columnCount())                    
            for column, d in enumerate(a.default):
                tablewidget.setItem(0, column, QtWidgets.QTableWidgetItem(d))
            
        if optional:
            include = QtWidgets.QCheckBox(helpstring, self.options)                                
            enabled = a.default is not None
            include.setChecked(enabled)           
            self.disableOnClick(tablewidget)(enabled)
            include.clicked.connect(self.disableOnClick(tablewidget))                
            self.registerDisplayStateInfo(a.dest, [include])
        else:
            include = QtWidgets.QLabel(helpstring, self.options)
            
        self.registerDisplayStateInfo(a.dest, [tablewidget])
        self.commandLineArgumentCreators.append(self.createFunctionToMakeAppendCommandLine(include, tablewidget, a))
        self.optionsLayout.addRow(include, tablewidget)

    def createFunctionToMakeAppendCommandLine(self, include_widget, tablewidget, argument):
        """
        function to create a function that generates a command line string,
        specialized for one given option (these functions are generated on-the-fly 
        while building the ui)
        """
        def to_command_line():
            data = []
            if type(include_widget) == QtWidgets.QCheckBox:
                checked = include_widget.isChecked()
            else:
                checked = True
            if checked:
                if type(tablewidget) == QtWidgets.QTableWidget:
                    if argument.option_strings:
                        for c in range(tablewidget.columnCount()):
                          cellText = "{0}".format(tablewidget.item(0, c).text() if tablewidget.item(0, c) else "")
                          if cellText:
                              data.extend([argument.option_strings[0], cellText])
                    else:
                        assert False # programming error
                else:
                    assert False # programming error
            else:
                return []
            return data
        return to_command_line           
 

    def makeCommandLine(self):
        """
        construct the command line from the ui state
        """
        commandline = []
        for c in self.commandLineArgumentCreators:
            commandline.extend(c())
        return commandline
        
    def hasOne(self, list_of_possibilities, cmdline):
        """
        True if an element of list_of_possibilities occurs in cmdline
        """
        for p in list_of_possibilities:
            if p in cmdline:
                return True
        return False
        
    def validateMutualExclusiveOptions(self):
        """
        check if mutex options specified
        """
        cmdline = " ".join(self.makeCommandLine())
        for m in self.parser._mutually_exclusive_groups:
            foundOne = False
            offending_options = []
            for a in m._group_actions:
                present = self.hasOne(a.option_strings, cmdline)
                if present and foundOne:
                    offending_options.append(a.option_strings)
                    return False, offending_options
                elif present:
                    offending_options.append(a.option_strings)
                    foundOne = True
        return True, []
        
    def onOk(self):
        """
        handle ok button pressed
        """
        validate, offensive_options = self.validateMutualExclusiveOptions()
        if validate:
            if self.ok_button_handler is None:
                self.accept()
            else:
                self.ok_button_handler(self)
        else:
            mutexes = "\n".join([",".join(o) for o in offensive_options])
            QtWidgets.QMessageBox.question(self, 'Validation error', "The following options are mutually exclusive:\n{0}".format(mutexes), QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            
    def onCancel(self):
        """
        handle cancel button pressed
        """
        if self.cancel_button_handler is None:
            self.reject()
        else:
            self.cancel_button_handler(self)

    def resetAllWidgets(self, argparser):
        helper = argparse.ArgumentParser(add_help=False, parents=[self.parser], fromfile_prefix_chars='@')
        # make sure default values don't get enabled
        for a in helper._get_optional_actions():
          a.default = None
        for a in helper._get_positional_actions():
          a.default = None
        # make sure all checkboxes that were already enabled are disabled first
        for a in self.destToWidget:
          for w in self.destToWidget[a]:
            if type(w) == QtWidgets.QCheckBox:
              w.setChecked(False)
              w.clicked.emit(False)
            elif type(w) == QtWidgets.QTableWidget:
              w.setColumnCount(1)
              w.setItem(0, 0, QtWidgets.QTableWidgetItem(""))

    def onLoad(self):
        """
        handle load button pressed
        """
        filename = QtWidgets.QFileDialog.getOpenFileName()
        if filename:
          helper = argparse.ArgumentParser(add_help=False, parents=[self.parser], fromfile_prefix_chars='@')
          self.resetAllWidgets(helper)
          result = helper.parse_args(['@{0}'.format(filename)])
          for a in helper._get_optional_actions():
            self.copyActionValuesToUi(a,result)
          for a in helper._get_positional_actions():
            self.copyActionValuesToUi(a,result)
          self.filename = filename

    def copyActionValuesToUi(self, a, result):
        """
        function to update ui after loading command line arguments from file
        a = argparse action 
        result = argparse parse result
        """
        if a.dest in self.destToWidget:
          for w in self.destToWidget[a.dest]:
            data = result.__getattribute__(a.dest)
            if type(w) == QtWidgets.QCheckBox:
              if data is not None:
                if type(data) == bool:
                    w.setChecked(data)
                    w.clicked.emit(data)
                else:
                    w.setChecked(True)
                    w.clicked.emit(True)
            elif type(w) == QtWidgets.QLineEdit:
              if data is not None:
                if type(data) == type([]):
                  w.setText(" ".join(["{0}".format(d) for d in data]))
                else:
                  w.setText("{0}".format(data))
            elif type(w) == QtWidgets.QSpinBox:
              if data is not None:
                w.setValue(int("{0}".format(data)))
            elif type(w) == QtWidgets.QComboBox:
              if data is not None:
                w.setCurrentIndex(w.findText("{0}".format(data)))                
            elif type(w) == QtWidgets.QTableWidget:
              #clear existing defaults first
              w.setColumnCount(1)
              w.setItem(0, 0, QtWidgets.QTableWidgetItem(""))
              cnt = w.columnCount()
              if data is not None:
                needed = len(data)
                if needed >= cnt:
                  for i in range(needed-cnt+1):
                    w.insertColumn(w.columnCount())                    
                for column, d in enumerate(data):
                  w.setItem(0, int("{0}".format(column)), QtWidgets.QTableWidgetItem(d))

    def onSave(self):
        """
        what to do when the save button is clicked
        """
        if not self.filename: 
          self.onSaveAs()
        else:
          try:
            with open(self.filename, "w") as f:
              c = self.makeCommandLine()
              for line in c:
                f.write(line+"\n")
          except IOError:
            import os.path
            QtWidgets.QMessageBox.critical(self,
                                       "Critical",
                                       "Couldn't write to file {0}".format(os.path.abspath(self.filename)))


    def onSaveAs(self):
        """
        what to do when the save as button is clicked
        """
        filename = QtWidgets.QFileDialog.getSaveFileName()
        if filename:
          self.filename = filename
          self.onSave()
        
    def parse_args(self):
        """
        method to ensure that the ui looks and feels identical to the argparse parser
        """
        cmdline = self.makeCommandLine()
        return self.parser.parse_args(cmdline)
            
if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    
    # EXPERIMENT USING BASIC PARSER     
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make-argument-true", help="optional boolean argument", action="store_true")
    parser.add_argument("-o","--make-other-argument-true", help="optional boolean argument 2", action="store_true", default=True)
    parser.add_argument("-n","--number", help="an optional number", type=int)
    parser.add_argument("-r","--restricted-number", help="one of a few possible numbers", type=int, choices=[1,2,3], default=2)
    parser.add_argument("-c", "--counting-argument", help="counting #occurrences", action="count")
    parser.add_argument("-d", "--default-value-argument", help="default value argument with a very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long description", type=float, default="3.14")
    parser.add_argument("-a", "--append-args", help="append arguments to list", type=str, action="append", default=["dish", "dash"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument('--foo', type=int, nargs='+')
    parser.add_argument('--bar', type=int, nargs=2, metavar=('bar', 'baz'))
    app = QtWidgets.QApplication(sys.argv)
    a = ArgparseUi(parser, left_label_alignment=True, use_scrollbars=True, use_save_load_button=True)
    a.show()
    app.exec_()
    print ("Ok" if a.result() == 1 else "Cancel")
    if a.result() == 1: # Ok pressed
        parsed_args = a.parse_args()
    else:
        parsed_args = None

    print (parsed_args)

    # EXPERIMENT USING PARENT PARSER
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--parent', type=int)
    foo_parser = argparse.ArgumentParser(parents=[parent_parser])
    foo_parser.add_argument('foo')
    foo_parser.description = "Come on! Let's bar that foo!!"
    foo_parser.epilog = "And this is how you bar a foo!"
    a = ArgparseUi(foo_parser, use_scrollbars=False, use_save_load_button=True, window_title="Simple config")
    a.show()
    app.exec_()
    print ("Ok" if a.result() == 1 else "Cancel")
    if a.result() == 1: # Ok pressed
        parsed_args = a.parse_args()
    else:
        parsed_args = None

    print (parsed_args)
