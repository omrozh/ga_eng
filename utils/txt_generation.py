import openai

openai.api_key = "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"


def gen_text(inp, max_tokens):
    title = openai.Completion.create(
        engine="text-davinci-003",
        prompt=inp + " give the output in Turkish",
        temperature=0.6,
        max_tokens=max_tokens,
        n=1,
        stop=None
    )
    usage_tokens = title.get("usage").get("total_tokens")
    title_data = title.get("choices")[0].get("text").replace("\"", "")
    return title_data, usage_tokens


def search_ai(inp, previous_messages=None):
    messages_total = []
    role = ""
    if previous_messages:
        for i in range(len(previous_messages)):
            if i == 0:
                role = previous_messages[i]
            else:
                messages_total.append({"role": "user" if i % 2 == 1 else "assistant", "content": previous_messages[i]})

    messages_total.append({"role": "system", "content": inp + ". reply to this in Turkish in a fitting way to your "
                                                              "character."})
    minus_index = 0
    if len(messages_total) > 4:
        minus_index = -3
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_total[minus_index:]
    )
    return response['choices'][0]['message']['content']
