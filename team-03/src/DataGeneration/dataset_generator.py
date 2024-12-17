# Class which provides managment data generation
import os
import numpy as np
import json
import h5py

from image_processing import *
from utils import *
import typing as tp

class DatasetGenerator():
    # Constants for inner logic
    DATA_LENGTH_FIELD = "size"          # For size field in *.hdf5 file
    DATA_SHAPE_FIELD = "data_shape"     # For shape field in *.hdf5 file
    X_DATA_PREFIX = "X_"                # For input data in *.hdf5 file
    Y_DATA_PREFIX = "Y_"                # For true data in *.hdf5 file
    HDF5_FORMAT = ".hdf5"
    INFO_FILE_NAME = "info.json"

    # Constants for json data
    DATA_NAME_FIELD = "name"
    DATA_DESCRIPTION_FILED = "description"
    
    def __init__(self, 
                dataset_name : str, 
                data_shape : tuple,
                data_description : str = "none.",
                is_supervised : bool = True,
                path : str = "./"):

        # Generate folder for data
        self.__dataset_path = os.path.join(path, dataset_name) 
        if os.path.isdir(self.__dataset_path) == False:
            os.mkdir(self.__dataset_path)

        # Save variables
        self.__dataset_name = dataset_name    
        self.__data_description = data_description
        self.__data_shape = data_shape
        self.__total_length = 0
        self.__is_supervised = is_supervised

        # Init hdf5 file
        self.__hdf5_path = os.path.join(self.__dataset_path, dataset_name + self.HDF5_FORMAT)
        self._fh = h5py.File(self.__hdf5_path, "w")
        self._fh[self.DATA_LENGTH_FIELD] = self.__total_length
        self._fh[self.DATA_SHAPE_FIELD] = self.__data_shape
        pass


    def append(self, 
            x_data : np.ndarray,
            y_data : np.ndarray = None) -> None:

        if self.__is_supervised == True and y_data is None:
            raise Exception("No y_data for supervised dataset")

        if False in np.equal(x_data.shape, self._fh[self.DATA_SHAPE_FIELD][()]) or False in np.equal(y_data.shape, self._fh[self.DATA_SHAPE_FIELD][()]):
            raise Exception("Bad input image shape")

        self._fh.create_dataset(self.X_DATA_PREFIX+str(self.__total_length), data=x_data)
        self._fh.create_dataset(self.Y_DATA_PREFIX+str(self.__total_length), data=y_data)
        self.__total_length += 1
        
        self._fh[self.DATA_LENGTH_FIELD][...] = self.__total_length
        self.dump_data_info()
        return


    def dump_data_info(self):
        # Dump json with dataset info for readablility
        data_info = {
            self.DATA_NAME_FIELD : self.__dataset_name,
            self.DATA_DESCRIPTION_FILED : self.__data_description,
            self.DATA_SHAPE_FIELD : self.__data_shape,
            self.DATA_LENGTH_FIELD : self.__total_length,
        }

        json_path = os.path.join(self.__dataset_path, self.INFO_FILE_NAME)
        with open(json_path, 'w') as jf:
            json.dump(data_info, jf)
        return


    def close(self):
        self._fh.close()
        return


    def __del__(self):
        self._fh.close()
        pass

