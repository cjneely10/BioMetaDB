.PHONY: build clean dist publish all

build:
	CYTHONIZE=1 ./setup.py build_ext --inplace

clean:
	rm -fr build dist BioMetaDB.egg-info

dist:
	./setup.py sdist

publish:
	twine upload dist/*

all: clean build dist publish
