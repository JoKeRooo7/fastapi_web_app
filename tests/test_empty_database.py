import pytest
import requests
import json


def setup_url(hand="/api/clients/create"):
    return f"http://127.0.0.1:8000{hand}"


def get_file():
    return {"avatar": open("cat.jpeg", "rb")}


def setup_data_and_files(add_str=""):
    data = {
        "username": f"test_user{add_str}",
        "password": f"test_password{add_str}",
        "email": f"test{add_str}@example.com",
        "gender": "Male",
        "first_name": f"Имя{add_str}",
        "last_name": f"Фамилия{add_str}",
        }
    return data
    # return {"data" : (None, json.dumps(data)),}


def setup_token(user_data, login_url):
    response = requests.post(
        login_url,
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )
    return response.json()["access_token"]


@pytest.mark.parametrize("user_number", range(1, 11))
def test_first_registration_user(user_number):
    url = setup_url()
    data = setup_data_and_files(add_str=str(user_number))
    response = requests.post(url, data=data, files=get_file())
    print(response.json())

    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь успешно зарегистрирован"
    response = requests.post(url, data=data, files=get_file())
    assert response.status_code == 400
    assert response.json()["detail"] == "Почта уже зарегистрирована!"


def test_registration_login():
    login_url = setup_url(hand="/api/login")
    data = setup_data_and_files(add_str="1")
    response = requests.post(
        login_url,
        json={
            "email": data["email"],
            "password": data["password"]
        }
    )
    assert response.status_code == 200, f"Ошибка: {response.json()}"
    assert response.json()["token_type"] == "barrer"


def test_match(first="1", second="2"):
    url = "/api/clients/{}/match"
    data_first = setup_data_and_files(add_str=first)
    data_second = setup_data_and_files(add_str=second)
    token_first = setup_token(data_first, setup_url(hand="/api/login"))
    token_second = setup_token(data_second, setup_url(hand="/api/login"))
    response = requests.post(
        setup_url(url.format(first)),
        headers={"Authorization": f"Bearer {token_first}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Лайкнул себя"
    response = requests.post(
        setup_url(url.format(second)),
        headers={"Authorization": f"Bearer {token_first}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Лайк!"
    response = requests.post(
        setup_url(url.format(second)),
        headers={"Authorization": f"Bearer {token_first}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Лайк уже существует"
    response = requests.post(
        setup_url(url.format(first)),
        headers={"Authorization": f"Bearer {token_second}"})
    assert response.status_code == 200


def test_get_list_1():
    data = setup_data_and_files(add_str="2")
    token = setup_token(data, setup_url(hand="/api/login"))
    response = requests.get(
        setup_url(hand="/api/list"),
        headers={"Authorization": f"Bearer {token}"},
        json={}
        )
    assert response.status_code == 200
    assert len(response.json()["user_list"]) == 10


def test_get_list2():
    data = setup_data_and_files(add_str="2")
    token = setup_token(data, setup_url(hand="/api/login"))
    response = requests.get(
        setup_url(hand="/api/list"),
        json={"gender": "Male"},
        headers={"Authorization": f"Bearer {token}"},)
    assert response.status_code == 200
    assert len(response.json()["user_list"]) == 10


def test_get_list3():
    data = setup_data_and_files(add_str="2")
    token = setup_token(data, setup_url(hand="/api/login"))
    response = requests.get(
        setup_url(hand="/api/list"),
        json={"gender": "Female"},
        headers={"Authorization": f"Bearer {token}"},)
    assert response.status_code == 404


def test_get_list4():
    data = setup_data_and_files(add_str="2")
    token = setup_token(data, setup_url(hand="/api/login"))
    response = requests.get(
        setup_url(hand="/api/list"),
        json={"gender": "Male", "order": "desc"},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_get_list_with_distance():
    data1 = setup_data_and_files(add_str="1")
    data2 = setup_data_and_files(add_str="2")
    data3 = setup_data_and_files(add_str="3")
    data4 = setup_data_and_files(add_str="4")
    data5 = setup_data_and_files(add_str="5")
    token1 = setup_token(data1, setup_url(hand="/api/login"))
    token2 = setup_token(data2, setup_url(hand="/api/login"))
    token3 = setup_token(data3, setup_url(hand="/api/login"))
    token4 = setup_token(data4, setup_url(hand="/api/login"))
    token5 = setup_token(data5, setup_url(hand="/api/login"))
    post_coordinate = "/api/coordinates/create"
    response1 = requests.post(
        setup_url(hand=post_coordinate),
        json={"latitude": 55.213421, "longitude": 55.213421},
        headers={"Authorization": f"Bearer {token1}"})
    response2 = requests.post(
        setup_url(hand=post_coordinate),
        json={"latitude": 55.213431, "longitude": 55.213441},
        headers={"Authorization": f"Bearer {token2}"})
    response3 = requests.post(
        setup_url(hand=post_coordinate),
        json={"latitude": 55.213411, "longitude": 55.214421},
        headers={"Authorization": f"Bearer {token3}"})
    response4 = requests.post(
        setup_url(hand=post_coordinate),
        json={"latitude": 70.213421, "longitude": 53.213421},
        headers={"Authorization": f"Bearer {token4}"})
    response5 = requests.post(
        setup_url(hand=post_coordinate),
        json={"latitude": 62.213421, "longitude": 44.213421},
        headers={"Authorization": f"Bearer {token5}"})
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    assert response4.status_code == 200
    assert response5.status_code == 200
    response = requests.get(
        setup_url(hand="/api/list"),
        json={"distance": 10},
        headers={"Authorization": f"Bearer {token1}"})
    print(response.json())
    assert response.status_code == 200
    id_list = [res["id"] for res in response.json()["user_list"]]
    assert 5 not in id_list
    assert 4 not in id_list
    assert 2 in id_list
