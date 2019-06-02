The code included has a scrip lstm_encdec.py. If models are untrained, it will train the models and then conduct evaluation.
For evaluation it simply loads data, uses a fraction of it, transaltes it into time series and calculates accuracy and loss for each of the 14 models.
These trained models, and their accuracy and loss will be stored in files inside the directory results/


Building:
	$python3 200262300_encdec.py

Requirements:
	Additonal packages that needed to be installed as user:
		1. pip3 install  /opt/built_binaries/tensorflow_1.12_gpu_py3/tensorflow-1.12.2-cp35-cp35m-linux_x86_64.whl --no-cache-dir --user
		2. pip install --user keras
		3. pip install --user sklearn

The script will train models, save models and evaluate the models.
Models, their weights and evaluate_generator results are all saved in ..results/

Note:
	Data was too large to be uploaded, it is stored on lin06. A trimmed version of data was used for training to make the total ETA feasible.

Link to trace:
	Reduced dataset : lin05- /home/sachando/CSC766/data/
	Link to repo : https://github.ncsu.edu/sachando/CSC766

	
