import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="预算管理系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header {
        color: #1f77b4;
        font-size: 28px;
        font-weight: bold;
        margin: 20px 0;
    }
    .subheader {
        color: #1f77b4;
        font-size: 20px;
        font-weight: bold;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<div class="header">Budget Management System</div>', unsafe_allow_html=True)

# 侧边栏 - 数据加载和过滤
st.sidebar.markdown("## System Settings")

# 加载当前版本的数据
@st.cache_data
def load_data():
    df = pd.read_excel('PNT_PO_Status_Report(2).xlsx', sheet_name='Sheet1')
    # 清理列名
    df.columns = df.columns.str.strip()
    return df

# 加载数据
df = load_data()

# 创建"上一版本"的模拟数据（用于对比演示）
@st.cache_data
def create_previous_version():
    df_prev = df.copy()
    # 模拟上一版本的变化：随机调整一些金额
    np.random.seed(42)
    mask = np.random.rand(len(df_prev)) > 0.7
    df_prev.loc[mask, 'PO Value - LC'] = df_prev.loc[mask, 'PO Value - LC'] * np.random.uniform(0.9, 1.1, mask.sum())
    df_prev['Version'] = 'Previous'
    return df_prev

df_prev = create_previous_version()

# ==================== Page Navigation ====================
tab1, tab2, tab3, tab4 = st.tabs(["Summary View", "Query by Category", "Version Comparison", "Detailed Data"])

# ==================== TAB 1: Summary View ====================
with tab1:
    st.markdown('<div class="subheader">Budget Summary Overview</div>', unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_po_value = df['PO Value - LC'].sum()
        st.metric("Total PO Amount", f"CNY {total_po_value:,.2f}")

    with col2:
        total_gr_value = df['GR Value - LC'].sum()
        st.metric("Total GR Amount", f"CNY {total_gr_value:,.2f}")

    with col3:
        total_invoice = df['Invoice Value - LC'].sum()
        st.metric("Total Invoice", f"CNY {total_invoice:,.2f}")

    with col4:
        total_commitment = df['PO Commitment -  LC'].sum()
        st.metric("Total Commitment", f"CNY {total_commitment:,.2f}")

    with col5:
        po_count = df['PO Number'].nunique()
        st.metric("PO Count", f"{po_count:,}")

    st.divider()

    # Status analysis
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**PO Line Status Distribution**")
        status_counts = df['PO Line Status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_status.update_layout(height=400)
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("**PO Line Type Distribution**")
        type_counts = df['PO Line Type'].value_counts()
        fig_type = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_type.update_layout(height=400)
        st.plotly_chart(fig_type, use_container_width=True)

    st.divider()

    # Brand budget distribution
    st.markdown("**Budget Distribution by Brand**")
    brand_budget = df.groupby('Brand')['PO Value - LC'].sum().sort_values(ascending=False)
    fig_brand = px.bar(
        x=brand_budget.index,
        y=brand_budget.values,
        labels={'x': 'Brand', 'y': 'Budget Amount (CNY)'},
        color=brand_budget.values,
        color_continuous_scale='Blues'
    )
    fig_brand.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_brand, use_container_width=True)

    st.divider()

    # Touchpoint budget distribution
    st.markdown("**Budget Distribution by Touchpoint**")
    touchpoint_budget = df.groupby('Touchpoint')['PO Value - LC'].sum().sort_values(ascending=False)
    fig_touchpoint = px.bar(
        x=touchpoint_budget.index,
        y=touchpoint_budget.values,
        labels={'x': 'Touchpoint', 'y': 'Budget Amount (CNY)'},
        color=touchpoint_budget.values,
        color_continuous_scale='Greens'
    )
    fig_touchpoint.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig_touchpoint, use_container_width=True)

# ==================== TAB 2: Query by Category ====================
with tab2:
    st.markdown('<div class="subheader">Budget Query by Category</div>', unsafe_allow_html=True)

    query_type = st.radio("Select Query Dimension", ["By Internal Order (IO)", "By Budget Executor"])

    if query_type == "By Internal Order (IO)":
        st.markdown("**Query by Internal Order (IO)**")

        io_list = sorted(df['Internal Order'].unique())
        selected_io = st.selectbox("Select Internal Order", io_list)

        df_filtered = df[df['Internal Order'] == selected_io]

        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total PO Amount", f"CNY {df_filtered['PO Value - LC'].sum():,.2f}")
        with col2:
            st.metric("Total GR Amount", f"CNY {df_filtered['GR Value - LC'].sum():,.2f}")
        with col3:
            st.metric("Total Invoice", f"CNY {df_filtered['Invoice Value - LC'].sum():,.2f}")
        with col4:
            st.metric("PO Count", df_filtered['PO Number'].nunique())

        st.divider()

        # Detailed statistics for this IO
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Budget Executor Distribution**")
            executor_budget = df_filtered.groupby('Budget Executor')['PO Value - LC'].sum().sort_values(ascending=False)
            fig_executor = px.bar(
                x=executor_budget.index,
                y=executor_budget.values,
                labels={'x': 'Budget Executor', 'y': 'Budget Amount (CNY)'}
            )
            fig_executor.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_executor, use_container_width=True)

        with col2:
            st.markdown("**GL Account Distribution**")
            gl_budget = df_filtered.groupby('GL Account')['PO Value - LC'].sum().sort_values(ascending=False)
            fig_gl = px.bar(
                x=gl_budget.index.astype(str),
                y=gl_budget.values,
                labels={'x': 'GL Account', 'y': 'Budget Amount (CNY)'}
            )
            fig_gl.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_gl, use_container_width=True)

        st.markdown("**All PO Details for This IO**")
        st.dataframe(
            df_filtered[['PO Number', 'PO Line', 'PO Line Description', 'Budget Executor', 
                         'PO Value - LC', 'GR Value - LC', 'Invoice Value - LC', 'PO Line Status']],
            use_container_width=True
        )

    else:  # By Budget Executor
        st.markdown("**Query by Budget Executor**")

        executor_list = sorted(df['Budget Executor'].unique())
        selected_executor = st.selectbox("Select Budget Executor", executor_list)

        df_filtered = df[df['Budget Executor'] == selected_executor]

        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total PO Amount", f"CNY {df_filtered['PO Value - LC'].sum():,.2f}")
        with col2:
            st.metric("Total GR Amount", f"CNY {df_filtered['GR Value - LC'].sum():,.2f}")
        with col3:
            st.metric("Total Invoice", f"CNY {df_filtered['Invoice Value - LC'].sum():,.2f}")
        with col4:
            st.metric("PO Count", df_filtered['PO Number'].nunique())
        with col5:
            st.metric("IO Count", df_filtered['Internal Order'].nunique())

        st.divider()

        # Detailed statistics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Internal Order Distribution**")
            io_budget = df_filtered.groupby('Internal Order')['PO Value - LC'].sum().sort_values(ascending=False).head(10)
            fig_io = px.bar(
                x=io_budget.index.astype(str),
                y=io_budget.values,
                labels={'x': 'Internal Order', 'y': 'Budget Amount (CNY)'}
            )
            fig_io.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_io, use_container_width=True)

        with col2:
            st.markdown("**PO Line Status Distribution**")
            status_budget = df_filtered.groupby('PO Line Status')['PO Value - LC'].sum()
            fig_status = px.pie(
                values=status_budget.values,
                names=status_budget.index,
                hole=0.3
            )
            fig_status.update_layout(height=400)
            st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("**All PO Details for This Executor**")
        st.dataframe(
            df_filtered[['PO Number', 'Internal Order', 'PO Line Description', 
                         'PO Value - LC', 'GR Value - LC', 'Invoice Value - LC', 'PO Line Status']],
            use_container_width=True
        )

# ==================== TAB 3: Version Comparison ====================
with tab3:
    st.markdown('<div class="subheader">Version Comparison Analysis</div>', unsafe_allow_html=True)

    st.info("Note: Current comparison is between current version and simulated previous version. In actual usage, you can upload historical version files.")

    # Overall amount comparison
    col1, col2, col3 = st.columns(3)

    current_total = df['PO Value - LC'].sum()
    previous_total = df_prev['PO Value - LC'].sum()
    change_amount = current_total - previous_total
    change_percent = (change_amount / previous_total * 100) if previous_total != 0 else 0

    with col1:
        st.metric("Current Version Total", f"CNY {current_total:,.2f}")
    with col2:
        st.metric("Previous Version Total", f"CNY {previous_total:,.2f}")
    with col3:
        st.metric(
            "Change Amount",
            f"CNY {change_amount:,.2f}",
            delta=f"{change_percent:.2f}%"
        )

    st.divider()

    # Comparison by Brand
    st.markdown("**Comparison by Brand**")

    current_by_brand = df.groupby('Brand')['PO Value - LC'].sum().reset_index()
    current_by_brand.columns = ['Brand', 'Current']

    previous_by_brand = df_prev.groupby('Brand')['PO Value - LC'].sum().reset_index()
    previous_by_brand.columns = ['Brand', 'Previous']

    comparison_brand = pd.merge(current_by_brand, previous_by_brand, on='Brand', how='outer').fillna(0)
    comparison_brand['Change'] = comparison_brand['Current'] - comparison_brand['Previous']
    comparison_brand['Change %'] = (comparison_brand['Change'] / comparison_brand['Previous'] * 100).replace([np.inf, -np.inf], 0)

    # Visualization
    fig_brand_compare = go.Figure(data=[
        go.Bar(x=comparison_brand['Brand'], y=comparison_brand['Current'], name='Current Version'),
        go.Bar(x=comparison_brand['Brand'], y=comparison_brand['Previous'], name='Previous Version')
    ])
    fig_brand_compare.update_layout(
        barmode='group',
        height=400,
        xaxis_tickangle=-45,
        hovermode='x unified'
    )
    st.plotly_chart(fig_brand_compare, use_container_width=True)

    st.dataframe(comparison_brand, use_container_width=True)

    st.divider()

    # Comparison by Executor
    st.markdown("**Comparison by Budget Executor**")

    current_by_executor = df.groupby('Budget Executor')['PO Value - LC'].sum().reset_index()
    current_by_executor.columns = ['Executor', 'Current']

    previous_by_executor = df_prev.groupby('Budget Executor')['PO Value - LC'].sum().reset_index()
    previous_by_executor.columns = ['Executor', 'Previous']

    comparison_executor = pd.merge(current_by_executor, previous_by_executor, on='Executor', how='outer').fillna(0)
    comparison_executor['Change'] = comparison_executor['Current'] - comparison_executor['Previous']
    comparison_executor['Change %'] = (comparison_executor['Change'] / comparison_executor['Previous'] * 100).replace([np.inf, -np.inf], 0)
    comparison_executor = comparison_executor.sort_values('Change', ascending=False)

    # Visualization
    fig_executor_compare = go.Figure(data=[
        go.Bar(x=comparison_executor['Executor'], y=comparison_executor['Current'], name='Current Version'),
        go.Bar(x=comparison_executor['Executor'], y=comparison_executor['Previous'], name='Previous Version')
    ])
    fig_executor_compare.update_layout(
        barmode='group',
        height=400,
        xaxis_tickangle=-45,
        hovermode='x unified'
    )
    st.plotly_chart(fig_executor_compare, use_container_width=True)

    st.dataframe(comparison_executor, use_container_width=True)

    st.divider()

    # PO with largest changes
    st.markdown("**POs with Largest Changes (Top 10)**")

    # Merge data for detailed comparison
    current_po = df.groupby('PO Number').agg({
        'PO Value - LC': 'sum',
        'PO Line Description': 'first',
        'Budget Executor': 'first'
    }).reset_index()

    previous_po = df_prev.groupby('PO Number').agg({
        'PO Value - LC': 'sum',
        'PO Line Description': 'first',
        'Budget Executor': 'first'
    }).reset_index()

    po_comparison = pd.merge(current_po, previous_po, on='PO Number', how='outer', suffixes=('_Current', '_Previous')).fillna(0)
    po_comparison['Change'] = po_comparison['PO Value - LC_Current'] - po_comparison['PO Value - LC_Previous']
    po_comparison['Change %'] = (po_comparison['Change'] / (po_comparison['PO Value - LC_Previous'] + 0.01) * 100).round(2)

    po_comparison = po_comparison.reindex(columns=['PO Number', 'PO Line Description_Current', 'Budget Executor_Current', 
                                                     'PO Value - LC_Current', 'PO Value - LC_Previous', 'Change', 'Change %'])
    po_comparison.columns = ['PO Number', 'Description', 'Executor', 'Current Amount', 'Previous Amount', 'Change Amount', 'Change %']

    po_top = po_comparison.nlargest(10, 'Change Amount')
    st.dataframe(po_top, use_container_width=True)

# ==================== TAB 4: Detailed Data ====================
with tab4:
    st.markdown('<div class="subheader">View and Export Complete Data</div>', unsafe_allow_html=True)

    # Data filtering
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_status = st.multiselect(
            "PO Line Status",
            df['PO Line Status'].unique(),
            default=df['PO Line Status'].unique()
        )

    with col2:
        selected_brand = st.multiselect(
            "Brand",
            df['Brand'].unique(),
            default=df['Brand'].unique()
        )

    with col3:
        selected_touchpoint = st.multiselect(
            "Touchpoint",
            df['Touchpoint'].unique(),
            default=df['Touchpoint'].unique()
        )

    # Apply filters
    df_display = df[
        (df['PO Line Status'].isin(selected_status)) &
        (df['Brand'].isin(selected_brand)) &
        (df['Touchpoint'].isin(selected_touchpoint))
    ]

    st.markdown(f"**Showing {len(df_display)} records (Total: {len(df)})**")

    # Display data table
    st.dataframe(
        df_display,
        use_container_width=True,
        height=500
    )

    # Export functionality
    st.divider()
    st.markdown("**Export Data**")

    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"budget_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Footer
st.divider()
st.markdown("""
---
Budget Management System | Data Last Updated: 2024 | Powered by Streamlit
""")
