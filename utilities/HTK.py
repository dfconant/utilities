#-------------------------------------------------------------------------------
# Name:        HTK
# Purpose:     To interact with .htk files
#
# Author:      David Moses
#
# Created:     Dec 10, 2013
# Copyright:   (c) David Moses 2013
#-------------------------------------------------------------------------------

import os
import numpy as np

import pathHandler
import hdfHandler

# In the MATLAB function named writeHTK, the sampling rate is multiplied by a
# scaling factor before being written to the file. The reason for doing this is
# unknown. That scaling factor is stored here as a static variable for
# conversion from what the file specifies as the sampling rate into the actual
# sampling rate (in Hz), assuming that the scaling factor was applied during
# the HTK file construction.
SAMPLING_RATE_FACTOR = 1e4

def readHTK(file_name, data_type = 'HTK', big_endian = True,
            scale_s_rate = True):
    """
    Reads data from a HTK file
    
    Parameters:
    - file_name     (string)  - The HTK file name
    - data_type     (string)  - Specifies the data type (view getFilePath for
                                more details)
    - big_endian    (Boolean) - Specifies whether or not the data is big endian
                                (if False, then the data is little endian)
    - scale_s_rate  (Boolean) - Specifies whether or note to divide the sampling
                                rate specified by the HTK file by the sampling
                                rate scaling factor
    
    Returns:
    A dictionary containing the data from the file
    """
    
    # Creates the endian variable that will be used when specifying data types
    if big_endian:
        endian = '>'
    else:
        endian = '<'
    
    # Obtains the full file path, which depends on the data type
    #file_path = getFilePath(file_name, data_type)
    
    # Opens the HTK file
    #print(file_name)
    with open(file_name, 'rb') as f:
    
        # Reads values from the header
        num_samples    = np.fromfile(f, dtype=endian+'i4', count=1)[0]
        sampling_rate  = np.fromfile(f, dtype=endian+'i4', count=1)[0]
        sample_size    = np.fromfile(f, dtype=endian+'i2', count=1)[0]
        parameter_kind = np.fromfile(f, dtype=endian+'i2', count=1)[0]

        # Reads the data
        data = np.fromfile(f, dtype=endian+'f4').reshape((num_samples, -1)).T
    
    # Scales the sampling rate (if desired)
    if scale_s_rate:
        sampling_rate = float(sampling_rate) / SAMPLING_RATE_FACTOR
        
    # Returns a dictionary containing the data from the file
    return {'num_samples':    num_samples,
            'sampling_rate':  float(sampling_rate),
            'sample_size':    sample_size, 
            'parameter_kind': parameter_kind,
            'data':           data}

def toHTK(file_data, file_name, data_type = 'HTK', big_endian = True,
          scale_s_rate = False):
    """
    Writes data to a HTK file.
    
    Parameters:
    - file_data     (dict)    - A dictionary containing the following items:
                                - 'num_samples'    : The number of samples
                                - 'sampling_rate'  : The sampling rate (in Hz)
                                - 'sample_size'    : Unknown
                                - 'parameter_kind' : Unknown
                                - 'data'           : The data points
                                The sample size and parameter kind items are
                                optional; the others are required.
    - file_name     (string)  - The HTK file name
    - data_type     (string)  - Specifies the data type (view getFilePath for
                                more details)
    - big_endian    (Boolean) - Specifies whether or not the data is big endian
                                (if False, then the data is little endian)
    - scale_s_rate  (Boolean) - Specifies whether or note to multiply the
                                sampling rate specified by the HTK file by the
                                sampling rate scaling factor
    """
    
    # Creates the endian variable that will be used when specifying data types
    if big_endian:
        endian = '>'
    else:
        endian = '<'
    
    # Obtains the full file path, which depends on the data type
    file_path = getFilePath(file_name, data_type)

    # Obtains relevant values from the file data dictionary. If the sample
    # size or the parameter kind keys are not in the dictionary, then
    # arbitrary values are used.
    num_samples   = file_data['num_samples']
    sampling_rate = file_data['sampling_rate']
    data          = file_data['data']
    
    try:
        sample_size = file_data['sample_size']
    except KeyError:
        sample_size = 0
        
    try:
        parameter_kind = file_data['parameter_kind']
    except KeyError:
        parameter_kind = 8971
    
    # Scales the sampling rate (if desired)
    if scale_s_rate:
        sampling_rate = float(sampling_rate) * SAMPLING_RATE_FACTOR
            
    # Opens the HTK file
    with open(file_path, 'wb') as f:
        
        # Writes the header values
        np.array(num_samples,    dtype=endian+'i4').tofile(f)
        np.array(sampling_rate,  dtype=endian+'i4').tofile(f)
        np.array(sample_size,    dtype=endian+'i2').tofile(f)
        np.array(parameter_kind, dtype=endian+'i2').tofile(f)
        
        # Writes the data
        np.array(data, dtype=endian+'f4').T.tofile(f)

def getFilePath(file_name, data_type = 'HTK'):
    """
    Obtains a full file path given the file name and the data type.
    
    Parameters:
    - file_name     (string)  - The HTK file name (which should be in the
                                directory specified by util.pathHandler.HTK_DIR)
    - data_type     (string)  - Specifies the data type, which will determine
                                what directory is searched for the file. Valid
                                options are:
                                - HTK    - The HTK directory 
                                - post   - The actual posteriogram directory
                                - raw    - The raw data directory
                                - other  - The directory specified in the file
                                           name (file_name is an absolute path)
                                - no_ext - The same as the option 'other',
                                           except the extension isn't ensured
                                - h_no_x - The same as 'HTK', except with
                                           no extension
    
    Returns:
    The absolute file path (as a string), after ensuring that it ends in '.htk'
    """
    
    if   data_type   == 'HTK':
        return pathHandler.getHTK(file_name)
    elif data_type == 'post':
        return pathHandler.getActualPosteriogram(file_name)
    elif data_type == 'raw':
        return pathHandler.getRawHTK(file_name)
    elif data_type == 'other':
        return pathHandler.ensureExtension(file_name, 'htk')
    elif data_type == 'no_ext':
        return file_name
    elif data_type   == 'h_no_x':
        return pathHandler.getHTK(file_name).replace('.htk', '')
    else:
        raise Exception('An invalid data type was specified.')
    
def createHTKFromHDF(hdf_file, htk_file):
    """
    Creates a htk file from the contents of a hdf5 file.
    """
    
    # Loads the hdf file
    hdf_data = hdfHandler.load(hdf_file)
    
    # Obtains the data and sampling rate from the hdf data
    sampling_rate = hdf_data.sampling_rate
    try:
        data = hdf_data.data
    except AttributeError:
        data = hdf_data.post
    
    # Determines the number of samples from the hdf data
    num_samples = data.shape[1]
    
    # Creates a file data dictionary for the current data
    file_data = {'sampling_rate': sampling_rate,
                 'num_samples'  : num_samples,
                 'data'         : data}
    
    # Writes the file data to the desired file
    toHTK(file_data, htk_file, data_type='other')
    
def createHTKDirFromHDFDir(hdf_dir, htk_dir):
    """
    For each hdf5 file in a specified directory, a htk file is created in a
    different directory using the contents of that hdf5 file.
    """
    
    # Creates the specified htk_dir if desired
    os.makedirs(htk_dir, exist_ok=True)
    
    # Finds all files in the hdf5 directory
    for _, _, filenames in os.walk(hdf_dir):
        for file_name in filenames:
            file_name = file_name.replace('.hdf5', '')
            createHTKFromHDF(os.path.join(hdf_dir, file_name),
                             os.path.join(htk_dir, file_name))
