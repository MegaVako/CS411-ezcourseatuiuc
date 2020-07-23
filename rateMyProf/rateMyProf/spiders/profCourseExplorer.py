import scrapy
import time
from rateMyProf.items import RatemyprofItem
from scrapy.spiders import XMLFeedSpider

class profCourseExplorer(XMLFeedSpider):
    name = "profCourseExplorer"
    allowed_domains = ["courses.illinois.edu"]
    year = str(2019)
    semester = "spring"
    base_url = "http://courses.illinois.edu/cisapp/explorer/schedule/{year}/{semester}.xml"
    url = base_url.format(year = year, semester = semester)

    start_urls = [url]
    itertag = 'subject'
        
    def parse_node(self, response, node):
        subjName = node.xpath(".//@id").get()
        link = node.xpath(".//@href").get()
        self.logger.debug(subjName)
        self.logger.debug(link)
        yield scrapy.Request(link, callback = self.parse_subj, meta={'subject_name': subjName})

    def parse_subj(self, response):
        for course in response.xpath("//course[@id]"):
            courseNum = course.xpath(".//@id").get()
            courseLink = course.xpath(".//@href").get()
            courseTittle = course.xpath(".//text()").get()

            self.logger.debug(courseNum)
            self.logger.debug(courseTittle)
            self.logger.debug(courseLink)
            yield scrapy.Request(courseLink, callback = self.parse_course, 
                meta={'course_dept': response.meta.get('subject_name'),
                    'course_num': courseNum,
                    'course_tittle': courseTittle}
            )
        
    def parse_course(self, response):
        # parse gened
        course_gened = response.xpath('//category[@id]//@id').getall() # <-- TODO fix
        course_gened_str = ''
        if len(course_gened) != 0:
            self.logger.debug("FOUND gened<++++++++++++++++++++++++++++++++++++")
            for num, gened in enumerate(course_gened):
                course_gened_str += gened
                if (num + 1) < len(course_gened):
                    course_gened_str += ', '

        # parse section
        for section in response.xpath("//section[@id]"):
            crn = section.xpath(".//@id").get()
            section_link = section.xpath(".//@href").get()
            description = response.xpath('.//description/text()').get()
            course_sec_info = response.xpath('.//courseSectionInformation/text()').get()
            credit_hour_str = response.xpath('.//creditHours/text()').get()
            credit_hour = int(credit_hour_str[0]) # <--
            
            self.logger.debug(str(crn))

            yield scrapy.Request(section_link, callback = self.parse_section, 
                meta={'course_dept': response.meta.get('course_dept'),
                        'course_num': response.meta.get('course_num'),
                        'crn' : crn, 
                        'description': description,
                        'credit_hour': credit_hour,
                        'course_sec_info': course_sec_info,
                        'course_tittle': response.meta.get('course_tittle'),
                        'course_gened': course_gened_str
                        }
            )

    def parse_section(self, response):
        section_type = response.xpath("//type[@code]/text()").get()
        if (section_type == None):
            self.logger.debug("NO TYPE FOUND!!!!!++++++++++++++++++++++++++++")
        
        #elif ('Lecture' in section_type):
        else:
            item = RatemyprofItem()

            for prof in response.xpath('.//instructor'):
                item['prof_fname'] = prof.xpath('.//@firstName').get()
                item['prof_lname'] = prof.xpath('.//@lastName').get()
                item['section_info'] = response.meta.get('course_sec_info')
                item['section_num'] = response.xpath('//sectionNumber/text()').get()
                item['section_type'] = section_type;

                item['course_name'] = response.meta.get('course_tittle')
                item['course_dept'] = response.meta.get('course_dept')
                item['course_num'] = response.meta.get('course_num')
                item['crn'] = response.meta.get('crn')
                item['course_semester'] = self.semester
                item['course_year'] = self.year
                item['course_description'] = response.meta.get('description')
                item['course_gened'] = response.meta.get('course_gened')
                item['course_credit_hour'] = response.meta.get('credit_hour')
                item['course_explorer_link'] = response.request.url

                item['course_hour_start'] = response.xpath("//start/text()").get()
                item['course_hour_end'] = response.xpath("//end/text()").get()
                item['course_date_start'] = response.xpath("//startDate/text()").get()
                item['course_date_end'] = response.xpath("//endDate/text()").get()
                item['course_location'] = response.xpath("//buildingName/text()").get()
                item['course_room_num'] = response.xpath("//roomNumber/text()").get()
                item['course_term'] = response.xpath("//partOfTerm/text()").get()

                yield item
        #else:
            #self.logger.debug("NOT A LEC")
            #self.logger.debug(section_type)
        pass
