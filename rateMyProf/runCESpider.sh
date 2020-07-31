now=`date +"%T"`
semester="FA2018"
scrapy crawl "profCourseExplorer" -o `echo $semester`_`echo $now`.csv -t csv 2>&1 | tee crawl_$now.log;
