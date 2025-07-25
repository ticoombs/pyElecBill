#!/usr/bin/python

# Electricty CSV Parser and Calculator

import argparse
import csv
import datetime


def rates_calc(_file):
    """
    Takes a csv of the rates on a per day basis and their cost per kWh
    Returns a 2 dimential list of kWh X time period X per day
    """
    with open(_file, 'rt') as ratesfile:
        reader = csv.reader(ratesfile)
        return list(reader)


def data_calc(_file, _filetype="_old", rates="", firstX="", restX="", first_var=""):
    """
    Takes a csv file with "StartDate,EndDate,Usage" where each row is a 30 min interval
    Returns an array of cost per day
    """

    total_cost = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    today = {}
    current = 0

    if _filetype != "_old":
        #Date/Time   0:00    0:30    1:00    1:30    2:00
        #20210927    0.076   0.086   0.076   0.085   0.077
        with open(_file, 'rt') as csvfile:
            dateformat = "%Y%m%d"
            timeformat = "%H:%M"
            reader = csv.DictReader(csvfile)
            for row in reader:
                # each row contains an array of the date and then all usage per-30min period
                date = datetime.datetime.strptime(row['Date/Time'], dateformat)
                day = int(date.weekday())
                month = int(date.month)
                for time, value in row.items():
                    try:
                        data = float(value)
                        hour = int(time.split(':')[0])
                        if args.debug:
                            print(f"Debug: Hour: {hour} - Value: {data}")
                        if rates:
                            total_cost[day] += (float((rates[hour][day])) * data)
                        if firstX:
                            if current != date:
                                current = date
                                today[date] = data
                            today[date] += data
                    except Exception as e:
                        if args.debug:
                            print(f"skipping: {time}-{value}. Err: {e}")

    else:
        #print("New Format")
        with open(_file, 'r') as csvfile:
            stringformat = "%Y-%m-%d %H:%M:%S"
            reader = csv.DictReader(csvfile)
            for row in reader:
                billable_time = datetime.datetime.strptime(f"{row['ReadDate']} {row['ReadTime']}", stringformat)
                # Day of Year
                date = billable_time.strftime('%j')
                # day is the day of the week as an integer, where Monday is 0 and Sunday is 6.
                day = int(billable_time.weekday())
                # time is the Hour
                hour = int(billable_time.hour)
                # end_date = datetime.datetime.strptime(row['EndDate'], stringformat)
                kwh_usage = float(row['ReadConsumption'])
                #print(day, hour, kwh_usage)
                if rates:
                    total_cost[day] += (float((rates[hour][day])) * kwh_usage)
                if firstX:
                    if current != date:
                        current = date
                        today[date] = kwh_usage
                    today[date] += kwh_usage

    if rates:
        if args.debug:
            print(total_cost)
        return total_cost
    if firstX:
        # We have caluclated all usage per day
        for days, value in today.items():
            if float(value) > float(first_var):
                rest = float(value) - float(first_var)
                now_value = float(firstX) * float(first_var) + float(rest) * float(restX)
            else:
                now_value = float(firstX) * float(first_var)
            today[days] = now_value
        return today


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Electriciy CSV parser")
    parser.add_argument("--data-csv", "-c", action="store", required=True, help="CSV Data File")
    parser.add_argument("--rates-csv", "-r", action="store", help="Rates CSV Files")
    parser.add_argument("--first-kwh-rate", "-f", action="store", help="Starting rate for X kWh")
    parser.add_argument("--next-kwh-rate", "-n", action="store", help="Rate for after kWh")
    parser.add_argument("--first-kwh", "-k", action="store", help="The X kWh variable")
    parser.add_argument("--supply-charge", "-s", action="store", required=True, help="Daily Supply Cost (Cents)")
    parser.add_argument("--debug", action="store_true", help="Turn on Debugging")

    args = parser.parse_args()

    # rates_map contains [<time>][date]
    # for 0:00 -> 0:59 on Tuesday it would be [0][1]
    # for 13:00 -> 13:59 on Sunday it would be [13][6]
    if args.rates_csv:
        quarter = 0
        rates_map = rates_calc(args.rates_csv)
        if args.debug:
            print(rates_map)
        for day, value in data_calc(args.data_csv, rates=rates_map).items():
            quarter += (value/100)
            print("Day: {} - Cost: {}".format(day, value/100))
        charge = float(90*float(args.supply_charge)/100)
        print("Quarter Cost: {} + {} = {}".format(quarter, charge, (quarter + charge)))

    elif args.first_kwh:
        day_cost = data_calc(
            args.data_csv,
            firstX=args.first_kwh_rate,
            restX=args.next_kwh_rate,
            first_var=args.first_kwh)
        yearly_cost = 0
        for day, value in day_cost.items():
            yearly_cost += value/100
            yearly_cost += float(args.supply_charge)/100
        print("Quarter Cost: {}".format(yearly_cost))
