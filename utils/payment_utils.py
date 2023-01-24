import stripe

stripe.api_key = "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 "


def create_token(card_information):
    return stripe.Token.create(
        card=card_information,
    )


def create_charge(amount, token_id):
    stripe.Charge.create(
        amount=int(amount*100),
        currency="usd",
        source=token_id,
        description="GrandAssembly token purchase",
    )
