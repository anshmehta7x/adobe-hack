import os
import re
import json
import pandas as pd
from collections import Counter
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import extract 

class PDFParser:
    def __init__(self, model, label_encoder, feature_list):
        if not all([model, label_encoder, feature_list]):
            raise ValueError("Model, label_encoder, and feature_list must be provided.")
        self.model = model
        self.label_encoder = label_encoder
        self.features = feature_list

    def _group_snippets_into_lines(self, snippets, y_tolerance=2.0):
        if not snippets:
            return []
        lines = []
        current_line_snippets = [snippets[0]]
        for i in range(1, len(snippets)):
            prev_snippet = snippets[i-1]
            current_snippet = snippets[i]
            if (current_snippet['page'] == prev_snippet['page'] and 
                abs(current_snippet['y_position'] - prev_snippet['y_position']) < y_tolerance):
                current_line_snippets.append(current_snippet)
            else:
                lines.append(current_line_snippets)
                current_line_snippets = [current_snippet]
        lines.append(current_line_snippets)
        return lines

    def _process_lines(self, grouped_lines, pdf_path):
        processed_lines = []
        for line_snippets in grouped_lines:
            line_snippets.sort(key=lambda s: s['bbox'][0])
            full_text = "".join(s['text'] for s in line_snippets).strip()
            if not full_text:
                continue
            toc_pattern = re.compile(r'^(.*?)\\.{3,}\\s*\\d+$')
            match = toc_pattern.match(full_text)
            if match:
                full_text = match.group(1).strip()
            elif full_text.endswith('...') and full_text.count('.') > 3:
                full_text = full_text.rstrip(' .')

            x0 = min(s['bbox'][0] for s in line_snippets)
            y0 = min(s['bbox'][1] for s in line_snippets)
            x1 = max(s['bbox'][2] for s in line_snippets)
            y1 = max(s['bbox'][3] for s in line_snippets)
            
            avg_font_size = sum(s['font_size'] for s in line_snippets) / len(line_snippets)
            
            processed_lines.append({
                "text": full_text,
                "page": line_snippets[0]['page'],
                "avg_font_size": avg_font_size,
                "y_position": line_snippets[0]['y_position'],
                "bbox": (x0, y0, x1, y1),
                "font_name": line_snippets[0]['font_name'],
                "source_pdf": os.path.basename(pdf_path)
            })
        return processed_lines

    def _get_doc_stats(self, lines):
        font_sizes = [round(l['avg_font_size'], 2) for l in lines if l['text']]
        if not font_sizes:
            return {'modal_font_size': 10.0}
        modal_font_size = Counter(font_sizes).most_common(1)[0][0]
        return {'modal_font_size': modal_font_size}

    def _engineer_features(self, lines, doc_stats, page_height, page_width):
        modal_font_size = doc_stats['modal_font_size']
        for i, line in enumerate(lines):
            font_name_lower = line['font_name'].lower()
            line['is_bold'] = any(indicator in font_name_lower for indicator in ['bold', 'black', 'heavy', 'sembold'])
            line['is_all_caps'] = line['text'].isupper() and len(line['text']) > 3
            line['text_len'] = len(line['text'])
            numbering_pattern = re.compile(
                r'^\s*(?:(?:Chapter|Section)\s+[\w\d]+|'
                r'\d{1,2}(?:\.\d{1,2})*\.?|'
                r'[A-Z]\.|'
                r'\([a-z]\)|'
                r'[ivx]+\.)'
            )
            line['starts_with_numbering'] = bool(numbering_pattern.match(line['text']))
            if modal_font_size > 0:
                line['relative_font_size'] = line['avg_font_size'] / modal_font_size
            else:
                line['relative_font_size'] = 1.0

            line['norm_y_pos'] = line['y_position'] / page_height
            line_center = (line['bbox'][0] + line['bbox'][2]) / 2
            page_center = page_width / 2
            line['is_centered'] = abs(line_center - page_center) < (0.1 * page_width)
            space_before = -1
            space_after = -1
            
            if i > 0 and lines[i-1]['page'] == line['page']:
                prev_line_bottom = lines[i-1]['bbox'][3]
                current_line_top = line['bbox'][1]
                space_before = current_line_top - prev_line_bottom
                
            if i < len(lines) - 1 and lines[i+1]['page'] == line['page']:
                current_line_bottom = line['bbox'][3]
                next_line_top = lines[i+1]['bbox'][1]
                space_after = next_line_top - current_line_bottom

            line['space_before'] = space_before
            line['space_after'] = space_after
        return lines

    def _create_features_for_new_pdf(self, pdf_path):
        print(f"Processing PDF: {os.path.basename(pdf_path)}")
        extractor = extract.TextExtractor(pdf_path)
        texts = extractor.extract_text_from_all_pages_multiprocessing()
        
        try:
            dims = extractor.get_page_dimensions(0)
            PAGE_WIDTH = dims["width"]
            PAGE_HEIGHT = dims["height"]
        except (IndexError, Exception) as e:
            print(f"Warning: Could not get page dimensions for {pdf_path}. Using default values. Error: {e}")
            PAGE_WIDTH, PAGE_HEIGHT = 612, 792 

        sorted_snippets = sorted(texts, key=lambda s: (s['page'], s['y_position'], s['bbox'][0]))
        grouped_lines = self._group_snippets_into_lines(sorted_snippets)
        final_lines = self._process_lines(grouped_lines, pdf_path)
        
        if not final_lines:
            return pd.DataFrame()

        document_stats = self._get_doc_stats(final_lines)
        featured_lines = self._engineer_features(final_lines, document_stats, PAGE_HEIGHT, PAGE_WIDTH)
        
        for line in featured_lines:
            line['page'] -= 1
            
        return pd.DataFrame(featured_lines)

    def _format_predictions_to_json(self, df_with_predictions):
        title_df = df_with_predictions[df_with_predictions['predicted_label'] == 'Title']
        document_title = " ".join(title_df.sort_values(by='bbox')['text'].tolist()) if not title_df.empty else "Title Not Found"

        outline = []
        heading_df = df_with_predictions[df_with_predictions['predicted_label'].str.startswith('H', na=False)]
        
        for _, row in heading_df.iterrows():
            outline.append({
                "level": row['predicted_label'],
                "text": row['text'],
                "page": row['page'] + 1
            })
            
        output_json = {
            "title": document_title,
            "outline": outline
        }
        return output_json

    def parse_and_save(self, pdf_path, output_dir="."):
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file not found at {pdf_path}")
            return None

        try:
            new_pdf_df = self._create_features_for_new_pdf(pdf_path)
            if new_pdf_df.empty:
                print(f"Could not extract any text lines from {pdf_path}.")
                return None

            X_new = new_pdf_df[self.features]
            predictions_encoded = self.model.predict(X_new)
            predictions_labels = self.label_encoder.inverse_transform(predictions_encoded)
            new_pdf_df['predicted_label'] = predictions_labels
            
            final_output = self._format_predictions_to_json(new_pdf_df)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            output_filename = os.path.basename(pdf_path).replace('.pdf', '.json')
            output_filepath = os.path.join(output_dir, output_filename)
            
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=4)
                
            print(f"Prediction complete. Output saved to {output_filepath}")
            return final_output
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None