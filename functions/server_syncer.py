import json

def server_syncer() -> None:
    with open("data/servers.json", "r") as f:
        servers = json.load(f)

    with open("data/up.json", "r") as f:
        data = json.load(f)

    if len(data) < len(servers):
        temp = [False for i in range(len(servers)-len(data))]
        data.extend(temp)
        with open("data/up.json", "w") as f:
            json.dump(data, f)
