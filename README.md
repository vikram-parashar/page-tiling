# HG Tile Studio

Professional bulk image tiling and print layout software built with PySide6.

---

## Overview

HG Tile Studio is a desktop application designed for print shops, photographers, and graphic designers who need to arrange multiple images onto printable sheets efficiently. It provides a complete pipeline from image scanning through layout generation to final export, with live preview, template management, and DPI-aware rendering.

---

## Features

### Image Handling
- **Recursive folder scanning** — Automatically discover images in nested directories
- **Multi-format support** — PNG, JPG, JPEG, BMP, WEBP, TIFF
- **Corrupted file protection** — Broken images are detected and skipped gracefully
- **Thumbnail generation** — Optional thumbnails for fast UI rendering
- **Image statistics** — Count, size, and corruption reports

### Layout Engine
- **6 layout modes:**
  - `grid` — Classic row-column grid with fixed gaps
  - `space-between` — Evenly distribute extra space between images
  - `space-around` — Equal space around each image
  - `space-evenly` — Equal spacing between and around images
  - `packed` — Zero-gap tight packing
  - `auto-fit` — Automatically calculate maximum images per page
- **Alignment** — Horizontal (left/center/right) and vertical (top/middle/bottom)
- **Pagination** — Overflow images automatically span multiple pages
- **DPI-aware** — All measurements in mm, converted to pixels at render time

### Scaling Engine
- **7 scaling modes:**
  - `fit` / `contain` — Aspect-ratio preserved, centered with background fill
  - `fill` / `cover` — Aspect-ratio preserved, crop to fill the cell
  - `stretch` — Distort to exactly fill the cell
  - `original` — Keep original size, centered with background
  - `smart-crop` — Placeholder for AI-based face-aware cropping (currently falls back to cover)
- **Auto-rotation** — Detects orientation mismatch and rotates accordingly
- **Alpha transparency** — RGBA images are pasted with proper alpha handling

### Cut Marks
- **Configurable** — Length, thickness, offset, and color
- **Per-corner marks** — Crop marks drawn at all four corners of each image cell
- **Toggle on/off** — Enable or disable per export job

### Export
- **3 output formats:** PNG, JPG, PDF
- **Multi-page PDF** — All pages combined into a single PDF document
- **JPG quality control** — 1–100 quality slider
- **Transparent background** — PNG export supports alpha transparency
- **DPI control** — 72 to 2400 DPI
- **Filename templates** — Variable-based naming with `{page}`, `{date}`, `{time}`, etc.

### Template System
- **Save/Load** — Persist and recall complete layout configurations
- **Export/Import** — Share templates as JSON files
- **Rename/Delete** — Full template management
- **Default template** — Built-in A4 portrait starter template
- **Auto-apply** — Loaded templates immediately update all controls

### Live Preview
- **QGraphicsView** — Hardware-accelerated preview rendering
- **Zoom** — Mouse wheel zoom + toolbar zoom in/out
- **Pan** — Middle-click drag to pan around the preview
- **Fit-to-screen** — Auto-fit preview to the viewport
- **Multi-page preview** — Vertically stacked page previews
- **Placeholder rendering** — Fast lightweight preview for large jobs

### Canvas Presets
- A4, A3, A5, Letter, Legal, and Custom
- Portrait / Landscape orientation toggle with auto-swap

---

## Project Structure

```
page-tiling/
├── main.py                    # Application entry point
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # pip-compatible dependency list
│
├── core/                      # Core engine modules
│   ├── __init__.py
│   ├── layout_engine.py       # Layout generation (grid, space-between, etc.)
│   ├── scaling_engine.py      # Image scaling (fit, fill, stretch, etc.)
│   ├── cutmarks.py            # Cut/crop mark generation
│   ├── export_engine.py       # PNG, JPG, PDF export engine
│   ├── image_loader.py        # Bulk image scanning and loading
│   └── template_manager.py    # JSON template persistence
│
├── gui/                       # GUI modules
│   ├── __init__.py
│   ├── main_window.py         # Main application window
│   ├── controls_panel.py      # Left sidebar settings panel
│   ├── preview_panel.py       # QGraphicsView live preview
│   └── dialogs.py             # Dialog collection
│
└── utils/                     # Utility modules
    ├── __init__.py
    ├── filename_builder.py    # Variable-based filename generation
    ├── cache.py               # Memory + disk cache with LRU eviction
    ├── dpi.py                 # DPI and print utility calculations
    └── mm_converter.py        # Measurement unit conversions
```

---

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Install with uv (recommended)

```bash
# Clone the repository
git clone https://github.com/vikram-parashar/page-tiling.git
cd page-tiling

# Install dependencies
uv sync
```

### Install with pip

```bash
# Clone the repository
git clone https://github.com/vikram-parashar/page-tiling.git
cd page-tiling

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Launch the Application

```bash
# With uv
uv run python main.py

# With pip (after activating venv)
python main.py
```

### Workflow

1. **Select Input Folder** — Choose a folder containing the images you want to tile
2. **Select Output Folder** — Choose where exported files will be saved
3. **Configure Settings** — Adjust canvas size, layout mode, margins, gaps, scaling, etc.
4. **Preview** — Click **Preview** to see a live layout preview on the right panel
5. **Generate** — Click **Generate** to export the tiled sheets as PNG, JPG, or PDF
6. **Save Template** (optional) — Save your current settings for future use

### Menu Actions

| Menu | Action | Description |
|------|--------|-------------|
| File | Select Input Folder | Open folder dialog for image input |
| File | Select Output Folder | Open folder dialog for export output |
| File | Exit | Close the application |
| Templates | Save Template | Save current settings as a reusable template |
| Templates | Load Template | Load a previously saved template |
| Help | About | Show application info |

### Preview Controls

| Control | Action |
|---------|--------|
| **+** button | Zoom in |
| **-** button | Zoom out |
| **Fit** button | Fit preview to viewport |
| **Reset** button | Reset zoom to 100% |
| **Clear** button | Clear the preview |
| Mouse wheel | Zoom in/out |
| Middle-click drag | Pan the preview |

---

## Configuration Reference

### Canvas Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Preset | A4 | Paper size preset |
| Width | 210 mm | Custom page width |
| Height | 297 mm | Custom page height |
| Orientation | Portrait | Portrait or Landscape |
| DPI | 300 | Render resolution |

### Layout Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Layout Mode | grid | grid, space-between, space-around, space-evenly, packed, auto-fit |
| Image Width | 35 mm | Target cell width per image |
| Image Height | 45 mm | Target cell height per image |
| Horizontal Gap | 2 mm | Space between columns |
| Vertical Gap | 2 mm | Space between rows |

### Margin Settings

| Setting | Default |
|---------|---------|
| Left | 5 mm |
| Right | 5 mm |
| Top | 5 mm |
| Bottom | 5 mm |

### Scaling Modes

| Mode | Behavior |
|------|----------|
| fit / contain | Preserve aspect ratio, fit inside cell, pad with background |
| fill / cover | Preserve aspect ratio, fill cell, crop overflow |
| stretch | Distort to exactly fill cell dimensions |
| original | Keep original pixel size, center in cell |
| smart-crop | AI face-aware crop (falls back to cover) |

### Export Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Format | PNG | PNG, JPG, or PDF |
| JPG Quality | 95 | Quality level for JPG export (1–100) |

### Cut Mark Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Enable | No | Toggle cut marks on/off |
| Length | 3 mm | Length of each cut mark line |
| Offset | 1 mm | Distance from image edge |

---

## Architecture

### Pipeline

```
Input Folder
    │
    ▼
ImageLoader ─── Scan images, filter formats, detect corruption
    │
    ▼
LayoutEngine ── Calculate positions, pagination, alignment
    │
    ├─────────────────────────────┐
    ▼                             ▼
PreviewPanel              ExportEngine
  (QGraphicsView)         (PIL + ReportLab)
  Live preview             PNG / JPG / PDF
```

### Data Flow

1. **ImageLoader** scans the input folder and returns a list of valid image paths
2. **LayoutEngine** takes image paths + `LayoutSettings` and produces a list of `LayoutPage` objects, each containing `LayoutItem` objects with position/size data
3. For **preview**, `PreviewPanel` renders lightweight rectangle placeholders via `QGraphicsScene`
4. For **export**, `ExportEngine` renders each page as a full-resolution PIL Image, applies scaling and cut marks, then saves as PNG/JPG or combines into a multi-page PDF via ReportLab

### Template Format

Templates are stored as JSON files in the `templates/` directory:

```json
{
    "template_name": "passport_layout",
    "created_at": "2025-01-15T10:30:00",
    "version": "1.0",
    "data": {
        "canvas": { "preset": "A4", "width_mm": 210, "height_mm": 297, "orientation": "portrait", "dpi": 300 },
        "layout": { "layout_mode": "auto-fit", "image_width_mm": 35, "image_height_mm": 45, "horizontal_gap_mm": 2, "vertical_gap_mm": 2 },
        "margins": { "left_mm": 5, "right_mm": 5, "top_mm": 5, "bottom_mm": 5 },
        "scaling": { "mode": "fit" },
        "background": { "type": "solid", "color": [255, 255, 255] },
        "cutmarks": { "enabled": false, "length_mm": 3, "offset_mm": 1, "thickness_px": 1 },
        "export": { "format": "PNG", "jpg_quality": 95 }
    }
}
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | >= 6.7.0 | Qt GUI framework |
| Pillow | >= 10.3.0 | Image processing and rendering |
| reportlab | >= 4.2.0 | PDF generation |
| numpy | >= 1.26.4 | Numerical operations |
| opencv-python | >= 4.10.0 | Advanced image processing |

---

## Development

### Running Individual Modules

Each module includes a standalone test section that can be run independently:

```bash
# Test the layout engine
python -m core.layout_engine

# Test the export engine (requires sample.jpg)
python -m core.export_engine

# Test the image loader (requires sample_images/ folder)
python -m core.image_loader

# Test the preview panel
python -m gui.preview_panel
```

### Adding a New Layout Mode

1. Add the mode name to `LayoutEngine.SUPPORTED_LAYOUTS` in `core/layout_engine.py`
2. Add a new `elif mode == "your-mode":` block in `_generate_page_items()`
3. Add the mode to the `QComboBox` in `gui/controls_panel.py` `_build_layout_section()`

### Adding a New Scaling Mode

1. Add the mode name to `ScalingEngine.SUPPORTED_MODES` in `core/scaling_engine.py`
2. Implement the scaling method and add it to the `scale_image()` dispatcher
3. Add the mode to the `QComboBox` in `gui/controls_panel.py` `_build_scaling_section()`

---

## License

This project is developed by **HARRY GRAPHICS**.
