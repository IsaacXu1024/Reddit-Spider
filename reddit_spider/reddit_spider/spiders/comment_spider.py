# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 17:23:23 2017

@author: Sunrise
"""
import scrapy

class CommentSpider(scrapy.Spider):    
    name = "comments"
    with open('start_info/start_urls.txt', 'r', encoding='utf-8') as f:        
        start_urls = []
        f_list = f.readlines()
        length = len(f_list)
        for i, line in enumerate(f_list, 1):
            if i != length:
                url = line[:-1]
            else:
                url = line
            start_urls.append(url)        
    allowed_domains = ['reddit.com']
    
    def __init__(self):
        self.max_urls_to_visit = 10000
        # Number of unique urls content was extracted from (not number of pages visited)
        self.n_visited_urls = 0
        self.visited_urls = set()
        with open('start_info/subreddits.txt', 'r', encoding='utf-8') as f: 
            self.subreddit_list = f.readlines()  
        load_file_to_set(self.visited_urls, filename='scraped_content/visited_url_file.txt')
        
    def parse(self, response):        
        # Reached max_urls_to_visit_condition
        if self.n_visited_urls >= self.max_urls_to_visit:
            raise scrapy.exceptions.CloseSpider('finished, max count of {} reached, {} pages visited'.format(self.max_urls_to_visit, self.n_visited_urls))
        
        # Checks if current page is a comments page if so, increment visited urls and add url to visited list
        comment_url = check_url_for_text(response.url, '/comments/')
        if comment_url:
            self.n_visited_urls += 1
            self.visited_urls.add(response.url)
        #else:
            #self.last_page_url = response.url
            
        # Reached max_urls_to_visit_condition
        if self.n_visited_urls >= self.max_urls_to_visit:
            raise scrapy.exceptions.CloseSpider('finished, max count of {} reached, {} pages visited'.format(self.max_urls_to_visit, self.n_visited_urls))
        
        # For every div class=md text on page, send it to pipelines to clean and save
        current_url = response.url
        for div in response.css("div.md"):
            # Creates a unique id for every comment based on comment and the url it was found in  
            div_p_text = div.css("div.md p::text").extract()
            p_text_list = list(''.join(div_p_text))
            cleaned_p_text = ''.join(list(filter(('\n').__ne__, p_text_list)))
            comment_id = current_url+' '+cleaned_p_text
            yield {
                    "id" : comment_id,
                    "div": div.extract(),
                   "link": div.css("a::attr(href)").extract(),
                   "link_text": div.css("a::text").extract()
                   }
        
        base_links = response.css("li.first")
        next_button_link = response.css("span.next-button")
        if next_button_link != []:
            base_links.append(next_button_link)
        for a in base_links:
            page_link = a.css("a::attr(href)")
            link_purpose = a.css("a::attr(data-event-action)").extract_first()
            link_rel = a.css("a::attr(rel)").extract_first()
            potential_url = page_link.extract_first()
            follow_link = url_matches_conditions(potential_url, link_purpose, link_rel, self.subreddit_list, self.visited_urls)
            if follow_link:
                yield response.follow(page_link[0], self.parse)

    def closed(self, reason):
        save_set_to_file(self.visited_urls, filename='scraped_content/visited_url_file.txt')
        #with open('../start_urls/start_urls.txt', 'w', encoding='utf-8') as f:
            #f.write(self.last_page_url)
                
"""
Saving visited_url functions and seen comments
"""

def load_file_to_set(s, filename='visited_url_file.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            f_lines = f.readlines()
            for line in f_lines:
                line_list = list(line)
                if line_list[-1] == '\n':
                    line_list.pop(-1)
                    line = ''.join(line_list)
                if line not in s:
                    s.add(line)
    
    except:
        url_file = open(filename, 'w', encoding='utf-8')
        url_file.close()
        
def save_set_to_file(s, filename='visited_url_file.txt'):
    f = open(filename, 'w', encoding='utf-8')    
    for line in s:
        write_line = line+'\n'
        f.write(write_line)
    f.close()
    
"""
Url filter functions
"""
    
def check_url_for_text(url, text):
    url_list = list(url)
    text_list = list(text)
    length = len(text_list)
    in_url_list = False
    for i, v in enumerate(url_list):
        if v == text_list[0] and url_list[i:i+length] == text_list:
            in_url_list = True
    return in_url_list

def check_if_sub(url, subreddit_list):
    link_in_sub = False
    for subreddit in subreddit_list:
        if check_url_for_text(url, '/'+subreddit+'/'):
            link_in_sub = True
    return link_in_sub    

def url_matches_conditions(url, url_purpose, url_rel, subreddit_list, visited_list):
    
    in_relevant_sub = check_if_sub(url, subreddit_list)
    is_unvisited = url not in visited_list
    is_comments_or_next_page = False
    
    if url_purpose == "comments" or url_rel == "nofollow next":
        is_comments_or_next_page = True
    
    if in_relevant_sub and is_comments_or_next_page and is_unvisited:
        return True
    
    return False
    
    