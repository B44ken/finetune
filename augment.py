import json, sys, random, re

dataset = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'dataset.json'))
out_file = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] if len(sys.argv) > 1 else 'dataset.json'
dropout = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
n_aug = int(sys.argv[4]) if len(sys.argv) > 4 else 2

result = []
for entry in dataset:
    result.append(entry)
    if m := re.search(r'b4444:\s*(.*?)<\|im_end\|>', entry.get('text', ''), re.DOTALL):
        content = m.group(1).strip()
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]
        if len(sents) >= 2:
            for i in range(n_aug):
                kept = [s for s in sents if random.random() > dropout] or [random.choice(sents)]
                aug = entry.copy()
                aug['source'] = f"{entry['source']}-aug-{i+1}"
                aug['text'] = entry['text'].replace(content, ' '.join(kept))
                result.append(aug)

json.dump(result, open(out_file, 'w'), indent=2, ensure_ascii=False)
print(f'{len(result)} total ({len(result)-len(dataset)} augmented)', file=sys.stderr)
