import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
current_palette = sns.color_palette()
import warnings
warnings.filterwarnings('ignore')
import itertools
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams
import time_series_conversion as ts
import plotting as pl
import dataframe_column_manipulation as dm
from IPython.display import clear_output

def pulling_time_columns(dataframe, time_start_column=7):
    """
    Input- Entry zillow data with time series columns. Optional the order of column the time series starts.
    Output- List of time series columns.
    """
    return list(dataframe.columns[time_start_column:])

def pulling_non_time_columns(dataframe, time_start_column=7):
    """
    Input- Entry zillow data with time series columns. Optional the order of column the time series starts.
    Output- List of non time series columns.
    """
    return list(dataframe.columns[:time_start_column])

def dataframe_to_dict(dataframe, columns, type_='records'):
    """
    Input- Entry dataframe. Optional type of dictionary needed
    Output-Output list of dictionaries with columns as the keys.
    """
    return dataframe[columns].to_dict(type_)

def update_dict_wide_to_long(dataframe, value_name= 'Value'):
    """
    Input- Entry zillow data with time series columns. 
    Output- Output list of dictionaries with columns as the keys.
    """
    df_dict = []
    for column in pulling_time_columns(dataframe):
        non_time_series_columns_dict = dataframe_to_dict(dataframe,pulling_non_time_columns(dataframe))
        for j,i in enumerate(dataframe[column]):
            non_time_series_columns_dict[j].update({value_name:i, 'Time':pd.to_datetime(column, format='%Y-%m')})
            df_dict.append(non_time_series_columns_dict[j])
    return df_dict
        
def convert_dict_back_dataframe(df_dict):
    """
    Input- Entry list of dictionaries 
    Output- Dataframe.
    """
    return pd.DataFrame(df_dict).set_index('Time')

def dataframe_wide_to_long(dataframe, value_name= 'Value'):
    """
    Input- Entry zillow data with time series columns in  wide format.
    Output- Dataframe in long format.
    """
    return convert_dict_back_dataframe(update_dict_wide_to_long(dataframe))

def melt_data(df, name='value', id_vars=['RegionName', 'City', 'State', 'Metro', 'CountyName', 'SizeRank']):
    melted = df.melt(id_vars = id_vars, 
        var_name='Time', value_name=name)
    melted['Time'] = pd.to_datetime(melted['Time'], infer_datetime_format=True)
    melted = melted.dropna(subset=[name])
    melted
    melted = melted.set_index('Time')
    return melted

def making_pdq(p, d, q):
    """
    Generating option for parameter of an AMIRA Model
    Input- Highest value for Auto-Regressive(p), Number of Differences (d), and Moving Average (q) terms.
    Output - List of tuples options 
    """
    
    # Define the p, d and q parameters to take any value between 0 and 2
    p = range(0,p)
    d = range(0,d)
    q = range(0,q)
    
    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p,d,q)) 
    return pdq

def making_pdqs(p, d, q, period=12):
    """
    Generating option for parameter of an SAMIRA Model
    Input- Highest value for Auto-Regressive(p), Number of Differences (d),  Moving Average (q), and Seasonality (s) terms.
    Output - List of tuples options 
    """
    
    # Define the p, d and q parameters to take any value between 0 and 2
    p = range(0,p)
    d = range(0,d)
    q = range(0,q)
    
    # Generate all different combinations of p, q and q triplets
    pdq = list(itertools.product(p,d,q))
    
    # Generate all different combinations of seasonal p, q and q triplets (use period for frequency)
    pdqs = [(x[0], x[1], x[2], period) for x in list(itertools.product(p, d, q))]
    
    return pdqs

def amira_output(Dataseries, pdq, pdqs): 
    parameter_results = []   
    for comb in pdq:
        for combs in pdqs:
            try:
                mod = sm.tsa.statespace.SARIMAX(Dataseries,
                                                order=comb,
                                                seasonal_order=combs,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)
                output = mod.fit()
                parameter_results.append([comb, combs, output.aic])
                #print('ARIMA {} x {}12 : AIC Calculated ={}'.format(comb, combs, output.aic))
            except:
                continue 
    parameter_results = pd.DataFrame(parameter_results, columns=['pdq', 'pdqs', 'aic'])
    return parameter_results

def samira_model(Dataseries,pdq, pdqs):
    mod = sm.tsa.statespace.SARIMAX(Dataseries,
                                                order=pdq,
                                                seasonal_order=pdqs,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)
    return mod

def find_best_model_parameters(Dataseries, pdq, pdqs):
    
    parameter_results = amira_output(Dataseries, pdq, pdqs)                         
    #parameter_results = parameter_results.sort_values('aic').iloc[0]
    return parameter_results.loc[parameter_results['aic'].idxmin()]


def best_aic(Dataseries, pdq, pdqs):
    parameter_results = amira_output(Dataseries, pdq, pdqs) 
    return parameter_results.min()

def next_year_output(Dataseries, pdq, pdqs, steps=12):
    results = find_best_model_parameters(Dataseries, pdq, pdqs)
    print(results)
    ARIMA_MODEL = sm.tsa.statespace.SARIMAX(Dataseries,
                                    order=results['pdq'],
                                    seasonal_order=results['pdqs'],
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)
    output = ARIMA_MODEL.fit()
    # Get forecast 500 steps ahead in future
    prediction = output.get_forecast(steps=steps)
    # Get confidence intervals of forecasts
    pred_conf = prediction.conf_int()
    pred_dict = {'Predicted':prediction.predicted_mean[-1],
                 'lower':pred_conf.iloc[-1]['lower Value'], 
                 'upper':pred_conf.iloc[-1]['upper Value'],
                 'Last': Dataseries[-1]}
    return pred_dict, prediction.predicted_mean,  pred_conf

def next_year_output1(Dataseries, pdq, pdqs, steps=12):
    
    ARIMA_MODEL = sm.tsa.statespace.SARIMAX(Dataseries,
                                    order=pdq,
                                    seasonal_order=pdqs,
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)
    output = ARIMA_MODEL.fit()
    # Get forecast 500 steps ahead in future
    prediction = output.get_forecast(steps=steps)
    # Get confidence intervals of forecasts
    pred_conf = prediction.conf_int()
    pred_dict = {'Predicted':prediction.predicted_mean[-1],
                 'lower':pred_conf.iloc[-1]['lower Value'], 
                 'upper':pred_conf.iloc[-1]['upper Value'],
                 'Last': Dataseries[-1]}
    return pred_dict, prediction.predicted_mean,  pred_conf

def samira_with_parameters(Dataseries, pdq, pdqs, steps=12, plot=False, name='Area'):
    ARIMA_MODEL = sm.tsa.statespace.SARIMAX(Dataseries,
                                    order=pdq,
                                    seasonal_order=pdqs,
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)
    output = ARIMA_MODEL.fit()
    # Get forecast 500 steps ahead in future
    prediction = output.get_forecast(steps=steps)
    # Get confidence intervals of forecasts
    pred_conf = prediction.conf_int()
    pred_dict = {'Predicted':prediction.predicted_mean[-1],
                 'lower':pred_conf.iloc[-1]['lower Value'], 
                 'upper':pred_conf.iloc[-1]['upper Value'],
                 'Last': Dataseries[-1]}
    
    if plot:
        ax = Dataseries.plot(label='Observed', figsize=(13,5), fontsize=12)
        prediction.predicted_mean.plot(ax=ax, label='Forecast')
        ax.fill_between(pred_conf.index,
                        pred_conf.iloc[:, 0],
                        pred_conf.iloc[:, 1], color='blue', alpha=.25)
        ax.set_title(f"Price Projection of {name}")
        ax.set_xlabel('Date')
        ax.set_ylabel('Mean Sales Price')
        plt.legend()
        plt.show()
    return pred_dict

def find_pdq_pdqs(p, d, q, Dataseries, period=12, steps=12):
    """
    Find the best pdq and PDQs combination for the SAMIRA Model based on AIC output
    """
    pdq = making_pdq(p, d, q)
    pdqs = making_pdqs(p, d, q, period)
    return find_best_model_parameters(Dataseries, pdq, pdqs)

class SAMIRA(object):
    
    def __init__(self, time_series):
        self.time_series = time_series
        pass
        
    def set_parameters(self, p=2,d=2,q=2, period=12, steps=12):
        parameters = ts.find_pdq_pdqs(p, d, q, self.time_series, period, steps)
        self.parameters = parameters.to_dict()
        pdq = parameters['pdq']
        pdqs = parameters['pdqs']
        self.model = ts.samira_model(self.time_series, pdq, pdqs)
        self.output = self.model.fit()
        return parameters

    def load_parameter(self, parameters):
        self.parameters = parameters
        pdq = parameters['pdq']
        pdqs = parameters['pdqs']
        self.model = ts.samira_model(self.time_series, pdq, pdqs)
        self.output = self.model.fit()


    def summary(self):
        return self.output.summary()

    def diagnostics(self):
        self.output.plot_diagnostics(figsize=(13, 8))
        plt.show
        pass

    def validation(self, start_year='2017', plot_year=False, area='Area'):
        self.prediction = self.output.get_prediction(start=pd.to_datetime(start_year), 
                                                    dynamic=False)
        self.confidence_interval_ = self.prediction.conf_int()     
        # Get the Real and predicted values 
        forecasted = self.prediction.predicted_mean 
        truth = self.time_series[start_year:] 
                # Compute the mean square error 
        self.mse = ((forecasted - truth) ** 2).mean() 
        
        if plot_year:
            ax = self.time_series[plot_year:].plot(figsize=(13,8), label='Observed', fontsize=12, color='b')
            #Plot predicted values 
            self.prediction.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.9, color='r') 
            

            #Plot the range for confidence intervals 
            ax.fill_between(self.confidence_interval_.index, 
                            self.confidence_interval_.iloc[:, 0], 
                            self.confidence_interval_.iloc[:, 1], color='g', alpha=.5, label= 'Confidence\nInterval')

            ax.set_ylabel("Mean Sale Price (USD)", fontsize=12)
            pl.dollar_tick(ax)
            ax.legend(bbox_to_anchor=(1.04,1), loc="upper left", ncol=1,fontsize=12)
            plt.title(f"Monthly Mean Housing Prices\nfor {area}", fontsize=18);
        pass

    def add_zip(self, zip):
        """
        Adding zip to model for future reference.
        """
        self.zip = zip
        pass

    def roi(self):
        self.roi1 = (self.output.get_forecast(steps=12).predicted_mean[-1]-self.time_series.iloc[-1])/self.time_series.iloc[-1]
        self.roi5 = (self.output.get_forecast(steps=60).predicted_mean[-1]-self.time_series.iloc[-1])/self.time_series.iloc[-1]
    
    def plotting_validation(self, start_year='2017', plot_year='2013', area='Area'):
        ax = self.time_series[plot_year:].plot(figsize=(13,8), label='Observed', fontsize=12)
        #Plot predicted values 
        self.prediction.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.9) 
            

        #Plot the range for confidence intervals 
        ax.fill_between(self.confidence_interval_.index, 
                            self.confidence_interval_.iloc[:, 0], 
                            self.confidence_interval_.iloc[:, 1], color='g', alpha=.5, label= 'Confidence\nInterval')

        ax.set_ylabel("Mean Sale Price (USD)", fontsize=12)
        pl.dollar_tick(ax)
        ax.legend(bbox_to_anchor=(1.04,1), loc="upper left", ncol=1,fontsize=12)
        plt.title(f"Monthly Mean Housing Prices\nfor the {area}", fontsize=18);         ax = self.time_series[plot_year:].plot(figsize=(13,8), label='Observed', fontsize=12)
        
        #Plot predicted values 
        self.prediction.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.9) 
            

        #Plot the range for confidence intervals 
        ax.fill_between(self.confidence_interval_.index, 
                            self.confidence_interval_.iloc[:, 0], 
                            self.confidence_interval_.iloc[:, 1], color='g', alpha=.5, label= 'Confidence\nInterval')

        ax.set_ylabel("Mean Sale Price (USD)", fontsize=12)
        pl.dollar_tick(ax)
        ax.legend(bbox_to_anchor=(1.04,1), loc="upper left", ncol=1,fontsize=12)
        plt.title(f"Monthly Mean Housing Prices\nfor the {area}", fontsize=18);
