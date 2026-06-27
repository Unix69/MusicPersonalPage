@echo off
:: --- Verifica se Python è installato ---
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python non trovato. Installa Python 3.8+ e riprova.
    pause
    exit /b
)

:: --- Rimuove eventuale venv fallito ---
IF EXIST venv (
    echo Rimuovo vecchio ambiente virtuale...
    rmdir /s /q venv
)

:: --- Crea ambiente virtuale ---
python -m venv venv

:: --- Attiva ambiente virtuale ---
call venv\Scripts\activate

:: --- Aggiorna pip ---
python -m pip install --upgrade pip

:: --- Aggiorna requirements.txt con versioni compatibili ---
(
echo Flask==2.2.5
echo Flask-Admin==1.6.1
echo Flask-SQLAlchemy==3.0.5
echo Flask-WTF==1.1.1
echo WTForms==3.0.1
echo python-dotenv==1.0.0
echo Pillow==9.5.0
) > requirements.txt

:: --- Installa pacchetti ---
pip install -r requirements.txt

:: --- Crea cartella immagini se non esiste ---
IF NOT EXIST "static\images" mkdir static\images

echo.
echo Installazione completata. Per avviare l'app usa start_app.bat
pause
