# Card Generator

This is CLI tool that generates Anki cards using OpenAI's API.

In interactive mode it takes user input for a German word and its part of speech, 
and generates a prompt for the OpenAI API. 
The API's response is then used to create a new Anki card with a help of API exposed by Anki Connect add-on.

Examples of input:
- Hund noun
- sich ändern verb

Config.yaml contains the Anki deck configuration and the OpenAI API key to use for completion.

## Prerequisites

- Python
- pip
- An OpenAI API key
- Anki
- Anki Connect (Anki add-on)

## Setup

1. Clone the repository.
2. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

## How to Use
1. Run the script:

```bash
python card-generator.py
```

2. You will be prompted to enter a German word followed by its part of speech, separated by a space. For example:

```bash
> Hund noun
```

3. The script will generate a prompt, send it to the OpenAI API, and use the response to create a new Anki card. If successful, it will print the ID of the new card.

4. To stop the script, use the CTRL+C keyboard combination.

Please note that the script runs in an infinite loop and can be stopped at any time by using the CTRL+C keyboard combination.

## Configuration

The `config.yaml` file contains the configuration for the Anki deck and the OpenAI API.

### LLM

- `model`: The OpenAI model used for generating the cards. By default, it's set to `gpt-3.5-turbo-0125`, but you can use any from OpenAI.
- `prompt_template`: The template used to generate the prompt for the OpenAI API.

### Anki

- `deck`: The name of the Anki deck where the cards will be added.
- `model`: The name of the Anki model used for the cards.
- `fields`: The fields used in the Anki model as list. Each list entry has a `name`, `description`, and `example` properties. The `name` is the name of the field, the `description` is a description of the field which is used by LLM to generate card value, and the `example` is an example of the generated field's content.
- `examples`: Examples of input and output for the script.
- `connect_url`: The URL used to connect to Anki Connect.

## Environment Variables

The `.env` file is used to store sensitive information such as API keys. You need to adjust template file with you secrets in the root directory of the project.

Here's an example of a `.env` file:

```ini
# OpenAI API key
OPENAI_API_KEY=your_api_key_here


