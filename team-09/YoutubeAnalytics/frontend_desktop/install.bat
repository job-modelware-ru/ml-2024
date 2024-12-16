python -m venv venv
if exist venv\Scripts\activate (
    call venv\Scripts\activate
    pip install -r requirements.txt
    deactivate
)