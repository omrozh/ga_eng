import requests

resp = requests.post("https://grandassembly.net/api/train", data={
    "api_key": "a6d6565a-ebd6-410c-9165-deaa63561813",
    "character_description": "Çağrı merkezi destek elemanısın."
})

print(resp.json())
