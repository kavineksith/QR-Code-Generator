# 🎯 QR Code Generator - CLI

A **production-ready**, fully-featured **QR code generator** written in Python. This tool supports both **command-line and interactive modes**, allowing you to create **custom-styled QR codes** with robust logging, error handling, and output management.

## 📦 Features

* ✅ Command-line and interactive interfaces
* 🎨 Styled QR codes with custom colors, gradients, and module styles
* 🔍 Detailed logging to both console and file
* ⚙️ Configurable error correction, box size, version, borders
* 📁 Output directory validation with permission checks
* 🧪 Custom exception classes for precise error diagnostics

## 📥 Installation

Make sure you have Python 3.10 or above. Install the dependencies with:

```bash
pip install qrcode pillow
```

## 🚀 Usage

### Command Line

#### Basic QR Code

```bash
python qr_generator.py "https://example.com"
```

#### Save to Custom File

```bash
python qr_generator.py "https://example.com" -o example.png
```

#### Styled QR Code

```bash
python qr_generator.py "https://example.com" --styled --drawer circle --color radial
```

#### Full Customization

```bash
python qr_generator.py "My Data" -o custom.png --version 5 --error-correction H \
--box-size 15 --border 2 --styled --drawer circle --color vertical
```

### Interactive Mode

```bash
python qr_generator.py --interactive
```

You will be prompted step-by-step to enter all required and optional inputs.


## ⚙️ Options

| Option               | Description                                                                            |
| -------------------- | -------------------------------------------------------------------------------------- |
| `--version`          | QR version (1–40). Auto-selects if omitted                                             |
| `--error-correction` | Error correction level: L, M, Q, H (default: L)                                        |
| `--box-size`         | Size of each box in pixels (default: 10)                                               |
| `--border`           | Border thickness in boxes (default: 4)                                                 |
| `--styled`           | Enable styled QR output                                                                |
| `--drawer`           | Module drawer style: `square`, `rounded`, `gapped`, `circle`, `vertical`, `horizontal` |
| `--color`            | Color mask: `radial`, `square`, `horizontal`, `vertical`, `solid`                      |
| `--foreground`       | Foreground color for solid mask (default: black)                                       |
| `--background`       | Background color for solid mask (default: white)                                       |

## 📁 Output

All generated QR codes are saved in the specified output directory (default: `qr_codes`). Logs are written to `qr_generator.log`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🛑 Disclaimer

This QR code generator is provided **as-is**, without any warranty. It is intended for educational, testing, or general use cases. The user is responsible for validating QR codes before use in critical applications (e.g., financial, medical, security-sensitive contexts).

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**
