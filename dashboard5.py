import streamlit as st
import pandas as pd
import os
import glob
import base64

# PDF 미리보기용 함수
def display_pdf(file_path):
    if not file_path.lower().endswith(".pdf"):
        st.warning("❗ 현재 미리보기는 PDF 형식만 지원됩니다.")
        return

    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_view = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
    st.markdown(pdf_view, unsafe_allow_html=True)

# CSV 로딩
df = pd.read_csv("문서등록대장.csv", encoding="cp949")

# 필요한 컬럼만
selected_columns = [
    "문서번호", "제목", "등록일자", "수신(발신)자", "연계유형", "공개구분",
    "공개제한근거", "첨부파일여부", "쪽수", "과제카드명", "최초발송일자"
]
df_selected = df[selected_columns]

# 페이지 설정
st.set_page_config(page_title="📑 문서등록대장 대시보드", layout="wide")
st.title("📑 문서등록대장 대시보드")

# 제목 검색
title_keyword = st.text_input("🔍 제목 검색:")

# 공개구분 필터
공개구분_옵션 = df_selected["공개구분"].dropna().unique().tolist()
선택_공개구분 = st.multiselect("공개구분 필터:", 공개구분_옵션, default=공개구분_옵션)

# 필터링
filtered_df = df_selected[
    df_selected["공개구분"].isin(선택_공개구분) &
    df_selected["제목"].str.contains(title_keyword, case=False, na=False)
]

# 분할 화면
left_col, right_col = st.columns([1, 1.5])

with left_col:
    st.subheader("📂 첨부파일 문서 목록")
    selected_file = None
    for _, row in filtered_df.iterrows():
        if row["첨부파일여부"] == "Y":
            문서번호 = str(row["문서번호"]).strip()
            제목 = row["제목"]
            search_pattern = os.path.join("attachment0", f"[{문서번호}*")
            matched_files = glob.glob(search_pattern)

            if matched_files:
                with st.expander(f"📌 {제목} ({문서번호})"):
                    for path in matched_files:
                        file_name = os.path.basename(path)
                        if st.button(f"📎 {file_name}", key=path):
                            selected_file = path

with right_col:
    st.subheader("📄 미리보기 / 파일 열기")
    if selected_file:
        file_name = os.path.basename(selected_file)
        st.info(f"📝 선택한 파일: `{file_name}`")

        # 새 창 열기 링크 (배포 환경에서만 동작)
        file_url = f"/{selected_file}"
        st.markdown(f'<a href="{file_url}" target="_blank">🔗 새 탭에서 열기</a>', unsafe_allow_html=True)

        # 다운로드
        with open(selected_file, "rb") as f:
            file_bytes = f.read()
            st.download_button(label="⬇️ 파일 다운로드", data=file_bytes, file_name=file_name)

        # PDF 미리보기
        display_pdf(selected_file)
