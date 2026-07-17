@echo off
REM 运行所有 UI 测试
python -m pytest tests/ui_tests/ %*
