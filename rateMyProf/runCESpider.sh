now=`date +"%T"`
scrapy crawl "profCourseExplorer" -o WI2018_`echo $now`.csv -t csv --logfile `echo $now` -L INFO;
