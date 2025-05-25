import json
import re


def _row_transformer(row):
    row = {'request': row['request'], 'response': row['response']}
    new_headers = {}
    for header in row['request']['headers']:
        new_headers[header['name']] = header['value']
    row['request']['headers'] = new_headers
    new_headers = {}
    for header in row['response']['headers']:
        new_headers[header['name']] = header['value']
    row['response']['headers'] = new_headers
    return row


def _check_excluded(excludes, url):
    for exclude in excludes:
        if re.findall(exclude, url):
            return False
    return True


def analyze(path, needle_url: str = None, excludes: set = None):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read().encode('unicode-escape').decode('unicode-escape')
        data = json.loads(content)
    data = data['log']['entries']
    if needle_url:
        data = [item for item in data if item['request']['url'].startswith(needle_url)]
    data = map(_row_transformer, data)
    if excludes:
        data = filter(lambda row: _check_excluded(excludes, row['request']['url']), data)
    return list(data)


res = json.dumps(analyze('isales.trcont.com.har.json', 'https://isales.trcont.com/', excludes={
    r'.+\.json.*',
}), indent=4)

with open('analysis.json', 'w', encoding='utf-8') as f:
    f.write(res)

