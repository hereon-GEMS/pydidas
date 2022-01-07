@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build
set GH_PAGES_SOURCES=source pydidas make.bat
if "%1" == "" goto help
if "%1" == "gh-pages" goto gh-pages

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


    git checkout gh-pages
    rm -rf build _sources _static
    git checkout master $(GH_PAGES_SOURCES)
    git reset HEAD
    make html
    mv -fv build/html/* ./
    rm -rf $(GH_PAGES_SOURCES) build
    git add -A
    git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages ; git checkout master


%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:gh-pages
git checkout gh-pages
del /r /f  build _sources _static
git checkout master %GH_PAGES_SOURCES%
git reset HEAD
./make.bat html
move /Y build/html/* ./
del /r /f %GH_PAGES_SOURCES% build
git add -A
git ci -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages ; git checkout master


:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
