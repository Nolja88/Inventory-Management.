import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd

# 앱 설정
st.set_page_config(page_title="대광건설기계 실시간 재고관리", layout="wide")

# 1. 구글 시트 연결 (실시간 공유의 핵심)
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. 데이터 불러오기 (TTL 5초 설정으로 실시간성 확보)
@st.cache_data(ttl=5)
def load_inventory():
    return conn.read(worksheet="Inventory")

df = load_inventory()

st.title("🚜 대광건설기계 실시간 재고관리")

# 3. 사이드바: 수입처 -> 모델 계층형 선택 (창 길어짐 방지)
st.sidebar.header("🔍 카테고리 선택")
vendor = st.sidebar.selectbox("1. 수입처 선택", df['수입처'].unique())
models = df[df['수입처'] == vendor]['모델명'].unique()
target_model = st.sidebar.selectbox("2. 완제품 모델 선택", models)

# 4. 메인 화면: 선택한 모델의 데이터만 필터링
st.subheader(f"📍 {target_model} 점검 리스트")
filtered_df = df[df['모델명'] == target_model]

# 5. 실시간 편집 에디터 (3인이 동시에 다른 행 수정 가능)
edited_df = st.data_editor(
    filtered_df,
    column_config={
        "현재재고": st.column_config.NumberColumn("실사수량", min_value=0),
        "비고": st.column_config.TextColumn("특이사항"),
        "점검완료": st.column_config.CheckboxColumn("완료")
    },
    disabled=["수입처", "모델명", "부품명"], # 중요 정보는 수정 불가 처리
    hide_index=True,
    use_container_width=True
)

# 6. 저장 버튼 (누르는 즉시 구글 시트 업데이트)
if st.button("💾 변경사항 전체 저장"):
    # 전체 데이터에서 수정한 부분만 업데이트 후 구글 시트로 전송
    df.update(edited_df)
    conn.update(worksheet="Inventory", data=df)
    st.success("데이터가 실시간으로 공유되었습니다!")
    st.balloons()
