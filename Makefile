sdist:
	python3 setup.py sdist

build:
	python3 setup.py build

upload:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
