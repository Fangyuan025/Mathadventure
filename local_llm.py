from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Use device:", device)

tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")
model = AutoModelForCausalLM.from_pretrained("microsoft/phi-1_5")

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device == "cuda" else -1
)

def ask_local_llm(prompt: str) -> str:
    print("LLM Request received, generating... " + prompt)

    try:
        outputs = generator(
            prompt,
            max_new_tokens=60,
            do_sample=False
        )
        print("LLM raw output:", outputs)

        response = outputs[0]["generated_text"]
        cleaned = response.replace(prompt, "").strip()

        if "." in cleaned:
            cleaned = cleaned.split(".")[0] + "."
        elif "\n" in cleaned:
            cleaned = cleaned.split("\n")[0]

        print ("test: " + cleaned)
        print("LLM Return to completion")
        return cleaned
    except Exception as e:
        print("LLM Error:", str(e))
        return "LLM failed to generate feedback."



