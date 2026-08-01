import requests

LOGIN_URL = 'http://127.0.0.1:8000/admin/login'
DASH_URL = 'http://127.0.0.1:8000/admin/dashboard'

s = requests.Session()
# submit form
resp = s.post(LOGIN_URL, data={'username':'admin','password':'admin123'}, allow_redirects=True)
print('Login status:', resp.status_code)
# fetch dashboard
r = s.get(DASH_URL)
print('Dashboard status:', r.status_code)
open('admin_dashboard_fetched.html','wb').write(r.content)
print('Saved admin_dashboard_fetched.html')
