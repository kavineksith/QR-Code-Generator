import os
import sys
import argparse
import logging
from typing import Optional, Union, Tuple
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer,
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask,
    SolidFillColorMask
)

# Custom Exceptions
class QRGenerationError(Exception):
    """Base class for QR generation errors"""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class InputValidationError(QRGenerationError):
    """Raised when input data is invalid"""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class FileSystemError(QRGenerationError):
    """Raised for filesystem-related errors"""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class PermissionError(FileSystemError):
    """Raised when permission issues occur"""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class QRCodeGenerator:
    """
    A production-ready QR code generator with comprehensive features:
    - Command-line interface
    - Interactive mode
    - Custom styling options
    - Robust error handling
    - Detailed logging
    """

    ERROR_CORRECTION_MAP = {
        'L': ERROR_CORRECT_L,
        'M': ERROR_CORRECT_M,
        'Q': ERROR_CORRECT_Q,
        'H': ERROR_CORRECT_H
    }

    MODULE_DRAWERS = {
        'square': SquareModuleDrawer,
        'rounded': RoundedModuleDrawer,
        'gapped': GappedSquareModuleDrawer,
        'circle': CircleModuleDrawer,
        'vertical': VerticalBarsDrawer,
        'horizontal': HorizontalBarsDrawer
    }

    COLOR_MASKS = {
        'radial': RadialGradiantColorMask,
        'square': SquareGradiantColorMask,
        'horizontal': HorizontalGradiantColorMask,
        'vertical': VerticalGradiantColorMask,
        'solid': SolidFillColorMask
    }

    def __init__(self, output_dir: str = "qr_codes"):
        """
        Initialize the QRCodeGenerator.
        
        Args:
            output_dir (str): Directory to save generated QR codes. Defaults to "qr_codes".
        """
        self.output_dir = output_dir
        self.logger = self._setup_logger()
        self._validate_and_create_output_dir()
        
    def _setup_logger(self) -> logging.Logger:
        """Configure and return a logger instance."""
        logger = logging.getLogger("QRCodeGenerator")
        logger.setLevel(logging.DEBUG)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler("qr_generator.log")
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatters and add to handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def _validate_and_create_output_dir(self) -> None:
        """Validate and create the output directory if it doesn't exist."""
        try:
            if not os.path.exists(self.output_dir):
                self.logger.info(f"Creating output directory: {self.output_dir}")
                os.makedirs(self.output_dir)
                self.logger.info(f"Successfully created directory: {self.output_dir}")
            
            # Test write permissions
            test_file = os.path.join(self.output_dir, ".permission_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            
        except PermissionError as e:
            self.logger.error(f"Permission denied for directory {self.output_dir}: {str(e)}")
            raise PermissionError(f"Insufficient permissions for directory {self.output_dir}") from e
        except OSError as e:
            self.logger.error(f"Filesystem error creating directory {self.output_dir}: {str(e)}")
            raise FileSystemError(f"Filesystem error: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error setting up output directory: {str(e)}")
            raise QRGenerationError(f"Unexpected error: {str(e)}") from e
    
    def _validate_input_data(self, data: str) -> None:
        """Validate input data for QR code generation."""
        if not isinstance(data, str):
            self.logger.error(f"Invalid input type: {type(data)}. Expected string.")
            raise InputValidationError("Input data must be a string")
        
        if not data.strip():
            self.logger.error("Empty input data provided")
            raise InputValidationError("Input data cannot be empty")
        
        self.logger.debug("Input data validation passed")
    
    def _generate_filename(self, data: str, extension: str = "png") -> str:
        """
        Generate a sanitized filename based on the QR code data.
        
        Args:
            data (str): The data to be encoded in the QR code
            extension (str): File extension. Defaults to "png".
            
        Returns:
            str: Generated filename
        """
        # Basic sanitization - replace problematic characters
        sanitized = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in data)
        # Limit length to avoid filesystem issues
        sanitized = sanitized[:50]
        return f"qr_{sanitized}.{extension}"
    
    def generate_qr_code(
        self,
        data: str,
        filename: Optional[str] = None,
        version: Optional[int] = None,
        error_correction: str = 'L',
        box_size: int = 10,
        border: int = 4,
        styled: bool = False,
        drawer_style: str = 'rounded',
        color_mask: str = 'radial',
        foreground_color: str = 'black',
        background_color: str = 'white',
        **kwargs
    ) -> str:
        """
        Generate a QR code and save it to a file.
        
        Args:
            data (str): Data to encode in the QR code
            filename (str, optional): Output filename. If None, will be generated automatically.
            version (int, optional): QR code version (1-40). None for auto.
            error_correction (str): Error correction level (L, M, Q, H). Defaults to 'L'.
            box_size (int): Size of each box in pixels. Defaults to 10.
            border (int): Border size in boxes. Defaults to 4.
            styled (bool): Whether to apply styling. Defaults to False.
            drawer_style (str): Module drawer style. Options: square, rounded, gapped, circle, vertical, horizontal.
            color_mask (str): Color mask style. Options: radial, square, horizontal, vertical, solid.
            foreground_color (str): Foreground color for solid masks.
            background_color (str): Background color for solid masks.
            **kwargs: Additional styling options.
            
        Returns:
            str: Path to the generated QR code image
            
        Raises:
            InputValidationError: If input data is invalid
            QRGenerationError: If QR code generation fails
            FileSystemError: If file operations fail
        """
        self.logger.info(f"Starting QR code generation for data: {data[:50]}...")

        try:
            # Input validation
            self._validate_input_data(data)
            
            # Convert error correction level
            try:
                error_correction_level = self.ERROR_CORRECTION_MAP[error_correction.upper()]
            except KeyError:
                raise InputValidationError(
                    f"Invalid error correction level: {error_correction}. Must be one of: {list(self.ERROR_CORRECTION_MAP.keys())}"
                )

            # Configure QR code
            qr = qrcode.QRCode(
                version=version,
                error_correction=error_correction_level,
                box_size=box_size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Generate image
            img = self._create_qr_image(
                qr,
                styled,
                drawer_style,
                color_mask,
                foreground_color,
                background_color,
                **kwargs
            )
            
            # Determine output filename
            output_filename = filename or self._generate_filename(data)
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save the image
            self._save_image(img, output_path)
            
            self.logger.info(f"Successfully generated QR code at: {output_path}")
            return output_path
            
        except InputValidationError:
            self.logger.error("Input validation failed - see previous error")
            raise
        except qrcode.exceptions.DataOverflowError as e:
            self.logger.error(f"Data too large for QR code: {str(e)}")
            raise InputValidationError("Data too large for QR code") from e
        except KeyboardInterrupt:
            self.logger.warning("QR generation interrupted by user")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate QR code: {str(e)}", exc_info=True)
            raise QRGenerationError(f"QR generation failed: {str(e)}") from e
    
    def _create_qr_image(
        self,
        qr: qrcode.QRCode,
        styled: bool,
        drawer_style: str,
        color_mask: str,
        foreground_color: str,
        background_color: str,
        **kwargs
    ) -> Union[qrcode.image.pil.PilImage, StyledPilImage]:
        """Create QR code image with optional styling."""
        try:
            if styled:
                self.logger.debug("Generating styled QR code")
                
                # Get module drawer class
                try:
                    drawer_class = self.MODULE_DRAWERS[drawer_style.lower()]
                except KeyError:
                    available = list(self.MODULE_DRAWERS.keys())
                    raise InputValidationError(
                        f"Invalid drawer style: {drawer_style}. Must be one of: {available}"
                    )
                
                # Get color mask class and initialize appropriately
                try:
                    if color_mask.lower() == 'solid':
                        color_mask_obj = SolidFillColorMask(
                            back_color=self._parse_color(background_color),
                            front_color=self._parse_color(foreground_color)
                        )
                    else:
                        color_mask_class = self.COLOR_MASKS[color_mask.lower()]
                        color_mask_obj = color_mask_class()
                except KeyError:
                    available = list(self.COLOR_MASKS.keys())
                    raise InputValidationError(
                        f"Invalid color mask: {color_mask}. Must be one of: {available}"
                    )
                
                return qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=drawer_class(),
                    color_mask=color_mask_obj,
                    **kwargs
                )
            else:
                self.logger.debug("Generating standard QR code")
                return qr.make_image(
                    fill_color=self._parse_color(foreground_color),
                    back_color=self._parse_color(background_color)
                )
        except Exception as e:
            self.logger.error(f"Failed to create QR image: {str(e)}")
            raise QRGenerationError(f"Image creation failed: {str(e)}") from e
    
    def _parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """Parse color string into RGB tuple."""
        # This is a simplified version - would need proper color parsing in production
        color_lower = color_str.lower()
        if color_lower == 'black':
            return (0, 0, 0)
        elif color_lower == 'white':
            return (255, 255, 255)
        elif color_lower == 'red':
            return (255, 0, 0)
        elif color_lower == 'green':
            return (0, 255, 0)
        elif color_lower == 'blue':
            return (0, 0, 255)
        # Add more color mappings as needed
        else:
            # Default to black if color not recognized
            return (0, 0, 0)
    
    def _save_image(self, img: Union[qrcode.image.pil.PilImage, StyledPilImage], path: str) -> None:
        """Save the QR code image to file with error handling."""
        try:
            self.logger.debug(f"Attempting to save image to: {path}")
            img.save(path)
            self.logger.debug("Image saved successfully")
        except PermissionError as e:
            self.logger.error(f"Permission denied saving to {path}: {str(e)}")
            raise PermissionError(f"Cannot save to {path}: permission denied") from e
        except OSError as e:
            self.logger.error(f"Filesystem error saving to {path}: {str(e)}")
            raise FileSystemError(f"Filesystem error saving image: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error saving image: {str(e)}")
            raise QRGenerationError(f"Failed to save image: {str(e)}") from e

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="QR Code Generator - Create customizable QR codes",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""Examples:
  Basic usage:
    python qr_generator.py "https://example.com" -o example.png
  
  Styled QR code:
    python qr_generator.py "https://example.com" --styled --drawer rounded --color radial
  
  Interactive mode:
    python qr_generator.py --interactive
  
  Full customization:
    python qr_generator.py "My Data" -o custom.png --version 5 --error-correction H 
    --box-size 15 --border 2 --styled --drawer circle --color vertical
"""
        )

        # Data input options
        data_group = parser.add_mutually_exclusive_group(required=False)
        data_group.add_argument(
            "data",
            nargs="?",
            help="Data to encode in the QR code"
        )
        data_group.add_argument(
            "-i", "--interactive",
            action="store_true",
            help="Run in interactive mode"
        )

        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "-o", "--output",
            dest="filename",
            help="Output filename (default: generated from data)"
        )
        output_group.add_argument(
            "-d", "--output-dir",
            default="qr_codes",
            help="Directory to save QR codes (default: qr_codes)"
        )

        # QR code parameters
        qr_group = parser.add_argument_group("QR Code Parameters")
        qr_group.add_argument(
            "-v", "--version",
            type=int,
            choices=range(1, 41),
            help="QR code version (1-40, default: auto)"
        )
        qr_group.add_argument(
            "-e", "--error-correction",
            choices=['L', 'M', 'Q', 'H'],
            default='L',
            help="Error correction level (L, M, Q, H). Default: L"
        )
        qr_group.add_argument(
            "-b", "--box-size",
            type=int,
            default=10,
            help="Size of each box in pixels. Default: 10"
        )
        qr_group.add_argument(
            "--border",
            type=int,
            default=4,
            help="Border size in boxes. Default: 4"
        )

        # Styling options
        style_group = parser.add_argument_group("Styling Options")
        style_group.add_argument(
            "-s", "--styled",
            action="store_true",
            help="Generate styled QR code"
        )
        style_group.add_argument(
            "--drawer",
            choices=['square', 'rounded', 'gapped', 'circle', 'vertical', 'horizontal'],
            default='rounded',
            help="Module drawer style for styled QR. Default: rounded"
        )
        style_group.add_argument(
            "--color",
            choices=['radial', 'square', 'horizontal', 'vertical', 'solid'],
            default='radial',
            help="Color mask style for styled QR. Default: radial"
        )
        style_group.add_argument(
            "--foreground",
            default="black",
            help="Foreground color (for solid masks). Default: black"
        )
        style_group.add_argument(
            "--background",
            default="white",
            help="Background color (for solid masks). Default: white"
        )

        return parser.parse_args()

    @staticmethod
    def get_interactive_input() -> dict:
        """Get input from user interactively with validation."""
        print("\nQR Code Generator - Interactive Mode")
        print("----------------------------------")
        
        inputs = {}
        
        # Get data
        while True:
            inputs['data'] = input("Enter data to encode (text/URL): ").strip()
            if inputs['data']:
                break
            print("Error: Data cannot be empty. Please try again.")
        
        # Get filename
        inputs['filename'] = input("Enter output filename (optional, press Enter to auto-generate): ").strip()
        if not inputs['filename']:
            inputs['filename'] = None
        
        # Get output directory
        inputs['output_dir'] = input(f"Enter output directory (default: qr_codes): ").strip()
        if not inputs['output_dir']:
            inputs['output_dir'] = "qr_codes"
        
        # Get QR parameters
        inputs['version'] = input("QR version (1-40, optional, press Enter for auto): ").strip()
        inputs['version'] = int(inputs['version']) if inputs['version'] else None
        
        inputs['error_correction'] = input("Error correction (L/M/Q/H, default: L): ").strip().upper()
        if inputs['error_correction'] not in ['L', 'M', 'Q', 'H']:
            inputs['error_correction'] = 'L'
        
        inputs['box_size'] = input("Box size in pixels (default: 10): ").strip()
        inputs['box_size'] = int(inputs['box_size']) if inputs['box_size'] else 10
        
        inputs['border'] = input("Border size in boxes (default: 4): ").strip()
        inputs['border'] = int(inputs['border']) if inputs['border'] else 4
        
        # Get styling options
        style_input = input("Create styled QR code? (y/N): ").strip().lower()
        inputs['styled'] = style_input in ('y', 'yes')
        
        if inputs['styled']:
            print("\nStyling Options:")
            print(f"Available drawer styles: {list(QRCodeGenerator.MODULE_DRAWERS.keys())}")
            inputs['drawer_style'] = input("Module drawer style (default: rounded): ").strip().lower()
            if inputs['drawer_style'] not in QRCodeGenerator.MODULE_DRAWERS:
                inputs['drawer_style'] = 'rounded'
            
            print(f"Available color masks: {list(QRCodeGenerator.COLOR_MASKS.keys())}")
            inputs['color_mask'] = input("Color mask style (default: radial): ").strip().lower()
            if inputs['color_mask'] not in QRCodeGenerator.COLOR_MASKS:
                inputs['color_mask'] = 'radial'
            
            if inputs['color_mask'] == 'solid':
                inputs['foreground_color'] = input("Foreground color (default: black): ").strip().lower()
                inputs['background_color'] = input("Background color (default: white): ").strip().lower()
        
        return inputs


def main():
    try:
        # Parse command line arguments
        args = QRCodeGenerator.parse_arguments()
        
        # Handle interactive mode
        if args.interactive or not args.data:
            user_inputs = QRCodeGenerator.get_interactive_input()
            # Merge interactive inputs with command-line args
            for key, value in user_inputs.items():
                if not hasattr(args, key) or key not in ['interactive']:
                    setattr(args, key, value)
        
        # Initialize generator with output directory
        generator = QRCodeGenerator(output_dir=args.output_dir)
        
        # Generate QR code
        qr_path = generator.generate_qr_code(
            data=args.data,
            filename=args.filename,
            version=args.version,
            error_correction=args.error_correction,
            box_size=args.box_size,
            border=args.border,
            styled=args.styled,
            drawer_style=args.drawer,
            color_mask=args.color,
            foreground_color=args.foreground,
            background_color=args.background
        )
        
        print(f"\nSuccessfully generated QR code: {qr_path}")
        print(f"Saved in directory: {os.path.abspath(args.output_dir)}")
        
    except InputValidationError as e:
        print(f"\nInput error: {e}", file=sys.stderr)
        sys.exit(1)
    except QRGenerationError as e:
        print(f"\nGeneration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()