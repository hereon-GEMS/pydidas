@ECHO OFF
REM Command file for Sphinx documentation

pushd %~dp0

IF "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=source
set BUILDDIR=build
set DOCSDIR=pydidas/docs
IF "%1" == "" goto help
IF "%1" == "gh-pages" (
	set USE_BRANCH=master
	goto gh-pages
)
IF "%1" == "gh-pages-dev" (
	set USE_BRANCH=develop
	goto gh-pages
)

%SPHINXBUILD% >NUL 2>NUL
IF errorlevel 9009 (
	ECHO.
	ECHO.The 'sphinx-build' command was not found. Make sure you have Sphinx
	ECHO.installed, then set the SPHINXBUILD environment variable to point
	ECHO.to the full path of the 'sphinx-build' executable. Alternatively you
	ECHO.may add the Sphinx directory to PATH.
	ECHO.
	ECHO.If you don't have Sphinx installed, grab it from
	ECHO.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:gh-pages
CD ../..
git fetch origin gh-pages
git checkout gh-pages
git clean -xfdq
git checkout %USE_BRANCH% pydidas
git reset HEAD
ECHO Checked out required files from %USE_BRANCH%.
%SPHINXBUILD% -M html %DOCSDIR%/%SOURCEDIR% %DOCSDIR%\%BUILDDIR% %SPHINXOPTS% %O%
ECHO Finished creating html docs.
REM Need to handle every item separately because directories cannot
REM be moved with wildcards:
ROBOCOPY %DOCSDIR%\%BUILDDIR%\html . *.* /S /MOVE /NFL /NDL
FOR /d %%a IN ("%CD%\pydidas\*") DO IF /i NOT "%%a"=="%CD%\pydidas\docs" RMDIR /S /Q "%%a"
FOR /r %%a IN ("%CD%\pydidas\*") DO IF DEL /F /Q "%%a"
RMDIR /S /Q pydidas\docs\source 
RMDIR /S /Q pydidas\docs\build
ECHO Deleted local files
git add --all
ECHO Added all files to staging
git commit -m "Generated gh-pages for %USE_BRANCH%"
ECHO Commited to git
git push origin gh-pages
ECHO Pushed to origin
git add --all
git stash
git checkout %USE_BRANCH%
git stash clear
git clean -xfdq
ECHO Changed back to %USE_BRANCH% branch.
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd

