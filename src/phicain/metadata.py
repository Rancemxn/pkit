import struct
import os
from loguru import logger
import sys

MAGIC_ENCRYPTED_DATA_BYTES = (-1124405112).to_bytes(
    4, "little", signed=True
)  # b'\x08\x19\x01\xBE'
MAGIC_RC4_KEY_BYTES = (1451223060).to_bytes(4, "little")  # b'\x14\x12\x78\x56'
HEADER_SIZE = 16


class MemReader:
    def __init__(self, baseAddr_bytes):
        self.baseAddr = baseAddr_bytes

    def read(self, offset: int, size: int) -> bytes:
        return self.baseAddr[offset : offset + size]

    def getInt(self, offset: int) -> int:
        return int.from_bytes(self.read(offset, 4), "little")


class RC4:
    def __init__(self, key_bytes):
        self.S = list(range(256))
        key_len = len(key_bytes)
        j = 0
        for i in range(256):
            j = (j + self.S[i] + key_bytes[i % key_len]) % 256  # KSA
            self.S[i], self.S[j] = self.S[j], self.S[i]
        self.i_prga = 0
        self.j_prga = 0

    def _get_keystream_byte(self):
        self.i_prga = (self.i_prga + 1) % 256
        self.j_prga = (self.j_prga + self.S[self.i_prga]) % 256
        self.S[self.i_prga], self.S[self.j_prga] = (
            self.S[self.j_prga],
            self.S[self.i_prga],
        )
        k = self.S[(self.S[self.i_prga] + self.S[self.j_prga]) % 256]
        return k

    def crypt(self, data_bytes):
        result = bytearray()
        for byte_val in data_bytes:
            keystream_byte = self._get_keystream_byte()
            result.append(byte_val ^ keystream_byte)
        return bytes(result)


def find_block_offsets(data, magic_bytes_to_find):
    offsets = []
    magic_len = len(magic_bytes_to_find)
    for i in range(len(data) - magic_len + 1):
        if data[i : i + magic_len] == magic_bytes_to_find:
            offsets.append(i)
    return offsets


def get_block_data_from_offset(data, offset, magic_bytes_value):
    magic_str = magic_bytes_value.hex()
    try:
        block_len = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
        block_data_start_in_file = offset + HEADER_SIZE
        logger.info(
            f"找到魔数 {magic_str} @ {hex(offset)}, 数据长度: {block_len}, 数据文件内起始: {hex(block_data_start_in_file)}"
        )
        return block_data_start_in_file, block_len
    except struct.error as e:
        logger.error(
            f"在偏移 {hex(offset)} 处理魔数 {magic_str} 的头部时发生结构解包错误: {e}"
        )
        return None, None


def decrypt_phigros_metadata(file_data) -> bytes:
    rc4_key_block_offsets = find_block_offsets(file_data, MAGIC_RC4_KEY_BYTES)
    logger.info(f"找到RC4密钥魔数的潜在偏移: {[hex(o) for o in rc4_key_block_offsets]}")

    rc4_key_start_offset_in_file, rc4_key_length = None, None
    for offset in rc4_key_block_offsets:
        start, length = get_block_data_from_offset(
            file_data, offset, MAGIC_RC4_KEY_BYTES
        )
        if (
            start is not None
            and length is not None
            and start + length <= len(file_data)
        ):
            rc4_key_start_offset_in_file = start
            rc4_key_length = length
            break

    if not rc4_key_start_offset_in_file or not rc4_key_length:
        raise RuntimeError()
    rc4_key_data = file_data[
        rc4_key_start_offset_in_file : rc4_key_start_offset_in_file + rc4_key_length
    ]
    logger.info(
        f"提取的RC4密钥数据长度: {len(rc4_key_data)} 字节，起始于文件偏移 {hex(rc4_key_start_offset_in_file)}"
    )

    encrypted_data_block_offsets = find_block_offsets(
        file_data, MAGIC_ENCRYPTED_DATA_BYTES
    )
    logger.info(
        f"找到加密元数据魔数的潜在偏移: {[hex(o) for o in encrypted_data_block_offsets]}"
    )

    encrypted_data_start_offset_in_file, encrypted_data_length = None, None
    for offset in encrypted_data_block_offsets:
        start, length = get_block_data_from_offset(
            file_data, offset, MAGIC_ENCRYPTED_DATA_BYTES
        )
        if (
            start is not None
            and length is not None
            and start + length <= len(file_data)
        ):
            encrypted_data_start_offset_in_file = start
            encrypted_data_length = length
            break

    if encrypted_data_start_offset_in_file is None or encrypted_data_length is None:
        raise RuntimeError()

    encrypted_metadata = file_data[
        encrypted_data_start_offset_in_file : encrypted_data_start_offset_in_file
        + encrypted_data_length
    ]
    logger.info(
        f"提取的加密元数据长度: {len(encrypted_metadata)} 字节，起始于文件偏移 {hex(encrypted_data_start_offset_in_file)}"
    )

    logger.info("正在使用提取的密钥进行RC4解密...")
    rc4_cipher = RC4(rc4_key_data)
    decrypted_metadata = rc4_cipher.crypt(encrypted_metadata)

    logger.info(f"RC4解密完成。解密后数据长度: {len(decrypted_metadata)} 字节")

    reader = MemReader(bytes(decrypted_metadata))
    offset_val_from_8 = reader.getInt(8)
    size_part1_offset = offset_val_from_8 - 8
    size_part2_offset = offset_val_from_8 - 4

    logger.debug(f"从解密数据偏移 8 读取的值: {hex(offset_val_from_8)}")
    logger.debug(
        f"将用于计算总大小的偏移: part1 @ {hex(size_part1_offset)}, part2 @ {hex(size_part2_offset)}"
    )

    size = reader.getInt(size_part1_offset) + reader.getInt(size_part2_offset)
    logger.debug(f"计算得到的元数据总大小: {size}")

    metadata = bytearray(reader.read(0, size))
    stringSize_offset = 28
    string_data_offset_val_offset = 24

    stringSize = reader.getInt(stringSize_offset)
    string_offset_in_metadata = reader.getInt(string_data_offset_val_offset)

    logger.info(
        f"字符串块大小: {stringSize}, 字符串块在元数据中的偏移: {hex(string_offset_in_metadata)}"
    )

    current_offset_in_string_block = 0
    while current_offset_in_string_block < stringSize:
        xor_val = current_offset_in_string_block % 0xFF

        i = 0
        while i == 0 or (xor_val != 0 and current_offset_in_string_block < stringSize):
            target_idx_in_metadata = (
                string_offset_in_metadata + current_offset_in_string_block
            )

            xor_val ^= metadata[target_idx_in_metadata]
            metadata[target_idx_in_metadata] = xor_val
            current_offset_in_string_block += 1
            i = 1

    decrypted_metadata = bytes(metadata)
    logger.info("第二阶段解密（字符串异或处理）完成。")

    return decrypted_metadata
