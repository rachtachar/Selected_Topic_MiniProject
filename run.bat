@echo off
chcp 65001 >nul
echo ========================================================
echo   AI Coding Assistant with Hybrid RAG (Vector + Graph)
echo ========================================================
echo.

:: 1. Check Ollama
echo [1/3] Checking Ollama service...
ollama list >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not running! Please start Ollama by running 'ollama serve'
    pause
    exit /b 1
)
echo [OK] Ollama is running.

:: 2. Check Vector DB and Graph DB
echo [2/3] Checking Codebase Indices...
if not exist "vector_db" (
    echo [INFO] Index not found. Running setup.py on online_dataset...
    python setup.py --project ./online_dataset/src/requests
) else (
    echo [OK] Indices found in vector_db and graph_db.
)


:: 3. Launch Streamlit Application
echo [3/3] Starting Streamlit Coding Assistant UI...
echo Open your browser at http://localhost:8501
python -m streamlit run app.py
pause
