import requests

url = "http://127.0.0.1:8000/api/clients/create"

def test_register_user():
    data={
        "username": "test_user",
        "password": "test_password",
        "email": "test@example.com",
        "gender": "Male",
        "first_name": "Имя",
        "last_name": "Фамилия",   
    }
    files = {
        "avatar": open("cat.jpeg", "rb")
    }
    response = requests.post(url, data=data, files=files)
    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь успешно зарегистрирован"

def test_repeat_user():
    data={
        "username": "test_user",
        "password": "test_password",
        "email": "test@example.com",
        "gender": "Male",
        "first_name": "Имя",
        "last_name": "Фамилия",   
    }
    files = {
        "avatar": open("cat.jpeg", "rb")
    }
    response = requests.post(url, data=data, files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Почта уже зарегистрирована!"
