import zlib

def compress_data(data):
    compressed_data = zlib.compress(data)
    return compressed_data

def decompress_data(compressed_data):
    decompressed_data = zlib.decompress(compressed_data)
    return decompressed_data
