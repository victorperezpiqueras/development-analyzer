import json


def transform_env():
    """
    Transforms the .env_full.json file into a .env.json file with the projects key as a string,
    so it can be used by the serverless framework env vars.
    """
    with open('.env_full.json') as f:
        data = json.load(f)
        data['projects'] = json.dumps(data['projects'])
        with open('.env.json', 'w') as env_file:
            json.dump(data, env_file)


if __name__ == '__main__':
    transform_env()
