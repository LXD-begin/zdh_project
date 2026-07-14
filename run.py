from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest


ROOT_DIR = Path(__file__).resolve().parent
TESTCASE_DIR = ROOT_DIR / "testcase"
OUTPUTS_DIR = ROOT_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
LOGS_DIR = OUTPUTS_DIR / "logs"


def ensure_output_dirs() -> tuple[Path, Path]:
    """创建报告目录和按日期划分的日志目录。"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    log_dir = LOGS_DIR / datetime.now().strftime("%Y%m%d")
    log_dir.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR, log_dir


def build_pytest_args(report_dir: Path, log_file: Path) -> list[str]:
    """构建 pytest 执行参数。"""
    pytest_args = [
        str(TESTCASE_DIR),
        "-v",
        "--log-file",
        str(log_file),
        "--log-file-mode",
        "w",
        "--log-file-level",
        "INFO",
    ]

    # 仅在安装 allure 插件时输出 Allure 结果，避免无关依赖导致执行失败。
    if importlib.util.find_spec("allure_pytest"):
        allure_result_dir = report_dir / f"allure-results-{datetime.now():%Y%m%d_%H%M%S}"
        allure_result_dir.mkdir(parents=True, exist_ok=True)
        pytest_args.extend(["--alluredir", str(allure_result_dir)])

    return pytest_args


def generate_allure_report(allure_result_dir: Path, report_dir: Path) -> None:
    """在本机存在 allure 命令时生成可查看的 Allure 报告。"""
    if not shutil.which("allure"):
        print("未检测到 allure 命令，已保留 Allure 结果文件，暂不生成 HTML 报告。")
        return

    allure_report_dir = report_dir / f"allure-report-{datetime.now():%Y%m%d_%H%M%S}"
    subprocess.run(
        [
            "allure",
            "generate",
            str(allure_result_dir),
            "-o",
            str(allure_report_dir),
            "--clean",
        ],
        check=False,
    )
    print(f"Allure 报告目录: {allure_report_dir}")


def main() -> int:
    """一键收集并执行项目中的全部测试用例。"""
    if not TESTCASE_DIR.exists():
        print(f"未找到测试用例目录: {TESTCASE_DIR}")
        return 1

    report_dir, log_dir = ensure_output_dirs()
    log_file = log_dir / f"pytest_{datetime.now():%H%M%S}.log"
    pytest_args = build_pytest_args(report_dir=report_dir, log_file=log_file)
    allure_result_dir: Path | None = None

    if "--alluredir" in pytest_args:
        allure_result_dir = Path(pytest_args[pytest_args.index("--alluredir") + 1])

    if "--alluredir" not in pytest_args:
        print("未检测到 allure-pytest，当前仅执行用例并输出日志，不生成 Allure 结果。")

    print(f"开始执行用例，测试目录: {TESTCASE_DIR}")
    print(f"日志文件: {log_file}")
    exit_code = pytest.main(pytest_args)

    if exit_code == 0 and allure_result_dir is not None:
        generate_allure_report(allure_result_dir=allure_result_dir, report_dir=report_dir)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
