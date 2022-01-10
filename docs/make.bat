@ECHO OFF
REM Command file for Sphinx documentation

pushd %~dp0

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=source
set BUILDDIR=build
set GH_PAGES_SOURCES=../pydidas source make.bat

if "%1" == "" goto help
if "%1" == "gh-pages" (
	set USE_BRANCH=master
	goto gh-pages
)
if "%1" == "gh-pages-dev" (
	set USE_BRANCH=develop
	goto gh-pages
)

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:gh-pages
git fetch origin gh-pages
echo Fetched remote gh-pages branch
git checkout gh-pages
echo Checkout out gh-pages branch
for /f %%a in ('dir .. /b') do (
	if %%a NEQ docs (
		echo deleting object %%a
		rmdir "%%a" /s/q 2>NUL || del "%%a" /s/q >NUL
rem old:		del %%a -r -force -s -q
	)
)
echo Deleted local files
git checkout %USE_BRANCH% %GH_PAGES_SOURCES%
git reset HEAD
echo checkout out required files from %USE_BRANCH%
echo Currently in directory %cd%.
./make.bat html
echo Finished creating html docs
move build/html/* ../ -force
echo moved Paged to root dir
del ../logs -r -force
del ../pydidas -r -force
del build -r -force
del source -r -force
echo deleted local files
git checkout %USE_BRANCH% make.bat
echo Updated make.bat file
git add -A
echo Added all files to staging
git commit -m "Generated gh-pages for %USE_BRANCH%"
echo Commited to git
git push origin gh-pages
echo Pushed to origin
git checkout %USE_BRANCH%
echo Changed back to %USE_BRANCH% branch.
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd

