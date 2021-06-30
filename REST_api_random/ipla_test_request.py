import requests
""" Just login - no more supported password """

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.ipla.tv/uzytkownik/zaloguj/natywnie',
    'Origin': 'https://www.ipla.tv',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'Sec-Fetch-Mode': 'cors',
    'Content-Type': 'text/plain',
}

data = '{"id":1,"jsonrpc":"2.0","method":"login","params":{"userAgentData":{"portal":"ipla","deviceType":"pc","application":"chrome","os":"windows","build":1,"osInfo":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"},"ua":"www_iplatv/12345 (Mozilla/5.0 Windows NT 10.0; Win64; x64 AppleWebKit/537.36 KHTML, like Gecko Chrome/77.0.3865.90 Safari/537.36)","authData":{"login":"tester3n@vp.pl","password":"123test","deviceId":{"type":"other","value":"b76d7eff-2880-48b0-92ab-4beae5ba73b1"}},"clientId":"4b9b98b3-c9a7-49db-a496-c4d504f6d78c"}}'

response = requests.post('https://b2c-www.redefine.pl/rpc/auth/', headers=headers, data=data)

print(response.json())