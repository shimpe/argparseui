                                                                        
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

    import argparse
    import sys
    from PyQt4 import QtGui
    
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
    a = ArgparseUi(parser)
    a.show()
    app.exec_()

    if a.result() == 1: # Ok pressed
        parsed_args = a.parse_args() # ask argparse to parse the options
        print parsed_args            # print the parsed_options

    # Do what you like with the arguments...
