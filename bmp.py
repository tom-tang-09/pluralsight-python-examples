""""A module for dealing with BMP bitmap image files"""


def _bytes_to_int32(b):
    """Convert a bytes object containing four bytes into an integer."""
    return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)


def dimensions(filename):
    """Determine the dimensions in pixels of a BMP image.

    Args:
        filename : The file name of BMP File.

    Returns:
        A tuple containing two integers with the with
        and height in pixels.

    Raises:
        ValueError: If the file was not  a BMP file.
        OSError: If there was a problem reading the file.
    """

    with open(filename, 'rb') as f:
        magic = f.read(2)
        if magic != b'BM':
            raise ValueError("{} is not a BMP file".format(filename))

        f.seek(18)
        width_bytes = f.read(4)
        height_bytes = f.read(4)

        return (_bytes_to_int32(width_bytes),
                _bytes_to_int32(height_bytes))


def write_grayscale(filename, pixels):
    """"Creates and writes a grayscale BMP file.

    Args:
        filename : The name of BMP file to be created

        pixels: A rectangular image stored as a sequence of rows.
            Each row must be an iterable series of integers in the
            range 0-255.

    Raises:
        OSError: If the file couldn't be written
    """

    height = len(pixels)
    width = len(pixels[0])

    with open(filename, 'wb') as bmp:
        # BMP Header
        bmp.write(b'BM')

        size_bookmark = bmp.tell()  # The next four btyes hold the filesize as a 32-bit
        bmp.write(b'\x00\x00\x00\x00')  # little-endian integer. Zero placeholder for now

        bmp.write(b'\x00\x00')  # unused 16-bit integer - should be zero
        bmp.write(b'\x00\x00')  # unused 16-bit integer - should be zero

        pixes_offset_bookmark = bmp.tell()  # The next four bytes hold the integer offset
        bmp.write(b'\x00\x00\x00\x00')  # to the pixel data. Zero placeholder for row.

        # Image Header
        bmp.write(b'\x28\x00\x00\x00')  # Image header size in bytes - 40 decimal
        bmp.write(_int_32_to_bytes(width))  # The image with in pixels
        bmp.write(_int_32_to_bytes(height))  # The image height in pixels
        bmp.write(b'\x01\x00')  # The number of image planes
        bmp.write(b'\x08\x00')  # Bits per pixel 8 for grayscale
        bmp.write(b'\x00\x00\x00\x00')  # No compression
        bmp.write(b'\x00\x00\x00\x00')  # Zero for uncompressed images
        bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
        bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
        bmp.write(b'\x00\x00\x00\x00')  # Use whole color table
        bmp.write(b'\x00\x00\x00\x00')  # All colors are important

        # Color palette - a linear grayscale
        for c in range(0, 256):
            bmp.write(bytes((c, c, c, 0)))  # Blue, Green, Red, Zero

        # Pixel data
        pixel_data_bookmark = bmp.tell()
        for row in reversed(pixels):  # BMP files are bottom to top
            row_data = bytes(row)
            bmp.write(row_data)
            padding = b'\x00' * (4 - (len(row) % 4))  # Pad row to multiple of four bytes
            bmp.write(padding)

        # End of file
        eof_bookmark = bmp.tell()

        # Fill in file size placeholder
        bmp.seek(size_bookmark)
        bmp.write(_int_32_to_bytes(eof_bookmark))

        # Fill in pixel offset placeholder
        bmp.seek(pixes_offset_bookmark)
        bmp.write(_int_32_to_bytes(pixel_data_bookmark))


def _int_32_to_bytes(i):
    """"Convert an integer to four bytes in little-endian format."""
    return bytes((i & 0xff,
                  i >> 8 & 0xff,
                  i >> 16 & 0xff,
                  i >> 32 & 0xff))
