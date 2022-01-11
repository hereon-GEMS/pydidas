@ECHO OFF
REM Command file for Sphinx documentation

pushd %~dp0

IF "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=source
set BUILDDIR=build
set GH_PAGES_SOURCES=../pydidas source make.bat

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
ECHO Fetched remote gh-pages branch
git checkout gh-pages
ECHO Checkout out gh-pages branch
rem Powershell		del ../%%a -r -force
rem for old-style shell:		rmdir "%%a" /s/q 2>NUL || del "%%a" /s/q >NUL
FOR /f %%a in ('dir .. /b') DO (
	IF %%a NEQ docs (
		ECHO Deleting object %%a
		IF EXIST %%a\NUL (
			rmdir "..\%%a" /s/q 2>NUL 
		)
		IF EXIST %%a (
			del "..\%%a" /s/q >NUL
		)	
	)
)
ECHO Deleted local files
git checkout %USE_BRANCH% %GH_PAGES_SOURCES%
git reset HEAD
ECHO Checked out required files from %USE_BRANCH%.
ECHO Currently in directory %cd%.
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
ECHO Finished creating html docs.
REM Need to handle every item separately because directories cannot
REM be moved with wildcards:
FOR /f %%a in ('dir build\html /b') DO (move /y build\html\%%a "..\")
ECHO Moved pages to root dir.
rmdir "..\logs" /s /q
rmdir "..\pydidas" /s /q
rmdir build /s /q
rmdir source /s /q
rem del ../logs -r -force
rem del ../pydidas -r -force
rem del ./build -r -force
rem del ./source /-r -force
ECHO Deleted local files
git checkout %USE_BRANCH% make.bat
ECHO Updated make.bat file
git add -A
ECHO Added all files to staging
git commit -m "Generated gh-pages for %USE_BRANCH%"
ECHO Commited to git
git push origin gh-pages
ECHO Pushed to origin
git checkout %USE_BRANCH%
ECHO Changed back to %USE_BRANCH% branch.
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd

