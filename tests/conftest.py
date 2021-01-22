pytest_plugins = [
    "tests.fixtures",
    "tests.acceptance.fixtures",
]


def pytest_addoption(parser):
    parser.addoption("--env", help="load env config")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--env"):
        import dotenv

        dotenv.load_dotenv(config.option.env)
