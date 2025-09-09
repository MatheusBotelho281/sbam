@echo off
echo Iniciando o banco de dados...
start cmd /k "python database.py"

echo Iniciando a aplicacao...
start cmd /k "python app.py"

echo Iniciando Ngrok na porta 9991...
start cmd /k "ngrok http 9991"

exit