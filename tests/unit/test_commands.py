from opencoverage import commands
from unittest.mock import Mock
from unittest.mock import patch


def test_run_consumer():
    with patch("uvicorn.Server.serve") as mocked_server, patch(
        "opencoverage.commands.Settings"
    ), patch("opencoverage.commands.HTTPApplication"):
        commands.run_command()
        mocked_server.assert_called_once()


def test_parse_env_vars(monkeypatch):
    monkeypatch.setenv("dsn", "dsn")
    monkeypatch.setenv("scm", "scm")
    with patch("uvicorn.Server.serve") as mocked_server, patch(
        "opencoverage.commands.HTTPApplication"
    ) as http_app:
        commands.run_command()
        mocked_server.assert_called_once()
        settings = http_app.mock_calls[0].args[0]
        assert settings.dsn == "dsn"
        assert settings.scm == "scm"


def test_load_env_file():
    mock_args = Mock()
    mock_args.env_file = ".env"
    with patch("uvicorn.Server.serve") as mocked_server, patch(
        "opencoverage.commands.Settings"
    ), patch("opencoverage.commands.HTTPApplication"), patch(
        "opencoverage.commands.parser.parse_known_args", return_value=(mock_args, None)
    ), patch(
        "opencoverage.commands.HTTPApplication"
    ), patch(
        "opencoverage.commands.dotenv.load_dotenv"
    ) as load_dotenv:
        commands.run_command()
        mocked_server.assert_called_once()
        load_dotenv.assert_called_with(".env")
