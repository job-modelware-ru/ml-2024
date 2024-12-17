import typing as tp

import numpy as np

# Class which store chunk information
class ImageChunk:
    def __init__(self, 
        img_source : np.ndarray, 
        row_start : int, 
        col_start : int,

        layers : int, 
        chunk_size : int, 
        offset_size : int, 
        
        row_offset_begin : int, 
        row_offset_end : int, 
        
        col_offset_begin : int, 
        col_offset_end : int):
        
        self.__chunk_data = np.zeros(shape=[layers, chunk_size + 2 * offset_size, chunk_size + 2 * offset_size])
        self.__chunk_data[:, offset_size - col_offset_begin : offset_size + chunk_size + col_offset_end, offset_size - row_offset_begin : offset_size + chunk_size + row_offset_end] = img_source[:, col_start - col_offset_begin : (col_start + chunk_size + col_offset_end), row_start - row_offset_begin : (row_start + chunk_size + row_offset_end)]

        self.row_start = row_start
        self.col_start = col_start
        
        self.layers = layers
        self.rows = chunk_size
        self.cols = chunk_size
        self.__offset = offset_size

        self.shape = self.__chunk_data.shape
        self.__data_layers = layers
        self.__data_rows = chunk_size + 2 * offset_size
        self.__data_cols = chunk_size + 2 * offset_size

        self.__row_offset_begin = row_offset_begin
        self.__row_offset_end = row_offset_end
        self.__col_offset_begin = col_offset_begin
        self.__col_offset_end = col_offset_end
        
        return

    def set_chunk_data(self, data : np.ndarray):
        if data.shape != self.shape:
            raise ValueError("ImageChunk 'set_chunk_data' error: shapes dont match!")
        else:
            self.__chunk_data = data
        return
    
    def get_data(self) -> np.ndarray:
        return self.__chunk_data

    def get_chunk_without_offset(self) -> np.ndarray:
        chunk_without_offset = self.__chunk_data[:, self.__offset : self.__data_cols - self.__offset, self.__offset : self.__data_rows - self.__offset]
        return chunk_without_offset

# class which provides separating images into chunks and conclusion from chunks
class BigImageManager:
    # constructor
    def __init__(self, 
        img : np.ndarray, 
        chunk_size_border : int, 
        offset_size: int, 
        layers_count : int):

        # original image data
        self.__img = img
        self.__img_layers = img.shape[0]
        self.__img_cols = img.shape[1]
        self.__img_rows = img.shape[2]

        # inflated image data (we work with it)
        is_need_to_inflate = False
        self.__inflated_rows = self.__img_rows
        if self.__img_rows % chunk_size_border != 0:
            new_rows = chunk_size_border - self.__img_rows % chunk_size_border
            self.__inflated_rows = self.__inflated_rows + new_rows
            is_need_to_inflate = True

        self.__inflated_cols = self.__img_cols
        if self.__img_cols % chunk_size_border != 0:
            new_cols = chunk_size_border - self.__img_cols % chunk_size_border
            self.__inflated_cols = self.__inflated_cols + new_cols
            is_need_to_inflate = True

        self.__inflated_layers = self.__img_layers
        if self.__img_layers % layers_count != 0:
            new_layers = layers_count - self.__img_layers % layers_count
            self.__inflated_layers = self.__inflated_layers + new_layers
            is_need_to_inflate = True

        if not is_need_to_inflate:
            self.__inflated_img = self.__img
        else:
            self.__inflated_img = np.zeros(shape=[self.__inflated_layers, self.__inflated_cols, self.__inflated_rows])
            self.__inflated_img[0 : self.__img_layers, 0 : self.__img_cols, 0 : self.__img_rows] = self.__img[:, :, :]

        self.__chunk_size_border = chunk_size_border
        self.__offset_size = offset_size
        self.__layers_count = layers_count
        return

    # method which provides splitting image into chunks
    def split_in_chunks(self) -> tp.List[ImageChunk]:
        chunks_list = []
        
        row_start = 0
        col_start = 0

        # Trying to go all chunks in rows in outer 'while True' loop 
        while True:
            # Trying to go all chunks in current row in inner 'while True' loop 
            while True:
                # chunk sizes init
                chunk_row_start = row_start
                chunk_col_start = col_start
                chunk_rows = min(self.__inflated_rows - chunk_row_start, self.__chunk_size_border)
                chunk_cols = min(self.__inflated_cols - chunk_col_start, self.__chunk_size_border)

                # offsets init
                chunk_row_offset_begin = 0 if chunk_row_start - self.__offset_size < 0 else self.__offset_size
                chunk_row_offset_end = 0 if chunk_row_start + chunk_rows == self.__inflated_rows else self.__offset_size
                chunk_col_offset_begin = 0 if chunk_col_start - self.__offset_size < 0 else self.__offset_size
                chunk_col_offset_end = 0 if chunk_col_start + chunk_cols == self.__inflated_cols else self.__offset_size

                # Generate new chunk
                new_chunk = ImageChunk(self.__inflated_img, 
                    chunk_row_start, chunk_col_start, self.__inflated_layers, 
                    self.__chunk_size_border, self.__offset_size, 
                    chunk_row_offset_begin, chunk_row_offset_end, chunk_col_offset_begin, chunk_col_offset_end)
                chunks_list.append(new_chunk)

                # If we need to stop process this row -> leave; else -> continue chunk separating
                if (chunk_col_start + chunk_cols == self.__inflated_cols):
                    break
                else:
                    col_start = col_start + self.__chunk_size_border

            # If we need to stop process this image -> leave; else -> continue chunk separating
            if (chunk_row_start + chunk_rows == self.__inflated_rows):
                break
            else:
                row_start = row_start + self.__chunk_size_border
                col_start = 0

        return chunks_list

    # Method which concatenate chunks into one big image
    def concatenate_chunks_into_image(
        self, 
        chunks_list:tp.List[ImageChunk]
        ) -> np.ndarray:

        new_img_inflate = np.zeros(shape=[self.__inflated_layers, self.__inflated_cols, self.__inflated_rows])

        for chunk in chunks_list:
            chunk_without_offset = chunk.get_chunk_without_offset()
            new_img_inflate[:, chunk.col_start : (chunk.col_start + chunk.cols), chunk.row_start : (chunk.row_start + chunk.rows)] = chunk_without_offset[:, :, :]

        new_img = new_img_inflate[0 : self.__img_layers, 0 : self.__img_cols, 0 : self.__img_rows]
        return new_img
