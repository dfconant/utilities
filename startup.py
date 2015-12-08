#-------------------------------------------------------------------------------
# Name:        startup
# Purpose:     To automate the execution of certain common commands,
#              specifically for when IPython is started
#
# Author:      David Moses
#
# Created:     22/08/2013
# Copyright:   (c) David Moses 2013
#-------------------------------------------------------------------------------

import os
import sys
import socket

# Creates a static variable that specifies whether or not the current system
# is running Linux
IS_LINUX = 'linux' in sys.platform

# Creates a static variable that specifies the name of the current system
HOST_NAME = socket.gethostname()

# Creates a static variable that specifies the absolute path for the directory
# containing all of the Python code and data (which is system-dependent)
if   HOST_NAME == 'Davids-MacBook-Pro-2.local':
    BASE_DIR = '/Users/david_conant/Dropbox/Python'
elif HOST_NAME in ['dura', 'crtx']:
    BASE_DIR = '/home/dfconant/python'
elif HOST_NAME == 'Cushing':
    BASE_DIR = 'C:\\Users\\David\\Documents\\My Dropbox\\David\\Lab\\Python'
else:
    raise Exception('Current host machine not recognized.')

# Creates static variables specifying which files to not import and which paths
# to not add to the current Python path
IGNORE_FILES = ('history', 'startup', 'RBM2', '__init__')
IGNORE_PATHS = ('data', 'theano', '.sync', '.SyncArchive', '.idea')

# Creates a static variable that specifies which built-in modules to import
# globally (with the respective aliases) 
IMPORT_LIST = ('os',                'sys',                   
               'numpy as np',       'scipy as sp',
               'matplotlib as mpl', 'matplotlib.pyplot as plt')

# Creates a static variable that specifies if the script is being run from
# within an IPython environment
try:
    RUN_FROM_IPYTHON = eval('__IPYTHON__')
except:
    RUN_FROM_IPYTHON = False

def main():

    # Changes directories to the base directory (which depends on the system)
    os.chdir(BASE_DIR)

    # Updates the PYTHONPATH with the current directory and sub-directories
    # and obtains a list of files that should be imported if currently in an
    # interactive environment
    files_to_import = updatePath()

    # If the script is not being run from an interactive environment, this
    # method terminates immediately
    if not RUN_FROM_IPYTHON:
        return

    # Enables auto-reloading, and enables pylab (for some machines only)
    import IPython
    ipython = IPython.get_ipython()
    ipython.magic('load_ext autoreload')
    ipython.magic('autoreload 2')
    if HOST_NAME in ['David-PC', 'boss']:
        ipython.magic('pylab qt')

    # Globally imports the modules in the import list
    for i in IMPORT_LIST:
        split_import = i.split()
        module_name = split_import[0]
        alias_name  = split_import[-1] if len(split_import) > 1 else None
        globalImport(module_name = module_name, alias_name = alias_name)

    # Loops through each file in the files_to_import list and attempts to
    # import each one
    for f in files_to_import:
        globalImport(module_name = f)

    # In graphical environments, change the default pyplot font size to 14
    if HOST_NAME in ['David-PC', 'boss']:
        globals()['plt'].rcParams['font.size'] = 14

    # Changes the CPU affinity (for Linux machines) so that multiple cores
    # are used during parallel processing
    if IS_LINUX:
        os.system('taskset -p 0xffffffff %d >/dev/null' % os.getpid())
        
def globalImport(module_name, alias_name = None):
    """
    Globally imports the desired module, with an alias name if desired.
    """
    if alias_name is None:
        alias_name = module_name
    try:
        if '.' in module_name:
            globals()[alias_name] = \
                __import__(module_name, fromlist=module_name.split('.')[0])
        else:
            globals()[alias_name] = __import__(module_name)
    except Exception as e:
        print('Module %s not imported due to the following error: %s' % 
              (module_name, str(e)))

def updatePath(ignore_paths = IGNORE_PATHS, ignore_files = IGNORE_FILES):
    """ 
    Updates PYTHONPATH to contain the appropriate directory and sub-directories
    and obtains a list of the Python files contained within them.
    
    Parameters:
    - ignore_paths   (list)     - A list (or tuple) containing paths to ignore
                                  (i.e. paths that will not be added to the
                                  PYTHONPATH)
    - ignore_files   (list)     - A list (or tuple) containing files that
                                  should not be flagged for eventual import
                                  
    Returns:
    A list of strings specifying the files that should be imported
    """
    
    # Initializes the list of the files that will be imported
    files_to_import = []

    # Import all .py files in the current folder (and subfolders)
    for path, dirs, files in os.walk(os.getcwd()):

        # Skips the current path (and all sub-directories) if it is one of the
        # paths that should be ignored (which is specified earlier).
        if any(list(p in path.split(os.sep)[-1] for p in ignore_paths)):
            while dirs: dirs.pop()
            continue

        # Adds the current directory to the system path (PYTHONPATH)
        sys.path.append(path)
    
        # Loops through each file and adds it to the list of files to eventually
        # import (if it meets certain criteria). The files are not immediately
        # imported because of possible dependencies with other modules that are
        # not part of the path yet.
        for name in files:
            if all(f not in name for f in ignore_files) and name[-3:] == '.py':
                files_to_import.append(name[:-3])

    return files_to_import

# Main method
if __name__ == '__main__':
    main()
