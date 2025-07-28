import joblib
from parser import PDFParser

# 1. Load the saved model and encoder
rf_model = joblib.load('random_forest_model.pkl')
le = joblib.load('label_encoder.pkl')

# 2. Define the feature list (must match the one used for training)
features = [
    'page', 'avg_font_size', 'y_position', 'is_bold', 'is_all_caps',
    'text_len', 'starts_with_numbering', 'relative_font_size',
    'norm_y_pos', 'is_centered', 'space_before', 'space_after'
]

# 3. Instantiate the parser with the loaded objects
pdf_parser = PDFParser(model=rf_model, label_encoder=le, feature_list=features)

# 4. Specify the PDF you want to process
pdf_file_path = "../hackathon-task/sample-1a/Datasets/Pdfs/program.pdf"  # <-- CHANGE THIS
output_dir = "json_outputs"

# 5. Run the parsing and save the JSON output
pdf_parser.parse_and_save(pdf_file_path, output_dir=output_dir)