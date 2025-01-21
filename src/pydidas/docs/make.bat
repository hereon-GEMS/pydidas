@ECHO OFF

REM Command file for Sphinx documentation
REM Copyright 2024, Helmholtz-Zentrum Hereon
REM
REM SPDX-License-Identifier: CC-BY-4.0

pushd %~dp0

IF "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)

set SOURCEDIR=src
set BUILDDIR=../sphinx

IF "%1" == "" goto help

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

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd

