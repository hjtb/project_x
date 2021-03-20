call activate general_development_37

waitress-serve --threads=6 --port=5000 --url-scheme=http run:app