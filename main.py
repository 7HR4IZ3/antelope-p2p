import socket
import threading
import struct
from serial_buffer import SerialBuffer
from utils import nanoseconds

class AntelopeNetClient:
    def __init__(self, peer, chain_id):
        self.peer = peer
        self.chain_id = chain_id
        self.socket = None
        self.handshake = False
        self.head_block_num = 0
        self.lib_block_num = 0
        self.heartbeat_interval = 20  # in seconds
        self.heartbeat_timer = None

    def connect(self):
        host, port = self.peer.split(':')
        self.socket = socket.create_connection((host, int(port)))
        self.attach_listeners()

    def attach_listeners(self):
        threading.Thread(target=self.receive_messages).start()

    def receive_messages(self):
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                self.handle_net_message(data)
        finally:
            print('Connection closed')
            if self.heartbeat_timer:
                self.heartbeat_timer.cancel()
                self.heartbeat_timer = None

    def handle_net_message(self, data):
        buffer = SerialBuffer(data)
        message_length = buffer.read_uint32()
        message_type = buffer.read_uint8()
        print(f'Received message type {message_type} with {message_length} bytes')

         # Log the raw data for debugging (convert bytes to hex for readability)
        self.log(f'Raw message data: {data.hex()}')

        if message_type == 0:  # handshake_message
            self.log('handshake_message')
            peer_handshake = {
                'networkVersion': buffer.read_uint16(),
                'chainId': buffer.read_uint8_array(32).hex(),
                'nodeID': buffer.read_uint8_array(32).hex(),
                'keyType': buffer.read_uint8(),
                'publicKey': buffer.read_uint8_array(33).hex(),
                'time': buffer.read_uint64(),
                'token': buffer.read_uint8_array(32).hex(),
                'signatureType': buffer.read_uint8(),
                'signature': buffer.read_uint8_array(65).hex(),
                'p2pAddress': buffer.read_string(),
                'libBlockNum': buffer.read_uint32(),
                'libBlockId': buffer.read_uint8_array(32).hex(),
                'headBlockNum': buffer.read_uint32(),
                'headBlockId': buffer.read_uint8_array(32).hex(),
                'os': buffer.read_string(),
                'agent': buffer.read_string(),
                'generation': buffer.read_uint16(),
            }

            if peer_handshake['chainId'] != self.chain_id:
                self.log('Chain ID mismatch')
                self.socket.close()
                return

            self.head_block_num = peer_handshake['headBlockNum']
            self.lib_block_num = peer_handshake['libBlockNum']

            info = {
                'generation': peer_handshake['generation'],
                'networkVersion': peer_handshake['networkVersion'],
                'head': peer_handshake['headBlockNum'],
                'lib': peer_handshake['libBlockNum'],
                'time': peer_handshake['time'],
                'agent': peer_handshake['agent'],
                'p2pAddress': peer_handshake['p2pAddress'],
            }
            print(info)

        elif message_type == 1:  # chain_size_message
            self.log('chain_size_message')
            chain_size_message = {}

        elif message_type == 2:  # go_away_message
            self.log('go_away_message')
            print(data)

        elif message_type == 3:  # time_message
            self.log('time_message')
            time_message = {
                'org': buffer.read_uint64(),
                'rec': buffer.read_uint64(),
                'xmt': buffer.read_uint64(),
                'dst': buffer.read_uint64(),
            }
            self.log('xmt:', time_message['xmt'])
            if not self.handshake:
                self.perform_handshake()

        elif message_type == 4:  # notice_message
            self.log('Notice Message')
            notice_message = {
                'known_trx': {
                    'mode': buffer.read_uint32(),
                    'pending': buffer.read_uint32(),
                    'ids': []
                },
                'known_blocks': {
                    'mode': buffer.read_uint32(),
                    'pending': buffer.read_uint32(),
                    'ids': []
                }
            }
            arr_len = buffer.read_var_uint32()
            for _ in range(arr_len):
                id = buffer.read_uint8_array(32)
                notice_message['known_trx']['ids'].append(id.hex())

            arr_len2 = buffer.read_var_uint32()
            for _ in range(arr_len2):
                id = buffer.read_uint8_array(32)
                notice_message['known_blocks']['ids'].append(id.hex())

            self.log(notice_message)

        else:
            self.log('Unknown message type:', message_type)


    def log(self, *args):
        print(f"[{self.peer}]", *args)

    def perform_handshake(self):

        body = SerialBuffer(bytearray(512))
        print("Buffer starting:", body.data.hex())

        # Network version (uint16)
        body.write_uint16(1212)

        # Chain ID (32 bytes)
        body.write_buffer(bytearray.fromhex(self.chain_id))

        # Node ID (32 bytes)
        body.write_buffer(bytearray([0]*32))  # Placeholder for random bytes

        body.write_uint8(0)  # Public key type (K1 type = 0)
        print("Buffer after writing public key type:", body.data.hex())
        body.write_buffer(bytearray(33))  # Public key data (33 zero bytes)
        print("Buffer after writing public key data:", body.data.hex())


        # Message Time (uint64)
        body.write_uint64(nanoseconds())

        # Token (32 bytes)
        body.write_buffer(bytearray([0]*32))

        # Signature (65 bytes)
        body.write_buffer(bytearray([0]*65))

        # P2P Address (string)
        body.write_string('127.0.0.1:9876')

        # LIB Block Num (uint32)
        body.write_uint32(0)

        # LIB Block ID (32 bytes)
        body.write_buffer(bytearray([0]*32))

        # Head Block Num (uint32)
        body.write_uint32(0)

        # Head Block ID (32 bytes)
        body.write_buffer(bytearray([0]*32))

        # OS (string)
        body.write_string('Linux')

        # Agent (string)
        body.write_string('Ghostbusters')

        # Generation (uint16)
        body.write_uint16(1)

        header = SerialBuffer(bytearray(5))
        header.write_uint32(len(body.data) + 1)
        header.write_uint8(0)

        message = header.data + body.data
        print("Final handshake message:", message.hex())
        try:
            self.socket.send(message)
            # existing code to build and send the handshake message
            self.log("Handshake message sent")
        except Exception as e:
            self.log(f"Error during handshake: {e}")
        finally:
            self.log("Handshake method completed")
            self.handshake = True

    def send_time_message(self):
        body = SerialBuffer(bytearray(4 * 8))
        body.write_uint64(0)
        body.write_uint64(0)
        body.write_uint64(nanoseconds())
        body.write_uint64(0)

        header = SerialBuffer(bytearray(5))
        header.write_uint32(len(body.data) + 1)
        header.write_uint8(3)
        message = header.data + body.data
        self.socket.send(message)

    def start_heartbeat(self):
        self.heartbeat_timer = threading.Timer(self.heartbeat_interval, self.send_time_message)
        self.heartbeat_timer.start()

test_client = AntelopeNetClient("waxp2p.sentnl.io:9876", '1064487b3cd1a897ce03ae5b6a865651747e2e152090f99c1d19d44e01aea5a4')
test_client.connect()