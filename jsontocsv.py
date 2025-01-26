import pandas, ijson

def json_to_csv(path_in, path_out):
    out = []

    for d in ijson.items(open(path_in), 'messages.item'):
        out += [{
            'author': d['author']['name'],
            'content': d['content'],
            'time': d['timestamp']
        }]

    df = pandas.DataFrame(out)
    df.to_csv(path_out, index=False)
