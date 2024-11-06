PYTHON_VERSION=3.12
PY=python$(PYTHON_VERSION)

remove_trash:
	find . -type d -name "__pycache__" -exec rm -rf {} +

clear: remove_trash

clean: clear

code_style:
	find . -name "*.py" -exec $(PY) -m pycodestyle {} \;

remove_db:
	rm -rf app/database/*.db app/database/*.rdb

# test_empty_db: remove_db start_server kill_server
# 	cd tests && $(PY) -m pytest test_empty_database.py
# 	kill_server

start_server: install
	cd app && $(PY) main.py &

start: start_server

install_libs:
	$(PY) -m pip install -r requirements.txt

kill_server:
	kill -9 $(shell lsof -t -i:8000)
	kill -9 $(shell lsof -t -i:6379)

install: install_libs

# uninstall:



# clear:
