# -*- coding: utf-8 -*-
"""
Created on Sat Jul  8 16:55:10 2017

@author: Sunrise
"""
def start_generation():
    with open('subreddits.txt', 'r', encoding='utf-8') as f:        
        subreddit_list = f.readlines()
    start_urls = generate_reddit_start_urls(subreddit_list)
    generate_start_urls_file(start_urls)

def generate_reddit_start_urls(subreddit_list):
    start_urls = []
    for subreddit in subreddit_list:
        base_url = "https://www.reddit.com/r/" + subreddit+"/"
        top = base_url + "top/"
        top_today = top + "?sort=top&t=day"
        top_week = top + "?sort=top&t=week"
        top_month = top + "?sort=top&t=month"
        top_year = top + "?sort=top&t=year"
        top_all = top + "?sort=top&t=all"
        start_urls.append(base_url)
        start_urls.append(top_today)
        start_urls.append(top_week)
        start_urls.append(top_month)
        start_urls.append(top_year)
        start_urls.append(top_all)
    return start_urls

def generate_start_urls_file(start_urls_list):
    length = len(start_urls_list)
    with open('start_urls.txt', 'w', encoding='utf-8') as f:
        for i, line in enumerate(start_urls_list, 1):
            write_line = line+'\n'
            if i == length:
                write_line = line
            f.write(write_line)