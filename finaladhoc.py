import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
%matplotlib inline

with open("/Users/nyaliwag/Downloads/transaction-data-adhoc-analysis.json") as f:
    data = pd.read_json(f, orient = "columns")  
data

#CODE OF TABLE 1
#split each item
single_datadf=data.assign(single_items=data.transaction_items.str.split(';')).explode('single_items')

#get the quantity of each item per order
# https://stackoverflow.com/questions/36505847/substring-of-an-entire-column-in-pandas-dataframe
single_datadf['quantity'] = single_datadf['single_items'].str[-2]

#turn quantity to int
# https://sparkbyexamples.com/pandas/pandas-convert-column-to-int/#:~:text=2.-,Convert%20Column%20to%20int%20(Integer),int64%20%2C%20numpy.
single_datadf["quantity"] = single_datadf["quantity"].astype('int')

#turn transdate to datetime format
# https://www.geeksforgeeks.org/how-to-filter-dataframe-rows-based-on-the-date-in-pandas/
single_datadf['transaction_date'] = pd.to_datetime(single_datadf['transaction_date'])

#make new column which only says the month 
# https://datascientyst.com/extract-month-and-year-datetime-column-in-pandas/
single_datadf['mm'] = pd.to_datetime(single_datadf['transaction_date']).dt.month

#get only the brand & item
single_datadf['items_name'] = single_datadf['single_items'].str[:-5]

single_datadf

#TABLE 1
#group by month to gather all in the same month
table1_pivot=single_datadf.pivot_table("quantity", columns=["mm"],index='items_name', aggfunc='sum')
table1_pivot

#TABLE 1 CHART
#https://stackoverflow.com/questions/50396479/create-a-plot-from-a-pandas-dataframe-pivot-table
table1chart=table1_pivot.plot(kind="bar")
plt.xlabel('Items Name')
plt.ylabel('Count of Total Sold')
plt.title('Total Count of Items Sold per Month')

table1chart

#CODE OF TABLE 2 
#getting the price of each item
price_df = single_datadf.copy()
price_df=price_df[["transaction_items", "quantity", "mm", "transaction_value"]]

price_df.loc[price_df['transaction_items'].str.contains(';'), 'single'] = 'duplicate'

#get the single item per order
#https://www.geeksforgeeks.org/how-to-drop-rows-in-dataframe-by-conditions-on-column-values/
index_price = price_df[ price_df['single'] == "duplicate" ].index

price_df.drop(index_price, inplace = True)

#get the brand & item
price_df['items_name'] = price_df['transaction_items'].str[:-5]

#remove duplicates
price_df=price_df.drop_duplicates(subset="items_name", keep="first")

#price per item
price_df["price_per_item"]=price_df["transaction_value"]/price_df["quantity"]

price_df

price_df[["items_name", "price_per_item"]]

#merging tables to put the price of each item 
#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html
merged_df=single_datadf.merge(price_df, how='left', on='items_name')

#to clean up the table, i decided to delete duplicated data 
#https://stackoverflow.com/questions/14984119/python-pandas-remove-duplicate-columns
merged_df.T.drop_duplicates().T

#remove unnecessary columns
#https://www.educative.io/answers/how-to-delete-a-column-in-pandas
merged_df.drop('quantity_y', inplace=True, axis=1)
merged_df.drop('mm_y', inplace=True, axis=1)
merged_df.drop('transaction_value_y', inplace=True, axis=1)
merged_df.drop('single', inplace=True, axis=1)

#get the price of the item per customer order
merged_df["itemorder_price"]=merged_df["quantity_x"]*merged_df["price_per_item"]

merged_df

#TABLE 2
merged_pivot=merged_df.pivot_table("itemorder_price", columns=["mm_x"],index='items_name', aggfunc='sum')
merged_pivot

table2chart=merged_pivot.plot(kind="bar")
plt.xlabel('Items Name')
plt.ylabel('Total Sale Value')
plt.title('Total Sales Value per Month')

table2chart

#FINAL TABLE
summary_df=single_datadf.copy()
#make a pivot table to get the total count of store visits the customer makes 
summary_pivot=summary_df.pivot_table("mail", columns=["mm"],index='name', aggfunc='count', fill_value="0")
summary_pivot

#repeaters
#purchase this month and the previous month 
#ill try to make it into a dataframe first because its easier to manipulate 
#https://www.statology.org/pandas-pivot-table-to-dataframe/

summary2_df = summary_pivot.reset_index()

#adding column names
summary2_df.columns = ['Name', 'January', 'February','March', 'April', 'May', 'June']

#customers per month summary
summary2_df.loc[summary2_df['January'].str.contains('0', na=False), 'Jan_Customer'] = 'No'
summary2_df.loc[~summary2_df['January'].str.contains('0', na=False), 'Jan_Customer'] = 'Yes'
summary2_df.loc[summary2_df['February'].str.contains('0', na=False), 'Feb_Customer'] = 'No'
summary2_df.loc[~summary2_df['February'].str.contains('0', na=False), 'Feb_Customer'] = 'Yes'
summary2_df.loc[summary2_df['March'].str.contains('0', na=False), 'Mar_Customer'] = 'No'
summary2_df.loc[~summary2_df['March'].str.contains('0', na=False), 'Mar_Customer'] = 'Yes'
summary2_df.loc[summary2_df['April'].str.contains('0', na=False), 'Apr_Customer'] = 'No'
summary2_df.loc[~summary2_df['April'].str.contains('0', na=False), 'Apr_Customer'] = 'Yes'
summary2_df.loc[summary2_df['May'].str.contains('0', na=False), 'May_Customer'] = 'No'
summary2_df.loc[~summary2_df['May'].str.contains('0', na=False), 'May_Customer'] = 'Yes'
summary2_df.loc[summary2_df['June'].str.contains('0', na=False), 'Jun_Customer'] = 'No'
summary2_df.loc[~summary2_df['June'].str.contains('0', na=False), 'Jun_Customer'] = 'Yes'

#get another summary
summary2_df['1'] = np.count_nonzero(summary2_df.iloc[:,6:8] == 'Yes', axis=1)
summary2_df['2'] = np.count_nonzero(summary2_df.iloc[:,7:9] == 'Yes', axis=1)
summary2_df['3'] = np.count_nonzero(summary2_df.iloc[:,8:10] == 'Yes', axis=1)
summary2_df['4'] = np.count_nonzero(summary2_df.iloc[:,9:11] == 'Yes', axis=1)
summary2_df['5'] = np.count_nonzero(summary2_df.iloc[:,10:12] == 'Yes', axis=1)
summary2_df['6'] = np.count_nonzero(summary2_df.iloc[:,11:13] == 'Yes', axis=1)

#sum
repeater = summary2_df.iloc[:,13:19][summary2_df.iloc[:,13:19]==2].count()
repeater

#engaged
summary3_df=summary2_df.copy()
summary3_df=summary3_df.drop(summary3_df.loc[:, 'January':'June'].columns, axis=1)
summary3_df=summary3_df.drop(summary3_df.loc[:, '1':'6'].columns, axis=1)

#engaged per month
summary3_df['Jan_Engaged_Count'] = (summary3_df[['Jan_Customer']] == 'Yes').sum(axis=1)
summary3_df['Feb_Engaged_Count'] = (summary3_df.iloc[:,1:3] == 'Yes').sum(axis=1)
summary3_df['Mar_Engaged_Count'] = (summary3_df.iloc[:,1:4] == 'Yes').sum(axis=1)
summary3_df['April_Engaged_Count'] = (summary3_df.iloc[:,1:5] == 'Yes').sum(axis=1)
summary3_df['May_Engaged_Count'] = (summary3_df.iloc[:,1:6] == 'Yes').sum(axis=1)
summary3_df['Jun_Engaged_Count'] = (summary3_df.iloc[:,1:7] == 'Yes').sum(axis=1)

#engaged count
summary3_df['1'] = np.where((summary3_df['Jan_Engaged_Count'] == 1), 1, 0)
summary3_df['2'] = np.where((summary3_df['Feb_Engaged_Count'] == 2) , 1, 0)
summary3_df['3'] = np.where((summary3_df['Mar_Engaged_Count'] == 3) , 1, 0)
summary3_df['4'] = np.where((summary3_df['April_Engaged_Count'] == 4) , 1, 0)
summary3_df['5'] = np.where((summary3_df['May_Engaged_Count'] == 5) , 1, 0)
summary3_df['6'] = np.where((summary3_df['Jun_Engaged_Count'] == 6) , 1, 0)

engaged = summary3_df.iloc[:,13:19].sum()
engaged

#inactive
#current month is 0
#before months >0
#https://www.analyticsvidhya.com/blog/2020/03/what-are-lambda-functions-in-python/
summary4_df=summary3_df.drop(summary3_df.loc[:, 'Jan_Engaged_Count':'6'].columns, axis=1)

#get per month data
summary4_df['1'] = np.where((summary4_df['Jan_Customer'] == 'No') & (summary4_df['Name'] == 'Yes'), 1, 0)
summary4_df['2'] = np.where((summary4_df['Feb_Customer'] == 'No') & (summary4_df['Jan_Customer'] == 'Yes'), 1, 0)
summary4_df['3'] = np.where((summary4_df['Mar_Customer'] == 'No') & ((summary4_df['Jan_Customer'] == 'Yes') | (summary4_df['Feb_Customer'] == 'Yes')) , 1, 0)
summary4_df['4'] = np.where((summary4_df['Apr_Customer'] == 'No') & ((summary4_df['Jan_Customer'] == 'Yes') | (summary4_df['Feb_Customer'] == 'Yes') | (summary4_df['Mar_Customer'] == 'Yes')) , 1, 0)
summary4_df['5'] = np.where((summary4_df['May_Customer'] == 'No') & ((summary4_df['Jan_Customer'] == 'Yes') | (summary4_df['Feb_Customer'] == 'Yes') | (summary4_df['Mar_Customer'] == 'Yes') | (summary4_df['Apr_Customer'] == 'Yes')) , 1, 0)
summary4_df['6'] = np.where((summary4_df['Jun_Customer'] == 'No') & ((summary4_df['Jan_Customer'] == 'Yes') | (summary4_df['Feb_Customer'] == 'Yes') | (summary4_df['Mar_Customer'] == 'Yes') | (summary4_df['Apr_Customer'] == 'Yes') | (summary4_df['May_Customer'] == 'Yes')) , 1, 0)


inactive = summary4_df.iloc[:,7:13].sum()
inactive

#make a dataframe finally
finalreport=pd.DataFrame({
    'repeater': repeater,
    'inactive': inactive,
    'engaged' : engaged
})

finalreport=finalreport.T
finalreport

summary_chart = finalreport.plot(kind='bar')
plt.xlabel('Customer Status')
plt.ylabel('Number of Customers')
summary_chart.set_xticklabels(finalreport.index)
plt.setp(plt.gca().get_xticklabels(), rotation=0, horizontalalignment='center')
plt.title('Monthly Count of Customer Status')

summary_chart

