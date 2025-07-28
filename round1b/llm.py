from llama_cpp import Llama

llm = Llama.from_pretrained(
    repo_id="stduhpf/google-gemma-3-1b-it-qat-q4_0-gguf-small",
    filename="gemma-3-1b-it-q4_0_s.gguf",
    verbose=False
)

def get_response(prompt,persona):

    words = prompt.split()
    estimated_max_words = 512 * 0.75  # heuristic for token-to-word ratio
    truncated_words = words[:int(estimated_max_words)]
    truncated_prompt = " ".join(truncated_words)


    messages = [
        {"role": "system", "content": f"{{Summarize the following text from point of view of a {persona} in exactly one sentence. No extra commentary."},
        {"role": "user", "content": truncated_prompt}
    ]
    resp = llm.create_chat_completion(messages=messages)
    summary = resp["choices"][0]["message"]["content"]
    return summary.strip()
