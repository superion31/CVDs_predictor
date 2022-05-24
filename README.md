## About the Project

CVDs (cardiovascular diseases) are the leading cause of death globally. In this project I try to predict whether a patient suffers or not from this type of heart disorders. To achieve that I am comparing the performace of four classification algorithms, namely

- Logistic Regression
- K Nearest Neighbors
- Decision Tree 
- Support Vector Machine

After tuning hyperparameters, the classifier with the best results is used to build a simple Web app where the user can insert some personal information and get the predicted result. The Web-app is hosted on Heroku and you can visit it on the following link https://cvdspredictor.herokuapp.com/

**Note**: Report was set in the form of Jupyter Notebook. Since github does not render plotly figures, I recommend reading it via the following link that leads to the nbviewer preview https://nbviewer.org/github/superion30/ML_project/blob/main/report_.ipynb

## Run Script

In case you want to run the code.py locally you can use the following commands on your terminal 

Clone repo 
```bash
git clone https://github.com/superion30/CVDs_predictor.git
```
Head to the repo directory 
```bash
cd ./CVDs_predictor
```
Set up a virtual environment 
```bash
python3 -m venv env
```
Jump into the virtual environment
```bash
source env/bin/activate
```
Install requirements 
```bash
pip3 install -r requirements.txt
```
Run the .py file you'd like
```bash
python3 code.py
```

## Contributing 

Feel free to contanct me for any remarks, corrections, additions and/or advice. 

Thank you in advance. 

Enjoy!
