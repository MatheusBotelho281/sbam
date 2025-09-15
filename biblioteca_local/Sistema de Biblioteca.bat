@echo off
echo Iniciando o banco de dados de livros...
start cmd /k "python database.py"

echo Iniciando o banco de dados de usuarios...
start cmd /k "python database_usuarios.py"

echo Aguardando 3 segundos para inicializar os bancos...
timeout /t 3 /nobreak >nul

echo Iniciando a aplicacao...
start cmd /k "python app.py"

echo Aguardando 5 segundos para inicializar a aplicacao...
timeout /t 5 /nobreak >nul

echo Iniciando Ngrok na porta 9991...
start cmd /k "ngrok http 9991"

echo.
echo Sistema de Biblioteca Amor Divino iniciado com sucesso!
echo.
echo - Banco de dados de livros: biblioteca.db
echo - Banco de dados de usuarios: usuarios_biblioteca.db
echo - Aplicacao rodando na porta 9991
echo - Ngrok disponibilizando acesso externo
echo.
echo Acesse: http://localhost:9991 para usar o sistema
echo.
pause

exit