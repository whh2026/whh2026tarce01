"""运行所有 UI 测试并生成报告"""
import subprocess
import sys
import os

os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

cmd = [
    sys.executable, "-m", "pytest", "tests/ui_tests/",
    "-v", "--tb=short",
    "--html=report_ui.html", "--self-contained-html",
    "-p", "no:allure_adaptor", "--no-header",
    "-s", "--timeout=180"
]

print("Running:", " ".join(cmd))
print()

with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                       text=True, encoding="utf-8", bufsize=1) as proc:
    with open("_test_run_final.txt", "w", encoding="utf-8") as f:
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            f.write(line)
            f.flush()

print(f"\nExit code: {proc.returncode}")
print("Report: report_ui.html")
print("Log: _test_run_final.txt")
