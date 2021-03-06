#!usr/bin/env python
# -*- coding: utf-8 -*-
# author: kuangdd
# date: 2020/12/10
"""
waveglow_train
"""
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(Path(__name__).stem)

import json
import argparse
import torch
from waveglow.train import train

if __name__ == "__main__":
    try:
        from setproctitle import setproctitle

        setproctitle('zhrtvc-waveglow-train')
    except ImportError:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default='waveglow/config.json',
                        help='JSON file for configuration')
    parser.add_argument('-r', '--rank', type=int, default=0,
                        help='rank of process for distributed')
    parser.add_argument('-g', '--group_name', type=str, default='',
                        help='name of group for distributed')
    args = parser.parse_args()

    # Parse configs.  Globals nicer in this case
    with open(args.config) as f:
        data = f.read()
    config = json.loads(data)
    train_config = config["train_config"]
    # global data_config
    data_config = config["data_config"]
    # global dist_config
    dist_config = config["dist_config"]
    # global waveglow_config
    waveglow_config = config["waveglow_config"]

    num_gpus = torch.cuda.device_count()
    if num_gpus > 1:
        if args.group_name == '':
            print("WARNING: Multiple GPUs detected but no distributed group set")
            print("Only running 1 GPU.  Use distributed.py for multiple GPUs")
            num_gpus = 1

    if num_gpus == 1 and args.rank != 0:
        raise Exception("Doing single GPU training on rank > 0")

    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = False
    train(num_gpus, args.rank, args.group_name,
          waveglow_config=waveglow_config,
          dist_config=dist_config,
          data_config=data_config,
          train_config=train_config,
          **train_config)
