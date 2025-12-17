@echo off
echo ===============================================
echo      A GUARDAR NA NUVEM (Backup)
echo ===============================================
echo.
git add .
echo Ficheiros preparados.
echo.
set /p desc="Escreva o que fez hoje (ou pressione ENTER para usar 'Atualizacao rapida'): "
if "%desc%"=="" set desc="Atualizacao rapida"

git commit -m "%desc%"
echo.
echo A enviar para o GitHub...
git push
echo.
echo ===============================================
echo      SUCESSO! TUDO GUARDADO NA NUVEM.
echo ===============================================
pause
