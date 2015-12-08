#-------------------------------------------------------------------------------
# Name:        pathHandler
# Purpose:     To provide path searching support for Python scripts
#
# Author:      David Moses
#
# Created:     Oct 22, 2013
# Copyright:   (c) David Moses 2013
#-------------------------------------------------------------------------------

import os
import re

import startup

# Obtains the following information from the startup module:
# 1) A Boolean specifying whether or not the current system is running Linux
# 2) A string specifying the name of the current system
# 3) A string specifying the absolute path for the directory containing all
#    of the Python data and code
IS_LINUX  = startup.IS_LINUX
HOST_NAME = startup.HOST_NAME
BASE_DIR  = startup.BASE_DIR

# Creates a static variable for the directory holding all the data
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Creates static variables for the sub-directories in the data directory
CORPUS_DIR = os.path.join(DATA_DIR, 'corpora')
HDF_DIR    = os.path.join(DATA_DIR, 'hdf')
HTK_DIR    = os.path.join(DATA_DIR, 'htk')
LOG_DIR    = os.path.join(DATA_DIR, 'logs')
PICKLE_DIR = os.path.join(DATA_DIR, 'pickles')

# Creates a static variable for the Matlab directory.
if HOST_NAME in ['dura', 'crtx']:
    MATLAB_DIR = os.path.join(os.sep + 'home', 'dmoses', 'matlab')
else:
    MATLAB_DIR = os.path.join(BASE_DIR, os.path.pardir, 'Matlab')

# Creates a static variable for the directory holding figures.
if HOST_NAME == 'boss':
    FIGURE_DIR = '/home/dmoses/Dropbox/David/Lab/Figures'
else:
    FIGURE_DIR = os.path.curdir

# Creates a static variable for the directory holding the Gump data.
GUMP_DIR = os.path.join(MATLAB_DIR, 'code', '@Gump')

# Creates static variables for the directories holding the Gump transcript,
# sentence, and posteriogram transcription files (respectively)
GUMP_TRANS_DIR = os.path.join(GUMP_DIR, 'Transcripts')
GUMP_SENT_DIR  = os.path.join(GUMP_DIR, 'Sentences')
GUMP_POST_DIR  = os.path.join(HTK_DIR, 'actual_posteriograms')

# Creates a static variable for the directory holding the raw experimental data.
# Handles the cases for Windows and Unix
if IS_LINUX:
    RAW_DATA_DIR = os.path.join(os.sep + 'data_store', 'human', 'HTK_raw')
else:
    RAW_DATA_DIR = os.path.join('C:' + os.sep, 'Users', 'David', 'Desktop',
                                'Lab_Data')

def ensureExtension(file_name, extension):
    """ 
    Ensures that the provided file name ends with the given extension
    
    Parameters:
    - file_name      (string)   - The file name or path (with or without a file
                                  extension)
    - extension      (string)   - The desired file extension
    
    Returns:
    The file name, which will end in the provided extension
    """
    
    # Ensures that the extension includes the . at the beginning of it (for
    # example, if the extension was 'txt', it will be changed to '.txt')
    if extension[0] != '.':
        extension = '.' + extension
    
    # Ensures that the file name ends in the extension
    if file_name[-len(extension):] != extension:
        file_name = file_name + extension
    
    # Returns the file name
    return file_name

def ensurePrefix(file_name, prefix, ensure_under = True):
    """
    Ensures that the provided file name ends starts with a given prefix.
    
    Parameters:
    - file_name      (string)   - The file name
    - prefix         (string)   - The desired prefix
    - ensure_under   (Boolean)  - Specifies whether or not to ensure that an
                                  underscore, '_', appears between the prefix
                                  and the rest of the file name
    
    Returns:
    The file name, which will begin with the desired prefix
    """
    
    if ensure_under and prefix[-1] != '_':
        prefix += '_'
    
    if len(file_name) < len(prefix) or file_name[:len(prefix)] != prefix:
        return prefix + file_name
    else:
        return file_name

def getNextFullResultDir(search_dir = 'log', create_dirs = ('log', 'hdf'),
                         prefix = 'full_sim'):
    """
    Returns the directory name that should be used for the next set of full
    results.
    
    Parameters:
    - search_dir     (string)   - Specifies which directory to search. Valid
                                  options are: 'log', 'hdf', 'htk'
    - create_dirs    (list)     - Specifies which directories any
                                  sub-directories should be created under.
                                  Valid options for elements of this list are
                                  the same as the valid options for search_dir
    - prefix         (string)   - The part of the sub-directory that appears
                                  before the number
                                  
    Returns:
    A string specifying the name of the sub-directory within search_dir that
    the next set of full results should be stored in
    """
    
    # Determines the search directory using the string
    search_dir_path = globals()[search_dir.upper() + '_DIR']
    
    # Determines the directories in which sub-directories will be made (if any)
    create_dirs_paths = None
    if create_dirs is not None:
        if type(create_dirs) not in [list, tuple]:
            create_dirs = [create_dirs]
        create_dirs_paths = [globals()[d.upper()+'_DIR'] for d in create_dirs]
    
    # Initializes the current sim number
    cur_num = 1
    
    # Increments the current sim number until a directory containing simulation
    # results under that number is not found
    while True:
        if not os.path.exists(os.path.join(search_dir_path,
                                           '%s_%d' % (prefix, cur_num))):
            break
        cur_num += 1
    
    # Constructs the new directory name
    new_dir_name = '%s_%d' % (prefix, cur_num)
    
    # Creates the directories (if desired). The log directory is for simulation
    # log files, and the hdf directory will hold any posteriograms that are
    # generated during the decoding.
    if create_dirs_paths is not None:
        for sub_dir in create_dirs_paths:
            os.makedirs(os.path.join(sub_dir, new_dir_name))
    
    # Returns the new directory name
    return new_dir_name

def getNextFileName(search_dir):
    """
    Returns the next appropriate file name in the directory. Names should
    progress in ascending numerical order. File extensions are ignored.

    Parameters:
    - search_dir     (string)   - Specifies which directory to search                               before the number

    Returns:
    A string specifying the next appropriate file name (without the extension)
    that should be used within the searched directory
    """

    # Obtains a list of all of the entries in the desired directory
    dir_entries = os.listdir(search_dir)

    # Loops through each of the directory entries and appends the list with
    # that entry without the file extension if a file extension is detected
    # for that entry
    for entry in dir_entries:
        if '.' in entry:
            dir_entries.append(entry[:entry.rfind('.')])

    # Initializes the current file number
    cur_num = 0

    # Increments the current file number until a file name using this
    # number is not found.
    while True:
        if not str(cur_num) in dir_entries:
            break
        cur_num += 1

    # Returns the new file name
    return str(cur_num)

def getPicklePath(file_name = None):
    """
    Returns the path to a pickle file (unless the file_name is None, in which
    case the directory holding the pickle files is returned).
    
    Parameters:
    - file_name      (string)   - The file name for the pickle
    
    Returns:
    The full path of a desired pickle file.
    """
    
    # Returns the pickle file directory if file_name is equal to None
    if not file_name:
        return PICKLE_DIR
    
    # Obtains a list of the files in the pickle directory
    pickle_files = []
    for full_path, _, files in os.walk(PICKLE_DIR):
        for file_path in files:
            pickle_files += [os.path.join(full_path, file_path)]
    
    # If the desired file is found, the path is returned. If not, the search is
    # repeated if the current file name didn't end in '.pickle' after changing
    # the file name to end in '.pickle'.
    for i in range(2):
        if i == 1:
            new_file_name = ensureExtension(file_name, '.pickle')
            if file_name == new_file_name:
                break
            else:
                file_name = new_file_name
        
        for cur_file_path in pickle_files:
            if file_name == cur_file_path.split(os.sep)[-1]:
                return cur_file_path
    
    # If the file was not found, a full path to where the file should be is
    # returned. This is useful for specifying the path of where a pickle file
    # should be saved.
    return os.path.join(PICKLE_DIR, file_name)

def getFilesInDir(parent_dir, filter_re = '.*'):
    """
    Returns a list containing the full paths to all the files in the specified
    directory and any of its subdirectories. Only file names that match the
    provided regular expression are included.
    
    Parameters:
    - parent_dir     (string)   - The directory in which the file search starts
    - filter_re      (string)   - The regular expression to which each file
                                  name will be attempted to be matched. If
                                  successful, that file will be included in the
                                  returned list. The default is to return every
                                  file.
    
    Returns:
    A list of strings representing the full paths to the desired files.
    """
    
    # Initializes the list of files
    file_list = []
    
    # Walks through the provided directory and loops through each file in that
    # directory. For each file, if it matches the regular expression provided,
    # its full path is added to the file list.
    for root, _, files in os.walk(parent_dir):
        for file_name in files:
            if re.match(pattern=filter_re, string=file_name):
                file_list.append(os.path.join(root, file_name))
    
    # Returns the file list
    return file_list

def getPickle(file_name):
    """
    Returns the path to a pickle file.
    
    Parameters:
    - file_name      (string)   - The file name for the pickle file
    
    Returns:
    The full path of the desired pickle file (after ensuring that the file
    ends in '.pickle')
    """
    
    return os.path.join(PICKLE_DIR, ensureExtension(file_name, '.pickle'))
    
def getTextCorpus(file_name):
    """
    Returns the path to a corpus file.
    
    Parameters:
    - file_name      (string)   - The file name for the text corpus
    
    Returns:
    The full path of the desired corpus file (after ensuring that the text file
    ends in '.txt')
    """
    
    return os.path.join(CORPUS_DIR, ensureExtension(file_name, '.txt'))

def getLogFile(file_name):
    """
    Returns the path to a log file.
    
    Parameters:
    - file_name      (string)   - The file name for the log file
    
    Returns:
    The full path of the desired log file (after ensuring that the text file
    ends in '.txt')
    """
    
    return os.path.join(LOG_DIR, ensureExtension(file_name, '.txt'))

def getHDF(file_name):
    """
    Returns the path to a hdf5 file.
    
    Parameters:
    - file_name      (string)   - The file name for the hdf5 file
    
    Returns:
    The full path of the hdf5 file (after ensuring that the file ends in
    '.hdf5')
    """
    
    return os.path.join(HDF_DIR, ensureExtension(file_name, '.hdf5'))

def getHTK(file_name):
    """
    Returns the path to a HTK file.
    
    Parameters:
    - file_name      (string)   - The file name for the HTK file
    
    Returns:
    The full path of the HTK file (after ensuring that the file ends in '.htk')
    """
    
    return os.path.join(HTK_DIR, ensureExtension(file_name, '.htk'))

def getActualPosteriogram(file_name):
    """
    Returns the path to a HTK file specifying a posteriogram transcription.
    
    Parameters:
    - file_name      (string)   - The file name for the HTK file
    
    Returns:
    The full path of the HTK file (after ensuring that the file ends in '.htk')
    from within the Gump posteriogram transcription directory
    """
    
    return os.path.join(GUMP_POST_DIR, ensureExtension(file_name, '.htk'))

def getSentence(file_name):
    """
    Returns the path to a text file that specifies a Gump sentence.
    
    Parameters:
    - file_name      (string)   - The file name for the sentence file
    
    Returns:
    The full path of the sentence file (after ensuring that the file ends in
    '.txt')
    """
    
    return os.path.join(GUMP_SENT_DIR, ensureExtension(file_name, '.txt'))

def getRawHTK(file_name):
    """
    Returns the path to a HTK file containing raw data.
    
    Parameters:
    - file_name      (string)   - The file name for the HTK file
    
    Returns:
    The full path of the HTK file containing the raw data (after ensuring that
    the file ends in '.htk')
    """
    
    return os.path.join(RAW_DATA_DIR, ensureExtension(file_name, '.htk'))
