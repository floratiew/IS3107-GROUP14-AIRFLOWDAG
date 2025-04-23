import requests

def get_token():
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {
        "email": "Jevan.Koh@u.nus.edu",
        "password": "JekoP4ssw0rd@123"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error:", response.status_code, response.text)
        return None
