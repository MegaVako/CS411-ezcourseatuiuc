now=`date +"%T"`
semester="FA2020"
scrapy crawl "profCourseExplorer" -o `echo $semester`_`echo $now`.csv -t csv 2>&1 | tee crawl_$now.log;
