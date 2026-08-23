# WeasyPrint libraries
$env:WEASYPRINT_DLL_DIRECTORIES="C:\msys64\ucrt64\bin"

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Start Django
python manage.py runserver