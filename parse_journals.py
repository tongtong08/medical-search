# -*- coding: utf-8 -*-
"""
解析NLM期刊列表文件，生成JSON供网页使用
"""
import json
import re

def parse_journals_nlm(filepath):
    """解析NLM期刊列表文件"""
    journals = []
    current = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('---'):
                if current.get('title') and (current.get('issn_print') or current.get('issn_online')):
                    # 选择有效的ISSN
                    issn = current.get('issn_print') or current.get('issn_online')
                    if issn:
                        journals.append({
                            'title': current['title'],
                            'issn': issn,
                            'abbr': current.get('abbr', '')
                        })
                current = {}
            elif line.startswith('JournalTitle:'):
                current['title'] = line[len('JournalTitle:'):].strip()
            elif line.startswith('MedAbbr:'):
                current['abbr'] = line[len('MedAbbr:'):].strip()
            elif line.startswith('ISSN (Print):'):
                issn = line[len('ISSN (Print):'):].strip()
                if issn and re.match(r'^\d{4}-\d{3}[\dXx]$', issn):
                    current['issn_print'] = issn
            elif line.startswith('ISSN (Online):'):
                issn = line[len('ISSN (Online):'):].strip()
                if issn and re.match(r'^\d{4}-\d{3}[\dXx]$', issn):
                    current['issn_online'] = issn
    
    # 添加最后一个
    if current.get('title') and (current.get('issn_print') or current.get('issn_online')):
        issn = current.get('issn_print') or current.get('issn_online')
        if issn:
            journals.append({
                'title': current['title'],
                'issn': issn,
                'abbr': current.get('abbr', '')
            })
    
    return journals

if __name__ == '__main__':
    journals = parse_journals_nlm('journals_nlm.txt')
    print(f"解析到 {len(journals)} 个有效期刊")
    
    # 保存为JSON
    with open('journals.json', 'w', encoding='utf-8') as f:
        json.dump(journals, f, ensure_ascii=False, indent=2)
    
    print("已保存到 journals.json")
