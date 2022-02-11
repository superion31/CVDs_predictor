import streamlit as st
import pickle
import numpy as np

#load jupyter clf
def load_clf():
    with open('saved_clf.pkl', 'rb') as file:
        clf = pickle.load(file)
    return clf

loaded_data = load_clf()
app_clf = loaded_data['model']

X = np.zeros([1,20])
X_trial = np.array([[1.657325, 0.397262, -2.294453, 1, -1.271119, 0.558237, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0]])

#app title
st.title("ML Application")

#===========================================================
#feature scaling
#===========================================================

#age
age =st.slider("Age", 0, 100, 20)
X[0,0] = (age - 52.88)/9.5

#restingbp
restbp = st.slider("Resting Blood Pressure", 80, 250, 130)
X[0,1] = (restbp - 133.02)/17.27

#cholesterol
chol = st.slider("Cholesterol", 80, 600, 250)
X[0,2] = (chol - 244.64)/59.11

#fasting bs
fastingbs = (">120", "<120")
fastbs = st.selectbox("Fasting Blood Pressure", fastingbs)
if fastbs == ">120":
    X[0,3] = 1
elif fastbs == "<120":
    X[0,3] = 0

#maxhr
maxhr = st.slider("Maximum Heart Rate", 60, 250, 140)
X[0,4] = (maxhr - 140.23)/24.5

#oldpeak
oldp = st.slider("Oldpeak", -1, 7, 1)
X[0,5] = (oldp - 0.9)/1.07

#===========================================================
#encoding
#===========================================================

#sex
sex = ("Male", "Female")
sx =st.selectbox("Sex", sex)
if sx == "Male":
    X[0,7] = 1
elif sx == "Female":
    X[0,6] = 1

#chest pain type
chpt = ("Typical Angina", "Atypical Angina", "Non - Anginal Pain", "Asymptomatic")
pain_type = st.selectbox("Chest Pain Type", chpt)
if pain_type == "Asymptomatic":
    X[0,8] = 1
elif pain_type == "Atypical Angina":
    X[0,9] = 1
elif pain_type == "Non - Anginal Pain":
    X[0,10] = 1
elif pain_type == "Typical Angina":
    X[0,11] = 1

#restingecg
rest = ("Normal", "ST-T", "LVH")
rst = st.selectbox("Resting ECG", rest)
if rst == "LVH":
    X[0,12] =1
elif rst == "Normal":
    X[0,13] = 1
elif rst == "ST-T":
    X[0,14] = 1

#exercise angina
xrcs = ("Yes", "No")
exrcs = st.selectbox("Exercise Angina", xrcs)
if exrcs == "Yes":
    X[0,15] = 1
elif exrcs == "No":
    X[0,16] = 1

#st slope
slope = ("Down", "Up", "Flat")
slp = st.selectbox("ST Slope Curve", slope)
if slp == "Down":
    X[0,17] = 1
elif slp == "Up":
    X[0,18] = 1
elif X[0,19] == "Flat":
    X[0,19] = 1

run = st.button("Predict")

if run:
    answer = app_clf.predict(X)
    if answer[0] == 0:
        st.subheader("You should run some tests!")

    elif answer[0] == 1:
        st.subheader("Examination seems good!")
