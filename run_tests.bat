@echo off
chcp 65001 >nul
set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8
cd /d f:\sjystraceai\whh2026tarce01
echo Starting UI tests at %date% %time%
python -m pytest tests/ui_tests/ -v --tb=short --html=report_ui.html --self-contained-html -p no:allure_adaptor --no-header -s --timeout=180
echo Tests completed at %date% %time%
echo Exit code: %ERRORLEVEL%
