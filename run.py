# run.py
from app import app
from index import display_page  # Ensures callbacks get registered

if __name__ == '__main__':
    app.run_server(debug=True)
