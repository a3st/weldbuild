import struct
from PIL import Image
from io import BytesIO

class ICOParser:
    ICO_HEADER = struct.Struct("HHH")
    IMAGE_INFO = struct.Struct("BBBBHHII")

    def __init__(
        self,
        bitmap_paths: list[str]
    ):
        self.buffer = bytearray()

        header = ICOParser.ICO_HEADER.pack(0, 1, len(bitmap_paths))
        self.buffer += header

        bitmap_data = bytearray()
        bitmap_offset = len(header) + ICOParser.IMAGE_INFO.size * len(bitmap_paths)

        for bitmap_path in bitmap_paths:
            if not bitmap_path.endswith(".png") or bitmap_path.endswith(".bmp"):
                raise ValueError("Unsupported format images for icons (Only .png or .bmp formats are supported)")
            
            with Image.open(bitmap_path, "r") as imgfp:
                width, height = imgfp.width, imgfp.height

                if width > 256 or height > 256:
                    raise ValueError("Unsupported image sizes (Image cannot be higher than 256x256)")

                output = BytesIO()
                imgfp.save(output, format='PNG')
                data = output.getvalue()
                bitmap_data += data
                size = len(data)

            image_info = ICOParser.IMAGE_INFO.pack(
                width,
                height,
                0,
                0,
                1,
                0,
                size,
                bitmap_offset
            )
            self.buffer += image_info
            bitmap_offset += size

        self.buffer += bitmap_data

    
    def save_to_file(self, file_path: str):
        with open(file_path, "wb") as fp:
            fp.write(self.buffer)
