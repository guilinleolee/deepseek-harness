"""
无API跨系统集成示例
Mano-P核心能力：直接操作GUI元素，无需API接口
"""

import asyncio
from mano_vla_client import ManoPVLAClient

async def extract_sap_to_excel():
    """示例：从SAP系统提取数据到Excel（无需API）"""
    client = ManoPVLAClient()

    # 任务描述：打开SAP → 导航到报表 → 选择日期范围 → 导出数据 → 保存为Excel
    task = """
    1. 打开SAP GUI客户端
    2. 登录公司SAP系统 (使用已保存的凭证)
    3. 导航到: Reporting → Financial Reports → P&L Summary
    4. 选择日期范围: 2024-01-01 到 2024-03-31
    5. 点击"Execute"执行报表
    6. 选择所有数据行
    7. 点击"Export" → "Download as Excel"
    8. 保存到: ~/Downloads/SAP_PnL_Report.xlsx
    """

    result = await client.cross_system_extract(
        source_app="SAP GUI",
        target_format="Excel"
    )

    print(f"提取结果: {result}")
    await client.close()

if __name__ == "__main__":
    asyncio.run(extract_sap_to_excel())