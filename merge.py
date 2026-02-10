import json
import glob
import sys
from datetime import datetime
all_convos = []


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
    messages = json.load(open(filename))['messages']
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
elif out_type == 'stats':
    print(f'(total: {len(all_convos)})')
