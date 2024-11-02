import requests


def setup_url(hand="/api/clients/create"):
    return f"http://127.0.0.1:8000{hand}"


def setup_data_and_files(add_str="", hand="/api/clients/create"):
    data={
            "username": f"test_user{add_str}",
            "password": f"test_password{add_str}",
            "email": f"test{add_str}@example.com",
            "gender": "Male",
            "first_name": f"Имя{add_str}",
            "last_name": f"Фамилия{add_str}",   
    }
    files = {
        "avatar": open("cat.jpeg", "rb")
    }
    return data, files


def setup_token(data, login_url):
    response = requests.post(
        login_url, 
        data={
            "email": data["email"],
            "password": data["password"]})
    return response.json()["access_token"]

def test_repeat_user():
    # 1
    url = setup_url()
    data, files = setup_data_and_files()
    requests.post(url, data=data, files=files)
    response = requests.post(url, data=data, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Почта уже зарегистрирована!"


def test_registration_login():
    # 2
    register_url = setup_url()
    login_url = setup_url(hand="/api/login")
    data, files = setup_data_and_files(add_str="1")
    requests.post(register_url, data=data, files=files)
    response = requests.post(
        login_url, 
        data={
            "email": data["email"],
            "password": data["password"]})
    assert response.status_code == 200
    assert response.json()["token_type"] == "barrer"


def test_match():
    # 3
    # 4 - номер записи в бд
    data_1, files = setup_data_and_files(add_str="3")
    requests.post(setup_url(), data=data_1, files=files)
    token1 = setup_token(data_1, setup_url(hand="/api/login"))

    data_2, files = setup_data_and_files(add_str="4")
    requests.post(setup_url(), data=data_2, files=files)
    token2 = setup_token(data_2, setup_url(hand="/api/login"))

    response = requests.post(
        setup_url(hand="/api/clients/3/match"), 
        headers={"Authorization": f"Bearer {token1}"})


    assert response.status_code == 400
    assert response.json()["detail"] == "Лайкнул себя"    

    response = requests.post(
        setup_url(hand="/api/clients/4/match"),
        headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Лайк!"

    response = requests.post(
        setup_url(hand="/api/clients/4/match"),
        headers={"Authorization": f"Bearer {token1}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Лайк уже существует"

    response = requests.post(
        setup_url(hand="/api/clients/3/match"),
        headers={"Authorization": f"Bearer {token2}"})
    assert response.status_code == 200
    