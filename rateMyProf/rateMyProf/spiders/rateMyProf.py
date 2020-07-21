import scrapy
import json
import base64
from scrapy_splash import SplashRequest

class rateMyProfSpider(scrapy.Spider):
    name = "rateMyProf"
    
    prof_name = ["Fleck", "Woodley"]
    start_urls = ['https://www.ratemyprofessors.com/search.jsp?query={name}'] 

    def start_requests(self):
        splash_args = {
            'wait': 2,
            'html': 1,
            'png': 1,
            'width': 600,
            'render_all': 1
        }
        for prof in self.prof_name:
            url = self.start_urls[0].format(name = prof)
            yield SplashRequest(
                url,
                self.parse,
                endpoint = 'render.json',
                args = splash_args
            )
   
    n = 0
    linkPerTxt = 100
    pngName = "screen_shot_{cnt}.png"
    htmlName = "rp_{cnt}.html"
    linkTxt = "linkProf_{cnt}.txt"

    school_name_match = "University Of Illinois at Urbana - Champaign"
    school_name_path = ".//span[@class='sub']/text()"

    link_arr = []
    def parse(self, response):
        self.logger.info("start parsing ===========================")
        prof_list = response.xpath("//li[@class='listing PROFESSOR']")
        curr_list = []

        if len(prof_list) != 0:
            for idx, prof in enumerate(prof_list):
                school_name = prof.xpath(self.school_name_path).extract()[0]
                self.logger.info(school_name)
                        #care 2 prof with same last name in uiuc
                if school_name == None: 
                    continue
                if self.school_name_match in school_name: 
                    self.logger.info("FOUND <+++++++++++++++++++++")
                    curr_list.append(idx)

            target_idx = 0
            if (len(curr_list) == 0):
                self.logger.debug("No info found on RateMyProf <++++++++++++")
            elif (len(curr_list) > 1):
                self.logger.debug("Found more than 1")
                target_idx = curr_list[0] #TODO for now
            else:
                target_idx = curr_list[0]

            link = prof_list[target_idx].xpath(".//a/@href").extract()[0]
            self.logger.info(link); 
            self.link_arr.append(link)
            self.logger.info("end parsing =============================")
            self.n += 1
            if(self.n == len(self.start_urls) or self.n == self.linkPerTxt):
                self.write_to_linkTxt();
        else:
            self.logger.debug(start_urls[0])
            self.logger.debug("No info found on RateMyProf <++++++++++++")

    def write_to_linkTxt(self):
        linkFile = open(self.linkTxt.format(cnt = str(self.n % self.linkPerTxt)), 'a')
        lowerBound = (self.n - 100) 
        if (lowerBound < 0):
            lowerBound = 0
        for l in range(lowerBound, self.n):
            link = "https://www.ratemyprofessors.com{detail}\n"
            linkFile.write(link.format(detail = self.link_arr[l]))
        linkFile.close()


    def get_screen_shot(self, response): # make sure endpoint = 'render.json'
        png_byte = base64.b64decode(response.data['png'])

        with open(self.pngName.format(cnt = str(self.n)), 'wb') as f:
            f.write(png_byte)

