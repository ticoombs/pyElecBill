# Electricity Cost Calculation

[Homepage](https://gitlab.com/ticoombs/pyElecBill)

I was sick of all the different constraints and calculating my bill

My current provider (AGL) allows me to download a CSV of all my data usage for the last 12 months at 30 minute incrementals.
So using the data for the past 12 months we can calculate our quartly costs and cross check those totals to see if we would actually benefit from moving electricity companies. 

## Current Issues:

- Does not calculate discounts
- Does not do "summer/winter" rates
  - You would need to create two rate plans, for that
- ~~First 11kWh is hard coded~~ - Fixed

## How To:

Before we make a calculation we need to do two things:
1. You need to create a matrix of the rates of the other companies you are trying to compare. See and of the provided `plan_` files for examples. 
2. Format your data to the "Quarter" you want to check. 

### Create your "Plan": 
- Columns are Days of Week, Starting from Monday -> Sunday
- Rows are 1 hour periods, 0:00->0:59 first row, 23:00->23:59 last row

### Format your data:

I used the following two commands to create quartly csv's and then ran it against each plan I was comparing.

```
head -n 1 mydata.csv > mydata_2017_q1.csv
egrep 0[1-3]\/2017 mydata.csv >> mydata_2017_q1.csv
```

## Help

```
usage: elec-parse.py [-h] --data-csv DATA_CSV [--rates-csv RATES_CSV]
                     [--first-kwh-rate FIRST_KWH_RATE]
                     [--next-kwh-rate NEXT_KWH_RATE] [--first-kwh FIRST_KWH]
                     --supply-charge SUPPLY_CHARGE [--debug]

Electriciy CSV parser

optional arguments:
  -h, --help            show this help message and exit
  --data-csv DATA_CSV, -c DATA_CSV
                        CSV Data File
  --rates-csv RATES_CSV, -r RATES_CSV
                        Rates CSV Files
  --first-kwh-rate FIRST_KWH_RATE, -f FIRST_KWH_RATE
                        Starting rate for X kWh
  --next-kwh-rate NEXT_KWH_RATE, -n NEXT_KWH_RATE
                        Rate for after kWh
  --first-kwh FIRST_KWH, -k FIRST_KWH
                        The X kWh variable
  --supply-charge SUPPLY_CHARGE, -s SUPPLY_CHARGE
                        Daily Supply Cost (Cents)
  --debug               Turn on Debugging
```

## Usage Examples


Calculate the quarter cost of the rate "plan_plannyplan.csv"
```
./elec-parse.py --data-csv MyUsageData_2018_Q2.csv --rates-csv plan_plannyplan.csv --supply-charge 135.3
```

Do another calculation with short usage flags
```
./elec-parse.py -c MyUsageData_2018_Q2.csv -r plan_simply_energy.csv -s 124.289
```

Check a "First X kWh = 29.7c | Everything else = 33.33c"
```
./elec-parse.py -c MyUsageData_2018_Q2.csv -f 29.7 -n 33.33 -s 135.3 -k 11
```


