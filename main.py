import os, jsontocsv, chains, api, sys

def main(name, json, openai_key):
    if not os.path.exists('gen.csv'):
        print('csv not found, creating...')
        jsontocsv.json_to_csv(json, 'gen.csv')

    print('loading chains from csv...')
    mychains = chains.from_csv('gen.csv', name)

    print('formatting chains...')
    chains.to_chatgpt(chains.pick_n(mychains), name, 'gen.jsonl')

    print('sending finetune to chatgpt...')
    if openai_key != '-':
        api.send_to_finetune(openai_key, 'gen.jsonl')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('usage: python main.py <name> <json> <openai_key>')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])