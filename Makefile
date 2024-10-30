remove_trash:
	find . -type d -name "__pycache__" -exec rm -rf {} +

clear: 
	remove_trash

clean:
	clear

# remove_db:
# 	rm -rf app/database/*.db

# start:

# all:

# install:

# uninstall:

# clear:
