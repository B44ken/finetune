import csv, random, json

CONTEXT = 8
NAME, CONTENT, TIMESTAMP = 0, 1, 2

def get_chains(msgs, name):
    ch = []
    for i in range(CONTEXT, len(msgs) - 1):
        if msgs[i][NAME] == name and msgs[i + 1][NAME] != name:
            ch += [msgs[i - CONTEXT:i+1]]
    return ch

def from_csv(file, name):
    reader = csv.reader(open(file, 'r'))
    rows = [row for row in reader]
    return get_chains(rows, name)

def pick_n(chains, n=70):
    return random.sample(chains, n)

def to_chatgpt(chains, name, path):
    # out = { 'messages': [] }
    out = []
    for chain in chains:
        out_chain = {
            'messages': [{
                'role': 'system',
                'content': f'continue this discord chat. you are {name}.',
            }]
        }
        for row in chain:
            out_chain['messages'] += [{
                'role': 'assistant' if row[NAME] == name else 'user',
                'content': f'{row[NAME]}, {row[TIMESTAMP].split("T")[1].split(".")[0]}: {row[CONTENT]}',
            }]
        out += [out_chain]
    f = open(path, 'w')
    f.write('\n'.join(
        json.dumps(x) for x in out
    ))
    # f.write('\n'.join([str(x) for x in out]))