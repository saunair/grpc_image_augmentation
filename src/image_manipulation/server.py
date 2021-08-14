from fire import Fire

from image_manipulation.communication_utils import spawn_server


def main():
    Fire(spawn_server)
