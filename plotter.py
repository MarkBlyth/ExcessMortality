#!/usr/bin/env python3

import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import gpr
import scipy.optimize


ENDPOINTS = True  # If true, discard the end 10 data, to deal with first- and last-week recordings being skewed
SHOW_VARIANCE = False
HYPERPARAMETERS = (
    {
        "l": 3459.6139006548638,
        "sigma_n": 1066055.3516169114,
        "sigma_f": 9813297.42152212,
    }
    if ENDPOINTS
    else {
        "l": 102.91871828628742,
        "sigma_n": 1173116.7613868096,
        "sigma_f": 1912997.585413025,
    }
)
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


class ScaledGPR(gpr.GPR):
    """
    Subclassed Gaussian process regressor. Automatically de-means the
    training data, then re-means the predicted outputs.
    """

    def __init__(self, X_data, y_data, cov):
        self._mean = np.mean(y_data)
        super().__init__(X_data, y_data - self._mean, cov)

    def predict(self, X):
        return super().predict(X) + self._mean


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
    # Load datafiles
    base_filenames, test_filename = get_filenames()
    base_lines = [load_csv_to_list(f) for f in base_filenames]
    base_deaths = []
    for linelist in base_lines:
        base_deaths += get_death_data(linelist)
    base_deaths.sort(key=lambda x: x[0])  # Used to remove endpoints by date
    training_data = (
        np.array(base_deaths)[10:-10].T if ENDPOINTS else np.array(base_deaths).T
    )  # date, counts

    test_lines = load_csv_to_list(test_filename)
    test_deaths = get_death_data(test_lines)
    test_data = np.array(test_deaths).T

    # Optimize a model, if we haven't already
    if HYPERPARAMETERS is None:
        # Estimate measurement noise from the variance of a subset of the data
        sorted_data = np.array(sorted(training_data.T, key=lambda x: x[0]))
        dates = np.logical_and(sorted_data[:, 0] >= 200, sorted_data[:, 0] <= 230)
        middle_data = sorted_data[dates, 1]
        # Define starting hyperparam guess
        noise_standard_deviation = np.std(middle_data)
        l = 100  # Arbitrary uess
        signal_standard_deviation = noise_standard_deviation  # Arbitrary guess

        # Define an objective to minimise
        def badness(pars):
            l, sigma_n, sigma_f = pars
            kernel = gpr.SEKernel(sigma_n ** 2, sigma_f ** 2, l ** 2)
            model = ScaledGPR(training_data[0], training_data[1], kernel)
            print(pars, model.log_likelihood)
            return -model.log_likelihood

        # Minimise it
        ret = scipy.optimize.minimize(
            badness, [l, noise_standard_deviation, signal_standard_deviation]
        )
        l, sigma_n, sigma_f = ret.x
        hyperparams = {"l": l ** 2, "sigma_n": sigma_n ** 2, "sigma_f": sigma_f ** 2}
        print(hyperparams)
    else:
        # Already optimized :)
        hyperparams = HYPERPARAMETERS

    # Build GP regression model
    kernel = gpr.SEKernel(**hyperparams)
    regressor = ScaledGPR(training_data[0], training_data[1], kernel)
    xs = list(range(1, 366))
    gpr_mean = regressor(xs)

    if SHOW_VARIANCE:
        gpr_cov = regressor.get_variance(xs)
        gpr_var = np.diag(gpr_cov)
        confidence_band = 2 * np.sqrt(gpr_var)

    # Plot everything
    fig, ax = plt.subplots()
    if SHOW_VARIANCE:
        ax.fill_between(
            xs,
            gpr_mean - confidence_band,
            gpr_mean + confidence_band,
            label="2\sigma confidence band",
        )
    ax.scatter(training_data[0], training_data[1], label="Weekly mortality rate, 2010-2019")
    ax.plot(xs, gpr_mean, "k", label="GPR mean weekly death rate")
    ax.plot(test_data[0], test_data[1], "r", label="Weekly mortality rate, 2020")
    ax.set_xlabel("Day of year")
    ax.set_ylabel("Number of deaths in preceeding week")
    ax.set_title("UK excess mortality, 2020")
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
