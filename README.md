
# Table of Contents

1.  [About](#org446d0e9)
2.  [Running](#orgbd36c5f)
3.  [Dependencies](#orgf0cd9c9)
4.  [Notes](#org3bd4e6d)


<a id="org446d0e9"></a>

# About

Runs a simple analysis of UK weekly deaths. 
Downloads weekly death statistics for 2010-2020 from the ONS website.
Parses the resulting CSV files.
Scatter-plots the number of deaths in the preceeding week against the day of the year those deaths were announced, for years 2010-2019.
Also overlayed is a line plot of the same data for 2020.
Excess mortality of Covid-19 can then be observed from this.


<a id="orgbd36c5f"></a>

# Running

```bash
./run_analysis.sh
```

Downloads and processes files, and plots the results.


<a id="orgf0cd9c9"></a>

# Dependencies

-   Python3
-   Numpy
-   Matplotlib
-   ssconvert (from Gnumeric), for converting filetypes


<a id="org3bd4e6d"></a>

# Notes

There's many things that could be done equally well in a different way:

-   Pandas for handling data
-   Pure-python file downloading
-   Pure-bash file processing (eg. gnuplot)

