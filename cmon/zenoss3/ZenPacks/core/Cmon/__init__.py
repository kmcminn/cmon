import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

from ZenPacks.core.Cmon.datasources.CmonDataSource import CmonDataSource
CmonDataSource.useZenCommand = lambda x: False
