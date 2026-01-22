预算管理系统 (Budget Management System)
概述
这是一个基于Streamlit框架的云端预算管理应用程序，用于PO预算的综合管理、分析和对比。
功能特性
1. 📈 汇总视图 (Summary View)
•	关键指标展示：
o	总PO金额
o	总GR金额
o	总发票金额
o	总承诺金额
o	PO单数量
•	可视化分析：
o	PO线状态分布 (饼图)
o	PO线类型分布 (饼图)
o	各品牌预算分布 (柱状图)
o	各触点预算分布 (柱状图)
2. 🔍 分类查询 (Query by Category)
支持两种查询维度：
按Internal Order (IO) 查询
•	选择特定的IO
•	显示该IO下的所有预算指标
•	预算执行人分布
•	GL账户分布
•	详细PO明细
按预算执行人 (Budget Executor) 查询
•	选择预算执行人
•	显示其负责的所有预算
•	Internal Order分布
•	PO线状态分布
•	详细PO明细
3. 📊 版本对比 (Version Comparison)
•	总额变化对比
•	品牌维度的对比分析
•	执行人维度的对比分析
•	变动最大的Top 10 PO明细
4. 📋 详细数据 (Detailed Data)
•	多维数据过滤：
o	PO Line Status
o	Brand
o	Touchpoint
•	完整数据表展示
•	CSV格式导出功能
技术栈
•	前端框架: Streamlit
•	数据处理: Pandas, NumPy
•	可视化: Plotly
•	数据源: Excel (XLSX)
•	部署平台: Streamlit Cloud / Docker / Heroku
快速开始
本地运行
1. 克隆项目
bash复制代码 收起
git clone <repository-url>
cd budget-management-system
复制
2. 创建虚拟环境
bash复制代码 收起
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows
复制
3. 安装依赖
bash复制代码 收起
pip install -r requirements.txt
复制
4. 运行应用
bash复制代码 收起
streamlit run budget_app.py
复制
应用将自动在浏览器中打开：http://localhost:8501
云端部署
Streamlit Cloud部署（推荐）
1.	准备GitHub仓库
o	确保所有必要文件上传到GitHub
2.	连接Streamlit Cloud
o	访问 https://streamlit.io/cloud
o	使用GitHub账号授权
o	选择仓库和分支
3.	部署
o	点击"New app"
o	选择main file为 budget_app.py
o	Streamlit将自动部署
Docker部署
bash复制代码 收起
docker build -t budget-app .
docker run -p 8501:8501 budget_app
复制
Heroku部署
详见 DEPLOYMENT_GUIDE.md
文件结构
复制代码 收起
budget-management-system/
├── budget_app.py                      # 主应用程序
├── requirements.txt                   # Python依赖
├── PNT_PO_Status_Report(2).xlsx       # 数据文件
├── DEPLOYMENT_GUIDE.md                # 部署指南
├── README.md                          # 本文档
├── Dockerfile                         # Docker配置（可选）
└── setup.sh                           # Heroku部署脚本（可选）
复制
数据要求
Excel文件格式
•	文件名：PNT_PO_Status_Report(2).xlsx
•	Sheet名称：Sheet1
•	必需列：
o	Company Code
o	Brand
o	Internal Order
o	GL Account
o	Budget Executor
o	PO Number
o	PO Line
o	PO Line Description
o	PO Requistioner
o	PO Creation Date
o	PO Delivery Date
o	PO Line Type
o	PO Line Status
o	Vendor
o	Node
o	Touchpoint
o	PO Value - LC
o	GR Value - LC
o	Invoice Value - LC
o	PO Commitment - LC
o	Outstanding Invoice Value - LC
常见问题
Q: 如何更新数据？
A: 替换Excel文件后，应用会自动重新加载数据。在Streamlit Cloud上，需要重新部署。
Q: 能否添加实时数据更新？
A: 可以通过连接数据库替换Excel，或使用API定期更新数据。
Q: 如何添加用户认证？
A: 可以使用Streamlit的认证库或在部署层面添加认证（如使用nginx）。
Q: 支持多用户并发访问吗？
A: Streamlit Cloud和部署版本都支持多用户并发访问。
性能优化
•	使用 @st.cache_data 缓存数据
•	对大数据集进行分页显示
•	优化Plotly图表渲染
•	使用session state管理应用状态
扩展功能建议
1.	✅ 添加数据上传功能
2.	✅ 支持多个数据源
3.	✅ 添加自定义报告生成
4.	✅ 邮件自动发送功能
5.	✅ 权限管理系统
6.	✅ 审计日志记录
贡献指南
欢迎提交问题和改进建议！
许可证
内部使用
技术支持
如有问题，请联系数据分析团队
________________________________________
最后更新: 2024年
开发框架: Streamlit 1.28.1
Python版本: 3.9+

