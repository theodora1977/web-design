import requests

BASE = 'http://127.0.0.1:8000'
ROUTES = ['/', '/about', '/gallary', '/services', '/contact', '/reviews', '/upload-page']
ADMIN_ROUTES = ['/admin/login', '/admin/dashboard', '/admin/services', '/admin/images']

s = requests.Session()

print('--- Public routes ---')
for r in ROUTES:
    url = BASE + r
    try:
        resp = s.get(url, timeout=5)
        text = resp.text.strip().replace('\n',' ')[:200]
        print(f'{r:16} {resp.status_code}  {text[:120]!r}')
    except Exception as e:
        print(f'{r:16} ERROR {e}')

print('\n--- Admin (attempt login) ---')
# login
login_url = BASE + '/admin/login'
try:
    r = s.post(login_url, data={'username':'admin','password':'admin123'}, allow_redirects=True, timeout=5)
    print('login:', r.status_code)
except Exception as e:
    print('login ERROR', e)

for rpath in ADMIN_ROUTES:
    url = BASE + rpath
    try:
        resp = s.get(url, timeout=5)
        text = resp.text.strip().replace('\n',' ')[:200]
        print(f'{rpath:18} {resp.status_code}  {text[:120]!r}')
    except Exception as e:
        print(f'{rpath:18} ERROR {e}')
