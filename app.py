import streamlit as st
import pandas as pd

# 한 화면 전체 활용을 위해 Wide 레이아웃 적용
st.set_page_config(page_title="수강신청 명렬표 확인 시스템", layout="wide")

# 인쇄 시 불필요한 UI(사이드바, 업로드버튼, 헤더)를 숨기고 A4 가로에 맞추는 CSS
st.markdown("""
    <style>
        /* 화면 표시용 밀도 조정 */
        .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; }
        div[data-testid="stSidebar"] { width: 220px !important; }
        
        /* 인쇄 전용 CSS (@media print) */
        @media print {
            @page { size: A4 landscape; margin: 8mm; }
            body { background-color: white !important; font-size: 10pt; }
            /* 사이드바, 업로드 버튼, 구분선, 인쇄 제외 요소 숨기기 */
            section[data-testid="stSidebar"], 
            .stFileUploader, 
            header, 
            footer, 
            .no-print { display: none !important; }
            
            /* 명렬표 및 카드를 한 화면에 맞춤 */
            .main .block-container { padding: 0 !important; margin: 0 !important; width: 100% !important; }
            .print-table-container { height: auto !important; max-height: none !important; border: 1px solid #999 !important; }
            .stColumns { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; page-break-inside: avoid; }
            div[data-testid="column"] { width: 100% !important; margin: 0 1px !important; }
        }

        /* 콤팩트 테이블 스타일 */
        table.compact-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; }
        table.compact-table th { background-color: #f2f2f2; border: 1px solid #ccc; padding: 2px 1px; font-weight: bold; }
        table.compact-table td { border: 1px solid #ddd; padding: 2px 1px; height: 18px; }
        .applied-row { background-color: #FFEB3B !important; color: #000000 !important; font-weight: bold; }
        .not-applied-row { color: #BBBBBB !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 수강신청 과목별 명렬표")

uploaded_file = st.file_uploader("수강편성 엑셀 파일(.xlsx)을 업로드하세요", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name=0)
    
    col_id = df.columns[0]
    col_name = df.columns[1]
    
    # 학번 정리 (5자리 문자열)
    df[col_id] = df[col_id].astype(str).str.split('.').str[0].str.zfill(5)
    
    subject_list = df.columns[2:].tolist()
    
    st.sidebar.header("🔍 과목 선택")
    selected_subject = st.sidebar.selectbox("과목을 선택하세요:", subject_list)
    
    if selected_subject:
        # 해당 과목 신청 여부
        df['신청여부'] = df[selected_subject].apply(
            lambda x: True if pd.notna(x) and str(x).strip() not in ['', '0', '0.0'] else False
        )
        
        # 반 구분
        df['반'] = df[col_id].str[1:3] + "반"
        
        # 상단 요약 정보 (총 인원 및 안내)
        class_summary = df.groupby('반')['신청여부'].sum().astype(int)
        total_count = class_summary.sum()
        
        col_title, col_print_btn = st.columns([4, 1])
        with col_title:
            st.subheader(f"📌 [{selected_subject}] 명렬표 (총 수강인원: {total_count}명)")
        with col_print_btn:
            st.caption("💡 Tip: `Ctrl + P` 누르면 A4 가로 인쇄 가능")

        classes = sorted(df['반'].unique())
        cols = st.columns(len(classes))
        
        # 반별 명렬표 한 화면에 배치
        for idx, cls in enumerate(classes):
            with cols[idx]:
                cls_df = df[df['반'] == cls][[col_id, col_name, '신청여부']].copy()
                cls_count = cls_df['신청여부'].sum()
                
                # HTML 구조로 스크롤 없이 밀도 높게 테이블 생성
                table_html = f"<table class='compact-table'>"
                table_html += f"<thead><tr><th colspan='2'>{cls}<br>({cls_count}명)</th></tr>"
                table_html += f"<tr><th>학번</th><th>이름</th></tr></thead><tbody>"
                
                for _, row in cls_df.iterrows():
                    row_class = "applied-row" if row['신청여부'] else "not-applied-row"
                    # 학번 뒤 2자리만 표시 원할 경우 row[col_id][-2:] 사용 가능, 현재는 5자리 전체
                    table_html += f"<tr class='{row_class}'><td>{row[col_id]}</td><td>{row[col_name]}</td></tr>"
                
                table_html += "</tbody></table>"
                
                st.write(table_html, unsafe_allow_html=True)