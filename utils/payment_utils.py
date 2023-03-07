import stripe

stripe.api_key = "*** "


def create_token(card_information):
    return stripe.Token.create(
        card=card_information,
    )


def create_charge(amount, token_id):
    stripe.Charge.create(
        amount=int(amount*100),
        currency="try",
        source=token_id,
        description="GrandAssembly token purchase",
    )


def get_card_info(token_id):
    return stripe.Token.retrieve(token_id)
