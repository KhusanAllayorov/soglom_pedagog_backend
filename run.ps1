# Backendni lokal ishga tushiradi.
#
# Ishlatish (loyiha ildizidan):
#   powershell -ExecutionPolicy Bypass -File run.ps1
#
# PYTHONDONTWRITEBYTECODE — Python .pyc fayllarini va __pycache__ papkalarini
# yaratmaydi, shuning uchun loyiha toza qoladi.

$env:PYTHONDONTWRITEBYTECODE = "1"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
