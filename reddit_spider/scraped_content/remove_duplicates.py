# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 13:14:40 2017

@author: Sunrise
"""

unique_comments_set = set()
with open("comments.txt", 'r', encoding='utf-8') as f:
    comment_list = f.readlines()
    for comment in comment_list:
        unique_comments_set.add(comment)

unique_comments_list = list(unique_comments_set)

with open("unique_comments.txt", 'w', encoding='utf-8') as f:
    for comment in unique_comments_list:
        f.write(comment)