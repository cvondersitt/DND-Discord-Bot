import os
from openai import OpenAI
key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=key)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
  ]
)
print(completion.choices[0].message.content)