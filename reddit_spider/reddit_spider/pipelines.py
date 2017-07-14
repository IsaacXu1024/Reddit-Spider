# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#import json
from scrapy.exceptions import DropItem

class JsonWriterPipeline(object):
    
    def open_spider(self, spider):
        self.file = open('scraped_content/comments.txt', 'a', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()
        
    def process_item(self, item, spider):
        cleaned_item = filter_reddit_comments(item['div'], item['link'], item['link_text'], filter_set=["[deleted]", "This is an archived post. You won't be able to vote or comment.", "[removed]"])
        if cleaned_item != None:
            line = cleaned_item + "\n"
            #line = json.dumps(item) + "\n"
            self.file.write(line)
            return item
        
        raise DropItem("Item was filtered")

class DuplicatesPipeline(object):

    def open_spider(self, spider):
        self.comments_seen = set()
        load_file_to_set(self.comments_seen, filename='scraped_content/comment_ids_seen.txt')

    def close_spider(self, spider):
        save_set_to_file(self.comments_seen, filename='scraped_content/comment_ids_seen.txt')
        
    def process_item(self, item, spider):
        if item['id'] in self.comments_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.comments_seen.add(item['id'])
            return item

"""
Filter Functions
"""    

def find_tags(p_text, tags):
    length = len(tags)
    for i, v in enumerate(p_text):
        if v == tags[0] and p_text[i:i+length] == tags:
            yield i, i+length
            
def replace_tags(p_text, tag, replacement_tag=[]):
    tags = find_tags(p_text, tag)
    for start, end in tags:
        p_text[start:end] = replacement_tag

def find_link(p_text):
    in_link = False
    if p_text[0:8] == list('<a href='):
        in_link = True
        link_start_idx = 0        
    for i in range(len(p_text)):
        if p_text[i-8:i+1] == list(' <a href=') or p_text[i-8:i+1] == ['\n', '<', 'a', ' ', 'h', 'r', 'e', 'f', '=']:
            in_link = True
            link_start_idx = i-7
        if p_text[i-3:i+1] == list('</a>') and in_link == True:
            link_end_idx = i + 1
            return link_start_idx, link_end_idx
            
def replace_links(p_text, link_text_list):
    n_links = len(link_text_list)
    for i in range(n_links):
        try:
            start, end = find_link(p_text)
        except:
            pass
        p_text[start:end] = link_text_list[i]

def not_in_filter_set(clean_text, filter_set=[]):
    filtered_set = set()
    for f in filter_set:
        filtered_set.add(f)
    return clean_text not in filtered_set    
    
def filter_reddit_comments(p_text, linkl, link_list, remove_text_list=['\u00bb ', '\n', '\n'], tag_filter=['p', 'strong', 'br', 'div', 'div class="md"', 'em', 'blockquote', 'ul', 'li', 'ol', 'sup'], filter_set=[], n_double_space_fix=3):
    p_text_list = list(p_text)
    link_text_list = []
    tag_list = []
    has_links = True
    
    if linkl != [] and link_list == []:
        for i in range(len(linkl)):
            link_list.append(str(linkl[i]))
            
    if linkl == [] and link_list == []:
        has_links = False
            
    for link_text in link_list:
        text_list = list(link_text)
        link_text_list.append(text_list)
    
    for remove_text in remove_text_list:
        tag_list.append(list(remove_text))
        
    for tag in tag_filter:
        header, footer = list('<'+tag+'>'), list('</'+tag+'>')
        tag_list.append(header)
        tag_list.append(footer)
        
    for tag in tag_list:
        replace_tags(p_text_list, tag, replacement_tag=list(' '))
    
    for i in range(n_double_space_fix):
        replace_tags(p_text_list, list('  '), list(' '))
    
    # Fix some commas
    replace_tags(p_text_list, list(' ,'), list(','))
    
    # Fix some periods
    replace_tags(p_text_list, list(' .'), list('.'))
    
    if has_links:    
        replace_links(p_text_list, link_text_list)
    
    while p_text_list[0] == ' ':
        p_text_list.pop(0)
        
    while p_text_list[-1] == ' ':    
        p_text_list.pop(-1)
        
    cleaned_p_text = ''.join(p_text_list)
    
    # Filters out subreddit headings
    if cleaned_p_text[:1] == '<':
        return None
    
    if not_in_filter_set(cleaned_p_text, filter_set):
        return cleaned_p_text    

"""
File/set loading functions, copied over from comment_spider.py
"""

def load_file_to_set(s, filename):
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
        
def save_set_to_file(s, filename):
    f = open(filename, 'w', encoding='utf-8')    
    for line in s:
        write_line = line+'\n'
        f.write(write_line)
    f.close()
    