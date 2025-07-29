from llama_cpp import Llama

llm = llm = Llama(
    model_path="/app/models/gemma-3-1b-it-q4_0_s.gguf",
    verbose=False,
    n_ctx=512 # Setting context size is good practice
)

def get_response(prompt, persona):
    max_context_tokens = 512
    max_output_tokens = 64

    system_prompt = f"Summarize the following text from point of view of a {persona} in exactly one sentence. No extra commentary."
    system_tokens = len(llm.tokenize(system_prompt.encode("utf-8")))

    words = prompt.split()

    # Use binary search for fast truncation
    low, high = 0, len(words)
    best_prompt = ""

    while low <= high:
        mid = (low + high) // 2
        test_prompt = " ".join(words[:mid])
        test_tokens = len(llm.tokenize(test_prompt.encode("utf-8")))
        total_tokens = system_tokens + test_tokens + max_output_tokens

        if total_tokens <= max_context_tokens:
            best_prompt = test_prompt
            low = mid + 1
        else:
            high = mid - 1

    # Fallback if no words fit (shouldn't happen)
    if not best_prompt:
        best_prompt = "Too long to summarize, so truncated heavily."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": best_prompt}
    ]

    try:
        resp = llm.create_chat_completion(messages=messages)
        summary = resp["choices"][0]["message"]["content"]
        return summary.strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Example usage
if __name__ == "__main__":
    example_prompt = "The universe is vast and full of mysteries. Scientists are constantly exploring the cosmos to understand its origins and the fundamental laws that govern it. "
    example_persona = "scientist"
    response = get_response(example_prompt, example_persona)
    print(response)  # Output the summary
