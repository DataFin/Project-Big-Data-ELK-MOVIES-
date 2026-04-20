@echo off
:: =============================================================
:: health-check.bat — Verification sante des services ELK
:: Equipe : Sandrine (lead), Audrey, Destine, Alexandre
:: Feature : F1 - Bootstrap stack
:: Description : Verifie que les 3 services ELK sont
::               operationnels et repond correctement
:: =============================================================

echo.
echo ========================================
echo   Verification sante des services ELK
echo ========================================
echo.

:: -------------------------------------------------------
:: TEST 1 : Elasticsearch
:: -------------------------------------------------------
echo [TEST 1] Elasticsearch (http://localhost:9200)
curl -s -o nul -w "%%{http_code}" http://localhost:9200 > temp_status.txt 2>&1
set /p STATUS=<temp_status.txt
del temp_status.txt

if "%STATUS%"=="200" (
    echo          Status : OK ^(200^) ✓
) else (
    echo          Status : ERREUR ^(code: %STATUS%^)
    echo          Verifiez que Docker est demarre
)

echo.

:: -------------------------------------------------------
:: TEST 2 : Cluster Elasticsearch
:: -------------------------------------------------------
echo [TEST 2] Cluster Elasticsearch
curl -s http://localhost:9200/_cluster/health
echo.
echo.

:: -------------------------------------------------------
:: TEST 3 : Kibana
:: -------------------------------------------------------
echo [TEST 3] Kibana (http://localhost:5601)
curl -s -o nul -w "%%{http_code}" http://localhost:5601/api/status > temp_status.txt 2>&1
set /p STATUS=<temp_status.txt
del temp_status.txt

if "%STATUS%"=="200" (
    echo          Status : OK ^(200^) ✓
) else (
    echo          Status : ERREUR ^(code: %STATUS%^)
    echo          Kibana n'est peut-etre pas encore pret
)

echo.

:: -------------------------------------------------------
:: TEST 4 : Index movies_raw
:: -------------------------------------------------------
echo [TEST 4] Index movies_raw
curl -s http://localhost:9200/movies_raw/_count
echo.
echo.

:: -------------------------------------------------------
:: TEST 5 : Index movies_clean (disponible apres F3/F4)
:: -------------------------------------------------------
echo [TEST 5] Index movies_clean
curl -s http://localhost:9200/movies_clean/_count
echo.
echo.

:: -------------------------------------------------------
:: TEST 6 : Etat des conteneurs Docker
:: -------------------------------------------------------
echo [TEST 6] Etat des conteneurs Docker
docker compose ps
echo.

echo ========================================
echo   Verification terminee
echo ========================================
echo.
echo   Elasticsearch : http://localhost:9200
echo   Kibana        : http://localhost:5601
echo.
pause
