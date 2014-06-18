#!/usr/bin/env python
# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
Download the needed external software packages.
"""
import sys
import os

# See the list of packages in
# http://scipionwiki.cnb.csic.es/bin/view/TWiki/PackagesInstall


URL_BASE = "http://scipionwiki.cnb.csic.es/files/scipion/software/em"
PACKAGES = {
    #'xmipp': 'xmipp.tgz',
    'bsoft': 'bsoft1_8_8_Fedora_12.tgz',
    'ctffind': 'ctffind_V3.5.tgz',
    'eman': 'eman2.pre2-1.linux64.tar.gz',
    'frealign': 'frealign_v9.07.tgz',
    'relion': 'relion-1.2.tgz',
    'spider': 'spider-web-21.13.tgz'}


def download(packages=None):
    if not packages:
        packages = PACKAGES.keys()
    for package in packages:
        try:
            os.system("wget -c %s/%s" % (URL_BASE, PACKAGES[package]))
        except KeyError as e:
            print 'Unknown package: %s' % e


if __name__ == '__main__':
    # Enter into the EM packages directory
    os.chdir(os.path.join(os.environ['SCIPION_HOME'], 'software', 'em'))
    download(sys.argv[1:])
