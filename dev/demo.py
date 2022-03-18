# -*- coding: utf-8 -*-
from dev.install import migrate, create_demo_user


def demo():
    migrate()
    create_demo_user(secure=False)


if __name__ == "__main__":
    demo()
