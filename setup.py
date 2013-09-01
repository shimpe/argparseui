##############################################################################
#      This file is part of argparseui.                                      #
#                                                                            #
#      argparseui is free software: you can redistribute it and/or modify    #
#      it under the terms of the GNU General Public License as published by  #
#      the Free Software Foundation, either version 3 of the License, or     #
#      (at your option) any later version.                                   #
#                                                                            #
#      argparseui is distributed in the hope that it will be useful,         #
#      but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#      GNU General Public License for more details.                          #
#                                                                            #
#      You should have received a copy of the GNU General Public License     #
#      along with argparseui.  If not, see <http://www.gnu.org/licenses/>.   #
##############################################################################

#!/usr/bin/env python

from distutils.core import setup

setup(name='argparseui',
      version='0.0.1',
      description='Auto-generated ui for argparse based scripts',
      author='Stefaan Himpe',
      author_email='stefaan.himpe@gmail.com',
      url='https://github.com/shimpe/argparseui',
      packages=['argparseui'],
      package_dir={'argparseui' : ''},
      classifiers=['Intended Audience :: Developers',
                   'Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'
                  ])


