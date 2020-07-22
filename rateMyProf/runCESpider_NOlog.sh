now=`date +"%T"`
scrapy crawl "profCourseExplorer" -o FA2018_`echo $now`.csv -t csv;
