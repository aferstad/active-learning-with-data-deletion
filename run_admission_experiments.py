#import matplotlib
#matplotlib.use('Agg')

#import input.census_import
import input.heart_import
import input.admission_import
import input.alcohol_import

#import experiment
import keep_delete_experiments

import importlib
importlib.reload(keep_delete_experiments)
#importlib.reload(input.census_import)
importlib.reload(input.heart_import)
importlib.reload(input.admission_import)
importlib.reload(input.alcohol_import)

from keep_delete_experiments import run_experiments, plot_results
#from input.census_import import get_census_data
from input.heart_import import get_heart_data
from input.admission_import import get_admission_data
from input.alcohol_import import get_alcohol_data

import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt

test = True

#heart, heart_with_dummies = get_heart_data('input/heart.csv')
#data = heart_with_dummies

data = get_admission_data()
#data = get_alcohol_data()

keeps = range(10, 70, 10)
deletes = range(0, 70, 10)
reps = 100
save_path_accuracy = 'output/admission_keep_delete_accuracy_50_rep_grid.png'
save_path_consistency = 'output/admission_keep_delete_consistency_50_rep_grid.png'

if test:
    keeps = [10, 20]
    deletes = [0, 10]
    reps = 1
    save_path_accuracy = 'output/test_admission_keep_delete_accuracy_50_rep_grid.png'
    save_path_consistency = 'output/test_admission_keep_delete_consistency_50_rep_grid.png'

methods = ['random', 'uncertainty', 'similar']
method_colors = {methods[0] : 'dodgerblue', methods[1] : 'orange', methods[2] : 'brown'}

accuracy_results, consistency_results = run_experiments(data = data, reps = reps, keeps = keeps, deletes=deletes, methods = methods)
plot_results(accuracy_results, keeps, deletes, save_path_accuracy, methods, method_colors, ylabel = 'accuracy')
plot_results(consistency_results, keeps, deletes, save_path_consistency, methods, method_colors, ylabel = 'consistency')
