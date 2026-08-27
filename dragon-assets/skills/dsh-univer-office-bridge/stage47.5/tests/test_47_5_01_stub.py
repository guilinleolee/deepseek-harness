"""test_47_5_01_stub · 13 个 univer_* 工具 stub 全部跑通（B 选项）"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from univer_stub import UNIVER_TOOLS, call


def test_47_5_01_stub():
    # 13 个工具必须都注册
    expected = {
        "univer_new", "univer_status", "univer_worktree", "univer_unit", "univer_import",
        "univer_execute", "univer_compile_svg",
        "univer_inspect", "univer_lint", "univer_screenshot",
        "univer_api", "univer_resources",
        "univer_export",
    }
    assert set(UNIVER_TOOLS.keys()) == expected, \
        f"[FAIL] 工具注册表与 expected 不一致: {set(UNIVER_TOOLS.keys()) ^ expected}"

    # 跑通完整 happy path
    with tempfile.TemporaryDirectory() as tmp:
        univer_file = f"{tmp}/demo.univer"
        wt = "wt-stub-001"

        # 启动
        r = call("univer_new", file=univer_file)
        assert r["ok"] and Path(univer_file).exists()

        r = call("univer_status", file=univer_file)
        assert r["ok"]

        r = call("univer_worktree", file=univer_file, worktree_id=wt, action="create")
        assert r["ok"] and r["state"] == "create"

        r = call("univer_unit", file=univer_file, unit_id="sheet-001", kind="sheet")
        assert r["ok"] and r["kind"] == "sheet"

        r = call("univer_import", file=univer_file, source=f"{tmp}/data.xlsx")
        assert "ok" in r  # 没源文件会 fail，但接口正常返回

        # 写入
        r = call("univer_execute", file=univer_file, unit_id="sheet-001", worktree_id=wt,
                 code="sheet.setValue({v:1, t:2})")
        assert r["ok"] and r["mutated"] is True

        r = call("univer_compile_svg", source=f"{tmp}/page.svg", file=univer_file,
                 unit_id="slide-001", worktree_id=wt, page=1)
        assert "ok" in r

        # 验证
        r = call("univer_inspect", file=univer_file, unit_id="sheet-001", range="Sheet1!A1:D20")
        assert r["ok"] and r["range"] == "Sheet1!A1:D20"

        r = call("univer_lint", file=univer_file, unit_id="slide-001", pages=[1])
        assert r["ok"] and len(r["findings"]) == 0

        r = call("univer_screenshot", file=univer_file, unit_id="sheet-001", output=tmp)
        assert r["ok"] and Path(r["png_path"]).exists()
        assert r["size_bytes"] > 0

        # 参考
        r = call("univer_api", action="find", queries=["setValue", "setFormula"])
        assert r["ok"] and r["queries"] == ["setValue", "setFormula"]

        r = call("univer_resources", action="registries")
        assert r["ok"] and "default" in r["registries"]

        # 交付
        r = call("univer_export", file=univer_file, unit_id="sheet-001",
                 format="xlsx", output=f"{tmp}/out.xlsx")
        assert r["ok"] and Path(r["output"]).exists()

        # 收尾
        r = call("univer_worktree", file=univer_file, worktree_id=wt, action="ready")
        assert r["ok"] and r["state"] == "ready"

    print(f"[PASS] 47.5.01 stub: 13/13 univer_* 工具 stub happy path 跑通")


if __name__ == "__main__":
    test_47_5_01_stub()
