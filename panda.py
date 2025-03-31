from operator import index
import re
import pandas as pd


def find_header_row(df: pd.DataFrame):
    for i in range(len(df)):
        if "Mã sinh viên" in df.iloc[i].values:
            return i
    return None


def extract_course_code(course_info: str):
    """Tách mã học phần từ chuỗi."""
    match = re.search(r"Mã HP:\s*(\w+)", str(course_info))
    return match.group(1) if match else None


file = @"C://Users//khanh//Documents//K62 KTPM Thiết kế và xây dựng phần mềm(124.2)_LT_01_(KTPM).xlsx"
df = pd.read_excel(file, header=None)

index_column = find_header_row(df)

if index_column is None:
    raise ValueError("Header row not found.")

columns = df.iloc[index_column]

ma_hp = df.iloc[index_column - 1]

print(ma_hp.values)
