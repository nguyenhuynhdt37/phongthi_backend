import re
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
import pandas as pd
from app.libs.formart.response import CustomException


def find_header_row(df: pd.DataFrame):
    for i in range(len(df)):
        if "Mã sinh viên" in df.iloc[i].values:
            return i
    return None


def extract_course_code(course_info: str):
    """Tách mã học phần từ chuỗi."""
    match = re.search(r"Mã HP:\s*(\w+)", str(course_info))
    return match.group(1) if match else None


def handleExcel(files: List[UploadFile]):
    data = {}

    for file in files:
        if not file.filename:
            raise ValueError("File name is empty.")

        # Đọc file Excel hoặc CSV
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file, header=None, sheet_name=0)
        elif file.filename.endswith(".csv"):
            df = pd.read_csv(file.file, header=None)
        else:
            raise ValueError(
                "Invalid file format. Only .xlsx and .csv files are supported."
            )

        # Xác định dòng tiêu đề
        index_Column = find_header_row(df)
        if index_Column is None:
            raise ValueError("Header row not found.")

        df.columns = df.iloc[index_Column]
        df = df.iloc[index_Column + 1 :].reset_index(drop=True)

        # Loại bỏ các dòng chứa chữ "Nghệ an, ngày" và "Giảng viên"
        df = df[
            ~df.apply(
                lambda row: row.astype(str)
                .str.contains("Nghệ an, ngày|Giảng viên", case=False, na=False)
                .any(),
                axis=1,
            )
        ]

        # Tìm mã học phần
        df["Mã HP"] = df.apply(extract_course_code, axis=1)

        # Nhóm dữ liệu theo mã học phần
        for course_code, group_df in df.groupby("Mã HP"):
            if course_code:
                if course_code not in data:
                    data[course_code] = []
                data[course_code].append(group_df.drop(columns=["Mã HP"]))

    # Gộp các DataFrame có cùng mã học phần
    merged_data = {
        code: pd.concat(dfs, ignore_index=True) for code, dfs in data.items()
    }

    return merged_data
