"""Download the SNL workbook using the existing MSAL GitHub Actions secrets."""
import os
from pathlib import Path
import msal
import requests

cache = msal.SerializableTokenCache()
cache.deserialize(os.environ['MSAL_CACHE'])
app = msal.PublicClientApplication(os.environ['MS_CLIENT_ID'], authority='https://login.microsoftonline.com/consumers', token_cache=cache)
accounts = app.get_accounts()
if not accounts:
    raise RuntimeError('No Microsoft account in token cache')
result = app.acquire_token_silent_with_error(['Files.Read'], account=accounts[0])
if not result or 'access_token' not in result:
    raise RuntimeError('Microsoft login failed: ' + str((result or {}).get('error', 'no token')))
url = 'https://graph.microsoft.com/v1.0/me/drive/root:/SNL%20Fall%2026.xlsx:/content'
r = requests.get(url, headers={'Authorization': 'Bearer ' + result['access_token']}, timeout=90)
r.raise_for_status()
import io, zipfile
with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    if 'xl/workbook.xml' not in z.namelist():
        raise ValueError('Downloaded content is not an Excel workbook')
Path('SNL Fall 26.xlsx').write_bytes(r.content)
print('Workbook downloaded and verified:', len(r.content), 'bytes')
