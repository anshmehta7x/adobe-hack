#!/usr/bin/env python3
import os
import glob
import joblib
from parser import PDFParser

def main():
    # Load the pre-trained model and dependencies
    try:
        rf_model = joblib.load('random_forest_model.pkl')
        le = joblib.load('label_encoder.pkl')
    except FileNotFoundError as e:
        print(f"Error loading model files: {e}")
        return
    
    # Define the features (same as in your training)
    features = [
        'page', 'avg_font_size', 'y_position', 'is_bold', 'is_all_caps',
        'text_len', 'starts_with_numbering', 'relative_font_size',
        'norm_y_pos', 'is_centered', 'space_before', 'space_after'
    ]
    
    # Instantiate the parser
    pdf_parser = PDFParser(model=rf_model, label_encoder=le, feature_list=features)
    
    # Input and output directories
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all PDF files in the input directory
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in /app/input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF file
    for pdf_path in pdf_files:
        try:
            print(f"Processing: {os.path.basename(pdf_path)}")
            
            # Parse the PDF and save the result
            result = pdf_parser.parse_and_save(pdf_path, output_dir)
            
            if result:
                output_filename = os.path.basename(pdf_path).replace('.pdf', '.json')
                print(f"Successfully processed {os.path.basename(pdf_path)} -> {output_filename}")
            else:
                print(f"Failed to process {os.path.basename(pdf_path)}")
                
        except Exception as e:
            print(f"Error processing {os.path.basename(pdf_path)}: {str(e)}")
            continue
    
    print("Processing complete!")

if __name__ == "__main__":
    main()