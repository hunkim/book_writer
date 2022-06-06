VENV = .book_venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
STREAMLIT = $(VENV)/bin/streamlit

run: $(VENV)/bin/activate
	$(STREAMLIT) run app.py --server.runOnSave=true --server.enableCORS=false --server.enableXsrfProtection=false --server.port=9001


test_db: $(VENV)/bin/activate
	$(PYTHON) firestore_db.py


$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt


clean:
	rm -rf __pycache__
	rm -rf $(VENV)