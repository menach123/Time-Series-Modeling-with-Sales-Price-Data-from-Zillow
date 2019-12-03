import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

def dollar_tick(ax, y_axis=True):
    """
    Input- Pre-existing plot, ax
    Output- The 
    """
    if y_axis:
        new_dollar_scale = ax.get_yticks().astype(int).astype(str)
    else:
        new_dollar_scale = ax.get_xticks().astype(int).astype(str)
    
    dollar_ticks = [new_dollar_scale[0]]
    for tick in new_dollar_scale[1:]:
        try:
            dollar_ticks.append("$"+ tick[:-3]+ ","+ tick[-3:])
        except:
            continue
    if y_axis:
        ax.set_yticklabels(dollar_ticks, fontsize=12)
    else:
        ax.set_xticklabels(dollar_ticks, fontsize=12)