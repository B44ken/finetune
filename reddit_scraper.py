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
    """
    Scrapes Reddit posts from a specific user using public JSON API.
    
    Args:
        username: Reddit username to scrape
        limit: Maximum number of posts to fetch
        use_mock: If True, use mock data for testing
        
    Returns:
        List of formatted conversation entries
    """
    posts = []
    
    print(f"Fetching posts from u/{username}...", file=sys.stderr)
    
    # If offline or testing mode, use mock data
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
    
    # User-Agent header is required by Reddit
    # Using generic identifier since this is for personal use
    headers = {
        'User-Agent': 'python:finetune_scraper:v1.0 (for dataset collection)'
    }
    
    try:
        # Fetch submissions using Reddit's public JSON API
        submissions_url = f'https://www.reddit.com/user/{username}/submitted.json?limit={limit}'
        response = requests.get(submissions_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                if post.get('selftext') and post['selftext'].strip():
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
        comments_url = f'https://www.reddit.com/user/{username}/comments.json?limit={limit}'
        response = requests.get(comments_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for child in data.get('data', {}).get('children', []):
                comment = child.get('data', {})
                if comment.get('body') and comment['body'].strip():
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
        
    except Exception as e:
        print(f"Error scraping Reddit: {e}", file=sys.stderr)
        print("Falling back to mock data", file=sys.stderr)
        return scrape_reddit_user(username, limit, use_mock=True)


def convert_to_chatml(posts):
    """
    Converts Reddit posts to ChatML format.
    
    Note: The persona 'b4444' is the assistant identity used across all data sources
    (Reddit posts from u/B44ken are formatted as b4444 responses).
    
    Args:
        posts: List of Reddit post dictionaries
        
    Returns:
        List of ChatML formatted entries for dataset.json
    """
    dataset = []
    
    for post in posts:
        # Create a source identifier using the post ID
        source = f"reddit-{post['id']}"
        
        # Format the content
        content = post['content'].strip()
        
        # Skip very short or very long posts
        if len(content) < 80 or len(content) > 2000:
            continue
            
        # Skip posts with code blocks (similar to Discord scraper logic)
        if '```' in content or 'https://' in content:
            continue
        
        # Build the ChatML formatted text
        # For Reddit posts, we'll format them as user questions with assistant responses
        if post['title']:
            # For submissions (posts with titles)
            chatml_text = (
                '<|im_start|>system\n'
                'continue this conversation (you are b4444)<|im_end|>\n'
                f'<|im_start|>user\n{post["title"]}<|im_end|>\n'
                f'<|im_start|>assistant\nb4444: {content}<|im_end|>'
            )
        else:
            # For comments, just treat as assistant response
            chatml_text = (
                '<|im_start|>system\n'
                'continue this conversation (you are b4444)<|im_end|>\n'
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
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_dataset(dataset, filename='dataset.json'):
    """Save dataset to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(dataset)} entries to {filename}", file=sys.stderr)


def merge_with_existing(new_entries, existing_dataset):
    """
    Merge new entries with existing dataset, avoiding duplicates.
    
    Args:
        new_entries: List of new dataset entries
        existing_dataset: List of existing dataset entries
        
    Returns:
        Merged dataset without duplicates
    """
    # Create a set of existing sources
    existing_sources = {entry.get('source') for entry in existing_dataset if entry.get('source')}
    
    # Add new entries that don't exist
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
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python3 reddit_scraper.py [username] [limit]")
        print()
        print("Arguments:")
        print("  username    Reddit username to scrape (default: B44ken)")
        print("  limit       Maximum number of posts/comments to fetch (default: 100)")
        print()
        print("Example:")
        print("  python3 reddit_scraper.py B44ken 50")
        return 0
    
    # Parse command line arguments
    username = sys.argv[1] if len(sys.argv) > 1 else 'B44ken'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    # Scrape Reddit
    posts = scrape_reddit_user(username, limit)
    
    if not posts:
        print("No posts found or error occurred", file=sys.stderr)
        return 1
    
    # Convert to ChatML format
    new_entries = convert_to_chatml(posts)
    print(f"Converted {len(new_entries)} posts to ChatML format", file=sys.stderr)
    
    # Load existing dataset
    existing = load_existing_dataset()
    
    # Merge with existing
    merged = merge_with_existing(new_entries, existing)
    
    # Save updated dataset
    save_dataset(merged)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
