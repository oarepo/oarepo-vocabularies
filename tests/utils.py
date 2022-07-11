def api_path(url):
    assert url.startswith('https://127.0.0.1:5000/api')
    return url[len('https://127.0.0.1:5000/api'):]


def replace_timestamps(data):
    if isinstance(data, dict):
        for k, v in list(data.items()):
            if k in ('created', 'updated'):
                data[k] = 'TS'
            elif k == '@v':
                data[k] = 'VER'
            else:
                replace_timestamps(v)
    elif isinstance(data, list):
        for d in data:
            replace_timestamps(d)
    return data
