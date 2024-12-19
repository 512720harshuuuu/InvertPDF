import fitz  # PyMuPDF
import os
from PIL import Image, ImageOps
import io
import argparse
from typing import Optional, Tuple

class PDFInverter:
    def __init__(self):
        self.supported_formats = ['.pdf']

    def invert_colors(self, input_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Invert colors in a PDF (black becomes white, white becomes black).
        
        Args:
            input_path (str): Path to the input PDF file
            output_path (str, optional): Path for the output PDF file. 
                                       If not provided, will append '_inverted' to input filename
        
        Returns:
            Tuple[bool, str]: (Success status, Message/Error description)
        """
        try:
            # Validate input file
            if not os.path.exists(input_path):
                return False, f"Input file not found: {input_path}"
            
            if not input_path.lower().endswith('.pdf'):
                return False, "Input file must be a PDF"
            
            # Generate output path if not provided
            if output_path is None:
                file_name, file_ext = os.path.splitext(input_path)
                output_path = f"{file_name}_inverted{file_ext}"
            
            # Open the PDF
            pdf_document = fitz.open(input_path)
            output_pdf = fitz.open()
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Get the page as an image with higher resolution for better quality
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Invert the colors
                inverted_img = ImageOps.invert(img)
                
                # Convert back to bytes
                img_byte_arr = io.BytesIO()
                inverted_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Create new PDF page
                new_page = output_pdf.new_page(width=page.rect.width,
                                             height=page.rect.height)
                new_page.insert_image(new_page.rect, stream=img_byte_arr)
            
            # Save the output PDF
            output_pdf.save(output_path)
            output_pdf.close()
            pdf_document.close()
            
            return True, f"Successfully inverted PDF colors: {output_path}"
            
        except Exception as e:
            return False, f"Error inverting PDF colors: {str(e)}"

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Invert colors in a PDF')
    parser.add_argument('input_path', help='Path to the input PDF file')
    parser.add_argument('--output_path', help='Path for the output PDF file (optional)')
    
    args = parser.parse_args()
    
    # Create inverter and process the file
    inverter = PDFInverter()
    success, message = inverter.invert_colors(args.input_path, args.output_path)
    
    # Print result
    if success:
        print("\033[92m" + message + "\033[0m")  # Green text for success
    else:
        print("\033[91m" + message + "\033[0m")  # Red text for error

if __name__ == "__main__":
    main()