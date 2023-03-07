def process_sentence(text):
    text = text.replace("!", "!<splitter>").replace("?", "?<splitter>").\
        replace(".", ".<splitter>")
    text_processed = text.split("<splitter>")
    text_final = []

    for i in text_processed:
        if len(i) > 1:
            text_final.append(i)

    return text_final