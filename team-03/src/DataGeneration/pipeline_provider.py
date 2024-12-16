# Class which provides pipelined data generation
import numpy as np

class Pipeline():
    def __init__(self, functions:list, stash_result:bool=False, ignore_exceptions:bool=False) -> None:
        self.__is_stashing_result = stash_result
        self.__stashed_result = []
        self.__methods = functions

        self.__ignore_exceptions = ignore_exceptions
        self.__was_exception = False
        pass

    def __stash_result(self, result) -> None:
        if type(result) == list:
            self.__stashed_result += result
        else:
            self.__stashed_result.append(result)
        return

    def __run_pipeline_func(self, current_method_idx:int=0, *args) -> None:
        # TODO : test this part of code for correct behavior
        # try:
        #     result = self.__methods[current_method_idx](*args)
        # except Exception as e:
        #     self.__was_exception = not self.__ignore_exceptions
        #     return
        
        result = self.__methods[current_method_idx](*args)

        if current_method_idx == len(self.__methods) - 1:
            if self.__is_stashing_result:
                self.stast_result(result)
            return

        if type(result) == list:
            for res_element in result:
                if type(res_element) == np.ndarray:
                    res_element = [res_element]
                
                self.__run_pipeline_func(current_method_idx + 1, *res_element)
                if self.__was_exception and (not self.__ignore_exceptions):
                    break
        else:
            if type(result) == np.ndarray:
                result = [result]
            self.__run_pipeline_func(current_method_idx + 1, *result)
            
        return

    def __call__(self, *args):
        self.__was_exception = False
        self.__run_pipeline_func(0, *args)
        return self.__stashed_result if self.__is_stashing_result else None
