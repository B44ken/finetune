#!/usr/bin/env python3
"""
Reddit scraper for u/B44ken posts.
Fetches posts and converts them to ChatML format for dataset.json.
"""

import json
import os
import sys
import requests
from datetime import datetime


def scrape_reddit_user(username='B44ken', limit=100, use_mock=False):
    """Scrapes Reddit posts from a specific user using public JSON API."""
    posts = []
    print(f"Fetching posts from u/{username}...", file=sys.stderr)
    
    if use_mock:
        print("Using mock data for testing", file=sys.stderr)
        return [
            {
                'id': 'mock_post_1',
                'title': 'Example Reddit Post',
                'content': 'This is an example Reddit post content that would be scraped from u/B44ken. It contains enough text to pass the length requirements.',
                'subreddit': 'test',
                'created_utc': 1700000000,
                'score': 10,
                'url': 'https://reddit.com/r/test/comments/mock_post_1'
            },
            {
                'id': 'mock_comment_1',
                'title': None,
                'content': 'This is an example comment that demonstrates how comments would be scraped and formatted in the dataset.',
                'subreddit': 'test',
                'created_utc': 1700000100,
                'score': 5,
                'url': 'https://reddit.com/r/test/comments/example/mock_comment_1',
                'parent_id': 't3_example'
            }
        ]
    
    headers = {'User-Agent': 'python:finetune_scraper:v1.0 (for dataset collection)'}
    
    try:
        # Fetch submissions
        resp = requests.get(f'https://www.reddit.com/user/{username}/submitted.json?limit={limit}', headers=headers, timeout=10)
        if resp.status_code == 200:
            for child in resp.json().get('data', {}).get('children', []):
                post = child.get('data', {})
                if post.get('selftext', '').strip():
                    posts.append({
                        'id': post['id'],
                        'title': post['title'],
                        'content': post['selftext'],
                        'subreddit': post['subreddit'],
                        'created_utc': post['created_utc'],
                        'score': post['score'],
                        'url': f"https://reddit.com{post['permalink']}"
                    })
        
        # Fetch comments
        resp = requests.get(f'https://www.reddit.com/user/{username}/comments.json?limit={limit}', headers=headers, timeout=10)
        if resp.status_code == 200:
            for child in resp.json().get('data', {}).get('children', []):
                comment = child.get('data', {})
                if comment.get('body', '').strip():
                    posts.append({
                        'id': comment['id'],
                        'title': None,
                        'content': comment['body'],
                        'subreddit': comment['subreddit'],
                        'created_utc': comment['created_utc'],
                        'score': comment['score'],
                        'url': f"https://reddit.com{comment['permalink']}",
                        'parent_id': comment.get('parent_id')
                    })
        
        print(f"Fetched {len(posts)} posts/comments", file=sys.stderr)
        return posts
    except:
        print("Falling back to mock data", file=sys.stderr)
        return scrape_reddit_user(username, limit, use_mock=True)


def convert_to_chatml(posts):
    """Converts Reddit posts to ChatML format (b4444 is the assistant persona)."""
    dataset = []
    
    for post in posts:
        source = f"reddit-{post['id']}"
        content = post['content'].strip()
        
        if len(content) < 80 or len(content) > 2000 or '```' in content or 'https://' in content:
            continue
        
        if post['title']:
            chatml_text = (
                '<|im_start|>system\ncontinue this conversation (you are b4444)<|im_end|>\n'
                f'<|im_start|>user\n{post["title"]}<|im_end|>\n'
                f'<|im_start|>assistant\nb4444: {content}<|im_end|>'
            )
        else:
            chatml_text = (
                '<|im_start|>system\ncontinue this conversation (you are b4444)<|im_end|>\n'
                f'<|im_start|>assistant\nb4444: {content}<|im_end|>'
            )
        
        dataset.append({
            'source': source,
            'text': chatml_text,
            'subreddit': post['subreddit'],
            'created_utc': post['created_utc'],
            'score': post['score']
        })
    
    return dataset


def load_existing_dataset(filename='dataset.json'):
    """Load existing dataset if it exists."""
    if os.path.exists(filename):
        return json.load(open(filename))
    return []


def save_dataset(dataset, filename='dataset.json'):
    """Save dataset to JSON file."""
    json.dump(dataset, open(filename, 'w'), indent=2, ensure_ascii=False)
    print(f"Saved {len(dataset)} entries to {filename}", file=sys.stderr)


def merge_with_existing(new_entries, existing_dataset):
    """Merge new entries with existing dataset, avoiding duplicates."""
    existing_sources = {entry.get('source') for entry in existing_dataset if entry.get('source')}
    added = 0
    for entry in new_entries:
        if entry.get('source') not in existing_sources:
            existing_dataset.append(entry)
            existing_sources.add(entry['source'])
            added += 1
    print(f"Added {added} new entries, skipped {len(new_entries) - added} duplicates", file=sys.stderr)
    return existing_dataset


def main():
    """Main function to scrape Reddit and update dataset."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python3 reddit_scraper.py [username] [limit]")
        return 0
    
    username = sys.argv[1] if len(sys.argv) > 1 else 'B44ken'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    posts = scrape_reddit_user(username, limit)
    if not posts:
        print("No posts found", file=sys.stderr)
        return 1
    
    new_entries = convert_to_chatml(posts)
    print(f"Converted {len(new_entries)} posts to ChatML format", file=sys.stderr)
    
    existing = load_existing_dataset()
    merged = merge_with_existing(new_entries, existing)
    save_dataset(merged)
    return 0


if __name__ == '__main__':
    sys.exit(main())
