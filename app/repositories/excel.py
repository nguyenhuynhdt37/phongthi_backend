from io import BytesIO
import re
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import pandas as pd
from app.libs.formart.response import CustomException, format_response


def find_header_row(df: pd.DataFrame):
    for i in range(len(df)):
        if "Mã sinh viên" in df.iloc[i].values:
            return i
    return None


def extract_course_code(course_info: str):
    """Tách mã học phần từ chuỗi."""
    match = re.search(r"Mã HP:\s*(\w+)", str(course_info))
    return match.group(1) if match else None


import pandas as pd
from typing import List
from io import BytesIO
from fastapi import UploadFile
from typing import Optional


async def handleExcel(files: List[UploadFile]):
    if not files:
        raise CustomException(404, "Không có file nào được tải lên.")
    print(files)
    data = {}  # Dictionary lưu DataFrame theo mã môn
    total_files = len(files)
    total_files_valid = 0
    for file_index, file in enumerate(files):
        if not file.filename:
            total_files_valid += 1
            continue

        content = await file.read()
        file_stream = BytesIO(content)

        # Đọc file Excel hoặc CSV
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file_stream, header=None, sheet_name=0)
        elif file.filename.endswith(".csv"):
            df = pd.read_csv(file_stream, header=None)
        else:
            total_files_valid += 1
            continue
        # Xác định dòng tiêu đề
        index_Column = find_header_row(df)
        if index_Column is None:
            raise ValueError("Header row not found.")

        ma_mon = extract_course_code(df.iloc[index_Column - 1].values[0])
        if ma_mon is None:
            total_files_valid += 1
            continue

        df.columns = list(df.iloc[index_Column].values)
        df = df.iloc[index_Column + 1 :].reset_index(drop=True)
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all")

        # Loại bỏ các dòng không cần thiết
        df = df[
            ~df.apply(
                lambda row: row.astype(str)
                .str.contains("Nghệ an, ngày|Giảng viên", case=False, na=False)
                .any(),
                axis=1,
            )
        ]

        attendance_cols = [f"B{i}" for i in range(1, 16) if f"B{i}" in df.columns]
        df_attendance = df[
            ["Mã sinh viên", "Họ và tên", "Ghi chú", "Ngày sinh"] + attendance_cols
        ]

        # Chuyển đổi giá trị vắng và phép
        for col in attendance_cols:
            df_attendance[col] = (
                df_attendance[col]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({"vắng": -1, "phép": -0.5, "v": -1, "p": -0.5, "nan": 0})
            )

        df_attendance[attendance_cols] = (
            df_attendance[attendance_cols]
            .apply(pd.to_numeric, errors="coerce")
            .fillna(0)
        )

        # Tính tổng số buổi vắng
        df_attendance["Tổng vắng"] = df_attendance[attendance_cols].sum(axis=1)

        # Đánh dấu sinh viên có số buổi vắng > 3
        df_attendance["Đủ điều kiện dự thi"] = df_attendance["Tổng vắng"].apply(
            lambda x: 0 if x < -3 else 1
        )
        print(df.columns)
        column_mapping = {
            "Mã sinh viên": "student_id",
            "Họ và tên": "full_name",
            "Ngày sinh": "date_of_birth",
            "Ghi chú": "notes",
            "Tổng vắng": "total_absences",
            "Đủ điều kiện dự thi": "eligible_for_exam",
        }
        # Đổi tên cột theo mapping
        df_attendance.rename(columns=column_mapping, inplace=True)
        # Tách họ và tên riêng biệt
        # Đặt lại tiêu đề cho cột
        columns = df_attendance.columns.values
        # df[["first_name", "last_name"]] = df["full_name"]
        columns[1] = "first_name"
        columns[2] = "last_name"
        df_attendance.columns = columns
        df_attendance = df_attendance.drop(columns=attendance_cols, errors="ignore")
        # Nếu mã môn đã tồn tại trong data, thì nối dữ liệu nhưng KHÔNG gộp dòng trùng mã sinh viên
        if ma_mon in data:
            existing_students = set(student["student_id"] for student in data[ma_mon])
            new_data = df_attendance[
                ~df_attendance["student_id"].isin(existing_students)
            ].to_dict(orient="records")
            data[ma_mon].extend(new_data)
        else:
            data[ma_mon] = df_attendance.to_dict(orient="records")
    if total_files == total_files_valid:
        raise CustomException(404, "Không có dữ liệu nào hợp lệ trong file.")
    return format_response(
        status_code=200,
        data={
            "data": data,
            "total_files": total_files,
            "total_files_valid": total_files_valid,
        },
        message="Thành công",
    )
