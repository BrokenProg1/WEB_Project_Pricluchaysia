from requests import get, post, delete
import datetime

# EXCURSIONS
req = get('http://127.0.0.1:5000/api/excursions')
print(req, req.content)

req = get('http://127.0.0.1:5000/api/excursions/1')
print(req, req.content)

req = post('http://127.0.0.1:5000/api/excursions', json={
    'id': '2',
    'title': 'excurs',
    'description': 'excursion.description',
    'price': '1000',
    'img': 'hhh/hh'
})
print(req, req.content)

req = delete('http://127.0.0.1:5000/api/excursions/2')
print(req, req.content)

# USERS
req = get('http://127.0.0.1:5000/api/users')
print(req, req.content)

req = get('http://127.0.0.1:5000/api/users/1')
print(req, req.content)

req = post('http://127.0.0.1:5000/api/users', json={
    'login': 'etykrs',
    'email': 'f@f.f',
    'hashed_password': 'c2e3b7daa5a0eecb2c989f1dae870e5b6c40a62f2d0e58b897bb3af959418b897d1f619c741534c9713165ec211eddf18704007ea80df49d4ce6043f312b4287',
    'role': 'user'
})
print(req, req.content)

req = delete('http://127.0.0.1:5000/api/users/5')
print(req, req.content)

# TICKETS
req = get('http://127.0.0.1:5000/api/tickets')
print(req, req.content)

req = get('http://127.0.0.1:5000/api/tickets/1')
print(req, req.content)

req = post('http://127.0.0.1:5000/api/tickets', json={
    'id_event': '1',
    'name_event': 'hu',
    'price_event': '7',
    'id_user': '1',
    'name_user': '1',
    'count_of_people': '1'
})
print(req, req.content)

req = delete('http://127.0.0.1:5000/api/tickets/3')
print(req, req.content)

# COMMENTS
req = get('http://127.0.0.1:5000/api/comments')
print(req, req.content)

req = get('http://127.0.0.1:5000/api/comments/1')
print(req, req.content)

req = post('http://127.0.0.1:5000/api/comments', json={
    'id_event': '1',
    'id_user': '2',
    'name_user': 'kl',
    'role_user': 'user',
    'text': 'comment.text',
    'date': datetime.datetime.now()  # Считаем, что работает
})
print(req, req.content)

req = delete('http://127.0.0.1:5000/api/comments/3')
print(req, req.content)