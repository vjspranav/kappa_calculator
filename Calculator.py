# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 11:24:33 2019
DIILAB , IIM-Bangalore
"""
import pandas as pd
import numpy as np
import os
from concurrent.futures.thread import ThreadPoolExecutor
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import f1_score
from statsmodels.stats.inter_rater import fleiss_kappa
import krippendorff

def cohkap(pdfilename, grtfilename, resultfilename, y=0):
    prediction_df = pd.read_csv(pdfilename).iloc[:,:2]
    ground_df = pd.read_csv(grtfilename)
    result_coh = resultfilename.strip('.csv') + '_coh.csv'
    result_f1 = resultfilename.strip('.csv') + '_f1.csv'
    mergedf_in = pd.merge(prediction_df, ground_df, on=prediction_df.columns[0], how='inner')
    merged_list = mergedf_in.values[:, 1:].transpose().tolist()
    kap = np.zeros(len(ground_df.columns[1:]))
    f1 = np.zeros(len(ground_df.columns[1:]))
    for i in range(len(ground_df.columns)-1):
        kap[i] = cohen_kappa_score(mergedf_in.iloc[:,1:2], mergedf_in.iloc[:,i+2:i+3], weights='quadratic')
        f1[i] = f1_score(merged_list[0], merged_list[i+1], average='weighted')
    columns = mergedf_in.columns.tolist()
    columns.remove(prediction_df.columns[0])
    columns.remove(prediction_df.columns[1])
    kap = pd.DataFrame(kap, index=[columns], columns=[pdfilename.split('/')[-1].strip('.csv')]).transpose()
    f1 = pd.DataFrame(f1, index=[columns], columns=[pdfilename.split('/')[-1].strip('.csv')]).transpose()
    if y:
        M = ground_df.values[:,1:].transpose()
        Entry.insert(E4, 0, krippendorff.alpha(M.tolist()))
    # Writing Coh
    if not os.path.exists(result_coh):
        kap.to_csv(result_coh, mode='a')
    else:
        kap.to_csv(result_coh, mode='a',header=False) 
    # Writing F1
    if not os.path.exists(result_f1):
        f1.to_csv(result_f1, mode='a')
    else:
        f1.to_csv(result_f1, mode='a',header=False) 

def calculate():
    predfolder, grfilename, resultfilename = Entry.get(E1), Entry.get(E2), Entry.get(E3) + '/Result.csv' 
    predfilename = os.listdir(predfolder)
    cohkap(predfolder + '/' + predfilename[0], grfilename, resultfilename, y=1)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for f in predfilename[1:]:
            executor.submit(cohkap, predfolder + '/' + f, 'Rated.csv', resultfilename)
    print('Calculations done, You can close the window')

'''
Creating the GUI
'''
from tkinter import *
from tkinter import filedialog
top = Tk()

def browsefilefunc(finame):
    filename = filedialog.askopenfilename()
    if filename:
        finame.set(filename)

def browsefolderfunc(foname):
    foldername = filedialog.askdirectory()
    if foldername: 
        foname.set(foldername)
        

L1 = Label(top, text="Interrelation calculator",).grid(row=0,column=0)
L2 = Label(top, text="Prediction files folder Location",).grid(row=1,column=0)
L3 = Label(top, text="Rater File Location",).grid(row=2,column=0)
L4 = Label(top, text="Where to save Result: ",).grid(row=3,column=0)
L4 = Label(top, text="Fleissis Score is: ",).grid(row=5,column=0)
foname1 = StringVar()
foname2 = StringVar()
finame = StringVar()
E1 = Entry(top, bd =5, textvariable=foname1, width=67)
E1.grid(row=1,column=1)
E2 = Entry(top, bd =5, textvariable=finame, width=67)
E2.grid(row=2,column=1)
E3 = Entry(top, bd =5, textvariable=foname2, width=67)
E3.grid(row=3,column=1)
E4 = Entry(top, bd =5, width=67)
E4.grid(row=5,column=1)
B=Button(top, text ="Evaluate",command = calculate, width=15, height=3).grid(row=4,column=1,)
browsefo1 = Button(top, text="Browse", command= lambda:browsefolderfunc(foname1)).grid(row=1, column=2)
browsefo2 = Button(top, text="Browse", command= lambda:browsefolderfunc(foname2)).grid(row=3, column=2)
browsefi = Button(top, text="Browse", command= lambda: browsefilefunc(finame)).grid(row=2, column=2)
T = Text(top, height=16, width=73)
T.grid(row = 6, column=1)
T.insert(END, '''
After clicking evaluate Result_cohen.csv will be created, compare
using this table. Result_f1.csv would contain the f1 scores
|=======================================================================|
|               Interpretation of Cohen’s kappa.                        |
|=======================================================================|
| Value of Kappa    |Level of Agreement  |% of Data that are Reliable   |
|-------------------|--------------------|------------------------------|
|   0–.20           |None                | 0–4%                         |
| .21–.39           |Minimal             | 4–15%                        |
| .40–.59           |Weak                | 15–35%                       |
| .60–.79           |Moderate            | 35–63%                       |
| .80–.90           |Strong              | 64–81%                       |
| Above.90          |Almost Perfect      | 82–100%                      |
-------------------------------------------------------------------------
''')
top.mainloop()