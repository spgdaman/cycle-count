import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime
from calendar import monthrange, month_abbr
from download import download_button

# 2021 Kenyan public holidays
holidays = [("Jan",1),("Apr",2),("Apr",4),("Apr",5),("May",1),("May",14),("Jun",1),("Oct",11),("Oct",20),("Dec",13),("Dec",24),("Dec",25),("Dec",26),("Dec",31)]

st.set_page_config(layout='wide')
st.sidebar.markdown("Select Parameter Filters")
file1 = st.sidebar.file_uploader('Inventory by location file in csv format')
file2 = st.sidebar.file_uploader('Rx Revenue Performance in csv format')
no = datetime.now()
no = int(no.strftime("%m"))
month = st.sidebar.number_input("Enter the month number:", min_value=1, max_value=12, value=no, step=1)

# @st.cache
# def cycle_count():
df = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df2[['Quantity','GrossAmount']].replace('', 0, inplace = True)
df2.sort_values("Quantity", inplace=True)
df2 = df2.rename(columns={"ProductName":"Name"})

# Get current year
year = date.today()
year = year.year


# Get month value and number of days in the month
month_name = month_abbr[month]
days_in_month = monthrange(year,month)
days_in_month = days_in_month[-1]

del df["textBox8"]
del df["textBox1"]
del df["textBox2"]
del df["textBox7"]
del df["textBox11"]
del df["textBox17"]
del df["textBox18"]
del df["textLocation"]
del df["textBox31"]
del df["textBox28"]
del df["textBox30"]
del df["textBox29"]
del df["textBox33"]
del df["textBox32"]
del df["textBox3"]
del df["textLocationValue"]
del df["textBox13"]
del df["textBox14"]
del df["textBox15"]
del df["textBox26"]
del df["textBox5"]
del df["textBox6"]
del df["textBox12"]
del df["textBox10"]
del df["textBox9"]
del df["textBox27"]

df = df.rename(columns={
    "textBox4":"Location",
    "textBox24":"Code",
    "textBox25":"Name",
    "textBox23": "Batch no.",
    "textBox22":"Expirydate",
    "textBox21":"QOH",
    "textBox34":"UOM",
    "textBox20":"Average Cost",
    "textBox19":"Value"
})

# deleting empty rows
df['Code'].replace('', np.nan, inplace = True) #  fill empty cells on Code column with na
df.dropna(subset=['Code'], inplace = True) # drop the rows with na on Code column

# merge Rx Revenue Performance with Shortlisted Drugs Data
df_join = pd.merge(
    df,
    df2,
    on = "Name",
    how="left"
)

# delete and assign new dataframes
del df
df = df_join
del df_join

# replace NaN with 0
df.replace(np.nan,0)
for index, value in df.dtypes.items(): 
    if value == 'object':
        df[index] = df[index].fillna('')
    else:
        df[index] = df[index].fillna(0)

# mix high and low value items using sorting
df.sort_values("Quantity", ascending=False, inplace=True)
df.sort_values("QOH", ascending=False, inplace=True)
df.sort_values("GrossAmount", ascending=False, inplace=True)
df = df.sample(frac=1).reset_index(drop=True)

# get a unique list of locations from the location column
locations = df["Location"].unique()

# initialize an empty dataframe for end results to be appended to
column_names = [
    "Location",
    "Value",
    "Average Cost",
    "QOH",
    "Expirydate",
    "Batch no.",
    "Code",
    "Name",
    "UOM",
    "Quantity",
    "GrossAmount",
    "Dates"        
]
final_df = pd.DataFrame(columns = column_names)


# isolate days for cycle count
cycle_count_days = []
days_to_allocate = 0

if 'Central Store' in df.values :
    central_store = df.loc[df["Location"] == "Central Store"]
    for i in range(1,days_in_month + 1):
        dates = date(year,month,i)
        holiday_dates = (month_name,i)
        if dates.weekday() in range(0,5) and holiday_dates not in holidays:
            #print(f"{dates} is a Weekday")
            #print(holiday_dates)
            cycle_count_days.append(dates)
    for i in cycle_count_days:
        days_to_allocate += 1

    # get the number of rows in the data frame and number of rows to allocate
    rows = len(central_store.index)

    rows_per_day = int(rows/days_to_allocate)

    remaining_rows = rows%days_to_allocate

    print(f"There are {rows_per_day} are rows to allocate, with {remaining_rows} left over")


    # Add a blank column for dates to be assigned
    central_store = central_store.assign(Dates='')

    # assign dates on set intervals factoring in remainders, to dataframe
    dates = []

    counter = 0
    for item in cycle_count_days:
        if counter <= rows_per_day:
            for i in range(0, rows_per_day):
                dates.append(item)
                counter += 1
        counter = 0
    
    if remaining_rows > 0:
        dates.extend(cycle_count_days[:remaining_rows])

    central_store['Dates'] = dates

    central_store.sort_values("Dates", ascending=True, inplace=True)

    final_df = final_df.append(central_store, ignore_index = True)


    for location in locations:
        if location in df.values and location != "Central Store":
            location = df.loc[df["Location"] == location]
            for i in range(1,days_in_month + 1):
                dates = date(year,month,i)
                holiday_dates = (month_name,i)
                if dates.weekday() in range(0,6) and holiday_dates not in holidays:
                    #print(f"{dates} is a Weekday")
                    #print(holiday_dates)
                    cycle_count_days.append(dates)
            # for i in cycle_count_days:
            #     days_to_allocate += 1

            days_to_allocate = len(cycle_count_days)

            # get the number of rows in the data frame and number of rows to allocate
            rows = len(location.index)
            location_name = location["Location"].unique()

            rows_per_day = int(rows/days_to_allocate)

            remaining_rows = rows%days_to_allocate

            print(f"There are {rows_per_day} are rows to allocate to {location_name}, with {remaining_rows} left over")


            # Add a blank column for dates to be assigned
            location = location.assign(Dates='')

            # assign dates on set intervals factoring in remainders, to dataframe
            dates = []

            counter = 0
            for item in cycle_count_days:
                if counter <= rows_per_day:
                    for i in range(0, rows_per_day):
                        dates.append(item)
                        counter += 1
                counter = 0
            
            if remaining_rows > 0:
                dates.extend(cycle_count_days[:remaining_rows])

            location['Dates'] = dates

            location.sort_values("Dates", ascending=True, inplace=True)

            final_df = final_df.append(location, ignore_index = True)

# final_df.to_csv("final_df.csv", index = False)

st.dataframe(final_df)

download_button_str = download_button(final_df, f"Cycle Count as at {month_name}, {year}.csv", 'Download CSV', pickle_it=False)
st.sidebar.markdown(download_button_str, unsafe_allow_html=True)