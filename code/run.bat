@echo off
rem Check if python 3 is already in path, then skip
call py3_env
@REM SET PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis\python;%PYTHONPATH%
@REM SET PATH=%OSGEO4W_ROOT%\apps\qgis\bin;%OSGEO4W_ROOT%\apps\qgis\python\plugins;%PATH%
@REM SET PROJ_LIB=%OSGEO4W_ROOT%\share\proj
@REM SET GDAL_LIB=%OSGEO4W_ROOT%\share
@REM SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins
@REM SET QGIS_PATH=%OSGEO4W_ROOT%\apps\qgis
@REM echo %PROJ_LIB%
python -m calc_heat_island %*