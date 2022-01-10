@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build
set GH_PAGES_SOURCES=pydidas docs/source docs/make.bat
if "%1" == "" goto help
if "%1" == "gh-pages" (
	set %USE_BRANCH%=master
	goto gh-pages
)
if "%1" == "gh-pages-dev" (
	set %USE_BRANCH%=develop
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
cd ..
git checkout gh-pages
del build -r -force
del _sources -r -force
del _static -r -force
del _images -r -force
git checkout %USE_BRANCH% %GH_PAGES_SOURCES%
git reset HEAD
./docs/make.bat html
move docs/build/html/* ./ -force
del logs -r -force
del pydidas -r -force
del docs/* -r -force
git add -A
git commit -m "Generated gh-pages for %USE_BRANCH%"
git push origin gh-pages
git checkout %USE_BRANCH%


:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
