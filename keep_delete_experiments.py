import matplotlib 
matplotlib.use('Agg') # Do not move this behind any other import, otherwise error will be given due to no display available

import experiment
import importlib
importlib.reload(experiment)
from experiment import Experiment

import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt


def run_repetitions(data, reps, keep, delete, print_progress=True):
    '''
    INPUT
        reps : number of experiments to run and average for current keep-delete pair
        keep : number of points to keep after training initial model
        delete : number of points to delete after training initial model
    OUTPUT
        accuracy_results : df with mean accuracy per point added, columns are random and uncertainty method
        consistency_results : df with mean consistency per point added, columns are random and uncertainty method
    DESCRIPTION
        run uncertainty and random experiment with reps repitions,
        all with the same keep and delete parameters
        outputs dataframe with mean accuracy per step for all repetitions
        one column for random and one for uncertainty method
    '''
    accuracies = []
    consistencies = []
    accuracies_uncertainty = []
    consistencies_uncertainty = []

    for i in range(reps):
        if print_progress:
            print(i)

        my_experiment = Experiment(data, i, 'lr', keep, delete)
        my_experiment.run_experiment(method='random')

        accuracies.append(my_experiment.accuracies)
        consistencies.append(my_experiment.consistencies)

        my_experiment = Experiment(data, i, 'lr', keep, delete)
        my_experiment.run_experiment(method='uncertainty')

        accuracies_uncertainty.append(my_experiment.accuracies)
        consistencies_uncertainty.append(my_experiment.consistencies)

    a = pd.DataFrame(accuracies).mean(axis=0)
    au = pd.DataFrame(accuracies_uncertainty).mean(axis=0)

    c = pd.DataFrame(consistencies).mean(axis=0)
    cu = pd.DataFrame(consistencies_uncertainty).mean(axis=0)

    accuracy_results = pd.concat([a, au], axis=1)
    accuracy_results.columns = ['random', 'uncertainty']

    consistency_results = pd.concat([c, cu], axis=1)
    consistency_results.columns = ['random', 'uncertainty']

    return accuracy_results, consistency_results

def run_experiments(data, reps, keeps, deletes):
    '''
    runs experiments for all combinations of keep and delete parameters
    returns 2 dataframes with accuracy results and consistency results
    '''
    accuracy_results = {}
    consistency_results = {}
    n_grid_items_complete = 0
    for keep in keeps:
        #print('keep = ' + str(keep))
        accuracy_results[keep] = {}
        consistency_results[keep] = {}
        for delete in deletes:
            print('Pct grid items complete: ' + str(
                round(100.0 * n_grid_items_complete /
                      (len(keeps) * len(deletes)))))
            accuracy_results[keep][delete], consistency_results[keep][delete] = run_repetitions(data, reps,
                                                    keep,
                                                    delete,
                                                    print_progress=False)
            n_grid_items_complete += 1

    return accuracy_results, consistency_results

def plot_results(results, keeps, deletes, save_path_name, ylabel):
    '''
    plots results in grid, and saves to png
    '''
    fig, axs = plt.subplots(len(keeps), len(deletes), sharex=True, sharey=True)
    fig.set_size_inches(30, 20)

    for i in range(len(keeps)):
        for j in range(len(deletes)):
            df = results[keeps[i]][deletes[j]]

            axs[i, j].plot(df.random, color = 'dodgerblue', label = 'random method')
            axs[i, j].plot(df.uncertainty, color = 'orange', label = 'uncertainty method')
            axs[i, j].axhline(y = df.random[0], color = 'green', alpha = 0.5, label = 'intitial ' + str(ylabel))
            axs[i, j].axvline(x = deletes[j], color = 'maroon', alpha = 0.5, label = '# points deleted')

            title = 'n_keep:' + str(keeps[i]) + ', '
            title += 'n_delete: ' + str(deletes[j])

            axs[i, j].set_title(title)



    # iterates over all subplots:
    for ax in axs.flat:
        ax.set(xlabel='n points added', ylabel=ylabel)
        ax.grid()
        #ax.legend()

        #ax.label_outer()  #hides x labels and tick labels for top plots and y ticks for right plots.

    handles, labels = axs[len(keeps)-1, len(deletes)-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right')

    #fig.legend()
    fig.savefig(save_path_name, dpi=200)
