import pandas as pd


file = "/home/huynh/Downloads/K62 KTPM Thiết kế và xây dựng phần mềm(124.2)_LT_01_(KTPM).xlsx"
df = pd.read_excel(file, header=None)
# df.columns = df.columns.str.strip()
i = 0
for i in range(len(df.columns)):
    if "Mã sinh viên" in df.iloc[i].values:
        i = i
        break

# df = df.drop(columns=["B" in df.columns])
print(len(df.columns))  # Số lượng cột hiện tại
print(len(df.iloc[i].values))  # Số lượng giá trị trong dòng i
# print(df.iloc[i].values)
