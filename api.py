# from openai import OpenAI
# import sys

# try:
#     client = OpenAI(api_key=sys.argv[1])

#     uploaded = client.files.create(
#         file=open(sys.argv[2], 'rb'),
#         purpose='fine-tune'
#     )

#     client.fine_tuning.jobs.create(
#         model='gpt-3.5-turbo-0125',
#         training_file=uploaded.id
#     )

#     print('finetune job created')
# except IndexError:
#     print('Usage: python finetune.py <api_key> <file_path>')
#     sys.exit(1)

def send_to_finetune(api_key, file_path):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    uploaded = client.files.create(
        file=open(file_path, 'rb'),
        purpose='fine-tune'
    )
    client.fine_tuning.jobs.create(
        model='gpt-4o-mini-2024-07-18',
        training_file=uploaded.id
    )
    print('finetune job created')