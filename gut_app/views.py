### Import all the packages useful in python
from flask import request
from flask import render_template,redirect,url_for
from gut_app import app
from werkzeug import secure_filename
import os
import io
import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
plt.switch_backend('agg') #solve 'invalid DISPLAY variable' in online version of app 
from patsy import dmatrices
from numpy import genfromtxt
import pickle
from sklearn.externals import joblib
import seaborn as sns
sns.set(style="ticks", palette="muted", color_codes=True) #Have the room to play with colors


import pickle
app.use_reloader=False

def GutPred():
    return pickle.load(open("fit_models/Random_Forest.pkl"))

#### Upload csv file
# This is the path to the upload directory
app.config['APP_ROOT'] = os.path.dirname(os.path.abspath(__file__))
# specify upload folder
app.config['uploads'] = os.path.join(app.config['APP_ROOT'],"uploads")
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
           
# Specify the path where the output image will be saved in the future
app.config['IMAGE_FOLDER'] = os.path.join(app.config['APP_ROOT'], "static", "image")

# projects: gut microbiome project page
# @app.route('/projects/gut_microbiome')
@app.route('/gut_microbiome_project')
def index():
    return render_template("gut_microbiome_interface.html")
    
# Route processes the file upload
@app.route('/upload', methods=['POST'])
def upload():  
    example = request.form.get('example_select')
    print ("Here is the dropdown menu example input")
    print (example)
    if example == "healthy":
        patient_table = pd.read_csv(os.path.join(app.config['APP_ROOT'],'healthy.csv'))
        filename = 'healthy.csv'
    elif example == "cancer":
        patient_table = pd.read_csv(os.path.join(app.config['APP_ROOT'],'cancer.csv'))  
        filename = 'cancer.csv'
    else: 
        file = request.files['file']# Get the name of the uploaded file
        if file and allowed_file(file.filename):
           filename = secure_filename(file.filename)
           print (filename)
           file.save(os.path.join(app.config['uploads'], filename))
           datatablepath = os.path.join(app.config['uploads'], filename)  #Moved up for testing #
           patient_table = pd.read_csv(datatablepath)   	
    X = patient_table[['Fusobacterium nucleatum_1','Fusobacterium nucleatum_2','Peptostreptococcus stomatis','Porphyromonas','Clostridium symbiosum','Clostridium hylemonae','Phascolarctobacterium succinatutens','unnamed Ruminococcus sp. 5_1_39BFAA','unnamed Ruminococcus sp. SR1/5','Streptococcus salivarius','Bacteroides dorei/vulgatus','Ruminococcus bromii','Bacteroides uniformis','Eubacterium rectale','Prevotella copri','butyrate-producing bacterium','Escherichia coli','Alistipes putredinis','Methanobrevibacter smithii','Parabacteroides distasonis','Faecalibacterium prausnitzii','Eubacterium eligens','Butyrivibrio crossotus','[Ruminococcus] torques','Bacteroides ovatus','Bifidobacterium longum','Faecalibacterium prausnitzii']].values
    X2 = patient_table[['Peptostreptococcus stomatis','Fusobacterium nucleatum_2','Streptococcus salivarius','Clostridium symbiosum','unnamed Ruminococcus sp. SR1/5']].values.flatten()
    X2_list = ['Peptostreptococcus stomatis','Fusobacterium nucleatum_2','Streptococcus salivarius','Clostridium symbiosum','unnamed Ruminococcus sp. SR1/5']
    X2_abun = X2.tolist()
    one_patient = pd.DataFrame({ 'Microbe species': X2_list, 'Relative Abundance': X2_abun })
    abundance_plot = pd.read_csv(os.path.join(app.config['APP_ROOT'],'top_5_abundance.csv'))
    ax = sns.violinplot(x="Relative Abundance", y="Microbe species", data=abundance_plot, scale="width")
    ax = sns.swarmplot(x="Relative Abundance", y="Microbe species", data=one_patient, color="blue",size = 10)
    unique_fig_name = filename
    plt.savefig(os.path.join(app.config['IMAGE_FOLDER'],"%s.png" % unique_fig_name), bbox_inches='tight')
    ax.cla() # This command line removes everything on ax, so that the old scatter points do not stay on the new graph
    RF_final = joblib.load(os.path.join(app.config['APP_ROOT'],"fit_models/RF_final.pkl"))#call for a picked function, here is the RF model
    result = int(RF_final.predict_proba(X)[:,1][0]*100)
    if result < 30:
        sentence = 'This patient is healthy'
    else:
        sentence = 'WARNING! Another round of test is highly recommended'
    return render_template("gut_microbiome_analyzed.html", the_result = result, sentence = sentence, image_name = unique_fig_name)










