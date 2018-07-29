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
    with open(_file, 'rb') as ratesfile:
        reader = csv.reader(ratesfile)
        return list(reader)


def data_calc(_file, rates="", firstX="", restX="", first_var=""):
    """
    Takes a csv file with "StartDate,EndDate,Usage" where each row is a 30 min interval
    Returns an array of cost per day
    """

    total_cost = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    today = {}
    current = 0

    with open(_file, 'rb') as csvfile:
        stringformat = "%d/%m/%Y %I:%M:%S %p"
        reader = csv.DictReader(csvfile)
        for row in reader:
            billable_time = datetime.datetime.strptime(row['StartDate'], stringformat)
            # Day of Year
            date = billable_time.strftime('%j')
            # day is the day of the week as an integer, where Monday is 0 and Sunday is 6.
            day = int(billable_time.weekday())
            # time is the Hour
            hour = int(billable_time.hour)
            # end_date = datetime.datetime.strptime(row['EndDate'], stringformat)
            kwh_usage = float(row['ProfileReadValue'])
            # print(day, time, kwh_usage)
            if rates:
                total_cost[day] += (float((rates[hour][day])) * kwh_usage)
            if firstX:
                if current != date:
                    current = date
                    today[date] = kwh_usage
                today[date] += kwh_usage
    if rates:
        return total_cost
    if firstX:
        # We have caluclated all usage per day
        for days, value in today.iteritems():
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
        for day, value in data_calc(args.data_csv, rates_map).items():
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
        for day, value in day_cost.iteritems():
            yearly_cost += value/100
            yearly_cost += float(args.supply_charge)/100
        print("Yearly Cost: {}".format(yearly_cost))
