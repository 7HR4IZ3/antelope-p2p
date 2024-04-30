export class SerialBuffer {

    /**
     * The data buffer.
     * @type {Buffer}
     */
    data;

    /**
     * The current offset in the buffer.
     * @type {number}
     */
    #offset = 0;


    textEnc = new TextEncoder();
    textDec = new TextDecoder();

    constructor(data) {
        this.data = data;
    }

    get offset() {
        return this.#offset;
    }

    get filled() {
        // console.log(this.#offset)
        return this.data.subarray(0, this.#offset);
    }

    /**
     * Reads an 8-bit unsigned integer from the buffer and advances the offset by 1 byte.
     *
     * @return {number} The 8-bit unsigned integer read from the buffer.
     */
    readUint8() {
        const value = this.data[this.#offset];
        console.log(this.#offset)
        this.#offset += 1;
        return value;
    }


    /**
     * Reads a 32-bit unsigned integer from the buffer and advances the offset by 4 bytes.
     *
     * @return {number} The 32-bit unsigned integer read from the buffer.
     */
    readUint32() {
        const value = this.data.readUInt32LE(this.#offset);
        this.#offset += 4;
        return value;
    }


    /**
     * Reads a 64-bit unsigned integer from the data buffer and advances the offset by 8 bytes.
     *
     * @returns {BigInt} The 64-bit unsigned integer read from the buffer.
     */
    readUint64() {
        const value = this.data.readBigUInt64LE(this.#offset);
        this.#offset += 8;
        return value;
    }

    writeUInt16(number) {
        this.data.writeUInt16LE(number, this.#offset);
        this.#offset += 2;
    }

    /**
     * Writes a buffer to the data buffer.
     * @param buffer {Buffer} - The buffer to write
     */
    writeBuffer(buffer) {
        buffer.copy(this.data, this.#offset);
        this.#offset += buffer.length;
    }

    /**
     * Writes an array of 8-bit unsigned integers to the buffer.
     * @param array {Uint8Array} - The array to write
     * @return {void}
     */
    writeUint8Array(array) {
        const buffer = Buffer.from(array);
        // this.data.writeUInt32LE(buffer.length, this.#offset);
        // this.#offset += 4;
        buffer.copy(this.data, this.#offset);
        this.#offset += buffer.length;
    }

    writeUInt64(number) {
        this.data.writeBigUInt64LE(number, this.#offset);
        this.#offset += 8;
    }

    writeUInt32(number) {
        this.data.writeUInt32LE(number, this.#offset);
        this.#offset += 4;
    }

    writeUInt8(number) {
        this.data[this.#offset] = number;
        this.#offset += 1;
    }

    /**
     * Writes a string to the buffer.
     * @param text {string} - The string to write
     * @return {void}
     */
    writeString(text) {
        const bytes = this.textEnc.encode(text);
        const buffer = Buffer.from(bytes);
        this.writeVarUInt32(buffer.length, this.#offset);
        buffer.copy(this.data, this.#offset);
        this.#offset += buffer.length;
    }

    /**
     * Writes a variable length unsigned 32-bit integer to the buffer.
     * @param value {number} - The value to write
     * @return {void}
     */
    writeVarUInt32(value) {
        while (true) {
            if (value >>> 7) {
                this.writeUInt8(0x80 | (value & 0x7f));
                value = value >>> 7;
            } else {
                this.writeUInt8(value);
                break;
            }
        }
    }

    /**
     * Reads a variable length unsigned 32-bit integer from the buffer.
     * @return {number}
     */
    readVarUInt32() {
        let v = 0;
        let bit = 0;
        while (true) {
            const b = this.readUint8();
            v |= (b & 0x7f) << bit;
            bit += 7;
            if (!(b & 0x80)) {
                break;
            }
        }
        return v >>> 0;
    }

    /**
     * Reads an array of 8-bit unsigned integers
     * @param number - The number of bytes to read
     * @return {Buffer}
     */
    readUInt8Array(number) {
        const array = this.data.subarray(this.#offset, this.#offset + number);
        this.#offset += number;
        return array;
    }

    readUint16() {
        const value = this.data.readUInt16LE(this.#offset);
        this.#offset += 2;
        return value;
    }

    /**
     * Reads a string from the buffer.
     * @return {string}
     */
    readString() {
        const length = this.readVarUInt32();
        const buffer = this.data.subarray(this.#offset, this.#offset + length);
        this.#offset += length;
        return this.textDec.decode(buffer);
    }
}
