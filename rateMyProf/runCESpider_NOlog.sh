now=`date +"%T"`
scrapy crawl "profCourseExplorer" -o FA2019_`echo $now`.csv -t csv;
