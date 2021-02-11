test:
	python -m pytest --cov-report term --cov=aioscrapy
	python -m mypy aioscrapy --ignore-missing-imports
	python -m flake8 aioscrapy
