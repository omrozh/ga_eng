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
