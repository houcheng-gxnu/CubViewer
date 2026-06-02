# CubeViewer

**CubeViewer** — a lightweight PyQt5 GUI for viewing `.cub` files directly in VMD with Tachyon ray-tracing export. No Multiwfn required.

> 轻量级 Cube 文件查看器，直接打开 .cub 文件，VMD 预览 + Tachyon 渲染。

## Features

- **Open `.cub` files directly** — skip the fchk → cube step
- **VMD live preview** with real-time isovalue & opacity sliders
- **Tachyon ray-tracing** export to high-res BMP/PNG
- **33 built-in rendering styles** — vcube2.0 classics, IboView-inspired, curated palettes (Morandi, Aurora, Cyberpunk, Ink Wash & more)
- **Hide hydrogen atoms** for clean heavy-atom views
- **Dashed bond drawing** for annotating interactions
- **Bilingual UI** (Chinese / English)

## When to Use

| Tool | Use Case |
|------|----------|
| **CubeViewer** | You already have `.cub` files — just view & render |
| **OrbitalViewer** | You have `.fchk` files — need full Multiwfn pipeline |

## Download

Pre-built executables (no Python required):

| Version | File |
|---------|------|
| Chinese | `CubeViewer_zh.exe` |
| English | `CubeViewer.exe` |

📥 **Download: [CubeViewer V1.0 →](https://cnb.cool/chem311/CubViewer/-/releases/tag/V1.0)**

## Dependencies

| Dependency | Role | Install |
|------------|------|---------|
| Python 3.8+ | Runtime | — |
| PyQt5 | GUI | `pip install PyQt5` |
| [VMD](https://www.ks.uiuc.edu/Research/vmd/) | 3D preview + Tachyon | Install & configure path |
| Tachyon | Ray tracing | Bundled with VMD |

## Quick Start

### 1. Install dependency

```bash
pip install PyQt5
```

### 2. Configure VMD path

Edit `fchk_orbital.ini` (auto-created on first run):

```ini
[paths]
vmd = C:\Program Files (x86)\University of Illinois\VMD\vmd.exe
tachyon = C:\Program Files (x86)\University of Illinois\VMD\tachyon_WIN32.exe
```

### 3. Run

```bash
# Chinese UI
python cubviewer_zh.py

# English UI
python cubviewer.py
```

### 4. Build exe (optional)

```bash
pyinstaller CubeViewer_zh.spec
```

## Project Structure

```
├── cubviewer.py           # English GUI
├── cubviewer_zh.py        # Chinese GUI
├── fchk_orbital.py        # Backend (VMD control, rendering)
├── fchk_orbital.ini       # VMD path config (auto-generated)
├── CubeViewer.spec        # PyInstaller spec (EN)
├── CubeViewer_zh.spec     # PyInstaller spec (ZH)
├── dist/
│   ├── CubeViewer_zh.exe  # Chinese pre-built
│   └── CubeViewer.exe     # English pre-built
└── README.md
```

## License

Academic use.
