@echo off
:: =============================================================
:: start.bat — Lancement de la stack ELK
:: Equipe : Sandrine (lead), Audrey, Destine, Alexandre
:: Feature : F1 - Bootstrap stack
:: Description : Demarre tous les services ELK en arriere-plan
::               et verifie qu'ils sont bien operationnels
:: =============================================================

echo.
echo ========================================
echo   Demarrage de la stack ELK Movies
echo ========================================
echo.

:: Verifier que Docker est en cours d'execution
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker Desktop n'est pas demarre !
    echo Veuillez demarrer Docker Desktop et reessayer.
    pause
    exit /b 1
)

echo [1/3] Docker Desktop detecte... OK
echo.

:: Demarrer les conteneurs en arriere-plan
echo [2/3] Demarrage des conteneurs ELK...
docker compose up -d

if %errorlevel% neq 0 (
    echo [ERREUR] Echec du demarrage des conteneurs.
    pause
    exit /b 1
)

echo.
echo [3/3] En attente que les services soient prets...
echo       (cela peut prendre 30 a 60 secondes)
echo.

:: Attendre 30 secondes que les services demarrent
timeout /t 30 /nobreak > nul

:: Verifier Elasticsearch
echo Verification Elasticsearch (http://localhost:9200)...
curl -s http://localhost:9200 > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Elasticsearch est operationnel
) else (
    echo [ATTENTION] Elasticsearch ne repond pas encore, patientez...
)

echo.
echo ========================================
echo   Stack ELK demarree avec succes !
echo ========================================
echo.
echo   Elasticsearch : http://localhost:9200
echo   Kibana        : http://localhost:5601
echo.
echo   Pour verifier l'etat des services : health-check.bat
echo   Pour arreter la stack             : stop.bat
echo.
pause
