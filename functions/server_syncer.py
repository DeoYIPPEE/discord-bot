import json

def server_syncer() -> None:
    with open("data/servers.json", "r") as f:
        servers = json.load(f)

    with open("up.txt", "r") as f:
        data = f.readlines()

    if len(data) < len(servers):
        data[-1] = f"{data[-1]}\n"
        temp = ["False\n" for i in range(len(servers)-len(data))]
        data.extend(temp)
        data[-1] = data[-1].replace("\n", "")
        with open("up.txt", "w") as f:
            f.writelines(data)