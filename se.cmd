@ECHO OFF

echo Running %USERNAME% private env

set SCRIPT_DIR=%~dp0

if exist %SCRIPT_DIR%\Alias.txt (
    SET MYSTUFF=%SCRIPT_DIR%
    goto ProbeDone
)

if exist c:\OneDrive\bin\Alias.txt (
    SET MYSTUFF=c:\OneDrive
    goto ProbeDone
)

if exist d:\OneDrive\bin\Alias.txt (
    SET MYSTUFF=d:\OneDrive
    goto ProbeDone
)

:ProbeDone
echo Env folder is %MYSTUFF%
SET ALIAS=%MYSTUFF%\Alias.txt
echo Alias is %Alias%

doskey /macrofile=%ALIAS%
SET path=%path%;%MYSTUFF%\bin;%MYSTUFF%\bin\SD
SET SDFORMEDITOR=sdforms.exe

color 1F

