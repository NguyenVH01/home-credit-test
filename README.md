# Home Credit 360° Review System

Hệ thống đánh giá hiệu suất 360° cho Home Credit, cho phép thu thập phản hồi đa chiều về hiệu quả làm việc của nhân viên.

## Tính năng chính

- Đăng nhập và phân quyền người dùng (Admin, Manager, Employee)
- Quản lý kỳ đánh giá
- Đánh giá hiệu suất 360° (từ cấp trên, đồng nghiệp, cấp dưới)
- Báo cáo và phân tích
- Giao diện người dùng đơn giản, hiện đại

## Yêu cầu hệ thống

- Python 3.8+
- SQLite3

## Cài đặt

1. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Cài đặt các gói phụ thuộc:
```bash
pip install -r requirements.txt
```

3. Cấu hình môi trường:
- Sao chép file `.env.example` thành `.env`
- Cập nhật các biến môi trường trong file `.env`

4. Khởi tạo cơ sở dữ liệu và tài khoản mặc định:
```bash
python init_data.py
```

5. Khởi chạy ứng dụng:
```bash
streamlit run app.py
```

## Cấu trúc dự án

```
├── app.py              # Ứng dụng Streamlit chính
├── models.py           # Mô hình dữ liệu
├── auth.py             # Xác thực và phân quyền
├── init_data.py        # Khởi tạo dữ liệu mặc định
├── requirements.txt    # Các gói phụ thuộc
├── .env               # Cấu hình môi trường
└── README.md          # Tài liệu hướng dẫn
```

## Tài khoản mặc định

- Admin 1:
  - Username: admin
  - Password: admin123

- Admin 2:
  - Username: ngoc.truc
  - Password: ngoctruc

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issue hoặc pull request để cải thiện hệ thống. 