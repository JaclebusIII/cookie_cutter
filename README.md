# Cookie Cutter Generator

Upload a photo of any shape and get a 3D-printable cookie cutter STL file.

## Motivation

I vibe coded this tool to allow my partner to automatically generate cookie cutters stl files to be 3d printed. 

Love you Kimmie :)

## Setup

Requires Python 3.11+ and [pyenv](https://github.com/pyenv/pyenv).

```bash
pyenv local 3.11.12
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run downloads the rembg background-removal model (~170MB) to `~/.u2net/`.

## Usage

```bash
source .venv/bin/activate
python app.py
```

Opens at `http://localhost:7860`.

1. Upload a photo of the shape you want
2. Click **Preview Contour** to see the detected outline
3. Adjust sliders until the preview looks right
4. Click **Generate STL** and download the file

## Controls

| Control | What it does |
|---|---|
| Contour Detail | Lower = more detail, higher = smoother outline |
| Pillow | Expands and rounds the contour outward for a softer shape |
| Wall Thickness | Thickness of the cutter walls in mm (default 2mm) |
| Cutter Height | How tall the cutter is in mm (default 20mm) |
| Max Size | Longest dimension of the finished cutter in mm (default 80mm) |

**Advanced** (expand if the contour isn't finding the shape correctly):

| Control | When to adjust |
|---|---|
| Alpha Threshold | Lower if parts of the subject are being cut off; raise if background bleeds in |
| Mask Blur | Increase if the outline is speckled or rough |
| Gap Fill | Increase if the outline has gaps or broken sections |

## Printing

Slice with 2–3 perimeters and 0% infill. PLA or PETG both work well.

## Tips

- Works best with a subject on a plain or simple background
- If the background is complex, remove it first with a tool like [remove.bg](https://www.remove.bg)
- Very fine features smaller than the wall thickness will be lost — this is physically correct
