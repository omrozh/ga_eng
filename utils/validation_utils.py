def validate_form_submit(values, user_obj):
    if not values["email"] or not values["username"] or not values["password"] or not values["phone_number"]:
        return False, "Missing Values"

    if len(values["password"]) < 6:
        return False, "Password too short"

    if len(values["username"]) < 6:
        return False, "Username too short"

    if len(values["username"]) > 128:
        return False, "Username too long"

    if values["email"] in [i.email for i in user_obj.query.filter_by(email=values["email"]).all()]:
        return False, "Email Used"

    if values["username"] in [i.username for i in user_obj.query.filter_by(username=values["username"]).all()]:
        return False, "Username Used"

    if values["phone_number"] in [i.phone_number for i in user_obj.query.filter_by(phone_number=values["phone_number"]).all()]:
        return False, "Phone Number Used"

    return True, "Registered"


def most_frequent(list_inp):
    counter = 0
    num = list_inp[0]

    for i in list_inp:
        curr_frequency = list_inp.count(i)
        if curr_frequency > counter:
            counter = curr_frequency
            num = i

    return num


def remove_all(list_inp, desired_remove):
    for i in list_inp:
        if i == desired_remove:
            list_inp.remove(i)
    return list_inp
