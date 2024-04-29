import {createConnection} from 'node:net';
import {randomBytes} from 'node:crypto';

import {SerialBuffer} from "./serial-buffer.mjs";
import {nanoseconds} from "./utils.mjs";

class AntelopeNetClient {

    #handshake = false;
    #peer;
    #socket;
    #xmt = null;

    #chainId;

    #headBlockNum = 0;
    #libBlockNum = 0;

    heartbeatInterval = 20000;
    heartbeatTimer = null;

    constructor(peer, chainId) {
        this.#peer = peer;
        this.#chainId = chainId;
    }

    connect() {
        const [host, port] = this.#peer.split(":");
        this.log(`Connecting...`);
        this.#socket = createConnection({host, port});
        this.attachListeners();
    }

    attachListeners() {
        this.#socket.on("connect", () => {
            this.log('Connected to peer');
            this.heartbeatTimer = setInterval(() => {
                this.sendTimeMessage();
            }, this.heartbeatInterval);
        });
        this.#socket.on("data", data => {
            this.handleNetMessage(data);
        });
        this.#socket.on('error', (err) => {
            console.log('Error:', err);
            if (this.heartbeatTimer) {
                clearTimeout(this.heartbeatTimer);
                this.heartbeatTimer = null;
            }
        });
        this.#socket.on('end', () => {
            console.log('Connection closed');
            if (this.heartbeatTimer) {
                clearTimeout(this.heartbeatTimer);
                this.heartbeatTimer = null;
            }
        });
    }


    /**
     * Handles a network message.
     *
     * @param {Buffer} data - The network message to be handled.
     *
     * @return {void}
     */
    handleNetMessage(data) {
        const buffer = new SerialBuffer(data);
        const messageLength = buffer.readUint32();
        const messageType = buffer.readUint8();
        this.log(`Received message type ${messageType} with ${messageLength} bytes`);

        switch (messageType) {

            // handshake_message
            case 0: {
                this.log('handshake_message');

                const peerHandshake = {
                    networkVersion: buffer.readUint16(),
                    chainId: buffer.readUInt8Array(32).toString('hex'),
                    nodeID: buffer.readUInt8Array(32).toString('hex'),
                    keyType: buffer.readUint8(),
                    publicKey: buffer.readUInt8Array(33).toString('hex'),
                    time: new Date(Number(buffer.readUint64() / BigInt(1000000))),
                    token: buffer.readUInt8Array(32).toString('hex'),
                    signatureType: buffer.readUint8(),
                    signature: buffer.readUInt8Array(65).toString('hex'),
                    p2pAddress: buffer.readString(),
                    libBlockNum: buffer.readUint32(),
                    libBlockId: buffer.readUInt8Array(32).toString('hex'),
                    headBlockNum: buffer.readUint32(),
                    headBlockId: buffer.readUInt8Array(32).toString('hex'),
                    os: buffer.readString(),
                    agent: buffer.readString(),
                    generation: buffer.readUint16(),
                };

                // check if the chain ID matches
                if (peerHandshake.chainId !== this.#chainId) {
                    this.log('Chain ID mismatch');
                    this.#socket.end();
                    return;
                }

                this.#headBlockNum = peerHandshake.headBlockNum;
                this.#libBlockNum = peerHandshake.libBlockNum;

                const info = {
                    generation: peerHandshake.generation,
                    networkVersion: peerHandshake.networkVersion,
                    head: peerHandshake.headBlockNum,
                    lib: peerHandshake.libBlockNum,
                    time: peerHandshake.time,
                    agent: peerHandshake.agent,
                    p2pAddress: peerHandshake.p2pAddress,
                };

                console.table(info);
                break;
            }

            // chain_size_message
            case 1: {
                this.log('chain_size_message');
                const chainSizeMessage = {}
                break;
            }

            // go_away_message
            case 2: {
                this.log('go_away_message');
                console.log(data);
                break;
            }

            // time_message
            case 3: {
                this.log('time_message');
                const timeMessage = {
                    org: buffer.readUint64(),
                    rec: buffer.readUint64(),
                    xmt: buffer.readUint64(),
                    dst: buffer.readUint64(),
                };
                this.#xmt = new Date(Number(timeMessage.xmt / BigInt(1000000)));
                this.log('xmt:', this.#xmt);
                if (!this.#handshake) {
                    this.performHandshake();
                }
                break;
            }
            // notice_message
            case 4: {
                this.log('Notice Message');
                const noticeMessage = {
                    known_trx: {
                        mode: undefined,
                        pending: undefined,
                        ids: []
                    },
                    known_blocks: {
                        mode: undefined,
                        pending: undefined,
                        ids: []
                    }
                };
                noticeMessage.known_trx.mode = buffer.readUint32();
                noticeMessage.known_trx.pending = buffer.readUint32();
                const arrLen = buffer.readVarUInt32();
                for (let i = 0; i < arrLen; i++) {
                    const id = Buffer.from(buffer.readUInt8Array(32));
                    noticeMessage.known_trx.ids.push(id.toString('hex'));
                }
                noticeMessage.known_blocks.mode = buffer.readUint32();
                noticeMessage.known_blocks.pending = buffer.readUint32();
                const arrLen2 = buffer.readVarUInt32();
                for (let i = 0; i < arrLen2; i++) {
                    const id = Buffer.from(buffer.readUInt8Array(32));
                    noticeMessage.known_blocks.ids.push(id.toString('hex'));
                }
                this.log(JSON.stringify(noticeMessage, null, 2));
                break;
            }

            // other cases
            default: {
                this.log('Unknown message type:', messageType);
            }
        }
    }

    log(...args) {
        console.log(`[${this.#peer}]`, ...args);
    }

    performHandshake() {
        const body = new SerialBuffer(Buffer.alloc(512));
        console.log("Buffer starting:", body.filled.toString('hex'))

        // Network version (uint16)
        body.writeUInt16(1212);

        // Chain ID (32 bytes)
        body.writeUint8Array(Buffer.from(this.#chainId, 'hex'));

        // Node ID (32 bytes)
        body.writeUint8Array(randomBytes(32));

        // Peer Public key (33 bytes)
        console.log("Buffer after writing public key type:", body.filled.toString('hex'));
        body.writeUInt8(0); // K1 type = 0
        body.writeBuffer(Buffer.alloc(33, 0)); // Public Key data (33 bytes)
        console.log("Buffer after writing public key data:", body.filled.toString('hex'));

        // Message Time (uint64)
        body.writeUInt64(nanoseconds());
        console.log("nanoseconds:", nanoseconds());

        // Token (32 bytes)
        body.writeBuffer(Buffer.alloc(32, 0));

        // Signature (65 bytes)
        body.writeUInt8(0);
        body.writeBuffer(Buffer.alloc(65, 0));

        // P2P Address (string)
        body.writeString('127.0.0.1:9876');

        // LIB Block Num (uint32)
        body.writeUInt32(0);

        // LIB Block ID (32 bytes)
        body.writeBuffer(Buffer.alloc(32, 0));

        // Head Block Num (uint32)
        body.writeUInt32(0);

        // Head Block ID (32 bytes)
        body.writeBuffer(Buffer.alloc(32, 0));

        // OS (string)
        body.writeString('Linux');

        // Agent (string)
        body.writeString('Antelope P2P Client');

        // Generation (uint16)
        body.writeUInt16(1);

        const header = new SerialBuffer(Buffer.alloc(5));
        // Message Length (uint32)
        header.writeUInt32(body.offset + 1);
        // Message Type (uint8)
        header.writeUInt8(0);

        const message = Buffer.concat([header.filled, body.filled]);
        console.log(header.filled.toString("hex"));
        console.log("Final handshake message:", message.toString('hex'));
        this.#socket.write(message);
        this.#handshake = true;
    }

    sendTimeMessage() {

        const body = new SerialBuffer(Buffer.alloc(4 * 8));
        // .org (uint64)
        body.writeUInt64(BigInt(0));
        // .rec (uint64)
        body.writeUInt64(BigInt(0));
        // .xmt (uint64)
        body.writeUInt64(nanoseconds());
        // .dst (uint64)
        body.writeUInt64(BigInt(0));

        const header = new SerialBuffer(Buffer.alloc(5));
        header.writeUInt32(body.offset + 1);
        header.writeUInt8(3);
        const message = Buffer.concat([header.filled, body.filled]);
        this.#socket.write(message);
    }
}

const testClient = new AntelopeNetClient(
    "waxp2p.sentnl.io:9876",
    '1064487b3cd1a897ce03ae5b6a865651747e2e152090f99c1d19d44e01aea5a4'
);

testClient.connect();
