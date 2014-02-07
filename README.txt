                                                                        
      This file is part of argparseui.
  
      argparseui is free software: you can redistribute it and/or modify
      it under the terms of the GNU General Public License as published by
      the Free Software Foundation, either version 3 of the License, or
      (at your option) any later version.
  
      argparseui is distributed in the hope that it will be useful,
      but WITHOUT ANY WARRANTY; without even the implied warranty of
      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
      GNU General Public License for more details.
  
      You should have received a copy of the GNU General Public License
      along with argparseui.  If not, see <http://www.gnu.org/licenses/>.
                                                                        

argparseui
==========

Purpose of argparseui
---------------------

argparseui can be used to quickly auto-generate a UI
from an argparse based command line tool

the UI has widgets that allow to set up the command line options

argparseui depends on PyQt

State of argparseui
-------------------

argparseui is a scratch-my-own-itch tool

as such it doesn't support all possibilities of argparse

use at your own risk, but feel free to log a bug/request

Basic Parser Usage
------------------
::

    import argparse
    import sys
    from PyQt4 import QtGui
    import argparseui
    
    # EXPERIMENT USING BASIC PARSER     
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make-argument-true", help="optional boolean argument", action="store_true")
    parser.add_argument("-o","--make-other-argument-true", help="optional boolean argument 2", action="store_true",  default=True)
    parser.add_argument("-n","--number", help="an optional number", type=int)
    parser.add_argument("-r","--restricted-number", help="one of a few possible numbers", type=int, choices=[1,2,3],  default=2)
    parser.add_argument("-c", "--counting-argument", help="counting #occurrences", action="count")
    parser.add_argument("-d", "--default-value-argument", help="default value argument", type=float, default="3.14")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("posarg", help="positional argument", type=str)

    app = QtGui.QApplication(sys.argv)
    a = argparseui.ArgparseUi(parser)
    a.show()
    app.exec_()

    if a.result() == 1: # Ok pressed
        parsed_args = a.parse_args() # ask argparse to parse the options
        print parsed_args            # print the parsed_options

    # Do what you like with the arguments...

Example using save/load button and keeping the dialog open when pressing ok
-----------------------------------------------------------------------------------------------------
::

    import argparse
    import sys
    from PyQt4 import QtGui
    import argparseui

    def do_something(argparseuiinstance):
        options = argparseuiinstance.parse_args()
        print ("Options: ", options)
         
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make-argument-true", help="optional boolean argument", action="store_true")
    parser.add_argument("-o","--make-other-argument-true", help="optional boolean argument 2", action="store_true",  default=True)

    app = QtGui.QApplication(sys.argv)
    a =     argparseui.ArgparseUi(parser,use_save_load_button=True,ok_button_handler=do_something)
    a.show()
    app.exec_()
    if a.result() != 1:
        # Do what you like with the arguments...
        print ("Cancel pressed")
 
Extended features
-----------------

You can pass some extra command line arguments to ArgparseUi::

  *helptext_default* = string [default: ' [default=%(default)s]']
  this argument can be used to customize the default value annotations in the ui

  *remove\_defaults\_from_helptext* = True/False [default: False]
  if enabled, this option will remove the default value annotations from 
  the labels in the ui

  *use\_save\_load_button* = True/False [default: False]
  if set to True, three extra buttons [Load options, Save Options, Save Options As] appear
  the options are saved to (or loaded from) a command line option file in a file format compatible with 
  argparse's built-in support for loading options from file

  *use_scrollbars* = True/False [default: False]
  if set to True, the options are embedded in a scrollable panel

  *window_title* = string [default: "Make your choice"]
  if set to a string, this string will be used as dialog title

  *left\_label\_alignment* = True/False [default: None]
  if set to True, the checkboxes are left-aligned. This may be useful on platforms 
  like KDE or MacOsx which by default use right-alignment
  
  *ok\_button\_handler* = function taking one argument [default:None]
  if set to None, the dialog will close upon clicking the ok button and its result will be set to 1
  if set to a function accepting an ArgparseUi instance as argument, clicking ok will call that function 
  with "self" as argument
  
  *cancel\_button\_handler* = function taking one argument [default:None]
  if set to None, the dialog will close upon clicking cancel and its result will be != 1
  if set to a function accepting an ArgparseUi instance as argument, clicking cancel will call that
  function with "self" as argument

Contributors
------------

The following people have contributed to argparseui

  * Stefaan Himpe
  * Thomas Hisch
