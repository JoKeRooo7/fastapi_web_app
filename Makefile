remove_trash:
	find . -type d -name "__pycache__" -exec rm -rf {} +

clear: 
	remove_trash

clean:
	clear

# code_style:

# remove_db:
# 	rm -rf app/database/*.db

# start:

# all:

# install:

# uninstall:

# clear:
