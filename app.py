import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64
import streamlit.components.v1 as components

# ==========================================
# 1. 웹페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(page_title="C&T Dye Finder", page_icon="logo.jpg", layout="wide")

if "lang" not in st.session_state: st.session_state.lang = "EN"
lang = st.session_state.lang
if "app_mode" not in st.session_state: st.session_state.app_mode = "tab3"

# ==========================================
# 2. 다국어 번역 데이터 사전 정의 (EN / KO / VN)
# ==========================================
t = {
    "EN": {
        "header": "C&T Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "menu_title": "Select Program",
        "tab1": "1. Fastness Matcher",
        "tab2": "2. Compatibility Analyzer",
        "tab3": "3. Fastness & Compatibility",
        "instruction_text": "Please set the minimum fastness grades from the left sidebar.",
        "sb_spec_title": "1. Set Min Specs",
        "sb_dye_select": "Select Dyes to Compare",
        "search_res_hdr": ":material/manage_search: Fastness Matching Results",
        "search_res_sub": "Results (Matching Dyes: {count})",
        "search_res_desc": "**Click the checkbox in the first column (`Select`) to choose dyes for comparison.**",
        "col_select": "Select",
        "col_group": "Group",
        "col_name": "Dye Name",
        "warn_limit": "Only up to 3 selected dyes are shown in click order.",
        "sim_hdr": ":material/monitoring: Compatibility Simulation",
        "no_match": "No dyes match the criteria.",
        "select_prompt": "Please check the **[Select]** checkbox above to compare dyes.\n\nGraph colors will be assigned as Yellow, Red, and Blue in the order selected.",
        "select_prompt_tab3": "Please select at least one dye from the left sidebar for comparison.",
        "err_time_data": "Time data columns are invalid.",
        "xaxis": "Process Time (min)",
        "yaxis": "Exhaustion / Fixation Rate (%)",
        "summary_hdr": ":material/dataset: Numeric Summary",
        "diag_hdr": ":material/troubleshoot: Field Diagnosis",
        "diag_excel": "**Excellent**\n\nBehaviors match closely. Low risk of tailing.",
        "diag_warn": "**Caution**\n\nMinor rate differences. Adjust temperature profile.",
        "diag_danger": "**Danger**\n\nHigh risk of tailing/face-back in bulk production.",
        "minute_unit": "min",
        "crit_light": "Light",
        "crit_p_light_acid": "Persp-Light(Acid)",
        "crit_p_light_alk": "Persp-Light(Alkali)",
        "crit_p_acid": "Persp(Acid)",
        "crit_p_alk": "Persp(Alkali)",
        "crit_wash": "Washing",
        "crit_chlor": "Chlorine",
        "rep_wash_title": "Repeated Wash",
        "rep_wash_times_label": "Wash Cycles",
        "rep_wash_grade_label": "Rep. Wash Grade",
        "rep_wash_none": "None",
    },
    "KO": {
        "header": "C&T Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "menu_title": "프로그램 선택",
        "tab1": "1. 요구견뢰도 매칭",
        "tab2": "2. 상용성 비교 분석",
        "tab3": "3. 통합 매칭 및 시뮬레이션",
        "instruction_text": "왼쪽 사이드바에서 원하는 요구 견뢰도 등급을 설정하세요.",
        "sb_spec_title": "1. 요구 스펙 설정 (이상)",
        "sb_dye_select": "비교 염료 선택",
        "search_res_hdr": ":material/manage_search: 견뢰도 스펙 매칭 결과",
        "search_res_sub": "검색 결과 (만족하는 염료: {count}개)",
        "search_res_desc": "**아래 표의 첫 번째 열(`선택`)을 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)",
        "col_select": "선택",
        "col_group": "염료그룹",
        "col_name": "염료명",
        "warn_limit": "안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.",
        "sim_hdr": ":material/monitoring: 선택 염료 상용성 시뮬레이션",
        "no_match": "검색 조건에 맞는 염료가 없습니다.",
        "select_prompt": "표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.",
        "select_prompt_tab3": "좌측 사이드바에서 비교 분석할 염료를 1개 이상 선택해 주세요.",
        "err_time_data": "상용성 시간 데이터 열(0, 5, 20...)이 올바르지 않습니다.",
        "xaxis": "공정 시간 (분)",
        "yaxis": "염착률 / 고착률 (%)",
        "summary_hdr": ":material/dataset: 수치 요약",
        "diag_hdr": ":material/troubleshoot: 현장 진단",
        "diag_excel": "**우수**\n\n거동이 거의 일치합니다. (Tailing 확률 매우 낮음)",
        "diag_warn": "**주의**\n\n구간별 미세한 속도 차이가 있습니다. 승온 조건 조절 권장.",
        "diag_danger": "**위험**\n\n대량 생산 시 불량(Tailing/Face-back) 발생 확률이 높습니다.",
        "minute_unit": "분",
        "crit_light": "일광",
        "crit_p_light_acid": "땀일광(산성)",
        "crit_p_light_alk": "땀일광(알칼리)",
        "crit_p_acid": "땀(산성)",
        "crit_p_alk": "땀(알칼리)",
        "crit_wash": "세탁",
        "crit_chlor": "염소수",
        "rep_wash_title": "반복세탁",
        "rep_wash_times_label": "세탁 횟수 선택",
        "rep_wash_grade_label": "반복세탁 요구 등급",
        "rep_wash_none": "적용 안 함",
    },
    "VN": {
        "header": "C&T Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "menu_title": "Chọn chương trình",
        "tab1": "1. Khớp độ bền",
        "tab2": "2. Phân tích tương thích",
        "tab3": "3. Độ bền & Tương thích",
        "instruction_text": "Vui lòng đặt cấp độ bền màu mong muốn từ thanh bên trái.",
        "sb_spec_title": "1. Đặt thông số tối thiểu",
        "sb_dye_select": "Chọn thuốc nhuộm so sánh",
        "search_res_hdr": ":material/manage_search: Kết quả khớp độ bền",
        "search_res_sub": "Kết quả (Số lượng: {count})",
        "search_res_desc": "**Nhấp vào hộp kiểm ở cột đầu tiên (`Chọn`) để so sánh thuốc nhuộm.**",
        "col_select": "Chọn",
        "col_group": "Nhóm",
        "col_name": "Tên thuốc nhuộm",
        "warn_limit": "Chỉ hiển thị tối đa 3 loại thuốc nhuộm được chọn.",
        "sim_hdr": ":material/monitoring: Mô phỏng tính tương thích",
        "no_match": "Không có thuốc nhuộm phù hợp.",
        "select_prompt": "Vui lòng chọn hộp kiểm **[Chọn]** phía trên để so sánh.",
        "select_prompt_tab3": "Vui lòng chọn ít nhất một loại thuốc nhuộm từ bảng.",
        "err_time_data": "Dữ liệu thời gian không hợp lệ.",
        "xaxis": "Thời gian (phút)",
        "yaxis": "Tỷ lệ hấp thụ / Cố định (%)",
        "summary_hdr": ":material/dataset: Tóm tắt số liệu",
        "diag_hdr": ":material/troubleshoot: Chẩn đoán thực tế",
        "diag_excel": "**Tuyệt vời**\n\nHành vi rất khớp. Nguy cơ tailing thấp.",
        "diag_warn": "**Chú ý**\n\nCó sự khác biệt nhỏ. Khuyến nghị điều chỉnh nhiệt độ.",
        "diag_danger": "**Nguy hiểm**\n\nNguy cơ cao bị lỗi khi sản xuất hàng loạt.",
        "minute_unit": "phút",
        "crit_light": "Ánh sáng",
        "crit_p_light_acid": "Mồ hôi-Ánh sáng (Axit)",
        "crit_p_light_alk": "Mồ hôi-Ánh sáng (Kiềm)",
        "crit_p_acid": "Mồ hôi (Axit)",
        "crit_p_alk": "Mồ hôi (Kiềm)",
        "crit_wash": "Giặt",
        "crit_chlor": "Clo",
        "rep_wash_title": "Giặt lặp lại",
        "rep_wash_times_label": "Số chu kỳ giặt",
        "rep_wash_grade_label": "Cấp độ yêu cầu",
        "rep_wash_none": "Không áp dụng",
    }
}

# 반복세탁 사이클 옵션 정의
cycle_opts_en = [t["EN"]["rep_wash_none"], "5 Cycles", "10 Cycles", "15 Cycles", "20 Cycles", "30 Cycles", "40 Cycles", "50 Cycles"]
cycle_opts_ko = [t["KO"]["rep_wash_none"], "5회", "10회", "15회", "20회", "30회", "40회", "50회"]
cycle_opts_vn = [t["VN"]["rep_wash_none"], "5 Chu kỳ", "10 Chu kỳ", "15 Chu kỳ", "20 Chu kỳ", "30 Chu kỳ", "40 Chu kỳ", "50 Chu kỳ"]

def get_excel_cycle_string(selected_val, lang):
    if lang == "KO": return selected_val
    if lang == "EN":
        mapping = {"5 Cycles": "5회", "10 Cycles": "10회", "15 Cycles": "15회", "20 Cycles": "20회", "30 Cycles": "30회", "40 Cycles": "40회", "50 Cycles": "50회"}
        return mapping.get(selected_val)
    if lang == "VN":
        mapping = {"5 Chu kỳ": "5회", "10 Chu kỳ": "10회", "15 Chu kỳ": "15회", "20 Chu kỳ": "20회", "30 Chu kỳ": "30회", "40 Chu kỳ": "40회", "50 Chu kỳ": "50회"}
        return mapping.get(selected_val)

# ==========================================
# 3. 로고 인코딩 및 UI 커스텀 CSS
# ==========================================
try:
    with open("logo.jpg", "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode()
except Exception:
    logo_base64 = ""

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
<style>
    [data-testid="stHeader"], #MainMenu, footer {{ display: none !important; }}
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] {{
        display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important;
    }}
    h2, h3 {{ font-weight: 700 !important; color: #111 !important; }}
    h3 {{ border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 24px; margin-top: 10px; }}
    hr {{ margin: 1.5em 0; }}
    [data-testid="stSidebar"] p strong {{
        display: block; border-left: 4px solid #1b489d; padding-left: 10px; 
        margin-top: 20px; margin-bottom: 8px; font-size: 16px; color: #333;
    }}
    .block-container {{ padding-top: 80px !important; }}
    [data-testid="stSidebar"] {{ padding-top: 60px !important; }}
    [data-testid="stSidebarUserContent"] {{ padding-top: 10px !important; }}
    .fixed-header {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 60px;
        background-color: #ffffff; box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        z-index: 999998; display: flex; align-items: center; padding-left: 20px;
        border-bottom: 1px solid #eaeaea;
    }}
    .fixed-header img {{ width: 45px; margin-right: 12px; }}
    .fixed-header h2 {{ margin: 0; padding: 0; font-size: 24px; font-weight: 700; color: #31333F; }}
    div[data-testid="stHorizontalBlock"]:has(#top-menu-marker) {{
        position: fixed !important; top: 11px !important; right: 20px !important; 
        width: 220px !important; z-index: 999999 !important;
        align-items: center !important; gap: 0.5rem !important;
    }}
    div.element-container:has(#top-menu-marker) {{
        display: none !important; margin: 0 !important; padding: 0 !important; height: 0 !important;
    }}
    div[data-testid="stHorizontalBlock"]:has(#top-menu-marker) div.stButton > button {{
        border-radius: 8px; padding: 0px 5px; height: 38px; min-height: 38px; margin: 0 !important; 
    }}
</style>
<div class="fixed-header">
    <img src="data:image/jpeg;base64,{logo_base64}" onerror="this.style.display='none'">
    <h2>{t[lang]['header']}</h2>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. 언어 전환 버튼 배치 (VN 추가)
# ==========================================
lang_cols = st.columns(3)
with lang_cols[0]:
    if st.button("🇺🇸 EN", use_container_width=True, type="primary" if lang == "EN" else "secondary"):
        st.session_state.lang = "EN"; st.rerun()
    st.markdown('<div id="top-menu-marker"></div>', unsafe_allow_html=True)
with lang_cols[1]:
    if st.button("🇰🇷 KO", use_container_width=True, type="primary" if lang == "KO" else "secondary"):
        st.session_state.lang = "KO"; st.rerun()
with lang_cols[2]:
    if st.button("🇻🇳 VN", use_container_width=True, type="primary" if lang == "VN" else "secondary"):
        st.session_state.lang = "VN"; st.rerun()


# ==========================================
# 5. 사이드바 - 메뉴 구성
# ==========================================
st.sidebar.markdown(f"**{t[lang]['menu_title']}**")
if st.sidebar.button(t[lang]["tab1"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab1" else "secondary"):
    st.session_state.app_mode = "tab1"; st.rerun()
if st.sidebar.button(t[lang]["tab2"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab2" else "secondary"):
    st.session_state.app_mode = "tab2"; st.rerun()
if st.sidebar.button(t[lang]["tab3"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab3" else "secondary"):
    st.session_state.app_mode = "tab3"; st.rerun()

st.sidebar.markdown("---")

criteria_map = {'일광': 'crit_light', '땀일광(산성)': 'crit_p_light_acid', '땀일광(알칼리)': 'crit_p_light_alk', 
                '땀(산성)': 'crit_p_acid', '땀(알칼리)': 'crit_p_alk', '세탁': 'crit_wash', '염소수': 'crit_chlor'}
criteria_list = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']


# =====================================================================
# [App 1] 요구견뢰도 스펙 매칭 전용
# =====================================================================
if st.session_state.app_mode == "tab1":
    @st.cache_data
    def load_spec_data():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df
    
    df1 = load_spec_data()
    if df1 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
    else:
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req1 = {}
        for c in criteria_list:
            if c in df1.columns:
                display_label = t[lang][criteria_map.get(c, c)]
                max_val = 7.0 if c == '일광' else 5.0
                req1[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"sld_{c}_tab1")

        # --- 반복세탁 UI (Tab 1) ---
        st.sidebar.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.sidebar.markdown(f"**{t[lang]['rep_wash_title']}**")
        cycles_list = cycle_opts_en if lang == "EN" else (cycle_opts_vn if lang == "VN" else cycle_opts_ko)
        
        sel_cycle1 = st.sidebar.selectbox(t[lang]["rep_wash_times_label"], cycles_list, key="sel_rep_wash_tab1")
        rep_wash_min1 = None
        rep_wash_col1 = None

        if sel_cycle1 != t[lang]["rep_wash_none"]:
            rep_wash_min1 = st.sidebar.slider(t[lang]["rep_wash_grade_label"], 1.0, 5.0, 1.0, 0.5, key="sld_rep_wash_tab1")
            rep_wash_col1 = get_excel_cycle_string(sel_cycle1, lang)
        # ---------------------------
                
        st.info(f"**{t[lang]['instruction_text']}**", icon=":material/info:")
        
        f_df1 = df1.copy()
        
        for c, min_val in req1.items():
            if c in f_df1.columns:
                f_df1[c] = pd.to_numeric(f_df1[c], errors='coerce')
                f_df1 = f_df1[f_df1[c] >= min_val]
        
        # 반복세탁 필터링 로직
        if rep_wash_col1 and rep_wash_col1 in f_df1.columns:
            f_df1[rep_wash_col1] = pd.to_numeric(f_df1[rep_wash_col1], errors='coerce')
            f_df1 = f_df1[f_df1[rep_wash_col1] >= rep_wash_min1]
                
        st.subheader(t[lang]["search_res_hdr"])
        st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df1))}*")
        
        # [수정됨] Tab 1 표 헤더 다국어 반영을 위해 column_config 구성
        disp_cols1 = ['염료명'] + [c for c in criteria_list if c in f_df1.columns]
        
        col_configs1 = {
            "염료명": st.column_config.TextColumn(label=t[lang]["col_name"])
        }
        for c in disp_cols1[1:]:
            col_configs1[c] = st.column_config.NumberColumn(label=t[lang][criteria_map.get(c, c)])
            
        if rep_wash_col1 and rep_wash_col1 in f_df1.columns:
            disp_cols1.append(rep_wash_col1)
            display_col_name = f"Rep.Wash ({sel_cycle1.split()[0]})" if lang == "EN" else (f"Giặt lặp lại ({sel_cycle1.split()[0]})" if lang == "VN" else f"반복세탁 ({sel_cycle1})")
            col_configs1[rep_wash_col1] = st.column_config.NumberColumn(label=display_col_name)
            
        st.dataframe(f_df1[disp_cols1], hide_index=True, use_container_width=True, column_config=col_configs1)


# =====================================================================
# [App 2] 상용성 그래프 단독
# =====================================================================
elif st.session_state.app_mode == "tab2":
    @st.cache_data
    def load_integrated_data_tab2():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df

    # [수정됨] 2번 프로그램도 integrated_dyes_data.xlsx를 사용하도록 변경
    df2 = load_integrated_data_tab2()
    
    if df2 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
    else:
        st.sidebar.markdown(f"**{t[lang]['sb_dye_select']}**")
        all_dyes2 = df2['염료명'].dropna().unique().tolist()
        
        # 사이드바에서 원하는 염료명 다중 선택
        selected_dyes_names = st.sidebar.multiselect("Select Dyes", options=all_dyes2, key="tab2_ms_dyes", label_visibility="collapsed")
                    
        st.subheader(t[lang]["sim_hdr"])
        if not selected_dyes_names:
            st.info(f"{t[lang]['select_prompt_tab3']}", icon=":material/touch_app:")
        else:
            time_pts2 = ['0', '5', '20', '25', '40', '80', '100']
            val_cols2 = [tc for tc in time_pts2 if tc in df2.columns]
            
            if len(val_cols2) < 2:
                st.warning(t[lang]["err_time_data"], icon=":material/warning:")
            else:
                fig2 = go.Figure()
                custom_colors2 = ['#FFD700', '#FF4B4B', '#1F77B4', '#9467bd', '#2ca02c', '#ff7f0e', '#e377c2']
                
                for idx, name in enumerate(selected_dyes_names):
                    row = df2[df2['염료명'] == name].iloc[0]
                    color = custom_colors2[idx % len(custom_colors2)]
                    label = f"{name}"
                    t_p1 = [tc for tc in val_cols2 if int(tc) <= 20]
                    v_p1 = [row[tc] for tc in t_p1]
                    t_p2 = [tc for tc in val_cols2 if int(tc) >= 25]
                    v_p2 = [row[tc] for tc in t_p2]
                    
                    fig2.add_trace(go.Scatter(x=t_p1, y=v_p1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                    fig2.add_trace(go.Scatter(x=t_p2, y=v_p2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                
                fig2.update_layout(
                    xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], 
                    xaxis=dict(tickmode='array', tickvals=[int(tc) for tc in val_cols2]), 
                    yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), 
                    legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=16), bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="lightgray", borderwidth=1)
                )
                fig2.add_vline(x=20, line_dash="dash", line_color="gray")
                fig2.add_vline(x=25, line_dash="dash", line_color="gray")
                st.plotly_chart(fig2, use_container_width=True)
                
                st.markdown(f"**{t[lang]['summary_hdr']}**")
                table_data2 = []
                for name in selected_dyes_names:
                    row = df2[df2['염료명'] == name].iloc[0]
                    rd = {t[lang]["col_name"]: name}
                    for tc in val_cols2: 
                        rd[f"{tc}{t[lang]['minute_unit']}"] = f"{row[tc]:.1f}%" if pd.notna(row[tc]) else "-"
                    table_data2.append(rd)
                st.dataframe(pd.DataFrame(table_data2), hide_index=True, use_container_width=True)
                
                if len(selected_dyes_names) >= 2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader(t[lang]['diag_hdr'])
                    all_matrix = np.array([[df2[df2['염료명'] == name].iloc[0][tc] for tc in val_cols2] for name in selected_dyes_names], dtype=float)
                    std_per_time = np.nanstd(all_matrix, axis=0)
                    max_dev = np.nanmax(std_per_time)
                    
                    if max_dev < 5: st.success(t[lang]["diag_excel"], icon=":material/check_circle:")
                    elif max_dev < 12: st.warning(t[lang]["diag_warn"], icon=":material/warning:")
                    else: st.error(t[lang]["diag_danger"], icon=":material/dangerous:")


# =====================================================================
# [App 3] 통합 매칭 및 시뮬레이션
# =====================================================================
elif st.session_state.app_mode == "tab3":
    @st.cache_data
    def load_integrated_data():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df
    
    df3 = load_integrated_data()
    if df3 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
    else:
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req3 = {}
        for c in criteria_list:
            if c in df3.columns:
                display_label = t[lang][criteria_map.get(c, c)]
                max_val = 7.0 if c == '일광' else 5.0
                req3[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"sld_{c}_tab3")

        # --- 반복세탁 UI (Tab 3) ---
        st.sidebar.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        st.sidebar.markdown(f"**{t[lang]['rep_wash_title']}**")
        cycles_list = cycle_opts_en if lang == "EN" else (cycle_opts_vn if lang == "VN" else cycle_opts_ko)
        
        sel_cycle3 = st.sidebar.selectbox(t[lang]["rep_wash_times_label"], cycles_list, key="sel_rep_wash_tab3")
        rep_wash_min3 = None
        rep_wash_col3 = None

        if sel_cycle3 != t[lang]["rep_wash_none"]:
            rep_wash_min3 = st.sidebar.slider(t[lang]["rep_wash_grade_label"], 1.0, 5.0, 1.0, 0.5, key="sld_rep_wash_tab3")
            rep_wash_col3 = get_excel_cycle_string(sel_cycle3, lang)
        # ---------------------------

        st.info(f"**{t[lang]['instruction_text']}**", icon=":material/info:")
        
        f_df3 = df3.copy()
        
        for c, min_val in req3.items():
            if c in f_df3.columns:
                f_df3[c] = pd.to_numeric(f_df3[c], errors='coerce')
                f_df3 = f_df3[f_df3[c] >= min_val]
        
        # 반복세탁 필터링 로직
        if rep_wash_col3 and rep_wash_col3 in f_df3.columns:
            f_df3[rep_wash_col3] = pd.to_numeric(f_df3[rep_wash_col3], errors='coerce')
            f_df3 = f_df3[f_df3[rep_wash_col3] >= rep_wash_min3]
                
        st.subheader(t[lang]["search_res_hdr"])
        st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df3))}*")
        st.write(t[lang]["search_res_desc"])
        
        f_df3.insert(0, '선택', False)
        disp_cols3 = ['선택', '염료명'] + [c for c in criteria_list if c in f_df3.columns]
        
        col_configs3 = {
            "선택": st.column_config.CheckboxColumn(label=t[lang]["col_select"], width="small"),
            "염료명": st.column_config.TextColumn(label=t[lang]["col_name"], width=150)
        }
        for c in disp_cols3[2:]:
            col_configs3[c] = st.column_config.NumberColumn(label=t[lang][criteria_map.get(c, c)], width=80)
        
        # 반복세탁 컬럼 동적 추가 및 스타일링
        if rep_wash_col3 and rep_wash_col3 in f_df3.columns:
            disp_cols3.append(rep_wash_col3)
            display_col_name = f"Rep.Wash ({sel_cycle3.split()[0]})" if lang == "EN" else (f"Giặt lặp lại ({sel_cycle3.split()[0]})" if lang == "VN" else f"반복세탁 ({sel_cycle3})")
            col_configs3[rep_wash_col3] = st.column_config.NumberColumn(label=display_col_name, width=100)

        if "tab3_selected_order" not in st.session_state:
            st.session_state.tab3_selected_order = []
            
        edited_df3 = st.data_editor(
            f_df3[disp_cols3], hide_index=True, use_container_width=True,
            column_config=col_configs3, disabled=[col for col in disp_cols3 if col != '선택'], key="tab3_editor"
        )
        
        curr_checked3 = edited_df3[edited_df3['선택'] == True]['염료명'].tolist()
        
        st.session_state.tab3_selected_order = [d for d in st.session_state.tab3_selected_order if d in curr_checked3]
        for d in curr_checked3:
            if d not in st.session_state.tab3_selected_order:
                st.session_state.tab3_selected_order.append(d)
        
        # [수정됨] 3번 프로그램 - 전체복사 / 선택복사 버튼 제거 완료

        sel_dyes3 = st.session_state.tab3_selected_order[:3]
        if len(curr_checked3) > 3: st.warning(t[lang]["warn_limit"], icon=":material/warning:")

        st.markdown("---")
        st.subheader(t[lang]["sim_hdr"])
        if not sel_dyes3:
            st.info(f"{t[lang]['select_prompt']}", icon=":material/touch_app:")
        else:
            time_pts3 = ['0', '5', '20', '25', '40', '80', '100']
            val_cols3 = [tc for tc in time_pts3 if tc in df3.columns]
            if len(val_cols3) < 2:
                st.warning(t[lang]["err_time_data"], icon=":material/warning:")
            else:
                fig3 = go.Figure()
                colors = ['#FFD700', '#FF4B4B', '#1F77B4']
                for idx, name in enumerate(sel_dyes3):
                    row = df3[df3['염료명'] == name].iloc[0]
                    color = colors[idx % len(colors)]
                    label = f"{name}"
                    t_p1 = [tc for tc in val_cols3 if int(tc) <= 20]
                    v_p1 = [row[tc] for tc in t_p1]
                    t_p2 = [tc for tc in val_cols3 if int(tc) >= 25]
                    v_p2 = [row[tc] for tc in t_p2]
                    
                    fig3.add_trace(go.Scatter(x=t_p1, y=v_p1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                    fig3.add_trace(go.Scatter(x=t_p2, y=v_p2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                    
                fig3.update_layout(
                    xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], 
                    xaxis=dict(tickmode='array', tickvals=[int(tc) for tc in val_cols3]), 
                    yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), 
                    legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=16), bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="lightgray", borderwidth=1)
                )
                fig3.add_vline(x=20, line_dash="dash", line_color="gray")
                fig3.add_vline(x=25, line_dash="dash", line_color="gray")
                st.plotly_chart(fig3, use_container_width=True)
                
                st.markdown(f"**{t[lang]['summary_hdr']}**")
                tb_data3 = []
                for name in sel_dyes3:
                    row = df3[df3['염료명'] == name].iloc[0]
                    rd = {t[lang]["col_name"]: name}
                    for tc in val_cols3: rd[f"{tc}{t[lang]['minute_unit']}"] = f"{row[tc]:.1f}%" if pd.notna(row[tc]) else "-"
                    tb_data3.append(rd)
                st.dataframe(pd.DataFrame(tb_data3), hide_index=True, use_container_width=True)
                
                if len(sel_dyes3) >= 2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader(t[lang]['diag_hdr'])
                    all_matrix = np.array([[df3[df3['염료명'] == name].iloc[0][tc] for tc in val_cols3] for name in sel_dyes3], dtype=float)
                    std_per_time = np.nanstd(all_matrix, axis=0)
                    max_dev = np.nanmax(std_per_time)
                    
                    if max_dev < 5: st.success(t[lang]["diag_excel"], icon=":material/check_circle:")
                    elif max_dev < 12: st.warning(t[lang]["diag_warn"], icon=":material/warning:")
                    else: st.error(t[lang]["diag_danger"], icon=":material/dangerous:")

# ==========================================
# 5. 최하단 공통 요소 (제작자 정보)
# ==========================================
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='text-align: center; color: #888888; font-size: 13px; margin-bottom: 10px;'>{t[lang]['created_by']}</p>", unsafe_allow_html=True)