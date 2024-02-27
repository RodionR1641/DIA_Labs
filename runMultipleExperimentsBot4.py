from simpleBot4_soln import runOnce
import pandas as pd
from scipy import ttest_ind
import mathplotlib.pyplot as plt

def runMultipleExperiments(noOfReps,follow):
    results = []

    for _ in range(noOfReps):
        results.append(runOnce(follow))
    return results

def runExperimentsWithDifferentParameters():
    resultsTable = {} # dictinoary of parameter value to list of results
    for condition in [True,False]:
        dirtCollectedList = runMultipleExperiments(10,condition) # 10 experiments
        resultsTable[condition] = dirtCollectedList
    
    results = pd.DataFrame(resultsTable)
    print(resultsTable)
    results.to_excel("roboticsExperiment.xlsx")
    # doing statistical analysis -> using t test to see if the means are statistically different
    print(ttest_ind(results[True],results[False]))

    # descriptive stats
    print(results.mean(axis=0)) # axis=0 means average of each column

    results.boxplot(grid=False)
    plt.show()

runExperimentsWithDifferentParameters()