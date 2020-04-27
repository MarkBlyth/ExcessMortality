#!/usr/bin/env python3

import matplotlib.pyplot as plt
import datetime as dt
import numpy as np

DATE_HEADER = "Week ended"
COUNTS_HEADER = "Total deaths, all ages"
MONTHS = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]


def date_to_day_of_year(date_str):
    if "/" in date_str:
        year, month, day = (int(x) for x in date_str.split("/"))
    else:
        daystr, monthstr, yearstr = date_str.split("-")
        day = int(daystr)
        year = int(yearstr)
        year = year + 2000 if year < 2000 else year
        # TODO replace this with a nice timedate formatter
        for i in range(12):
            if monthstr.upper() in MONTHS[i]:
                month = i + 1
                break
    return (dt.date(year, month, day) - dt.date(year, 1, 1)).days + 1


def load_csv_to_list(filename):
    with open(filename, "r") as infile:
        lines = infile.read().splitlines()
    return lines


def extract_fields_from_list(data_list, fields_list):
    ret_dict = {}
    for row in data_list:
        fields_in_this_row = [
            field for field in fields_list if field in row[:30]
        ]  #:30 because headers sometimes get mentioned twice
        if len(fields_in_this_row) > 0:
            ret_dict = {**ret_dict, **{field: row for field in fields_in_this_row}}
    return ret_dict


def get_death_data(lines_list, date_header=DATE_HEADER, counts_header=COUNTS_HEADER):
    fields_dict = extract_fields_from_list(lines_list, [date_header, counts_header])
    raw_dates = fields_dict[date_header].split(",")[1:]
    date_numbers = [date_to_day_of_year(x) for x in raw_dates if x != ""]
    raw_counts = fields_dict[counts_header].split(",")[2:]
    count_numbers = [int(x) for x in raw_counts if x != ""]
    return [
        [date_numbers[i], count_numbers[i]] for i in range(len(count_numbers))
    ]  # zip


def get_filenames():
    # Hard-coded, since this script is only intended to be used by the
    # same .sh script that downloaded and named the files in the first
    # place
    base_data = [str(yr) + ".csv" for yr in range(2010, 2020)]
    test_data = "2020.csv"
    return base_data, test_data


def main():
    base_filenames, test_filename = get_filenames()
    base_lines = [load_csv_to_list(f) for f in base_filenames]
    base_deaths = []
    for linelist in base_lines:
        base_deaths += get_death_data(linelist)
    training_data = np.array(base_deaths).T  # date, counts

    test_lines = load_csv_to_list(test_filename)
    test_deaths = get_death_data(test_lines)
    test_data = np.array(test_deaths).T

    fig, ax = plt.subplots()
    ax.scatter(training_data[0], training_data[1], label="2010-2019")
    ax.plot(test_data[0], test_data[1], "r", label="2020")
    ax.x_label("Day of year")
    ax.y_label("Number of deaths in preceeding week")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
