
# class SerialBuffer:
#   """
#   A class to represent a serial buffer for reading and writing data.
#   """

#   def __init__(self, data):
#     """
#     Initializes the SerialBuffer with the provided data.

#     Args:
#       data: A bytearray object representing the data buffer.
#     """
#     self.data = bytearray(data)
#     self.offset = 0

#   @property
#   def filled(self):
#     """
#     Returns a bytearray containing the data from the beginning of the buffer
#     up to the current offset.
#     """
#     return self.data[:self.offset]

#   def read_uint8(self):
#     """
#     Reads an 8-bit unsigned integer from the buffer and advances the offset by 1 byte.

#     Returns:
#       The 8-bit unsigned integer read from the buffer.
#     """
#     value = self.data[self.offset]
#     self.offset += 1
#     return value

#   def read_uint32(self):
#     """
#     Reads a 32-bit unsigned integer from the buffer and advances the offset by 4 bytes.

#     Returns:
#       The 32-bit unsigned integer read from the buffer.
#     """
#     value = int.from_bytes(self.data[self.offset:self.offset+4], byteorder='little', signed=False)
#     self.offset += 4
#     return value

#   def read_uint64(self):
#     """
#     Reads a 64-bit unsigned integer from the buffer and advances the offset by 8 bytes.

#     Returns:
#       The 64-bit unsigned integer read from the buffer.
#     """
#     value = int.from_bytes(self.data[self.offset:self.offset+8], byteorder='little', signed=False)
#     self.offset += 8
#     return value


#   def write_buffer(self, buffer):
#       end_offset = self.offset + len(buffer)
#       if end_offset <= len(self.data):
#           self.data[self.offset:end_offset] = buffer
#           self.offset = end_offset
  
#   def write_uint8_array(self, array):
#       self.write_buffer(bytearray(array))

#   def write_uint8(self, number):
#       # # if self.offset < len(self.data):
#       # self.data[self.offset] = number
#       # self.offset += 1
#       struct.pack_into('<B', self.data, self.offset, number)
#       self.offset += 1


#   def write_uint16(self, number):
#       struct.pack_into('<H', self.data, self.offset, number)
#       self.offset += 2

#   def write_uint32(self, number):
#       struct.pack_into('<I', self.data, self.offset, number)
#       self.offset += 4

#   def write_uint64(self, number):
#       struct.pack_into('<Q', self.data, self.offset, number)
#       self.offset += 8

#   def write_var_uint32(self, value):
#       while True:
#           if value >> 7:
#               self.write_uint8(0x80 | (value & 0x7f))
#               value = value >> 7
#           else:
#               self.write_uint8(value)
#               break

#   def write_string(self, text):
#       bytes_text = text.encode('utf-8')
#       self.write_var_uint32(len(bytes_text))
#       self.data[self.offset:self.offset + len(bytes_text)] = bytes_text
#       self.offset += len(bytes_text)

#   def read_var_uint32(self):
#     """
#     Reads a variable-length unsigned 32-bit integer from the buffer.

#     Returns:
#       The 32-bit unsigned integer read from the buffer.
#     """
#     v = 0
#     bit = 0
#     while True:
#       b = self.read_uint8()
#       v |= (b & 0x7f) << bit
#       bit += 7
#       if not (b & 0x80):
#         break
#     return v

#   def read_uint8_array(self, number):
#     """
#     Reads a specified number of bytes from the buffer and returns them as a bytearray.

#     Args:
#       number: The number of bytes to read.

#     Returns:
#       A bytearray containing the data read from the buffer.
#     """
#     array = self.data[self.offset:self.offset+number]
#     self.offset += number
#     return bytearray(array)

#   def read_uint16(self):
#     """
#     Reads a 16-bit unsigned integer from the buffer and advances the offset by 2 bytes.

#     Returns:
#       The 16-bit unsigned integer read from the buffer.
#     """
#     value = int.from_bytes(self.data[self.offset:self.offset+2], byteorder='little', signed=False)
#     self.offset += 2
#     return value

#   def read_string(self):
#     """
#     Reads a string from the buffer. The length of the string is prefixed with a variable-length
#     unsigned integer.

#     Returns:
#       The string read from the buffer.
#     """
#     length = self.read_var_uint32()
#     buffer = self.data[self.offset:self.offset+length]
#     self.offset += length
#     return buffer.decode('utf-8')


import struct

class SerialBuffer:
    def __init__(self, data):
        self.data = bytearray(data)
        self.__offset = 0
    
    @property
    def filled(self):
        # print(self.__offset)
        return bytearray(self.data[0:self.__offset])
    
    @property
    def offset(self):
        return self.__offset

    def read_uint8(self):
        value = self.data[self.__offset]
        print(self.__offset)
        self.__offset += 1
        return value

    def read_uint16(self):
        value = struct.unpack_from('<H', self.data, self.__offset)[0]
        self.__offset += 2
        return value

    def read_uint32(self):
        value = struct.unpack_from('<I', self.data, self.__offset)[0]
        self.__offset += 4
        return value

    def read_uint64(self):
        value = struct.unpack_from('<Q', self.data, self.__offset)[0]
        self.__offset += 8
        return value

    def read_var_uint32(self):
        v = 0
        bit = 0
        while True:
            b = self.read_uint8()
            v |= (b & 0x7f) << bit
            bit += 7
            if not (b & 0x80):
                break
        return v >> 0

    def read_string(self):
        length = self.read_var_uint32()
        value = self.data[self.__offset:self.__offset + length]
        self.__offset += length
        return value.decode('utf-8')


    def write_buffer(self, buffer):
        end_offset = self.__offset + len(buffer)
        if end_offset <= len(self.data):
            self.data[self.__offset:end_offset] = buffer
            self.__offset = end_offset
    
    def write_uint8_array(self, array):
        self.write_buffer(bytearray(array))

    def write_uint8(self, number):
        # # if self.__offset < len(self.data):
        # self.data[self.__offset] = number
        # self.__offset += 1
        struct.pack_into('<B', self.data, self.__offset, number)
        self.__offset += 1

    def write_uint16(self, number):
        struct.pack_into('<H', self.data, self.__offset, number)
        self.__offset += 2

    def write_uint32(self, number):
        struct.pack_into('<I', self.data, self.__offset, number)
        self.__offset += 4

    def write_uint64(self, number):
        struct.pack_into('<Q', self.data, self.__offset, number)
        self.__offset += 8

    def write_var_uint32(self, value):
        while True:
            if value >> 7:
                self.write_uint8(0x80 | (value & 0x7f))
                value = value >> 7
            else:
                self.write_uint8(value)
                break

    def write_string(self, text):
        bytes_text = text.encode('utf-8')
        self.write_var_uint32(len(bytes_text))
        self.data[self.__offset:self.__offset + len(bytes_text)] = bytes_text
        self.__offset += len(bytes_text)

    def read_var_uint32(self):
        v = 0
        bit = 0
        while True:
            b = self.read_uint8()
            v |= (b & 0x7f) << bit
            bit += 7
            if not (b & 0x80):
                break
        return v >> 0

    def read_uint8_array(self, number):
        array = self.data[self.__offset:self.__offset + number]
        self.__offset += number
        return array

    def read_uint16(self):
        value = struct.unpack_from('<H', self.data, self.__offset)[0]
        self.__offset += 2
        return value

    def read_string(self):
        length = self.read_var_uint32()
        value = self.data[self.__offset:self.__offset + length].decode('utf-8')
        self.__offset += length
        return value
