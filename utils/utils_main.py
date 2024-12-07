import os
import json
import yaml
import argparse 
import modules


def load_config(args, config_path="./configs/configs.yaml", api_key_path="./configs/api_key.yaml"):
    # check loading success or not
    success = True

    # load configs
    if os.path.exists(config_path):
        with open(config_path) as f:
            configs = yaml.load(f, Loader=yaml.FullLoader)
    else:
        print(f"configs.yaml is not found in {config_path}")
        success = False
    
    # load api key
    if os.path.exists(api_key_path):
        with open(api_key_path) as f:
            api_key = yaml.load(f, Loader=yaml.FullLoader)
            if "API_KEY" in api_key:
                configs["api_key"] = api_key
            elif args.api_key is not None:
                api_key = {"API_KEY": args.api_key}
                with open(api_key_path, "w") as f:
                    yaml.dump(api_key, f)
                configs["api_key"] = api_key
            else:
                print("API_KEY is neither found in api_key.yaml nor in args --api_key")
                os.remove(api_key_path)
                success = False
    elif args.api_key is not None:
        api_key = {"API_KEY": args.api_key}
        with open(api_key_path, "w") as f:
            yaml.dump(api_key, f)   
        configs["api_key"] = api_key
    else:    
        print("api_key.yaml is not found and --api_key is not given")
        success = False

    return configs if success else None