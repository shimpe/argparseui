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
from argparseui import __version__

with open('README.txt') as f:
      long_description = f.read()

setup(name='argparseui',
      version=__version__,
      description='Auto generate ui for argparse based command-line tools',
      long_description=long_description,
      author='Stefaan Himpe',
      author_email='stefaan.himpe@gmail.com',
      url='https://github.com/shimpe/argparseui',
      packages=['argparseui'],
      classifiers=['Intended Audience :: Developers',
                   'Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'
                  ])


