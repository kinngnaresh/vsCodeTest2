import ezdxf
import os
import tkinter as tk
from tkinter import filedialog

FEED_RATE = 800


def browse_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select DXF File",
        filetypes=[("DXF Files", "*.dxf")]
    )


def write_polyline(gcode, points, closed):
    if not points:
        return

    x0, y0 = points[0]
    gcode.write(f"G0 X{x0:.4f} Y{y0:.4f}\n")

    for x, y in points[1:]:
        gcode.write(f"G1 X{x:.4f} Y{y:.4f}\n")

    if closed:
        gcode.write(f"G1 X{x0:.4f} Y{y0:.4f}\n")

    gcode.write("\n")


def process_entity(entity, gcode):
    etype = entity.dxftype()
    print("Found:", etype)

    if etype == "LINE":
        x1, y1 = entity.dxf.start.x, entity.dxf.start.y
        x2, y2 = entity.dxf.end.x, entity.dxf.end.y

        gcode.write(f"G0 X{x1:.4f} Y{y1:.4f}\n")
        gcode.write(f"G1 X{x2:.4f} Y{y2:.4f}\n\n")

    elif etype == "LWPOLYLINE":
        points = list(entity.get_points("xy"))
        write_polyline(gcode, points, entity.closed)

    elif etype == "POLYLINE":
        points = [(v.dxf.location.x, v.dxf.location.y)
                  for v in entity.vertices]
        write_polyline(gcode, points, entity.is_closed)

    elif etype == "INSERT":
        # explode block
        for e in entity.explode():
            process_entity(e, gcode)


def convert(path):
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()

    output_path = os.path.splitext(path)[0] + ".gcode"

    with open(output_path, "w") as gcode:
        gcode.write("G21\n")
        gcode.write("G90\n")
        gcode.write(f"F{FEED_RATE}\n\n")

        for entity in msp:
            process_entity(entity, gcode)

        gcode.write("M30\n")

    print("✅ Conversion finished")
    print("Saved:", output_path)


if __name__ == "__main__":
    file_path = browse_file()

    if not file_path:
        print("No file selected")
    else:
        convert(file_path)
