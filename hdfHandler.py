#-------------------------------------------------------------------------------
# Name:        hdfHandler
# Purpose:     To handle interactions between Python and .hdf5 files
#
# Author:      David Moses
#
# Created:     Jan 13, 2014
# Copyright:   (c) David Moses 2013
#-------------------------------------------------------------------------------

import numpy as np
import warnings
import tables
import os

import pathHandler
import bundle

# TODO: Make a single HDF file that holds all results

# Initializes a static variable that is used to identify key, value list pairs
# when saving/loading dicts
DICT_IDENTIFIER = '________dict________'

def save(obj, file_name, use_abs_path = False):
    """
    Saves an object into an hdf5 file using a separate function.
    
    Parameters:
    - obj            (object)   - The object to save
    - file_name      (string)   - The desired file name for the hdf5 file
    - use_abs_path   (bool)     - Specifies whether or not the provided file
                                  name is an absolute path or a relative path
                                  (relative to pathHandler.HDF_DIR)
    """

    write(file_name, '/', obj, mode='w', use_abs_path=use_abs_path)

def load(file_name, obj = None, use_abs_path = False, ignore = ()):
    """
    Loads and returns the data from a hdf5 file in the form of an object.
    
    Parameters:
    - file_name      (string)     - The desired file name
    - obj            (Object)     - An object with a structure similar to the
                                    structure of the hdf5 file. For example, if
                                    the file has a group named A with sub-nodes
                                    B and C, the object should have an
                                    attribute A with sub-attributes named B and
                                    C. If an object is not provided, an attempt
                                    to infer it from the file name is made.
    - use_abs_path   (Boolean)    - Specifies whether or not the provided file
                                    name is an absolute path or a relative path
                                    (relative to pathHandler.HDF_DIR)
    - ignore         (list)       - A list of strings containing locations to
    
    Returns:
    The object after it has been updated with the data from the file.
    """
    
    # Loads the file
    with openFile(file_name, mode='r', use_abs_path=use_abs_path) as f:

        # If no object was provided, an attempt is made to infer the desired
        # object type from the file name
        if obj is None:

            # TODO: This shouldn't be done here
            # Tries to infer the object type from the file name
            try:
                if 'modkn' in file_name:
                    import LM
                    obj = LM.modknLM(order=int(file_name.split('modkn-')[1][0]))
                elif 'lda' in file_name:
                    import LDA
                    obj = LDA.LDA(classes=[])
            except:
                pass
            
            # If the object still has not been loaded at this point, a Bundle
            # object is used as the default.
            if obj is None:
                obj = bundle.Bundle()
        
        # Creates a dictionary that holds any dictionaries encountered
        encountered_dicts = {}

        # Loops through each node in the data
        for i in f.walk_nodes(f.root):
            
            # Obtains the location of the node as well as its type
            loc, node_type = str(i).split()[:2]

            # If the current node is specifying the file's root, it is skipped
            if loc == '/':
                continue

            # If any part of the location is specified in the ignore list,
            # then the current node is skipped
            if set(ignore).intersection(loc.split('/')):
                continue

            # Attempts to read data from the node. If a UnicodeDecodeError
            # occurs, a warning is displayed and the current node is
            # skipped. If a NoSuchNodeError occurs (which will happen if the
            # current node specifies a group), then an empty Bundle is added
            # to the object at the location specified by the current node's
            # location, and the loop continues to the next node.
            try:
                value = i.read()
            except UnicodeDecodeError:
                warnings.warn(('UnicodeDecodeError occurred during loading ' +
                              'of %s. This value was skipped.' % loc))
                continue
            except tables.NoSuchNodeError:
                addVar(obj, loc, bundle.Bundle())
                continue
            
            # If the node is a bytes object and not a string, it is converted
            # to a string. Note that the check for whether or not it is a
            # string is performed due to discrepancies between Python 2.x and
            # 3.x.
            if type(value) is bytes and type(value) is not str:
                # noinspection PyArgumentList
                value = str(value, encoding='utf-8')

            # If the node is a list containing a list of strings as the first
            # element, this first element is used as the new value. This is done
            # because of the way that string lists are saved in the hdf5 file
            # (see the save method for more details).
            if type(value) is list    and len(value) == 1 and \
               type(value[0]) is list and type(value[0][0]) is str:
                value = value[0]

            # If the value is a 0-dimensional array, which can happens when
            # trying to load saved scalars, the 0-dimensional array is
            # converted to a scalar
            try:
                if value.ndim == 0:
                    value = np.array([value], dtype=value.dtype)[0]
            except AttributeError:
                pass

            # If the current node is part of a dictionary specification, then
            # special steps are taken
            if DICT_IDENTIFIER in loc:
                
                # Obtains the name of the dictionary variable for which this
                # node is specifying a key, value pair as well as the key
                name, key = loc.split(DICT_IDENTIFIER)
                
                # If this dictionary has not yet been encountered, it is
                # initialized and added to the list of encountered dictionaries
                if name not in encountered_dicts.keys():
                    encountered_dicts[name] = {}
                
                # If '/' is in the key, it means that the value is actually
                # an object. If this is the case, a bundle is used to
                # store the values specified for that object across multiple
                # nodes.
                if '/' in key:
                    key, var_name = key.split('/', 1)
                    if key not in encountered_dicts[name].keys():
                        encountered_dicts[name][key] = bundle.Bundle()
                    setattr(encountered_dicts[name][key], var_name, value)
                
                # Otherwise, the key, value pair is stored in the dictionary
                else:
                    encountered_dicts[name][key] = value
                
                # Continues to the next node
                continue

            # The location of the node represents the location of that node's
            # value within the provided object. This location is used to assign
            # the current value to the appropriate attribute within the object
            # (or one of the object's sub-objects).
            addVar(obj, loc, value)

    # Loops through each encountered dictionary and adds them to the object
    for key, val in encountered_dicts.items():
        addVar(obj, key, val)

    # If the length of the object's dictionary is 1, signifying that the object
    # only contains one value, then that value is returned. Otherwise, the
    # object is returned.
    if len(obj.__dict__) == 1:
        return list(obj.__dict__.values())[0]
    else:
        return obj

def read(file_name, key, use_abs_path = False):
    """
    Reads and returns one value from a .hdf5 file as specified by a key.
    
    Parameters:
    - file_name      (string)     - The desired file name
    - key            (string)     - The key that corresponds to the desired
                                    value
    - use_abs_path   (bool)       - Specifies whether or not the provided file
                                    name is an absolute path or a relative path
                                    (relative to pathHandler.HDF_DIR)
    
    Returns:
    The desired value from within the hdf5 file
    """
    
    with openFile(file_name, mode='r', use_abs_path=use_abs_path) as f:
        return f.get_node(where='/' + key).read()

def write(file_name, key, value, mode = 'a', use_abs_path = False):
    """
    Writes a value to a .hdf5 file at the location specified by the key.

    Parameters:
    - file_name      (string)    - The desired file name
    - key            (string)    - The key that specifies where to write the
                                   value
    - value          (object)    - The value to write
    - mode           (string)    - The mode in which to open the file (view
                                   the pytables documentation for more details)
    - use_abs_path   (bool)      - Specifies whether or not the provided file
                                   name is an absolute path or a relative path
                                   (relative to pathHandler.HDF_DIR)

    Returns:
    The desired value from within the hdf5 file
    """

    # Ensures that the key starts with a '/'
    if key[0] != '/':
        key = '/%s' % key

    # Opens the desired .hdf5 file (or creates one if the file does not exist)
    with openFile(file_name, mode=mode, use_abs_path=use_abs_path) as f:

        # If the provided value has a __dict__, then a list of the variables of
        # the object (sorted by ascending 'depth') is obtained. Here, 'depth'
        # refers to the level inside the object at which the variable
        # resides. For example, if the provided object has some object as one
        #  of its variables, then that sub-object's variables would have a
        # depth of 1. Depth is specified by how many '/' characters are in
        # the variable name (view extractDataFromObject for more details).
        if hasattr(value, '__dict__'):
            variables = sorted(extractDataFromObject(value),
                               key=lambda var: var['name'].count('/'))

        # Otherwise, an attempt is made to store the value as is
        else:
            variables = [createDictFromValue(name='', value=value)]

        # Loops through each variable
        for v in variables:

            # Obtains the descriptors for the current variable and adds the
            # desired key location to the start of the name
            name  = key + v['name']
            dtype = v['dtype']
            shape = v['shape']
            data  = v['data']

            # Separates the "location" of the variable away from its name,
            # which will be used to determine which group the variable should
            # be stored in
            last_slash_index = name.rfind('/')
            loc  = name[:last_slash_index]
            name = name[last_slash_index+1:]

            # If the length of the computed location string is zero,
            # it is set equal to the root location ('/')
            if not len(loc):
                loc = '/'

            # If a node at the current location already exists, it is removed
            try:
                f.remove_node(loc, name=name, recursive=True)
            except LookupError:
                pass

            # If the location of the variable does not already exist as a group
            # within the file, then a new group is created
            if loc not in [str(x).split()[0] for x in f.walk_groups(f.root)]:
                last_slash_index_loc = loc.rfind('/')
                new_loc  = loc[:last_slash_index_loc]
                new_name = loc[last_slash_index_loc+1:]
                if len(new_loc) == 0:
                    new_loc = '/'
                f.create_group(new_loc, new_name, new_name)

            # If the data is a numpy array containing strings, it is converted
            # to a list of strings
            if dtype is np.ndarray and type(data[0]) is np.str_:
                data = [str(s) for s in data]
                dtype = list

            # Stores the data
            if dtype in [list, tuple] or (shape != () and type(data[0]) is str):
                array = f.create_vlarray(loc, name, tables.ObjectAtom())
                for d in data:
                    array.append(d)
            elif data is None:
                pass
            else:
                f.create_array(loc, name, data)

def getFileHierarchy(file_name, use_abs_path = False):
    """
    Obtains the hierarchy (object tree) of a file.

    Parameters:
    - file_name      (string)     - The desired file name
    - use_abs_path   (bool)       - Specifies whether or not the provided file
                                    name is an absolute path or a relative path
                                    (relative to pathHandler.HDF_DIR)

    Returns:
    The file hierarchy (as a string)
    """

    with openFile(file_name, mode='r', use_abs_path=use_abs_path) as f:
        return str(f)

def extractDataFromObject(obj):
    """
    Extracts data from an object and returns the data as a list of dictionaries.
    
    Parameters:
    - obj            (object)     - An object (or a single variable)
    
    Returns:
    A list of dictionaries containing the data from the object in a format that
    is used throughout this module (see the write method)
    """
    
    # Initializes the list of variables
    variables = []
    
    # If the provided "object" is actually a single variable, such as a simple
    # list, then a Bundle object is used to represent it
    if not hasattr(obj, '__dict__'):
        b = bundle.Bundle()
        b.value = obj
        obj = b
    
    # Defines a function that can store a value given a name
    # noinspection PyUnusedLocal
    def storeValue(cur_name, cur_value, var_list):
        
        # If the current variable has a __dict__ attribute, then this method
        # is called recursively on the current variable to obtain the list of
        # variables that it contains. These variable names are appended (at the
        # front) with the name of the current variable to specify that they
        # were obtained recursively.
        if hasattr(cur_value, '__dict__'):
            sub_vars = extractDataFromObject(cur_value)
            for sub_var in sub_vars:
                sub_var['name'] = cur_name + '/' + sub_var['name']
            var_list += sub_vars

        # Otherwise, the current variable is added to the list of variables
        # using the appropriate format
        else:
            var_list.append(createDictFromValue(cur_name, cur_value))
    
    # Loops through each variable in the object
    for name, value in vars(obj).items():

        # If the current variable is a dict, it is handled appropriately
        if type(value) is dict:
            for key, val in value.items():
                storeValue(name + DICT_IDENTIFIER + str(key), val, variables)
        
        # Otherwise, the storeValue function is called to store the item
        else:
            storeValue(name, value, variables)

    # Returns the list of variables
    return variables

def createDictFromValue(name, value):
    """  
    Creates a dictionary given a value and its name. This dictionary is
    specified to be compatible with the h5py.File.create_dataset method.
    
    Parameters:
    - name           (string)   - The name of the variable
    - value          (variable) - The value of the variable
    
    Returns:
    A dictionary of the appropriate format
    """
    
    return {'name': name, 'dtype': type(value), 'shape': np.shape(value),
            'data': value}

def addVar(obj, loc, value):
    """
    Adds a value to an object given a desired location.
    """

    cur_ref = obj
    locs = loc.split('/')
    for cur_loc in locs[:-1]:
        if cur_loc != '':
            cur_ref = getattr(cur_ref, cur_loc)
    setattr(cur_ref, locs[-1], value)

def openFile(file_name, mode = 'r', use_abs_path = False):
    """
    Opens an existing or creates a hdf5 file.
    
    Parameters:
    - file_name      (string)   - The desired file name
    - mode           (string)   - The mode in which the file will be opened.
    - use_abs_path   (bool)     - Specifies whether or not the provided file
                                  name is an absolute path or a relative path
                                  (relative to pathHandler.HDF_DIR)
    
    Returns:
    The hdf5 file (as a tables.file.File object)
    """
    
    # Determines the desired path
    desired_path = file_name if use_abs_path else pathHandler.getHDF(file_name)

    # Returns the opened HDF file
    return tables.open_file(desired_path, mode)

def saveNext(data, parent_path, make_dir = True, use_abs_path = False):
    """
    Saves data to a hdf5 file that is part of a numerically-named sequence
    of hdf5 files within a specified directory.

    Parameters:
    - data           (variable) - The data to save (could be an object,
                                  array, list, int, etc.)
    - parent_path    (string)   - The path to the parent directory containing
                                  the sequenced files. This path should either
                                  be relative to the hdf directory or absolute.
    - make_dir       (bool)     - Specifies what should be done in the event
                                  that the directory specified by the provided
                                  provided path does not exist. If this is
                                  True, the directory will be made in that
                                  event. Otherwise, an IOError will be raised.
    - use_abs_path   (bool)     - Specifies whether or not the provided file
                                  name is an absolute path or a relative path
                                  (relative to pathHandler.HDF_DIR)
    """

    # Determines the absolute path to the desired directory
    abs_path = parent_path if use_abs_path else pathHandler.getHDF(parent_path)

    # If the desired directory does not exist, then it is either created or
    # an IOError is raised
    if not os.path.exists(abs_path):
        if make_dir:
            os.makedirs(abs_path)
        else:
            raise IOError('Desired directory does not exist.')

    # Finds the next appropriate file path in the directory
    file_name = pathHandler.getNextFileName(abs_path)

    # Saves the provided data to the determined file path
    save(data, file_name=os.path.join(abs_path, file_name), use_abs_path=True)

def getAllFileNames(include_ext = False):
    """
    Gets a list of all of the .hdf5 file names in the HDF directory.

    Parameters:
    - include_ext    (bool)     - Specifies whether or not to include the
                                  extensions in the returned file names

    Returns:
    A list of strings containing the file names
    """

    _, _, file_names = os.walk(pathHandler.HDF_DIR).next()
    if include_ext:
        return file_names
    else:
        return [s[:s.rfind('.')] for s in file_names]


