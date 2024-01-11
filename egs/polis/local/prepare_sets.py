import argparse
import os
import sys

from sklearn.model_selection import train_test_split

from sd_benchmark.logger import logger


def save(param, data):
    logger.info(f"Save {param}: {len(data)}")
    with open(param, 'w') as txt_file:
        for line in data:
            txt_file.write(f'{line}\n')


def take_fraction(data, fraction):
    return data[:int(len(data) * fraction)]


def main(argv):
    logger.info("Starting")
    parser = argparse.ArgumentParser(description="Prepare train/dev/val sets")
    parser.add_argument("--input", nargs='?', required=True, help="All file list")
    parser.add_argument("--out-dir", nargs='?', required=True, help="Output dir")
    args = parser.parse_args(args=argv)

    with open(args.input, 'r') as txt_file:
        lines = txt_file.readlines()
    lines = [line.strip() for line in lines]
    logger.info(f"Read {len(lines)}")
    train, rem_dev = train_test_split(lines, train_size=0.8, random_state=1)
    test, dev = train_test_split(rem_dev, train_size=0.5, random_state=1)

    logger.info(f"Train {len(train)}")
    logger.info(f"Dev {len(dev)}")
    logger.info(f"Test {len(test)}")
    save(os.path.join(args.out_dir, "train.all.txt"), train)
    save(os.path.join(args.out_dir, "dev.all.txt"), dev)
    save(os.path.join(args.out_dir, "test.all.txt"), test)

    fraction = 0.1
    save(os.path.join(args.out_dir, "train.mini.txt"), take_fraction(train, fraction))
    save(os.path.join(args.out_dir, "dev.mini.txt"), take_fraction(dev, fraction))
    save(os.path.join(args.out_dir, "test.mini.txt"), take_fraction(test, fraction))

    logger.info("done")


if __name__ == "__main__":
    main(sys.argv[1:])
