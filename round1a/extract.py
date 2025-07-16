import pymupdf # type: ignore

class TextExtractor:
    
    def __init__(self, filename) -> None:
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
                            "page": page_number + 1,  # keep output 1-based for user
                            "bbox": span['bbox'],
                            "y_position": span['bbox'][1]
                        }


    def extract_text_from_all_pages(self):
        all_texts = []
        for page_number in range(self.page_count):  # 0-based
            all_texts.extend(list(self.extract_text_from_page(page_number)))
        return all_texts


if __name__ == "__main__":
    # Example usage
    extractor = TextExtractor("../hackathon-task/sample-1a/Datasets/Pdfs/STEMPathwaysFlyer.pdf")
    # print(extractor.get_metadata())
    all_texts = extractor.extract_text_from_all_pages()
    print(all_texts[:5])


'''
[
    {
        "text": "Overview Foundation Level Extensions",
        "font_size": 22.5,
        "font_name": "TimesNewRoman-Bold",
        "flags": 20,
        "page": 1,
        "bbox": [72.0, 80.0, 400.0, 100.0],
        "y_position": 80.0
    },
    {
        "text": "2.1 Intended Audience",
        "font_size": 14.0,
        "font_name": "Arial-Bold",
        "flags": 20,
        "page": 6,
        "bbox": [72.0, 140.0, 400.0, 160.0],
        "y_position": 140.0
    },
    ...
]
'''