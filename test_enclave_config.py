import json
from enclave_config import EnclaveConfig

CONFIG_PATH = "config/main_config-test.json"

def main():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    config = config["enclave"]
    c = EnclaveConfig(config)
    print("enclave_config:")
    print(c.enclave_config.contents)
    print("enclave_keys:")
    print(c.enclave_keys.contents)   

if __name__ == "__main__":
    main()