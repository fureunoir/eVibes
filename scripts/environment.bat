@echo off
setlocal enabledelayedexpansion

:: Check if .env file exists
if not exist .env (
  echo .env file not found!
  exit /b 1
)

:: Read and set variables from .env file
for /f "usebackq tokens=1,* delims==" %%i in (.env) do (
  set "line=%%i"
  if not "!line!"=="" (
    if "!line:~0,1!" neq "#" (
      set "key=%%i"
      set "value=%%j"
      setx !key! "!value!"
      set "!key!=!value!"
    )
  )
)

echo Environment variables have been exported.
