@echo off
REM Incident Response Simulation - Analysis Runner
REM This script runs all analysis tools to generate reports

echo ============================================
echo Incident Response Simulation - Analysis
echo ============================================
echo.

echo Running log analysis...
cd scripts\analysis
python log_analyzer.py
cd ..\..

echo.
echo Running timeline generation...
cd scripts\forensics
python timeline_generator.py
cd ..\..

echo.
echo Running evidence extraction...
cd scripts\forensics
python evidence_extractor.py
cd ..\..

echo.
echo ============================================
echo Analysis Complete!
echo ============================================
echo.
echo Reports generated in the reports/ directory:
echo   - log_analysis_report.txt
echo   - incident_timeline.txt
echo   - evidence_report.txt
echo   - evidence_package.json
echo.
pause

