# pip install pandas
# pip install timedelta
# pip install openpyxl
# pip install pathlib
###############################################################################

import pandas as pd
import numpy as np
import datetime as dt
from pathlib import Path
from os import chdir
import os.path

path = r'C:\Users\Jacob Shughrue\Dropbox\Coding\Python\Harrys'
chdir(path)  # set working directory
print(f"Current directory: {Path.cwd()}")

# import Excel sheets # case-sensitive
filename = 'exercise_data.xlsx'
sheet1 = 'data'
sheet2 = 'Viewable Products'

data = pd.read_excel(filename, sheet_name=sheet1)
products = pd.read_excel(filename, sheet_name=sheet2)

# join two csv files on "viewable_product_id"
df = pd.merge(data, products)

# set the 'id' column to be the index column
# df.set_index("id", inplace=True)

# rename columns
df = df.rename(columns={
    "created_at": "plan_start_date",
    "removed_at": "plan_end_date",
    "created_by_client_type": "plan_start_type",
    "removed_by_client_type": "plan_end_type",
    "abbrev": "product_name",
    "viewable_product_id": "product_id"
})

# replace "www" with "web"
df['plan_start_type'] = df['plan_start_type'].str.replace('www', 'web')
df['plan_end_type'] = df['plan_end_type'].str.replace('www', 'web')

# replace blank values with "on_going" to indicate current subscription
df['plan_end_type'] = df['plan_end_type'].replace(np.nan, "on_going")
df['plan_end_date'] = df['plan_end_date'].replace(np.nan, "on_going")

# Set variable for last date in file
feb012017 = date_time_obj = dt.datetime.strptime('2017-02-01 14:24:00', '%Y-%m-%d %H:%M:%S')

# replace text value 'on_going' with last date in file
df.loc[df.plan_end_date == 'on_going', 'plan_end_date'] = feb012017

# remove rows with data quality issues:
dq_rule_failure = df.loc[
    (df['plan_end_type'] == 'on_going') & df['plan_end_date'].notnull() & (df['plan_end_date'] != feb012017)]

df = df[~df['user_id'].isin(dq_rule_failure['user_id'])]
print("{} rows dropped due to data quality issues".format(dq_rule_failure['user_id'].count()))

# change type of column to datetime
df['plan_end_date'] = pd.to_datetime(df['plan_end_date'], format='%Y-%m-%d %H:%M:%S.%f')

# create columns for the first customer sale date and last customer sale date for the entire customer lifetime
df['first_cust_sale_date'] = (df.groupby(['user_id'])['plan_start_date'].transform('min'))

df['last_cust_sale_date'] = (df.groupby(['user_id'])['plan_start_date'].transform('max'))

# create temporary column - get the maximum plan_end_date per customer less the first_cust_sale_date column - for use in function below
df['max_plan_end_date_per_user'] = round(
    (df.groupby(['user_id'])['plan_end_date'].transform('max') - df['first_cust_sale_date']).dt.total_seconds() / 86400,
    1)  # where 86400 seconds is one day


# create a function for column creation
def is_on_going(row):
    if row['plan_end_type'] == 'on_going':
        return round(((feb012017 - row['first_cust_sale_date']).total_seconds()) / 86400, 1)
    else:
        return row['max_plan_end_date_per_user']  # temporary column - see above


df['total_cust_lifetime_length_days'] = df.apply(is_on_going, axis=1)  # create a new column based on the function

df['repeat_cust_flag'] = (df['last_cust_sale_date'] - df[
    'first_cust_sale_date']).dt.total_seconds() / 86400 >= 1


# create a column for line subscription duration days
def insert_name_here(row):
    if row['plan_end_type'] == 'on_going':
        return round(((feb012017 - row['plan_start_date']).total_seconds()) / 86400, 1)
    else:
        return round(((row['plan_end_date'] - row['plan_start_date']).total_seconds()) / 86400, 1)


df['line_subscription_duration_days'] = df.apply(insert_name_here, axis=1)  # create a new column based on the function

# creation of line_one_time_purchase_flag
df['line_one_time_purchase_flag'] = df['line_subscription_duration_days'] < 0.5


# create a column for subscription_occurrence_count
# this has been refacted in the IPYNB to match the logic of the cust_id occurence count column
def rename_me(row): # modified to just show the number not "one time purchase" can likely be optimized out of a function
        return df.user_id.eq(
            row.user_id).sum()  # because this code needs to look at the entire df, row[] cannot be used


df['subscription_occurrence_count'] = df.apply(rename_me, axis=1)  # create a new column based on the function

#########################
counts = df.groupby(['user_id'])['user_id'].count()
#df['subscription_occurrence_count'] = np.where(df['id'] == counts['user_id'], counts[[2]], np.nan)
##########################

# create cancelled_line_flag
# if line_one_time_purchase_flag = True THEN 'one_time_purchase'
# if plan_end_date = 'on_going' THEN 'False'
# elif return 'True' aka true this line was cancelled

def name_me_later(row):
    if row['line_one_time_purchase_flag']:
        return 'one_time_purchase'
    elif row['plan_end_type'] == 'on_going':
        return False
    else:
        return True


df['cancelled_line_flag'] = df.apply(name_me_later, axis=1)  # create a new column based on the function

################ potential refactor for the above ################# # create cancelled_line_flag # does appear to work and does not use.apply

df['cancelled_line_flag'] = np.where(
    df['line_one_time_purchase_flag'],  # condition
    "one_time_purchase",  # value
    df['plan_end_type'] != 'on_going'  # else
)
###############################

# create cust_cancellation_count column
# counts the unique number of times a user cancelled a product (aka =='True') then uses a merge to apply the distinct count to the df
df = df.merge(
    df.loc[df['cancelled_line_flag'].astype(str) == 'True', 'user_id'].value_counts().rename(
        'cust_cancellation_count'),
    how='outer', left_on='user_id', right_index=True).fillna(
    0)  # uses an outer join so customers that have not cancelled are not dropped

# look = look = [df['cancelled_line_flag'], 'user_id']
# look2 = df.loc[df['cancelled_line_flag'].astype(str) == 'True', 'user_id'].value_counts()


# create a column for count_of_unique_lifetime_products
# df['count_of_unique_lifetime_products'] = df.groupby('user_id')['product_name'].nunique() # stand alone fucntion before merge
df = df.merge(df.groupby('user_id')['product_name'].nunique().rename('count_of_unique_lifetime_products'),
              how='outer',
              left_on='user_id', right_index=True)

# create a lookup table for a 'Product Type' market lens
product_type_table = pd.DataFrame(
    {'product_name': [
        'ShaveCream', 'DailyFaceWash', 'DailyFaceLotionSPF15', 'HarrysBlades', 'Blades2GelsPlan',
        'Blades,Gel,PostShave', 'FoamingShaveGel',
        'PostShaveBalm', 'BladesPlan', 'RazorBlades', 'Blades1GelPlan', 'ShaveGroomPlan'],

        'product_type': ['Pre/Post Shave', 'FaceCare', 'FaceCare', 'Blades', 'Bundle',
                         'Bundle', 'Pre/Post Shave', 'Pre/Post Shave', 'Blades', 'Blades', 'Bundle', 'Bundle']})

# create a column for product_type
df = df.merge(product_type_table, how='left', on='product_name')

# df_test = df = df.merge(product_type_table, how='left', left_on='product_name', right_on='product_name')

# fruit_colors.merge(fruit_prices, on='name', how='left')

# create a column for the count of sales dates per customer
df['cust_id_occurrence_count'] = df.groupby(['user_id'])['user_id'].transform('count')

# create column for customer_subscription_change_flag
df['customer_subscription_change_flag'] = (df['repeat_cust_flag'] == True) & (df['cust_cancellation_count'] >= 1) & (
            df['count_of_unique_lifetime_products'] > 1)

# Set variable for last date in file #note: this repeated from earlier in the code
feb012017 = date_time_obj = dt.datetime.strptime('2017-02-01 14:24:00', '%Y-%m-%d %H:%M:%S')

# set the 'id' column to be the index column
df.set_index("id", inplace=True)

df = df.drop(columns=['max_plan_end_date_per_user'])  # drop temporary column

# reorder columns for export
df = df[[
    'cust_id_occurrence_count',
    'cancelled_line_flag',
    'cust_cancellation_count',
    'line_subscription_duration_days',
    'line_one_time_purchase_flag',
    'first_cust_sale_date',
    'last_cust_sale_date',
    'repeat_cust_flag',
    'count_of_unique_lifetime_products',
    # 'first_subscription_flag', # not including this
    'subscription_occurrence_count',
    'total_cust_lifetime_length_days',
    'customer_subscription_change_flag',
    'product_id',
    'user_id',
    'plan_start_type',
    'plan_end_type',
    'plan_start_date',
    'plan_end_date',
    'product_name',
    'product_type',
    'quantity',
    'price',
    'starter_set_count',
    'other_set_count',
    'blade_count',
    'handle_count',
    'shave_gel_count',
    'shave_cream_count',
    'face_wash_count',
    'aftershave_count',
    'lipbalm_count',
    'razorstand_count',
    'face_lotion_count',
    'travel_kit_count']]

# sort
df = df.sort_values(['user_id', 'id'], ascending=[True, True])

# write to csv
# df.to_csv(os.path.join(r'C:\Users\Jacob Shughrue\Dropbox\Coding\Python\Harrys', 'df_python_export.csv'))

# create a column for repeat customer flag

###############################################################################
# pd.set_option('display.max_columns', None)
# pd.reset_option("display.max_columns")
# cols = list(df.columns.values) #list all column headers

# print(df.head(10))
# print(df.dtypes['days_since_first_purchase_to_date'])  # get data type

# print(df.loc[df['id'] == 1833947, 'last_cust_sale_date'])

# print(df.loc[1325, 'line_lifetime_length_days'])  # where 1325 is a row
###############################################################################

# drop columns
# df = df.drop(columns=['test', 'cust_id_occurrence'])
# df = df.drop(columns=['test', 'cust_id_occurrence'])
# df = df.drop(columns=['line_days_since_first_purchase_to_date'])

# Project Notes:
# 1) 77 rows had data issues in the raw data file; these rows showed a removed at time but removal type was blank. Ex. row 1549123. To circumvent, these CUSTOMERS were dropped from the table
# Solution: Pop rows off for all customers who had a plan_end_date that was populated but the plan_end_type was empty


###############old content below##################
# create a column tracking how long it has been since the customers first purchase, despite if they have cancelled it or not
# df['line_days_since_first_purchase_to_date'] = round((((df.groupby(['user_id'])['plan_start_date'].transform(
#     'max')) - df['first_cust_sale_date']).dt.total_seconds() / 86400), 1)

# df['test'] = round((((df.groupby(['user_id'])['plan_end_date'].transform('max')) - df[
#   'first_cust_sale_date']).dt.total_seconds() / 86400), 1)0=-e


