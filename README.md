# ⚙️ Smart Exam Room Backend REST API (FastAPI & MySQL)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)

Máy chủ Backend dịch vụ cho hệ thống **Phòng Thi Thông Minh**. Xử lý danh sách thí sinh, sơ đồ chỗ ngồi tự động, điểm danh thi và bảo mật JWT.

---

## ✨ Tính Năng

- 💺 **Thuật toán sắp xếp sơ đồ phòng thi:** Tự động chia chỗ ngồi cho thí sinh tránh trùng lặp môn thi/mã đề.
- 🔑 **Auth & Phân quyền:** Xác thực Cán bộ coi thi & Admin quản lý.

```bash
git clone https://github.com/nguyenhuynhdt37/phongthi-backend-python.git
cd phongthi-backend-python
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 👨‍💻 Tác Giả

**Nguyễn Xuân Huỳnh** — [GitHub Profile](https://github.com/nguyenhuynhdt37)
