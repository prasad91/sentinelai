from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);
