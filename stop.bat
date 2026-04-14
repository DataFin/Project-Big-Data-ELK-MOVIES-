@echo off
:: =============================================================
:: stop.bat — Arret de la stack ELK
:: Equipe : Sandrine (lead), Audrey, Destine, Alexandre
:: Feature : F1 - Bootstrap stack
:: Description : Arrete proprement tous les services ELK
::               sans supprimer les donnees indexees
:: =============================================================

echo.
echo ========================================
echo   Arret de la stack ELK Movies
echo ========================================
echo.

:: Arreter les conteneurs sans supprimer les volumes
:: Les donnees Elasticsearch sont conservees grace au volume
docker compose stop

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Stack ELK arretee avec succes !
    echo ========================================
    echo.
    echo   Les donnees sont conservees.
    echo   Pour redemarrer : start.bat
    echo.
) else (
    echo [ERREUR] Probleme lors de l'arret des conteneurs.
)

pause
