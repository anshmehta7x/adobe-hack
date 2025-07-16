import pymupdf
import time
from multiprocessing import Pool, cpu_count


class TextExtractor:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.document = pymupdf.open(filename)
        if not self.document:
            raise ValueError(f"Failed to open document: {filename}")

        self.metadata = {
            "title": self.document.metadata.get("title", "Unknown Title"),
            "author": self.document.metadata.get("author", "Unknown Author"),
            "subject": self.document.metadata.get("subject", "Unknown Subject"),
            "keywords": self.document.metadata.get("keywords", "Unknown Keywords"),
            "creationDate": self.document.metadata.get("creationDate", "Unknown Creation Date"),
            "creator": self.document.metadata.get("creator", "Unknown Creator"),
            "modDate": self.document.metadata.get("modDate", "Unknown Modification Date"),
            "producer": self.document.metadata.get("producer", "Unknown Producer"),
            "format": self.document.metadata.get("format", "Unknown format"),
            "encryption": self.document.metadata.get("encryption", "Unknown encryption used"),
        }

        self.name = self.document.name
        self.page_count = len(self.document)

    def get_metadata(self):
        return self.metadata

    def extract_text_from_page(self, page_number):
        if page_number < 0 or page_number >= self.page_count:
            raise ValueError(f"Page number {page_number} is out of range. Document has {self.page_count} pages.")

        page = self.document.load_page(page_number)
        texts = page.get_text("dict")['blocks']
        for text in texts:
            if 'lines' in text:
                for line in text['lines']:
                    for span in line['spans']:
                        yield {
                            "text": span['text'],
                            "font_size": span['size'],
                            "font_name": span['font'],
                            "flags": span['flags'],
                            "page": page_number + 1,
                            "bbox": span['bbox'],
                            "y_position": span['bbox'][1]
                        }

    def extract_text_from_all_pages(self):
        all_texts = []
        for page_number in range(self.page_count):
            all_texts.extend(list(self.extract_text_from_page(page_number)))
        return all_texts

    def extract_text_from_all_pages_multiprocessing(self):
        cpu = cpu_count()
        vectors = [(i, cpu, self.filename, self.page_count) for i in range(cpu)]
        
        with Pool() as pool:
            results = pool.map(extract_text_segment, vectors)
        
        all_texts = []
        for result in results:
            all_texts.extend(result)
        return all_texts


def extract_text_segment(vector):
    idx = vector[0]
    cpu = vector[1]
    filename = vector[2]
    total_pages = vector[3]
    
    doc = pymupdf.open(filename)
    
    seg_size = int(total_pages / cpu + 1)
    seg_from = idx * seg_size
    seg_to = min(seg_from + seg_size, total_pages)
    
    segment_texts = []
    
    for page_number in range(seg_from, seg_to):
        page = doc.load_page(page_number)
        texts = page.get_text("dict")['blocks']
        for text in texts:
            if 'lines' in text:
                for line in text['lines']:
                    for span in line['spans']:
                        segment_texts.append({
                            "text": span['text'],
                            "font_size": span['size'],
                            "font_name": span['font'],
                            "flags": span['flags'],
                            "page": page_number + 1,
                            "bbox": span['bbox'],
                            "y_position": span['bbox'][1]
                        })
    
    return segment_texts


if __name__ == "__main__":
    extractor = TextExtractor("../hackathon-task/sample-1a/Datasets/Pdfs/program.pdf")
    
    t0 = time.perf_counter()
    all_texts = extractor.extract_text_from_all_pages_multiprocessing()
    t1 = time.perf_counter()
    
    # print(all_texts)
    print(f"Multiprocessing time: {t1 - t0:.2f} seconds")
