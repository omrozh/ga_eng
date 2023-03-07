import openai
openai.api_key = "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"

turkish_chars = {
    "\\u011f": "ğ",
    "\\u011e": "Ğ",
    "\\u0131": "ı",
    "\\u0130": "İ",
    "\\u00f6": "ö",
    "\\u00d6": "Ö",
    "\\u00fc": "ü",
    "\\u00dc": "Ü",
    "\\u015f": "ş",
    "\\u015e": "Ş",
    "\\u00e7": "ç",
    "\\u00c7": "Ç"
}


def gen_text(inp):
    title = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": inp + " give the output in Turkish"},
        ]
    )
    turkish_text = title.get("choices")[0].get("message").get("content")
    for i in turkish_chars.keys():
        turkish_text.replace(i, turkish_chars.get(i))
    return title.get("choices")[0].get("message").get("content"), title.get("usage").get("total_tokens")
