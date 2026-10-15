import urllib.request
import ssl
import urllib.error

ctx = ssl.create_default_context()
backend = 'https://career-lens-x75r.onrender.com/api'
frontend = 'https://careerlens-iota.vercel.app'

print('=== 1. Live Health Check ===')
req = urllib.request.Request(f'{backend}/health/live')
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print('GET /health/live:', res.status, res.read().decode())

print('=== 2. Readiness Check ===')
req = urllib.request.Request(f'{backend}/health/ready')
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print('GET /health/ready:', res.status, res.read().decode())

print('=== 3. Base Health Check with Tracing ===')
req = urllib.request.Request(f'{backend}/health', headers={'X-Request-ID': 'test_trace_prod_001'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print('GET /health:', res.status, 'Trace:', res.headers.get('X-Request-ID'), res.read().decode().strip())

print('=== 4. CORS Preflight Check on Auth ===')
req = urllib.request.Request(
    f'{backend}/auth/login',
    headers={
        'Origin': frontend,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization, X-Request-ID'
    },
    method='OPTIONS'
)
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print('OPTIONS /auth/login:', res.status)
    print('  Allow-Origin:', res.headers.get('Access-Control-Allow-Origin'))
    print('  Allow-Methods:', res.headers.get('Access-Control-Allow-Methods'))
    print('  Allow-Headers:', res.headers.get('Access-Control-Allow-Headers'))

print('=== 5. CORS Preflight Check on Recommended Jobs ===')
req = urllib.request.Request(
    f'{backend}/jobs/recommended',
    headers={
        'Origin': frontend,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type, Authorization, X-Request-ID'
    },
    method='OPTIONS'
)
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    print('OPTIONS /jobs/recommended:', res.status)
    print('  Allow-Origin:', res.headers.get('Access-Control-Allow-Origin'))

print('=== 6. Protected Endpoint 401 without Token ===')
try:
    req = urllib.request.Request(f'{backend}/auth/me')
    with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
        print('GET /auth/me unexpected status:', res.status)
except urllib.error.HTTPError as e:
    print('GET /auth/me expected status:', e.code, 'Trace:', e.headers.get('X-Request-ID'), e.read().decode().strip())

print('=== 7. Vercel Frontend HTML Check ===')
req = urllib.request.Request(frontend, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, context=ctx, timeout=15) as res:
    html = res.read().decode()
    print('GET Vercel Frontend:', res.status, 'HTML length:', len(html))
    print('Contains root element:', '<div id="root">' in html)
