#importing libraries 
import pandas as pd
import numpy as np 
import random 
import pickle
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC                
from sklearn.model_selection import train_test_split, KFold                                  
from sklearn.preprocessing import OneHotEncoder, StandardScaler                          
from sklearn.compose import ColumnTransformer                             
from seaborn import pairplot, catplot
random.seed(13)
pd.options.mode.chained_assignment = None

#inserting df 
df = pd.read_csv('heart.csv')

#normally 1 stands for heart disease
#for facilitation when reading the confusion matrix we change up to 0 for heart disease
df['HeartDisease'] = np.where(df.HeartDisease == 0, 0, -1)   # 1 to -1
df['HeartDisease'] = np.where(df.HeartDisease == -1, -1, 1)  # 0 to 1
df['HeartDisease'] = np.where(df.HeartDisease == 1, 1, 0)    # -1 to 0

#checking for missing values 
def na_check():
  if df.isna().any().sum() == 0:
    print("There are no missing values.")
  else: 
    print("You need to deal with missing values.")

#plotting variables 
def Pairplot():
  pairplot(df, 
         vars = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak'],  
         hue='HeartDisease',
         plot_kws = {'alpha': 0.6, 's': 80, 'edgecolor': 'k'})

  catplot(x = 'ChestPainType', y = 'RestingBP', hue = 'HeartDisease', kind = 'box', data = df)
  catplot(x = 'FastingBS', y = 'Cholesterol', hue = 'HeartDisease', kind = 'box', data = df)
  catplot(x = 'RestingECG', y = 'MaxHR', hue = 'HeartDisease', kind = 'box', data = df)
  catplot(x = 'ExerciseAngina', y = 'MaxHR', hue = 'HeartDisease', kind = 'box', data = df)
  catplot(x = 'ST_Slope', y = 'Oldpeak', hue = 'HeartDisease', kind = 'box', data = df)

#dropping outliers
df = df.drop(index=df[df['RestingBP'] == 0].index)
df = df.drop(index=df[df['Cholesterol'] == 0].index)

#seperating dependent and independent variables
X_primary = df.drop(columns = ['HeartDisease']).copy()
y = df['HeartDisease']

#encoding categorical data
X = pd.get_dummies(X_primary, columns=['Sex',
                                       'ChestPainType',
                                       'RestingECG',
                                       'ExerciseAngina',
                                       'ST_Slope'])

#split into train and test 
X_rem, X_test, y_rem, y_test = train_test_split(X,y, test_size=0.2)

#apply feature scaling 
#Identify witch columns we want to scale.
cols_to_scale = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']

#Call scaler and fit to train data.
sc = StandardScaler()
sc.fit(X_rem[cols_to_scale])

#Transform train and test set.
X_rem[cols_to_scale] = sc.transform(X_rem[cols_to_scale])
X_test[cols_to_scale] = sc.transform(X_test[cols_to_scale])

#pick logistic regression hyperparameters 
def log_clf():

  c_values = [0.001, 0.005, 0.01, 0.05, 0.1, 1, 10 , 50, 100, 500, 1000]
  solver_types = ['lbfgs', 'liblinear', 'saga']
  kf = KFold( n_splits=10, shuffle=False, random_state=None )
  column_names = ['c value', 'solver type', 'validation recall', 'validation precision']
  log_df = pd.DataFrame(columns = column_names )
  values_of_c = []
  types_of_solver = []
  valid_rec_values = []
  valid_pre_values = []

  for sol_type in solver_types:
    for c in c_values:
      clf = LogisticRegression(C = c, solver = sol_type, max_iter = 10000)
      valid_rec_score = 0
      valid_pre_score = 0
      for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        clf.fit(X_train, y_train)
        y_valid_pred = clf.predict(X_valid)
        valid_rec_score += metrics.recall_score(y_valid, y_valid_pred)/10
        valid_pre_score += metrics.precision_score(y_valid, y_valid_pred)/10
      values_of_c.append(c)
      types_of_solver.append(sol_type)
      valid_rec_values.append(valid_rec_score)
      valid_pre_values.append(valid_pre_score)

  log_df['c value'] = values_of_c
  log_df['solver type'] = types_of_solver
  log_df['validation recall'] = valid_rec_values
  log_df['validation precision'] = valid_pre_values
   
  lbfgs = log_df[log_df['solver type'] == 'lbfgs']
  liblinear = log_df[log_df['solver type'] == 'liblinear']
  saga = log_df[log_df['solver type'] == 'saga']
    
  fig = make_subplots(rows=2, cols=2, subplot_titles=("lbfgs", "liblinear", "saga"))

  fig.add_trace(go.Scatter(x=lbfgs['c value'], y=lbfgs['validation recall'], name = 'recall',
                        line = dict(color='royalblue')), row = 1, col =1)

  fig.add_trace(go.Scatter(x=lbfgs['c value'], y=lbfgs['validation precision'], name = 'precision',
                        line = dict(color='red')),row =1, col =1)

  fig.add_trace(go.Scatter(x=liblinear['c value'], y=liblinear['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 1, col =2)

  fig.add_trace(go.Scatter(x=liblinear['c value'], y=liblinear['validation precision'], showlegend=False,
                        line = dict(color='red')),row =1, col =2)

  fig.add_trace(go.Scatter(x=saga['c value'], y=saga['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 2, col =1)

  fig.add_trace(go.Scatter(x=saga['c value'], y=saga['validation precision'], showlegend=False,
                        line = dict(color='red')),row =2, col =1)

  fig.update_xaxes(type="log")
    
  fig.update_layout(title = 'Logistic Regression')

  fig.show()

#saving the results for the final evaluation
log_solver_type = 'saga'
log_c_value = 0.01

#pick knn hypeparameters 
def knn_clf():
    
  nn_values = [] 
  i =5 
  while i<=40:
    nn_values.append(i)
    i = i+2
  weight_types = ['uniform', 'distance']
  kf = KFold( n_splits=10, shuffle=False, random_state=None )
  column_names = ['nearest neighbors needed', 'weight type', 'validation recall', 'validation precision']
  knn_df = pd.DataFrame(columns = column_names )
  values_of_n = []
  types_of_weights = []
  valid_rec_values = []
  valid_pre_values = []

  for w in weight_types:
    for n in nn_values:
      clf = KNeighborsClassifier(n_neighbors = n, weights = w)
      valid_rec_score = 0
      valid_pre_score = 0
      for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        clf.fit(X_train, y_train)
        y_valid_pred = clf.predict(X_valid)
        valid_rec_score += metrics.recall_score(y_valid, y_valid_pred)/10
        valid_pre_score += metrics.precision_score(y_valid, y_valid_pred)/10
      values_of_n.append(n)
      types_of_weights.append(w)
      valid_rec_values.append(valid_rec_score)
      valid_pre_values.append(valid_pre_score)

  knn_df['nearest neighbors needed'] = values_of_n
  knn_df['weight type'] = types_of_weights
  knn_df['validation recall'] = valid_rec_values
  knn_df['validation precision'] = valid_pre_values
    
  uniform = knn_df[knn_df['weight type'] == 'uniform']
  distance = knn_df[knn_df['weight type'] == 'distance']
    
  fig = make_subplots(rows=1, cols=2, subplot_titles=("uniform", "distance"))

  fig.add_trace(go.Scatter(x=uniform['nearest neighbors needed'], y=uniform['validation recall'], name = 'recall',
                        line = dict(color='royalblue')), row = 1, col =1)

  fig.add_trace(go.Scatter(x=uniform['nearest neighbors needed'], y=uniform['validation precision'], name = 'precision',
                        line = dict(color='red')),row =1, col =1)

  fig.add_trace(go.Scatter(x=distance['nearest neighbors needed'], y=distance['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 1, col =2)

  fig.add_trace(go.Scatter(x=distance['nearest neighbors needed'], y=distance['validation precision'], showlegend=False,
                        line = dict(color='red')),row =1, col =2)
    
  fig.update_layout(title = 'K Nearest Neighbors')

  fig.show()

#decision tree 
def tree_clf():
  
  max_depth_values = []
  i = 4
  while i<=15:
    max_depth_values.append(i)
    i = i+1
  criterion_types = ['gini', 'entropy']
  kf = KFold( n_splits=10, shuffle=False, random_state=None )
  column_names = ['maximum depth', 'criterion type', 'validation recall', 'validation precision']
  tree_df = pd.DataFrame(columns = column_names )
  values_of_depth = []
  types_of_criterion = []
  valid_rec_values = []
  valid_pre_values = []

  for crit in criterion_types:
    for depth in max_depth_values:
      clf = DecisionTreeClassifier(criterion = crit, max_depth = depth)
      valid_rec_score = 0
      valid_pre_score = 0
      for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        clf.fit(X_train, y_train)
        y_valid_pred = clf.predict(X_valid)
        valid_rec_score += metrics.recall_score(y_valid, y_valid_pred)/10
        valid_pre_score += metrics.precision_score(y_valid, y_valid_pred)/10
      values_of_depth.append(depth)
      types_of_criterion.append(crit)
      valid_rec_values.append(valid_rec_score)
      valid_pre_values.append(valid_pre_score)

  tree_df['maximum depth'] = values_of_depth
  tree_df['criterion type'] = types_of_criterion
  tree_df['validation recall'] = valid_rec_values
  tree_df['validation precision'] = valid_pre_values
    
  gini = tree_df[tree_df['criterion type'] == 'gini']
  entropy = tree_df[tree_df['criterion type'] == 'entropy']
    
  fig = make_subplots(rows=1, cols=2, subplot_titles=("gini", "entropy"))

  fig.add_trace(go.Scatter(x=gini['maximum depth'], y=gini['validation recall'], name = 'recall',
                        line = dict(color='royalblue')), row = 1, col =1)

  fig.add_trace(go.Scatter(x=gini['maximum depth'], y=gini['validation precision'], name = 'precision',
                        line = dict(color='red')),row =1, col =1)

  fig.add_trace(go.Scatter(x=entropy['maximum depth'], y=entropy['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 1, col =2)

  fig.add_trace(go.Scatter(x=entropy['maximum depth'], y=entropy['validation precision'], showlegend=False,
                        line = dict(color='red')),row =1, col =2)
    
  fig.update_layout(title = 'Decision Tree')

  fig.show()

#saving the results for the final evaluation
knn_weight_type = 'distance'
knn_n_value = 11

#svm pick hyperparameters 
def svm_clf():

  c_values = [0.05, 0.1, 0.5, 1, 5, 10 , 50, 100, 500, 1000]
  kernel_types = ['linear', 'poly', 'rbf', 'sigmoid']
  kf = KFold( n_splits=10, shuffle=False, random_state=None )
  column_names = ['c value', 'kernel type', 'validation recall', 'validation precision']
  svm_df = pd.DataFrame(columns = column_names )
  values_of_c = []
  types_of_kernel = []
  valid_rec_values = []
  valid_pre_values = []

  for kern_type in kernel_types:
    for c in c_values:
      clf = SVC(C = c, kernel = kern_type)
      valid_rec_score = 0
      valid_pre_score = 0
      for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        clf.fit(X_train, y_train)
        y_valid_pred = clf.predict(X_valid)
        valid_rec_score += metrics.recall_score(y_valid, y_valid_pred)/10
        valid_pre_score += metrics.precision_score(y_valid, y_valid_pred)/10
      values_of_c.append(c)
      types_of_kernel.append(kern_type)
      valid_rec_values.append(valid_rec_score)
      valid_pre_values.append(valid_pre_score)

  svm_df['c value'] = values_of_c
  svm_df['kernel type'] = types_of_kernel
  svm_df['validation recall'] = valid_rec_values
  svm_df['validation precision'] = valid_pre_values
    
  linear = svm_df[svm_df['kernel type'] == 'linear']
  poly = svm_df[svm_df['kernel type'] == 'poly']
  rbf = svm_df[svm_df['kernel type'] == 'rbf']
  sigmoid = svm_df[svm_df['kernel type'] == 'sigmoid']
    
  fig = make_subplots(rows=2, cols=2, subplot_titles=('linear', 'poly', 'rbf', 'sigmoid'))

  fig.add_trace(go.Scatter(x=linear['c value'], y=linear['validation recall'], name = 'recall',
                        line = dict(color='royalblue')), row = 1, col =1)

  fig.add_trace(go.Scatter(x=linear['c value'], y=linear['validation precision'], name = 'precision',
                        line = dict(color='red')),row =1, col =1)

  fig.add_trace(go.Scatter(x=poly['c value'], y=poly['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 1, col =2)

  fig.add_trace(go.Scatter(x=poly['c value'], y=poly['validation precision'], showlegend=False,
                        line = dict(color='red')),row =1, col =2)

  fig.add_trace(go.Scatter(x=rbf['c value'], y=rbf['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 2, col =1)

  fig.add_trace(go.Scatter(x=rbf['c value'], y=rbf['validation precision'], showlegend=False,
                        line = dict(color='red')),row =2, col =1)

  fig.add_trace(go.Scatter(x=sigmoid['c value'], y=sigmoid['validation recall'], showlegend=False,
                        line = dict(color='royalblue')), row = 2, col =2)

  fig.add_trace(go.Scatter(x=sigmoid['c value'], y=sigmoid['validation precision'], showlegend=False,
                        line = dict(color='red')),row =2, col =2)

  fig.update_xaxes(type="log")
    
  fig.update_layout(title = 'Support Vector Machine')

  fig.show()

#saving the results for the final evaluation
tree_max_depth = 7
tree_criterion_type = 'gini'

#algorithms comparison 
def clf_comp():
    
    names = ['accuracy', 'F1-score']
    comp_df = pd.DataFrame(columns = names)
    accuracy_scores = []
    f1_scores = []
    kf = KFold(n_splits=10, shuffle=False, random_state=None)
    
    log_clf = LogisticRegression(C = log_c_value, solver = log_solver_type, max_iter = 10000)
    log_acc = 0
    log_f1 = 0
    for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        log_clf.fit(X_train, y_train)
        y_valid_pred = log_clf.predict(X_valid)
        log_acc +=metrics.accuracy_score(y_valid, y_valid_pred)/10
        log_f1 += metrics.f1_score(y_valid, y_valid_pred)/10
    accuracy_scores.append(log_acc)
    f1_scores.append(log_f1)
    
    knn_clf = KNeighborsClassifier(n_neighbors = knn_n_value, weights = knn_weight_type)
    knn_acc = 0
    knn_f1 = 0
    for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        knn_clf.fit(X_train, y_train)
        y_valid_pred = knn_clf.predict(X_valid)
        knn_acc += metrics.accuracy_score(y_valid, y_valid_pred)/10
        knn_f1 += metrics.f1_score(y_valid, y_valid_pred)/10
    accuracy_scores.append(knn_acc)
    f1_scores.append(knn_f1)
    
    tree_clf = DecisionTreeClassifier(criterion = tree_criterion_type, max_depth = tree_max_depth)
    tree_acc = 0
    tree_f1 = 0
    for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        tree_clf.fit(X_train, y_train)
        y_valid_pred = tree_clf.predict(X_valid)
        tree_acc += metrics.accuracy_score(y_valid, y_valid_pred)/10
        tree_f1 += metrics.f1_score(y_valid, y_valid_pred)/10    
    accuracy_scores.append(tree_acc)
    f1_scores.append(tree_f1)
    
    svm_clf = SVC(C = svm_c_value , kernel = svm_kernel_type)
    svm_acc = 0
    svm_f1 = 0
    for train_index, test_index in kf.split(X_rem):
        X_train, X_valid = X_rem.iloc[train_index], X_rem.iloc[test_index]
        y_train, y_valid = y_rem.iloc[train_index], y_rem.iloc[test_index]
        svm_clf.fit(X_train, y_train)
        y_valid_pred = svm_clf.predict(X_valid)
        svm_acc += metrics.accuracy_score(y_valid, y_valid_pred)/10
        svm_f1 += metrics.f1_score(y_valid, y_valid_pred)/10 
    accuracy_scores.append(svm_acc)
    f1_scores.append(svm_f1)
        
    comp_df['accuracy'] = accuracy_scores
    comp_df['F1-score'] = f1_scores
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Accuracy", "F1-Score"))
    
    fig.add_trace(go.Bar(x = ['Log', 'K-NN', 'Decision Tree', 'SVM'], y = comp_df['accuracy'])
                         , row =1, col =1)
    
    fig.add_trace(go.Bar(x = ['Log', 'K-NN', 'Decision Tree', 'SVM'], y = comp_df['F1-score'])
                         , row =1, col =2)
    
    fig.update_layout(title = 'Final Comparison')
    
    fig.show()

#saving the results for the final evaluation
svm_c_value = 0.5
svm_kernel_type = 'poly'

#final regressor chosen: SVM
final_clf = SVC(C = svm_c_value , kernel = svm_kernel_type)

#fit the regresson to the whole train set 
final_clf.fit(X_rem, y_rem)

#make predictions to the test set 
y_pred = final_clf.predict(X_test)
evaluate_accuracy = metrics.accuracy_score(y_test, y_pred)

#print the expected accuracy 
#print("Exprected overall accuracy is "+str(evaluate_accuracy))

#define the app regressor 
app_regressor = SVC(C = svm_c_value, kernel = svm_kernel_type)

#scale the whole (encoded) dataset  
X[cols_to_scale] = sc.transform(X[cols_to_scale])
X

#fit the app regressor to the whole dataset
app_regressor.fit(X, y)

#saving the classifier 
app_regressor = {"model": app_regressor}
with open('saved_clf.pkl', 'wb') as file:
    pickle.dump(app_regressor, file)

#commands you will need to load the classifier 
with open('saved_clf.pkl', 'rb') as file:
    clf = pickle.load(file)

clf_loaded = clf['model']
