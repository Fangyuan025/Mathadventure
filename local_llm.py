from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import re

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

        # 去掉多余的前缀，比如 A: Answer: 等（不区分大小写）
        cleaned = re.sub(r"^(answer|a)\s*[:：\-–]\s*", "", cleaned, flags=re.IGNORECASE)

        # 去掉控制字符和换行
        cleaned = cleaned.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

        # 只保留第一句（第一个句号为止）
        match = re.search(r"^(.*?[\.!?])", cleaned)
        if match:
            cleaned = match.group(1).strip()

        print("test:", cleaned)
        print("LLM Return to completion")
        return cleaned

    except Exception as e:
        print("LLM Error:", str(e))
        return "LLM failed to generate feedback."



