import json
import glob
import sys
import os
from datetime import datetime
import hashlib
all_convos = []


def generate_discord_id(convo):
    """Generate a unique ID for a Discord conversation based on content."""
    # Create a hash of the conversation content for a unique identifier
    # Using SHA256 and 16 chars for better collision resistance
    content = ''.join([f"{m['name']}:{m['content']}" for m in convo])
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def attempt_add(convo, final_len_min=80, final_len_max=2000, min_msgs=2, max_msgs=4):
    for msg in convo:
        if '```' in msg['content']:
            return
        msg['content'] = msg['content'].strip()
    while convo and convo[-1]['name'] != 'b4444':
        convo = convo[:-1]
    if not convo or convo[-1]['name'] != 'b4444' or not final_len_min <= len(convo[-1]['content']) <= final_len_max or 'https://' in convo[-1]['content'] or len(convo) < min_msgs:
        return
    all_convos.append(convo[-max_msgs:])


for filename in glob.glob('*-*.json'):
    # Skip known non-Discord files
    if filename in ['package-lock.json']:
        continue
    
    try:
        data = json.load(open(filename))
        if 'messages' not in data:
            continue
        messages = data['messages']
    except (json.JSONDecodeError, KeyError):
        continue
    
    conv = []
    last_time = None

    for msg in messages:
        cnt = msg['content'].strip()
        time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))

        if last_time and (time - last_time).total_seconds() > 3600:
            attempt_add(conv)
            conv = []

        if conv and msg['author']['name'] == conv[-1]['name']:
            conv[-1]['content'] += '\n' + cnt
        else:
            conv.append({'name': msg['author']['name'], 'content': cnt})
        last_time = time

    attempt_add(conv)

out_type = sys.argv[sys.argv.index('-t') + 1] if '-t' in sys.argv else 'stats'
if out_type == 'plain':
    for conv in all_convos:
        print(*[f'\n{m["name"]}: {m["content"]}' for m in conv], '\n--')
    print(f'(total: {len(all_convos)})')
elif out_type == 'llm':
    out = [{'text': '<|im_start|>system\ncontinue this discord conversation (you are b4444)<|im_end|>' + '\n'.join([
            f'\n<|im_start|>{'assistant' if m['name'] == 'b4444' else 'user'}\n{m["name"]}: {m["content"]}<|im_end|>' for m in conv
            ])} for conv in all_convos]
    print(json.dumps(out, indent=2, ensure_ascii=False))
elif out_type == 'dataset':
    # New mode: output to dataset.json with source tracking
    out = []
    for conv in all_convos:
        conv_id = generate_discord_id(conv)
        entry = {
            'source': f'discord-{conv_id}',
            'text': '<|im_start|>system\ncontinue this discord conversation (you are b4444)<|im_end|>' + '\n'.join([
                f'\n<|im_start|>{'assistant' if m['name'] == 'b4444' else 'user'}\n{m["name"]}: {m["content"]}<|im_end|>' for m in conv
            ])
        }
        out.append(entry)
    
    # Load existing dataset if it exists
    dataset_file = 'dataset.json'
    existing = []
    if os.path.exists(dataset_file):
        try:
            with open(dataset_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Merge with existing, avoiding duplicates
    existing_sources = {entry.get('source') for entry in existing if entry.get('source')}
    added = 0
    for entry in out:
        if entry['source'] not in existing_sources:
            existing.append(entry)
            existing_sources.add(entry['source'])
            added += 1
    
    # Save to dataset.json
    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    
    print(f'Added {added} new Discord entries to dataset.json (total: {len(existing)})', file=sys.stderr)
elif out_type == 'stats':
    print(f'(total: {len(all_convos)})')
