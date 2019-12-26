# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 11:24:33 2019
DIILAB , IIM-Bangalore
"""

# Importing all necesary Libraries
import pandas as pd
import numpy as np
import os
from concurrent.futures.thread import ThreadPoolExecutor
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import f1_score
from statsmodels.stats.inter_rater import fleiss_kappa
import krippendorff
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog

# To raise an exception if result file already exists
class ExistsError(Exception):
    pass

# To disable the evaluate button till all the fields have been updated
def validateentry(*args):
    x = foname1.get()
    y = foname2.get() 
    z = finame.get()
    if x and y and z:
        B.config(state='normal', text='Evaluate')
    else:
        B.config(state='disabled', text='Fill all above fields')    

# Function for creating a scatter graph of Cohen's Kappa and F1 Score
def savegraph(result_coh, result_f1):
    
    dataset = pd.read_csv(result_coh)
    x = dataset.iloc[:,0:1]
    y = dataset.iloc[:,1:]
    
    #Graph Cohen
    fig, ax = plt.subplots()
    plt.scatter(y.values.transpose().tolist()[0], x.values.transpose().tolist()[0], color='red', label=y.columns[0])
    plt.scatter(y.values.transpose().tolist()[1], x.values.transpose().tolist()[0], color='blue', label=y.columns[1])
    plt.scatter(y.values.transpose().tolist()[2], x.values.transpose().tolist()[0], color='green', label=y.columns[2])
    plt.scatter(y.values.transpose().tolist()[3], x.values.transpose().tolist()[0], color='yellow', label=y.columns[3])
    plt.title('Predictor vs CohenKappa value')
    plt.xlabel('Cohen Kappa values')
    plt.ylabel('Predicted Files')
    ax.legend(loc="upper left", bbox_to_anchor=(1,1))
    plt.savefig(result_coh.strip('.csv') + '.png', bbox_inches='tight')
    
    dataset = pd.read_csv(result_f1)
    x = dataset.iloc[:,0:1]
    y = dataset.iloc[:,1:]
    
    #Graph F1
    fig, ax = plt.subplots()
    plt.scatter(y.values.transpose().tolist()[0], x.values.transpose().tolist()[0], color='red', label=y.columns[0])
    plt.scatter(y.values.transpose().tolist()[1], x.values.transpose().tolist()[0], color='blue', label=y.columns[1])
    plt.scatter(y.values.transpose().tolist()[2], x.values.transpose().tolist()[0], color='green', label=y.columns[2])
    plt.scatter(y.values.transpose().tolist()[3], x.values.transpose().tolist()[0], color='yellow', label=y.columns[3])
    plt.title('Predictor vs F1 value')
    plt.xlabel('F1 values')
    plt.ylabel('Predicted Files')
    ax.legend(loc="upper left", bbox_to_anchor=(1,1))
    plt.savefig(result_f1.strip('.csv') + '.png', bbox_inches='tight')


#Function for calculating the values.    
def cohkap(pdfilename, grtfilename, resultfilename, y=0):

    #Reading the respective csv files 
    prediction_df = pd.read_csv(pdfilename)[['image', 'label']]
    ground_df = pd.read_csv(grtfilename)
    result_coh = resultfilename.strip('.csv') + '_coh.csv'
    result_f1 = resultfilename.strip('.csv') + '_f1.csv'

    #performing inner merge
    mergedf_in = pd.merge(prediction_df, ground_df, on='image', how='inner')
    merged_list = mergedf_in.values[:, 1:].transpose().tolist()
    kap = np.zeros(len(ground_df.columns[1:]))
    f1 = np.zeros(len(ground_df.columns[1:]))

    #Making a matrix of Kohen's kappa Values and f1 values of all cases of predictions with each rater
    for i in range(len(ground_df.columns)-1):
        kap[i] = cohen_kappa_score(mergedf_in.iloc[:,1:2], mergedf_in.iloc[:,i+2:i+3], weights='quadratic')
        f1[i] = f1_score(merged_list[0], merged_list[i+1], average='weighted')
    columns = mergedf_in.columns.tolist()
    columns.remove('image')
    columns.remove('label')
    kap = pd.DataFrame(kap, index=[columns], columns=[pdfilename.split('/')[-1].strip('.csv')]).transpose()
    f1 = pd.DataFrame(f1, index=[columns], columns=[pdfilename.split('/')[-1].strip('.csv')]).transpose()
    if y:
        M = ground_df.values[:,1:].transpose()
        E4.delete(0, END)
        Entry.insert(E4, 0, krippendorff.alpha(M.tolist()))

    # Writing Coh to csv
    if not os.path.exists(result_coh):
        kap.to_csv(result_coh, mode='a')
    else:
        kap.to_csv(result_coh, mode='a',header=False) 
    # Writing F1 to csv
    if not os.path.exists(result_f1):
        f1.to_csv(result_f1, mode='a')
    else:
        f1.to_csv(result_f1, mode='a',header=False) 


# Functio to invoke on click of the Evaluate button, Also raises exceptions if reult file exit 
def calculate():
    E5.delete(0, END)
    Entry.insert(E5, 0, 'Running')
    predfolder, grfilename, resultfilename = Entry.get(E1), Entry.get(E2), Entry.get(E3) + '/Result.csv' 
    predfilename = os.listdir(predfolder)
    result_coh = resultfilename.strip('.csv') + '_coh.csv'
    result_f1 = resultfilename.strip('.csv') + '_f1.csv'
    try:
        if os.path.exists(result_coh) or os.path.exists(result_f1):
            raise ExistsError
    except ExistsError:
            E5.delete(0, END)
            Entry.insert(E5, 0, 'Delete the existing result files in the result folder location or change folder location')
            B.config(state='disabled')
            return 0
            
    cohkap(predfolder + '/' + predfilename[0], grfilename, resultfilename, y=1)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for f in predfilename[1:]:
            executor.submit(cohkap, predfolder + '/' + f, 'Rated.csv', resultfilename)
    savegraph(result_coh, result_f1)
    print('Calculations done, You can close the window')
    E5.delete(0, END)
    Entry.insert(E5, 0, 'Success')
    C.config(state='normal')

'''
Creating the GUI
'''
top = Tk()

# Function for browsefile
def browsefilefunc(finame):
    filename = filedialog.askopenfilename()
    if filename:
        finame.set(filename)
        
# Function for browsefolder
def browsefolderfunc(foname):
    foldername = filedialog.askdirectory()
    if foldername: 
        foname.set(foldername)
        
# Function for close button
def close():
    top.destroy()

L1 = Label(top, text="Interrelation calculator",).grid(row=0,column=0)
L2 = Label(top, text="Prediction files folder Location",).grid(row=1,column=0)
L3 = Label(top, text="Rater File Location",).grid(row=2,column=0)
L4 = Label(top, text="Where to save Result: ",).grid(row=3,column=0)
L5 = Label(top, text="Krippendorff's Alpha is: ",).grid(row=5,column=0)
L6 = Label(top, text="State: ",).grid(row=6, column=0)
foname1 = StringVar(top)
foname2 = StringVar(top)
finame = StringVar(top)

#Validating if input has been given
foname1.trace("w", validateentry)
foname2.trace("w", validateentry)
finame.trace("w", validateentry)

E1 = Entry(top, bd =5, textvariable=foname1, width=67)
E1.grid(row=1,column=1)
E2 = Entry(top, bd =5, textvariable=finame, width=67)
E2.grid(row=2,column=1)
E3 = Entry(top, bd =5, textvariable=foname2, width=67)
E3.grid(row=3,column=1)
E4 = Entry(top, bd =5, width=67)
E4.grid(row=5,column=1)
E5 = Entry(top, bd =5, width=67)
E5.grid(row=6,column=1)
B=Button(top, text ="Fill all above fields",command = calculate, width=15, height=3, state='disabled')
B.grid(row=4,column=1,)
C=Button(top, text ="Close",command = close, width=10, state='disabled')
C.grid(row=4,column=2,)
browsefo1 = Button(top, text="Browse", command= lambda:browsefolderfunc(foname1)).grid(row=1, column=2)
browsefo2 = Button(top, text="Browse", command= lambda:browsefolderfunc(foname2)).grid(row=3, column=2)
browsefi = Button(top, text="Browse", command= lambda: browsefilefunc(finame)).grid(row=2, column=2)
T = Text(top, height=16, width=73)
T.grid(row = 7, column=1)
T.insert(END, '''
After clicking evaluate Result_cohen.csv will be created, compare
using this table. Result_f1.csv would contain the f1 scores
|=======================================================================|
|               Interpretation of Cohens kappa.                        |
|=======================================================================|
| Value of Kappa    |Level of Agreement  |% of Data that are Reliable   |
|-------------------|--------------------|------------------------------|
|   0.20           |None                | 04%                         |
| .21.39           |Minimal             | 415%                        |
| .40.59           |Weak                | 1535%                       |
| .60.79           |Moderate            | 3563%                       |
| .80.90           |Strong              | 6481%                       |
| Above.90          |Almost Perfect      | 82100%                      |
-------------------------------------------------------------------------
''')
top.mainloop()

