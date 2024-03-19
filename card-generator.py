from dotenv import load_dotenv
from openai import OpenAI
from string import Template
import httpx
import os
import json
import yaml


def generate_fields_description(fields):
    fields_descr = ""
    for field in fields:
        fields_descr += f"${field['name']}: {field['description']}"
    return f"{fields_descr}"


def generate_fields_template(fields):
    target = ""
    first = True
    for field in fields:
        if not first:
            target += ", "
        target += f"\"{field['name']}\": \"${field['name']}\""
        first = False
    return f"{{{target}}}"


def generate_examples(examples):
    generated = ""
    first = True
    for example in examples:
        if not first:
            generated += ", "
        generated += f"\"{example['input']}\": \"{example['output']}\""
        first = False
    return f"{{{generated}}}"


def compute_prompt(conf, word, pos):
    return Template(conf['llm']['prompt_template']).substitute(
        german_word=word,
        part_of_speech=pos,
        fields_description=generate_fields_description(conf['anki']['fields']),
        fields_json_template=generate_fields_template(conf['anki']['fields']),
        examples=generate_examples(conf['anki']['examples'])
    )


def load_config():
    with open('config.yaml', 'r') as f:
        config_data = yaml.safe_load(f)
    return config_data


if __name__ == '__main__':
    # load secrets
    load_dotenv()

    # initialize OpenAI client
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    # load configuration
    config = load_config()
    # read model name
    model_name = config['llm']['model']
    # read anki model name
    anki_model_name = config['anki']['model']
    # read anki deck name
    anki_deck_name = config['anki']['deck']
    # read anki connect url
    anki_connect_url = config['anki']['connect_url']

    print(f'Input german word followed by part of speach separated by space. For example: Hund noun')
    # infinite loop broken by CTRL+C combination
    while True:
        try:
            input_words = input('> ').split()
            # TODO: allow to input one word and guess part of speach automatically
            if len(input_words) < 2:
                print(f'There are {len(input_words)} words, at least 2 are expected separated by space, the last one '
                      f'is part of speach. Try again.')
                continue

            # unpacking list into two variables
            # join all the words expect the last one into one string, put the last one in separate variable
            german_word, part_of_speach = ' '.join(input_words[0: -1]), input_words[-1]
            print(f'German word: {german_word}, part of speach: {part_of_speach}')

            # generate prompt
            note_fields_prompt = compute_prompt(config, german_word, part_of_speach)
            print(f'Generated prompt:\n {note_fields_prompt}')
            completion = openai_client.chat.completions.create(
                messages=[
                    {
                        'role': 'user',
                        'content': note_fields_prompt
                    }
                ],
                model=model_name,
                temperature=0.7
            )

            # TODO: add json validation to prevent creating invalid cards
            card_fields = completion.choices[0].message.content
            print(f'Generated anki card parameters:\n {card_fields}')

            print(f'Invoke AnkiConnect API to create a card')
            req_data = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": f'{anki_deck_name}',
                        "modelName": f'{anki_model_name}',
                        "fields": json.loads(card_fields)
                    }
                }
            }
            resp = httpx.post(anki_connect_url, json=req_data)
            status_code = resp.status_code
            if status_code == 200:
                resp_payload = resp.json()
                error = resp_payload.get('error')
                result = resp_payload.get('result')

                if error is None and result is not None:
                    print(f'Card with id {result} was created successfully')
                elif resp.json()['error'] is not None:
                    print(f'Error occurred: {error}')
            else:
                print(f'Unknown error occurred: {status_code}')

        except KeyboardInterrupt:
            print('\nExiting...')
            break

        except Exception as e:
            print(f'Error occurred: {e}')
            continue
