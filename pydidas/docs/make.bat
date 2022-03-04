@ECHO OFF
REM Command file for Sphinx documentation

pushd %~dp0

IF "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=source
set BUILDDIR=build
set GH_PAGES_SOURCES=../../pydidas %SOURCEDIR% make.bat

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
git fetch origin gh-pages
git checkout gh-pages
git clean -xfdg
git checkout %USE_BRANCH% %GH_PAGES_SOURCES%
git reset HEAD
ECHO Checked out required files from %USE_BRANCH%.
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
ECHO Finished creating html docs.
REM Need to handle every item separately because directories cannot
REM be moved with wildcards:
FOR /f %%a in ('dir %BUILDDIR%\html /b') DO (move /y %BUILDDIR%\html\%%a "..\..\")
CD ../..
rmdir logs /s /q
rmdir pydidas /s /q

ECHO Deleted local files
git checkout %USE_BRANCH% make.bat
ECHO Updated make.bat file
git add --all ':!pydidas' ':!logs'
git add pydidas/docs/make.bat
ECHO Added all files to staging
git commit -m "Generated gh-pages for %USE_BRANCH%"
ECHO Commited to git
git push origin gh-pages
ECHO Pushed to origin
git add --all
git stash
git checkout %USE_BRANCH%
git stash clear
ECHO Changed back to %USE_BRANCH% branch.
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
