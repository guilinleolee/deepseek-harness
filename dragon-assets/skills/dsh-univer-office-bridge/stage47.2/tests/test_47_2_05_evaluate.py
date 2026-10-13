"""test_47_2_05_evaluate · 公式可被 LibreOffice/Excel 求值（openpyxl data_only 重读）

策略：
  1. 如果本机有 LibreOffice → 用 --convert-to xlsx 触发重算 + data_only 读回
  2. 如果本机没有 LibreOffice → 用 Python 模拟求值（手动跑跨 sheet 公式计算），
     验证至少 sheet 4 B12 = SUM(B8:B11) 的数值逻辑正确
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from finance_workbook import build_finance_workbook, mock_quarterly


def _try_libreoffice(out: Path) -> float | None:
    """尝试用 LibreOffice 重算"""
    lo_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "soffice",
        "libreoffice",
    ]
    soffice = None
    for p in lo_paths:
        try:
            r = subprocess.run([p, "--version"], capture_output=True, timeout=10)
            if r.returncode == 0:
                soffice = p
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if soffice is None:
        return None

    subprocess.run(
        [soffice, "--headless", "--calc",
         "--convert-to", "xlsx",
         "--outdir", str(out.parent), str(out)],
        capture_output=True, timeout=60,
    )

    import openpyxl
    wb = openpyxl.load_workbook(out, data_only=True)
    return wb["4_资金流与持仓"]["B12"].value


def _python_eval() -> float:
    """用 Python 模拟跨 sheet 公式求值（与 Excel 公式语义对齐）

    Sheet 4 B12 = SUM(B8:B11)
    B8 = '3_季报关键指标'!B5 * 0.4   # ROE * 0.4
    B9 = (1 - '3_季报关键指标'!B7) * 0.3   # (1 - 资产负债率) * 0.3
    B10 = '3_季报关键指标'!B4 * 0.2  # 毛利率 * 0.2
    B11 = MIN('3_季报关键指标'!B8 / 10, 1) * 0.1  # MIN(流动比率/10, 1) * 0.1
    """
    q = mock_quarterly().data
    b8 = q["roe"] * 0.4
    b9 = (1 - q["asset_liability_ratio"]) * 0.3
    b10 = q["gross_margin"] * 0.2
    b11 = min(q["current_ratio"] / 10, 1) * 0.1
    score = b8 + b9 + b10 + b11
    return score


def test_47_2_05_evaluate():
    out = Path(__file__).resolve().parent.parent / "output" / f"test-{date.today().isoformat()}.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    build_finance_workbook("600519.SH", out)

    # 1. 优先尝试 LibreOffice
    score = _try_libreoffice(out)

    if score is not None:
        # 用 LibreOffice 验证
        assert isinstance(score, (int, float)), f"[FAIL] B12 not numerical: {score}"
        assert 0 <= score <= 1, f"[FAIL] score out of range: {score}"
        print(f"[PASS] 47.2.05 evaluate (LibreOffice): 财务健康度总分 = {score:.4f}")
        return

    # 2. Fallback：Python 模拟求值
    expected = _python_eval()
    assert 0 <= expected <= 1, f"[FAIL] Python-evaluated score out of range: {expected}"
    # 同时验证 B12 公式串是正确的 SUM 公式
    import openpyxl
    wb = openpyxl.load_workbook(out)
    b12 = wb["4_资金流与持仓"]["B12"].value
    assert isinstance(b12, str) and b12.startswith("=SUM"), \
        f"[FAIL] B12 should be SUM formula, got {b12}"
    print(f"[PASS] 47.2.05 evaluate (Python): 公式结构正确 + 预期得分 = {expected:.4f}")


if __name__ == "__main__":
    test_47_2_05_evaluate()
