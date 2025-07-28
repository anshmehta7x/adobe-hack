from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="stduhpf/google-gemma-3-1b-it-qat-q4_0-gguf-small",
    filename="gemma-3-1b-it-q4_0_s.gguf",
    verbose=False
)

text= '''
1. Make the desired changes in the app. Bear in mind the following: 
• If you change the dimensions of the image, the image may not align correctly in 
the PDF. 
• Transparency information is preserved only for masks that are specified as 
index values in an indexed color space. 
• If you're working in Photoshop, flatten the image. 
• Image masks aren't supported. 
• If you change image modes while editing the image, you may lose valuable 
information that can be applied only in the original mode. 
•  2. In the editing app, choose File > Save. The object is automatically updated and 
displayed in the PDF when you bring Acrobat to the foreground. 
Note: For Photoshop, if the image is in a format supported by Photoshop 6.0 or later, your 
edited image is saved back into the PDF. However, if the image is in an unsupported format, 
Photoshop handles the image as a generic PDF image. The edited image is saved to disk 
instead of the PDF.
'''


def get_response(prompt):
    messages = [
        {"role": "user", "content": f"Summarise the following in 1 sentence, don't say anything else : {prompt}"}
    ]
    resp = llm.create_chat_completion(messages=messages)
    return resp["choices"][0]["message"]["content"]
