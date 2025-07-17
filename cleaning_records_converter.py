import pandas as pd
import streamlit as st
import re
from io import BytesIO
import base64

# 设置页面标题和布局
st.set_page_config(page_title="清洗服务记录转换工具", page_icon="🧹", layout="wide")
st.title("🧹 清洗服务记录转换工具")
st.markdown("""
将无序繁杂的清洗服务记录文本转换为结构化的表格数据，并导出为Excel文件。
""")

# 创建示例文本
sample_text = """
张师傅在2023年10月15日为阳光花园小区的1号楼2单元302室进行了深度清洁，清洗方式为湿式清洁，清洗内容包括地面、墙面和窗户，共进行了3次，总金额为300元，付款方式为微信支付。
李师傅在2023年11月20日为绿景小区的2号楼1单元101室进行了日常清洁，清洗方式为干式清洁，清洗内容包括地面和墙面，共进行了2次，总金额为200元，付款方式为支付宝支付。
王师傅在2023年12月5日为金色家园小区的3号楼3单元203室进行了深度清洁，清洗方式为湿式清洁，清洗内容包括地面、墙面和窗户，共进行了4次，总金额为400元，付款方式为现金支付。
赵师傅在2024年1月10日为蓝天海岸小区的5号楼4单元501室进行了精细清洁，清洗方式为湿式清洁，清洗内容包括地面、墙面、窗户和天花板，共进行了1次，总金额为500元，付款方式为银行转账。
刘师傅在2024年2月15日为世纪城小区的8号楼2单元1503室进行了日常清洁，清洗方式为干式清洁，清洗内容包括地面和家具，共进行了2次，总金额为350元，付款方式为支付宝支付。
孙师傅在2024年3月22日为幸福里小区的12号楼3单元601室进行了深度清洁，清洗方式为湿式清洁，清洗内容包括地面、墙面、窗户和卫生间，共进行了3次，总金额为450元，付款方式为微信支付。
"""

# 文本输入区域
with st.expander("📝 输入清洗服务记录文本", expanded=True):
    input_text = st.text_area("请输入清洗服务记录（每行一条记录）:",
                             value=sample_text,
                             height=300,
                             placeholder="请输入清洗服务记录文本...")

# 处理按钮
if st.button("🚀 转换文本为表格", use_container_width=True):
    if not input_text.strip():
        st.warning("请输入清洗服务记录文本！")
        st.stop()

    # 处理文本
    lines = input_text.strip().split('\n')
    data = []
    errors = []

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        try:
            # 使用正则表达式提取信息
            师傅 = re.search(r'^(.+?)在', line)
            师傅 = 师傅.group(1).strip() if 师傅 else "未知"

            日期 = re.search(r'在(.+?)日', line)
            日期 = 日期.group(1).strip() + '日' if 日期 else "日期未知"

            小区 = re.search(r'为(.+?)小区的', line)
            小区 = 小区.group(1).strip() + '小区' if 小区 else "未知小区"

            楼号 = re.search(r'(\d+)号楼', line)
            楼号 = 楼号.group(1) if 楼号 else "未知"

            单元号 = re.search(r'号楼(\d+)单元', line)
            单元号 = 单元号.group(1) if 单元号 else "未知"

            房号 = re.search(r'单元(\d+室)', line)
            房号 = 房号.group(1) if 房号 else "未知"

            清洗方式 = re.search(r'进行了(.+?)清洁', line)
            清洗方式 = 清洗方式.group(1).strip() + '清洁' if 清洗方式 else "未知"

            清洗内容 = re.search(r'包括(.+?)，共进行了', line)
            清洗内容 = 清洗内容.group(1).strip() if 清洗内容 else "未知"

            次数 = re.search(r'共进行了(\d+)次', line)
            次数 = int(次数.group(1)) if 次数 else 0

            金额 = re.search(r'总金额为(\d+)元', line)
            金额 = int(金额.group(1)) if 金额 else 0

            付款方式 = re.search(r'付款方式为(.+?)$', line)
            付款方式 = 付款方式.group(1).strip() if 付款方式 else "未知"

            # 添加到数据列表
            data.append([
                师傅, 小区, 日期, 小区, f"{楼号}号楼{单元号}单元",
                房号, 清洗方式, 清洗内容, 次数, 金额, 付款方式
            ])
        except Exception as e:
            errors.append(f"行 {i+1} 解析失败: {str(e)}")
            st.warning(f"行 {i+1} 解析失败: {str(e)}")

    # 定义表头
    columns = ['师傅', '区域', '日期', '物业', '地址', '房号', '清洗方式', '清洗内容', '数量', '金额', '付款方式']

    if data:
        # 创建DataFrame
        df = pd.DataFrame(data, columns=columns)

        # 显示成功信息
        st.success(f"成功解析 {len(data)} 条记录！")

        # 显示数据表格
        st.subheader("清洗服务记录表格")
        st.dataframe(df, use_container_width=True)

        # 添加统计信息
        col1, col2, col3 = st.columns(3)
        col1.metric("总记录数", len(df))
        col2.metric("总金额", f"{df['金额'].sum()} 元")
        col3.metric("平均金额", f"{df['金额'].mean():.0f} 元")

        # 添加图表
        st.subheader("数据可视化")
        tab1, tab2, tab3 = st.tabs(["按师傅统计", "按清洗方式统计", "按金额分布"])

        with tab1:
            st.bar_chart(df['师傅'].value_counts())

        with tab2:
            st.bar_chart(df['清洗方式'].value_counts())

        with tab3:
            st.bar_chart(df['金额'])

        # 导出Excel功能
        st.subheader("导出数据")

        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='清洗服务记录')
            workbook = writer.book
            worksheet = writer.sheets['清洗服务记录']

            # 设置列宽
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(idx, idx, max_len)

        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="清洗服务记录.xlsx">⬇️ 下载Excel文件</a>'
        st.markdown(href, unsafe_allow_html=True)

    else:
        st.error("未能解析出任何记录，请检查输入格式！")

# 使用说明
st.divider()
st.subheader("使用说明")
st.markdown("""
1. 在文本框中输入清洗服务记录（每行一条记录）
2. 点击 **🚀 转换文本为表格** 按钮
3. 查看解析后的表格数据
4. 点击 **⬇️ 下载Excel文件** 导出数据

### 输入格式示例:张师傅在2023年10月15日为阳光花园小区的1号楼2单元302室进行了深度清洁，清洗方式为湿式清洁，清洗内容包括地面、墙面和窗户，共进行了3次，总金额为300元，付款方式为微信支付。
李师傅在2023年11月20日为绿景小区的2号楼1单元101室进行了日常清洁，清洗方式为干式清洁，清洗内容包括地面和墙面，共进行了2次，总金额为200元，付款方式为支付宝支付。

text
""")

# 页脚
st.divider()
st.caption("© 2023 清洗服务记录转换工具 | 使用Python和Streamlit构建")