install:
	pip install -r requirements.txt
virtual-env:
	python3 -m venv venv
	source venv/bin/activate
conda-deactivate:
	conda deactivate
	conda env remove -n env_name
