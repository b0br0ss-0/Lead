import pyaqsapi as aqs
import csv
import datetime
aqs.aqs_credentials('aengstrom@utah.gov', 'taupefox34')
def get_lead_data(dates:list):
    for yr in dates:
        data=aqs.bysite.sampledata('14129',datetime.date(yr,1,1),datetime.date(yr,12,31),'49','035','1001')
        print(data)
        if yr==dates[0]:
            data.to_csv('lead.csv', mode='a', index=False, header=True)
        else:
            data.to_csv('lead.csv', mode='a', index=False, header=False)
def csv_sorter(input_filename: str, output_filename: str, column_index: int):
        #Sorts CSV file by sample date
    with open(input_filename, 'r', newline ='') as input_file, open(output_filename, 'w', newline='') as output_file:
        reader = csv.reader(input_file)
        header = next(reader)  # Read the header row
        sorted_data = sorted(reader, key=lambda row: row[column_index], reverse=False)
            
        writer = csv.writer(output_file)
        writer.writerow(header)  # Write the header row
        writer.writerows(sorted_data)

def daily_concentrations(input_filename:str, output_filename: str):
    with open(input_filename, 'r') as infile, open(output_filename, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header= next(reader)
        writer.writerow([header[9], header[13]])

        for row in reader:
            # Modify row if needed, for example:
            if row[18]=='EVERY 6TH DAY' and not row[21]:
                modified_row = [row[9], row[13]] 
                writer.writerow(modified_row)

def month_average(input_filename:str, monthly_output_name:str):
    
    all_lead_data=[]
    with open(input_filename, 'r') as file:
        reader=csv.DictReader(file)
        for row in reader:
            all_lead_data.append((row['date_local'], row['sample_measurement'], row['qualifier'], row['sample_frequency']))
    monthly_average={}
    for line in all_lead_data:
        if not line[2] and line[3]=='EVERY 6TH DAY':
            if line[0][0:7] not in monthly_average:
                monthly_average[line[0][0:7]]={'values':[float(line[1])], 'n':1, 'average':float(line[1])}

            else:
                monthly_average[line[0][0:7]]['values'].append(float(line[1]))
                monthly_average[line[0][0:7]]['n']+=1
                monthly_average[line[0][0:7]]['average']=sum(monthly_average[line[0][0:7]]['values'])/monthly_average[line[0][0:7]]['n']



    with open(monthly_output_name, 'w', newline='') as output:
        writer= csv.writer(output)
        for month in monthly_average:
            writer.writerow([month, monthly_average[month]['average']])

def three_month_average(filename: str, output_filename: str):
    month_data=[]
    with open(filename, 'r', newline='') as month:
        reader=csv.reader(month)
        for line in reader:
            month_data.append(line)
    print(month_data)
    with open(output_filename, 'w', newline='') as output:
        writer= csv.writer(output)
        for month in range(len(month_data)):
            if month==0 or month==len(month_data)-1:
                continue
            else:
                three_month_avg= sum([float(month_data[month-1][1]),float(month_data[month][1]),float(month_data[month+1][1])])/3
                print(three_month_avg)
                writer.writerow([month_data[month][0], three_month_avg])

def lead_design_values(input_filename: str, year_range: int, years:list):
    from collections import defaultdict
    year_data = defaultdict(list)
    with open(input_filename, 'r', newline='') as three_month_avg:
        reader = csv.reader(three_month_avg)
        for line in reader:
            year = int(line[0][0:4])
            value = float(line[1])
            year_data[year].append(value)
    dvs = []
    for start_year in range(years[0], years[1] - (year_range-2)):  # Slide from years[0] to years[1] - 2
        window_years = range(start_year, start_year+year_range)
        window_values = []
        for y in window_years:
            window_values.extend(year_data.get(y, []))
        if window_values:
            max_val = max(window_values)
            dvs.append((start_year + year_range-1, max_val))  
    return dvs

import numpy as np
from scipy import stats 
mine_concentrator=[
    (2010, 0.4992),
    (2011, 0.322),
    (2012, 0.209),
    (2013, 0.737855),
    (2014, 0.285955),
    (2015, 0.216559),
    (2016, 0.388887),
    (2017, 0.531469201),
    (2018, 0.391723444),
    (2019, 0.187245424),
    (2020, 0.22921039),
    (2021, 0.22921087),
    (2022, 0.335761597),
    (2023, 0.37510337),
    (2024, 0.36319)]
smelter_refinery=[
    (2010, 3.1033),
    (2011, 3.104),
    (2012, 2.806),
    (2013, 3.308182),
    (2014, 3.278825),
    (2015, 2.680235),
    (2016, 5.451017),
    (2017, 5.704836147),
    (2018, 7.444708276),
    (2019, 5.589297939),
    (2020, 2.731244232),
    (2021, 2.734198846),
    (2022, 3.791516084),
    (2023, 1.806821135),
    (2024, 6.16366)]
combined = [(year1, mc_val + sr_val) for ((year1, mc_val), (year2, sr_val)) in zip(mine_concentrator, smelter_refinery) if year1 == year2]
pre_2017 = np.array([total_val for (year, total_val) in combined if year <= 2016])
post_2017 = np.array([total_val for (year, total_val) in combined if year > 2016])
print(np.std(pre_2017, ddof=1), np.std(post_2017, ddof=1))
print(np.mean(pre_2017), np.mean(post_2017))
print(stats.ttest_ind(a=pre_2017, b=post_2017, equal_var=True))

    

#print(aqs.aqs_sites_by_county('49','035'))
#get_lead_data([2010,2011,2012,2013,2014,2015,2016,2017])     
#csv_sorter('lead.csv', 'sorted_data.csv', 9)
#daily_concentrations('sorted_data.csv', 'daily_concentration.csv')
#month_average('sorted_data.csv','monthly_avg.csv')
#three_month_average('monthly_avg.csv','three_month_average.csv')
# monitoring_years=[2010,2017]

# for emissions_year in lead_design_values('three_month_average.csv',1,monitoring_years):
#  print(emissions_year[1])
#Bob Ross


