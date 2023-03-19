import openai
openai.api_key = "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"


def gen_text(inp):
    title = openai.Completion.create(
        engine="text-davinci-003",
        prompt=inp + " give the output in Turkish",
        temperature=0.6,
        max_tokens=1000,
        n=1,
        stop=None
    )
    usage_tokens = title.get("usage").get("total_tokens")
    title_data = title.get("choices")[0].get("text").replace("\"", "")
    return title_data, usage_tokens
