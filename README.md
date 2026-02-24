# Local LLaMA Backend (Test Project)

## 1. Giới thiệu
Dự án này xây dựng một backend AI chạy **local** nhằm mục đích **thử nghiệm và đánh giá**
việc tích hợp mô hình ngôn ngữ lớn (LLaMA) với framework FastAPI.


## 2. Mục tiêu thử nghiệm
- Chạy mô hình LLaMA local bằng định dạng GGUF
- Load mô hình một lần khi server khởi động
- Cung cấp API đơn giản để gửi câu hỏi và nhận phản hồi từ mô hình
- Đánh giá hiệu năng, độ ổn định và khả năng mở rộng của hệ thống


## 3. Công nghệ sử dụng
- Python
- FastAPI
- LLaMA (GGUF) thông qua thư viện `ctransformers`
- Uvicorn

## 4. Yêu cầu hệ thống
- Python 3.8 trở lên
- RAM: tối thiểu 8GB (khuyến nghị 16GB+)
- GPU: không bắt buộc (có GPU sẽ cải thiện tốc độ)
- Disk: tối thiểu 10GB trống để lưu model

## 5. Tạo và kích hoạt môi trường ảo

### Windows
```bash
py -3.11 -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình Model

Tải model LLaMA định dạng GGUF (ví dụ: LLaMA 2 7B Chat Q4_K_M)

Đặt file model vào thư mục models/

Model không được đưa lên Git repository

Ví dụ cấu hình trong code:

MODEL_PATH = "models/llama-2-7b-chat.Q4_K_M.gguf"

# Chạy ứng dụng
uvicorn main:app --reload

Sau khi chạy, truy cập:

Swagger UI: http://127.0.0.1:8000/docs