#!/bin/bash

BASE="https://www.ons.gov.uk/file?uri=%2fpeoplepopulationandcommunity%2fbirthsdeathsandmarriages%2fdeaths%2fdatasets%2fweeklyprovisionalfiguresondeathsregisteredinenglandandwales%2f"

declare -a arr=("2010/publishedweek2010.xls"
                "2011/publishedweek2011.xls"
                "2012/publishedweek2012.xls"
                "2013/publishedweek2013.xls"
                "2014/publishedweek2014.xls"
                "2015/publishedweek2015.xls"
                "2016/publishedweek522016.xls"
                "2017/publishedweek522017.xls"
                "2018/publishedweek522018withupdatedrespiratoryrow.xls"
                "2019/publishedweek522019.xls"
                "2020/publishedweek152020corrected.xlsx"
            )


for i in "${arr[@]}"
do
    ADDR="$BASE$i"
    NAME="${i[@]:5}"

    OUTFILE="${i[@]:0:4}.csv"

    echo "$ADDR"

    wget "$ADDR" -O "$NAME"
    ssconvert "$NAME" "$OUTFILE" -S
    if [ $OUTFILE = "2020.csv" ];then
        mv "$OUTFILE.4" "$OUTFILE"
    else
        mv "$OUTFILE.3" "$OUTFILE"
    fi
done
rm *xls *xlsx *0 *1 *2 *3 *4 *5 *6 *7 *8 *9 *10

python3 plotter.py
