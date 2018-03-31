import scrapy 
import json
import os
from datetime import datetime

class H2RSpider(scrapy.Spider):
    name = "h2r"

    start_urls = [
        'https://hentai2read.com/hentai-list'
    ]

    # os.chdir('..')
    # root = os.path.abspath(os.curdir)
    # os.chdir('scrapers')
    # meta_num = len([x for x in os.listdir(root + '/data') if 'meta' in x])
    # file_path = f'{root}/data/meta_{meta_num}.json'

    # with open(file_path, 'w+') as f:
    #     f.write(json.dumps({
    #         "meta": {
    #             "date": str(datetime.now())
    #         }
    #     })a)

    def parse(self, response):
        content = response.css('section.content')   
        for manga in content.css('div.img-container'):
            basic_info = {
                'title': manga.css('h2.rf-title::text').extract_first(),
                'url': manga.css('div.img-overlay a::attr(href)').extract_first(),
                'thumbnail': manga.css('img::attr(data-src)').extract_first()
            }
            yield scrapy.Request(basic_info['url'], callback=self.parse_manga_info, meta={'basic_info': basic_info})
        
        # Next pages
        current_page = response.css('ul.pagination li.active')
        next_page = current_page.xpath('following-sibling::li[1]')
        link = next_page.css('a::attr(href)').extract_first()
        # if '2' not in link:
        link = response.urljoin(link)
        yield scrapy.Request(link, callback=self.parse)

    def parse_manga_info(self, response):
        def parse_alt_titles(alt_titles_selector_list):
            titles = alt_titles_selector_list.extract_first().split(',')
            return titles

        def parse_rating(rating_selector_list):
            rating = rating_selector_list.extract_first()
            index = rating.index('/')
            with_index = rating.index('with')
            votes_index = rating.index('votes')

            num_votes = stoi(rating[with_index+5: votes_index-1])
            score = stoi(rating[index-1])
            return {
                'score': score,
                'votes': num_votes
            }

        # Parse string to int, remove all nonnumeric chars
        def stoi(value):
            output = ''.join(ch for ch in value if ch.isdigit())
            try:
                output = int(output)
            except:
                output = None
            return output

        def extract_value(key, selector_list, multiple_values=False):
            if multiple_values:
                output = []
                query = '//b[text()="' + key + '"]//following-sibling::*'
                siblings = selector_list.xpath(query)
                for sibling in siblings:
                    output.append(sibling.css('a::text').extract_first())
            else:
                query = '//b[text()="' + key + '"]//following-sibling::a[1]//text()'
                output = selector_list.xpath(query)
                output = output.extract_first()
            return output

        info = response.css('div ul.list')
        alt_titles = info.css('li::text')
        rating = response.css('div.push-10-t small::text')
        
        output = {
            'alt_titles': parse_alt_titles(alt_titles),
            'parody': extract_value('Parody', info, True),
            'ranking': stoi(extract_value('Ranking', info)),
            'rating': parse_rating(rating),
            'status': extract_value('Status', info),
            'release_year': stoi(extract_value('Release Year', info)),
            'views': stoi(extract_value('View', info)),
            'author': extract_value('Author', info, True),
            'artist': extract_value('Artist', info, True),
            'category': extract_value('Category', info, True),
            'content': extract_value('Content', info, True),
            'character': extract_value('Character', info, True),
            'language': extract_value('Language', info)
        }
        output = {**response.meta['basic_info'], **output}
        
        yield output