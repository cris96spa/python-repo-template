from main import main


def test_main_runs_the_showcase(capsys):
    main(5)

    output = capsys.readouterr().out
    assert "Random sum demo" in output
