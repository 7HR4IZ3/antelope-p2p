import struct

class SerialBuffer:
    def __init__(self, data):
        self.data = bytearray(data)
        self.__offset = 0
    
    @property
    def filled(self):
        print(self.__offset)
        return bytearray(self.data[0:self.__offset])
    
    @property
    def offset(self):
        return self.__offset

    def read_uint8(self):
        value = self.data[self.__offset]
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
        # if self.__offset < len(self.data):
        self.data[self.__offset] = number
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
