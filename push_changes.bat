@echo off
echo ========================================================
echo  Attempting to read commit message from commit_message.txt
echo ========================================================

REM Check if commit_message.txt exists and is not empty
if not exist "commit_message.txt" (
    echo ERROR: commit_message.txt not found.
    pause
    exit /b 1
)

set "firstLine="
for /f "usebackq delims=" %%L in ("commit_message.txt") do (
    set "firstLine=%%L"
    goto :foundFirstLine
)

:foundFirstLine
if not defined firstLine (
    echo ERROR: commit_message.txt is empty.
    pause
    exit /b 1
)

REM Use the first line as the main commit title. 
REM Subsequent lines in commit_message.txt can serve as the extended description.
REM git commit requires the full message to be passed with -m or -F.
REM For simplicity here, we'll use the whole file content for the commit message.
REM Git itself handles multi-line messages well when passed with -F.
REM However, batch scripting makes passing multi-line from variable to -m tricky.
REM So we will use the -F option with git commit.

echo Commit message will be read from commit_message.txt
echo.

echo ========================================================
echo  Adding all changes to staging...
echo ========================================================
git add .

echo.
echo ========================================================
echo  Committing changes with message from commit_message.txt...
echo ========================================================
git commit -F "commit_message.txt"

if errorlevel 1 (
    echo ERROR: Git commit failed. See messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo  Pushing changes to origin main...
echo ========================================================
git push origin main
REM If your default branch is not 'main', change 'main' above 
REM (e.g., to 'master' or your branch name).

if errorlevel 1 (
    echo ERROR: Git push failed. Ensure remote 'origin' is configured and reachable.
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo  Done.
echo ========================================================
pause