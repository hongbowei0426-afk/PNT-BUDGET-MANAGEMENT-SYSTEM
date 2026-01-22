import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="PNT PO 预算管理仪表板",
    page_icon="💰",
    layout="wide",
)

# --- Constants ---
# 标准化的数据文件名
DEFAULT_DATA_FILE = 'budget_data.xlsx'
DEFAULT_SHEET_NAME = 'Sheet1'

# --- Utility Functions ---
def get_data_file_path():
    """
    获取数据文件路径。
    首先检查当前工作目录，如果文件不存在则检查脚本目录。
    """
    # 方案1: 检查当前工作目录
    if os.path.exists(DEFAULT_DATA_FILE):
        return DEFAULT_DATA_FILE

    # 方案2: 检查脚本所在目录
    script_dir = Path(__file__).parent
    script_dir_file = script_dir / DEFAULT_DATA_FILE
    if script_dir_file.exists():
        return str(script_dir_file)

    # 方案3: 检查上级目录
    parent_dir = script_dir.parent
    parent_dir_file = parent_dir / DEFAULT_DATA_FILE
    if parent_dir_file.exists():
        return str(parent_dir_file)

    # 如果都不存在，返回默认路径（将由异常处理捕获）
    return DEFAULT_DATA_FILE

def validate_data_file(file_path):
    """
    验证数据文件是否存在和有效。

    Args:
        file_path: 文件路径

    Returns:
        tuple: (是否有效, 错误消息)
    """
    if not os.path.exists(file_path):
        return False, f"文件 '{file_path}' 不存在"

    if not file_path.endswith('.xlsx'):
        return False, f"文件格式错误。期望 .xlsx 格式，实际为 {Path(file_path).suffix}"

    return True, ""

# --- Data Loading and Caching ---
@st.cache_data
def load_data(file_path=None):
    """
    加载来自Excel文件的PO数据。

    Args:
        file_path: 可选的文件路径。如果不提供，使用默认路径。

    Returns:
        DataFrame: 处理后的数据框

    Raises:
        FileNotFoundError: 如果文件不存在
        ValueError: 如果文件格式错误或数据无效
    """
    if file_path is None:
        file_path = get_data_file_path()

    # 验证文件
    is_valid, error_msg = validate_data_file(file_path)
    if not is_valid:
        raise FileNotFoundError(error_msg)

    try:
        # 加载Excel文件
        df = pd.read_excel(file_path, sheet_name=DEFAULT_SHEET_NAME)

        # 基础数据清理
        df['PO Net Price'] = pd.to_numeric(df['PO Net Price'], errors='coerce').fillna(0)
        df['GR an Lager-value'] = pd.to_numeric(df['GR an Lager-value'], errors='coerce').fillna(0)
        df['Invoice amount'] = pd.to_numeric(df['Invoice amount'], errors='coerce').fillna(0)
        df['Actual PO Cost'] = df[['GR an Lager-value', 'Invoice amount']].max(axis=1)

        return df

    except pd.errors.ParserError as e:
        raise ValueError(f"无法解析Excel文件: {str(e)}")
    except Exception as e:
        raise ValueError(f"加载数据时发生错误: {str(e)}")

# --- Main Application Logic ---
try:
    # 尝试加载数据
    df = load_data()

    st.title("📊 PNT 采购订单 (PO) 预算管理仪表板")

    # --- 1. 汇总视图 (KPIs and Charts) ---
    st.header("1. 汇总视图 (Budget Overview)")
    total_budget = df['PO Net Price'].sum()
    total_actual_cost = df['Actual PO Cost'].sum()
    remaining_budget = total_budget - total_actual_cost

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="总计划预算 (Total Budget)", value=f"¥ {total_budget:,.2f}")
    kpi2.metric(label="总实际成本 (Total Actual Cost)", value=f"¥ {total_actual_cost:,.2f}")
    kpi3.metric(label="剩余预算 (Remaining Budget)", value=f"¥ {remaining_budget:,.2f}", delta=f"¥ {remaining_budget - total_budget:,.2f}")

    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("按品牌预算分布 (Budget by Brand)")
        brand_budget = df.groupby('Brand')['PO Net Price'].sum().reset_index()
        fig_brand = px.pie(brand_budget, names='Brand', values='PO Net Price', hole=0.4)
        st.plotly_chart(fig_brand, use_container_width=True)

    with col2:
        st.subheader("按PO状态金额分布 (Amount by PO Status)")
        status_budget = df.groupby('PO status')['PO Net Price'].sum().reset_index()
        fig_status = px.bar(status_budget, x='PO status', y='PO Net Price', color='PO status')
        st.plotly_chart(fig_status, use_container_width=True)

    # --- 2. 分类查询 (Detailed Queries) ---
    st.header("2. 分类查询 (Detailed Queries)")
    query_type = st.radio("选择查询维度:", ('按 Internal Order (IO) 查询', '按 PO 执行人查询'), horizontal=True)

    if query_type == '按 Internal Order (IO) 查询':
        io_list = df['Internal Order'].dropna().unique()
        selected_io = st.selectbox("选择 Internal Order:", io_list)
        st.subheader(f"查询结果: {selected_io}")
        io_df = df[df['Internal Order'] == selected_io]
        st.dataframe(io_df)
        total_io_budget = io_df['PO Net Price'].sum()
        st.info(f"该IO下属的PO总预算为: ¥ {total_io_budget:,.2f}")

    elif query_type == '按 PO 执行人查询':
        executor_list = df['PO executor'].dropna().unique()
        selected_executor = st.selectbox("选择 PO 执行人:", executor_list)
        st.subheader(f"查询结果: {selected_executor}")
        executor_df = df[df['PO executor'] == selected_executor]
        st.dataframe(executor_df)
        total_executor_budget = executor_df['PO Net Price'].sum()
        st.success(f"该执行人负责的PO总预算为: ¥ {total_executor_budget:,.2f}")


    # --- 3. 版本对比 (Version Comparison) ---
    st.header("3. 预算变动对比 (Comparison with Previous Version)")
    st.write("上传旧版的Excel文件，系统将自动对比预算变动情况。")
    uploaded_file_old = st.file_uploader("上传旧版 Excel 文件", type=['xlsx'])

    if uploaded_file_old is not None:
        try:
            df_old = pd.read_excel(uploaded_file_old, sheet_name=DEFAULT_SHEET_NAME)
            df_old['PO Net Price'] = pd.to_numeric(df_old['PO Net Price'], errors='coerce').fillna(0)
            total_budget_old = df_old['PO Net Price'].sum()
            total_budget_new = total_budget

            st.subheader("总金额变动")
            st.metric(label="旧版总预算", value=f"¥ {total_budget_old:,.2f}")
            st.metric(label="新版总预算", value=f"¥ {total_budget_new:,.2f}", delta=f"¥ {total_budget_new - total_budget_old:,.2f}")

            st.subheader("明细变动对比")
            comparison_df = df.merge(df_old[['PO Number', 'PO Net Price']], on='PO Number', how='outer', suffixes=('_new', '_old'))
            comparison_df['PO Net Price_new'] = comparison_df['PO Net Price_new'].fillna(0)
            comparison_df['PO Net Price_old'] = comparison_df['PO Net Price_old'].fillna(0)
            comparison_df['budget_change'] = comparison_df['PO Net Price_new'] - comparison_df['PO Net Price_old']
            changed_items = comparison_df[comparison_df['budget_change'] != 0]
            st.write("预算发生变动的PO明细:")
            st.dataframe(changed_items[['PO Number', 'PO Net Price_old', 'PO Net Price_new', 'budget_change']].sort_values(by='budget_change', ascending=False))
        except Exception as e:
            st.error(f"处理上传的文件时发生错误: {str(e)}")

    # --- 4. 详细数据视图 ---
    st.header("4. 完整数据视图 (Full Data View)")
    st.dataframe(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="下载数据为 CSV",
        data=csv,
        file_name='pnt_po_status_report.csv',
        mime='text/csv',
    )


except FileNotFoundError as e:
    st.error(
        f"**错误：数据文件未找到！**\n\n"
        f"详细信息: {str(e)}\n\n"
        f"**解决方案：**\n"
        f"1. 请确保您已将名为 `{DEFAULT_DATA_FILE}` 的数据文件放置在以下位置之一:\n"
        f"   - 应用程序所在的目录\n"
        f"   - 应用程序的父目录\n"
        f"   - 当前工作目录\n\n"
        f"2. 文件必须是 `.xlsx` 格式\n"
        f"3. 确保 Excel 文件包含名为 '{DEFAULT_SHEET_NAME}' 的工作表"
    )
except ValueError as e:
    st.error(
        f"**错误：数据验证失败！**\n\n"
        f"详细信息: {str(e)}\n\n"
        f"请检查您的 Excel 文件格式和数据内容是否正确。"
    )
except Exception as e:
    st.error(f"**处理数据时发生意外错误:** {str(e)}\n\n请联系技术支持。")
