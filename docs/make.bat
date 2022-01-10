@ECHO OFF
REM Command file for Sphinx documentation

pushd %~dp0
set CUR_LOC=%CD%

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=source
set BUILDDIR=build

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
echo The current locaction is %CUR_LOC%
if %CUR_LOC:~-4% == "docs" (
	cd ..
	set GH_PAGES_SOURCES=../pydidas source make.bat
	set LOCAL_PATH=
	set RESULTS=../
)
if %CUR_LOC:~-7% == "pydidas" (
	set GH_PAGES_SOURCES=pydidas docs/source docs/make.bat
	set LOCAL_PATH=docs/
	set RESULTS=
)
git checkout gh-pages
del %LOCAL_PATH%build -r -force
del %RESULTS%_sources -r -force
del %RESULTS%_static -r -force
del %RESULTS%_images -r -force
git checkout %USE_BRANCH% %GH_PAGES_SOURCES%
git reset HEAD
./%LOCAL_PATH%make.bat html
move %LOCAL_PATH%/build/html/* ./ -force
del %RESULTS%logs -r -force
del %RESULTS%pydidas -r -force
del %RESULTS%docs/* -r -force
git add -A
git commit -m "Generated gh-pages for %USE_BRANCH%"
git push origin gh-pages
git checkout %USE_BRANCH%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
