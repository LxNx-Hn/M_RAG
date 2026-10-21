"""Recompress embedded PNG streams without changing pixels or PNG metadata."""

import base64
import re
import struct
import zlib


def reencode_svg_pngs(svg):
    def replace(match):
        png = base64.b64decode(match[1])
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        chunks, offset = [], 8
        while offset < len(png):
            size = struct.unpack(">I", png[offset : offset + 4])[0]
            end = offset + size + 12
            chunks.append((png[offset + 4 : offset + 8], png[offset:end]))
            offset = end
        assert offset == len(png)
        compressed = b"".join(data[8:-4] for kind, data in chunks if kind == b"IDAT")
        original = zlib.decompress(compressed)
        packed = zlib.compress(original, level=9)
        assert zlib.decompress(packed) == original
        body = b"IDAT" + packed
        replacement = (
            struct.pack(">I", len(packed)) + body + struct.pack(">I", zlib.crc32(body))
        )
        output, emitted = [png[:8]], False
        for kind, data in chunks:
            if kind == b"IDAT":
                if not emitted:
                    output.append(replacement)
                    emitted = True
            else:
                output.append(data)
        return "data:image/png;base64," + base64.b64encode(b"".join(output)).decode(
            "ascii"
        )

    return re.sub(r"data:image/png;base64,([A-Za-z0-9+/=\s]+)", replace, svg)
