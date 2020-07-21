# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RatemyprofItem(scrapy.Item):
    # define the fields for your item here like:
    prof_fname = scrapy.Field()
    prof_lname = scrapy.Field()
    section_info = scrapy.Field()
    section_num = scrapy.Field()
    section_type = scrapy.Field()

    course_name = scrapy.Field()
    course_dept = scrapy.Field()
    course_num = scrapy.Field()
    crn = scrapy.Field()
    course_semester = scrapy.Field()
    course_year = scrapy.Field()
    course_description = scrapy.Field()
    course_gened = scrapy.Field()
    course_credit_hour = scrapy.Field()
    course_explorer_link = scrapy.Field()

    course_hour_start = scrapy.Field()
    course_hour_end = scrapy.Field()
    course_date_start = scrapy.Field()
    course_date_end = scrapy.Field()
    course_location = scrapy.Field()
    course_room_num = scrapy.Field()
    course_term = scrapy.Field()


    # rmp_link = scrapy.Field() # rmp for rate my prof <-- no longer using
    # rmp does not allow crawling

    pass

class courseItem(scrapy.Item):
    pass
