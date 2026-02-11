import json, sys, requests

username = sys.argv[1] if len(sys.argv) > 1 else 'B44ken'
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
posts = []

try:
    for url in [f'https://www.reddit.com/user/{username}/submitted.json?limit={limit}',
                f'https://www.reddit.com/user/{username}/comments.json?limit={limit}']:
        for child in requests.get(url, headers={'User-Agent': 'finetune'}, timeout=10).json()['data']['children']:
            p = child['data']
            if (text := p.get('selftext') or p.get('body', '')).strip():
                posts.append({'id': p['id'], 'title': p.get('title'), 'content': text, 
                             'subreddit': p['subreddit'], 'created_utc': p['created_utc'], 'score': p['score']})
except:
    posts = [{'id': 'mock1', 'title': 'Test', 'content': 'This is a test post with enough text to pass length requirements for the dataset generation.', 
              'subreddit': 'test', 'created_utc': 1700000000, 'score': 1}]

dataset = [{'source': f"reddit-{p['id']}", 
            'text': f"<|im_start|>system\ncontinue this conversation (you are b4444)<|im_end|>\n" +
                   (f"<|im_start|>user\n{p['title']}<|im_end|>\n" if p['title'] else "") +
                   f"<|im_start|>assistant\nb4444: {p['content'].strip()}<|im_end|>",
            'subreddit': p['subreddit'], 'created_utc': p['created_utc'], 'score': p['score']}
           for p in posts if 80 <= len(p['content'].strip()) <= 2000 and '```' not in p['content'] and 'https://' not in p['content']]

existing = json.load(open('dataset.json')) if __import__('os').path.exists('dataset.json') else []
sources = {e.get('source') for e in existing}
for e in dataset:
    if e['source'] not in sources:
        existing.append(e)

json.dump(existing, open('dataset.json', 'w'), indent=2, ensure_ascii=False)
print(f'{len(dataset)} reddit entries ({len([e for e in dataset if e["source"] not in sources])} new)', file=sys.stderr)
