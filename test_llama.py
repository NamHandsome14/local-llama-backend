from ctransformers import AutoModelForCausalLM
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

print("🔄 Đang load model LLaMA 2, vui lòng chờ...")

llm = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    model_file="llama-2-7b-chat.Q4_K_M.gguf",
    model_type="llama",
    context_length=2048,
    max_new_tokens=256,
    gpu_layers=0,
    local_files_only=True
)

print("🤖 Model đã load xong!\n")

# ===== TEST PROMPT =====
prompt = "Giải thích ngắn gọn LLaMA là gì bằng tiếng Việt."

print("📨 Prompt:")
print(prompt)
print("\n🧠 AI đang trả lời...\n")

response = llm(prompt)

print("✅ CÂU TRẢ LỜI:\n")
print(response)
