import os
import io
import json
import zipfile

import msal
import requests

client_id = os.environ["MS_CLIENT_ID"]
cache_data = os.environ["MSAL_CACHE"]

cache = msal.SerializableTokenCache()
cache.deserialize(cache_data)

app = msal.PublicClientApplication(
    client_id,
    authority="https://login.microsoftonline.com/consumers",
    token_cache=cache,
)

accounts = app.get_accounts()
if not accounts:
    raise RuntimeError("No Microsoft account in authentication cache")

result = app.acquire_token_silent_with_error(
    ["Files.Read"],
    account=accounts[0],
)

if not result or "access_token" not in result:
    raise RuntimeError(
        "Microsoft authentication expired or failed. "
        "Manual reauthentication may be required."
    )

url = (
    "https://graph.microsoft.com/v1.0/me/drive/root:"
    "/SNL%20Fall%2026.xlsx:/content"
)

response = requests.get(
    url,
    headers={"Authorization": "Bearer " + result["access_token"]},
    timeout=60,
)
response.raise_for_status()

data = response.content

with zipfile.ZipFile(io.BytesIO(data)) as workbook:
    if "xl/workbook.xml" not in workbook.namelist():
        raise RuntimeError("Downloaded file is not a valid Excel workbook")

print("SUCCESS: OneDrive workbook downloaded and verified")
print("Workbook size:", len(data), "bytes")
