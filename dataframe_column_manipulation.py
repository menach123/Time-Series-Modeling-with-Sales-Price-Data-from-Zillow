import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns

def splitting_pulling_text_dataseries(dataseries, text_= ',', split = 0, start = 0, end = None):
    """
    Input- Dataseries with a piece of text that can be uniformly split all the data points
        Optional- Spliting text
                - starting 
    Output- List of spliced strings
    """
    return [x.split(text_)[split][start:end] for x in dataseries.values]

def splice_dataseries_text(dataseries, start = 0, end = None):
    """
    Input- Dataseries with a piece of text that can be uniformly split all the data points
        Optional- Spliting text
                - starting 
    Output- List of spliced strings
    """
    return [x[start:end] for x in dataseries.values]

def dataframe_column_difference(old, new):
    """
    Input- Two numerical dataseries  
    Output- Dataseries of differences
    """
    return new-old

def dataframe_column_percent_difference(old, new):
    """
    Input- Two numerical dataseries  
    Output- Dataseries of percent difference
    """
    return dataframe_column_difference(old, new)/old

def crash_analysis(Dataframe, plot=False, target_column='Median_Home_Price', reference_column='ZipCode'):
    """
    To analysis the effect of the 2008 recession on region's home pricing.

    Input - Timeseries dataframe that has been lengthen for the original wide format.
    Output - Dataframe 
    """
    dict_crash_zip_data=[]
    for zipcode in Dataframe[reference_column].unique():
        temp_df = Dataframe.loc[Dataframe[reference_column] == zipcode]
        pre_crash_peak = temp_df['2004':'2010'][target_column].max()
        post_crash_low = temp_df['2008':][target_column].min()
        percent_crash_decrease = (post_crash_low- pre_crash_peak)*100/pre_crash_peak
        post_crash_high =  temp_df['2008':][target_column].max()
        recovery_percentage = (post_crash_high-pre_crash_peak)*100/pre_crash_peak
        dict_crash_zip_data.append({'ZipCode': zipcode, 'CrashHigh': pre_crash_peak,
                                    'CrashLow': post_crash_low, 'PostCrashHigh': post_crash_high, 
                                    'CrashLoss': percent_crash_decrease, 'Recovery': recovery_percentage})
    crash_data = pd.DataFrame(dict_crash_zip_data)
    if plot:
        ax = plt.figure(figsize=(13,5))
        ax = sns.distplot(crash_data.Recovery, label='Increase from the High Before the\nRecession to the Highs Since')
        ax = sns.distplot(crash_data.CrashLoss, color='red', label='Decrease from the Pre-Recession\nHighs to the Recession Lows');
        ax.set_title("""Distribution of the Percentage Changes in Zip Codes
        Related to the 2008 Recession""",
                fontsize=16)
        ax.set_ylabel('Probabilties', fontsize=12)
        ax.set_xlabel('Percent (%)', fontsize=12)
        ax.legend();
        print(f"{crash_data.Recovery.loc[crash_data.Recovery<=0].count()} zip codes have not recovery from the 2008 crash.")
        print(f"{round(crash_data.Recovery.mean(),1)}% is the average increase from the pre recession's high.") 
        print(f"{round(crash_data.CrashLoss.mean(),1)}% is the average decrease in the recession.") 
    return crash_data
