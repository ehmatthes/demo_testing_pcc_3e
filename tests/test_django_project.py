"""Test the Learning Log project.

- Copy project to tmp dir.
- Build a venv there.
- Install [specified] version of Django there.
- Run migrations.
- Start runserver.
- Run functionality tests.
"""

import shutil
import os
import subprocess
from pathlib import Path
from time import sleep

import requests

import utils


def test_django_project(tmp_path, python_cmd):
    """Test the Learning Log project."""

    # Copy project to temp dir.
    src_dir = (Path(__file__).parents[1] / 'chapter_20'
            / 'deploying_learning_log')
    dest_dir = tmp_path / 'learning_log'
    shutil.copytree(src_dir, dest_dir)

    # All remaining work needs to be done in dest_dir.
    os.chdir(dest_dir)

    # Build a fresh venv for the project.
    cmd = f"{python_cmd} -m venv ll_env"
    output = utils.run_command(cmd)
    assert output == ''

    # Get python command from ll_env.
    llenv_python_cmd = (dest_dir
            / 'll_env' / 'bin' / 'python')

    # Run `pip freeze` to prove we're in a fresh venv.
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)
    assert output == ''

    # Install requirements, and requests for testing.
    cmd = f"{llenv_python_cmd} -m pip install -r requirements.txt"
    output = utils.run_command(cmd)
    cmd = f"{llenv_python_cmd} -m pip install requests"
    output = utils.run_command(cmd)

    # Run `pip freeze` again, verify installations.
    cmd = f"{llenv_python_cmd} -m pip freeze"
    output = utils.run_command(cmd)
    assert "Django==" in output
    assert "django-bootstrap5==" in output
    assert "platformshconfig==" in output
    assert "requests==" in output

    # Make migrations, call check.
    cmd = f"{llenv_python_cmd} manage.py migrate"
    output = utils.run_command(cmd)
    assert 'Operations to perform:\n  Apply all migrations: admin, auth, contenttypes, learning_logs, sessions\nRunning migrations:\n  Applying contenttypes.0001_initial... OK\n  Applying auth.0001_initial... OK\n  Applying admin.0001_initial... OK\n  Applying admin.0002_logentry_remove_auto_add... OK\n  Applying admin.0003_logentry_add_action_flag_choices... OK\n  Applying contenttypes.0002_remove_content_type_name... OK\n  Applying auth.0002_alter_permission_name_max_length... OK\n  Applying auth.0003_alter_user_email_max_length... OK\n  Applying auth.0004_alter_user_username_opts... OK\n  Applying auth.0005_alter_user_last_login_null... OK\n  Applying auth.0006_require_contenttypes_0002... OK\n  Applying auth.0007_alter_validators_add_error_messages... OK\n  Applying auth.0008_alter_user_username_max_length... OK\n  Applying auth.0009_alter_user_last_name_max_length... OK\n  Applying auth.0010_alter_group_name_max_length... OK\n  Applying auth.0011_update_proxy_permissions... OK\n  Applying auth.0012_alter_user_first_name_max_length... OK\n  Applying learning_logs.0001_initial... OK\n  Applying learning_logs.0002_entry... OK\n  Applying learning_logs.0003_topic_owner... OK\n  Applying sessions.0001_initial... OK' in output

    cmd = f"{llenv_python_cmd} manage.py check"
    output = utils.run_command(cmd)
    assert "System check identified no issues (0 silenced)." in output

    # Start development server.
    #   To verify it's not running after the test:
    #   `$ ps aux | grep runserver`
    # I may have other projects running on 8000; run this on 8008.
    # Log to file, so we can verify we haven't connected to a
    #   previous server process, or an unrelated one.
    #   shell=True is necessary for redirecting output.
    runserver_log = dest_dir / 'runserver_log.txt'
    cmd = f"{llenv_python_cmd} manage.py runserver 8008"
    cmd += f" > {runserver_log} 2>&1"
    server_process = subprocess.Popen(cmd, shell=True,
            start_new_session=True)

    # Wait until server is ready.
    url = 'http://localhost:8008/'
    connected = False
    attempts, max_attempts = 1, 50
    while attempts < max_attempts:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                connected = True
                break
        except requests.ConnectionError:
            attempts += 1
            sleep(0.2)

    # Verify connection.
    assert connected

    # Pause for log file to be written.
    sleep(2)
    log_text = runserver_log.read_text()
    assert 'Error: That port is already in use' not in log_text
    assert 'Watching for file changes with StatReloader' in log_text
    assert '"GET / HTTP/1.1" 200' in log_text

    # Run functionality tests against the runnig project.
    func_test_path = (Path(__file__).parent / 'resources'
            / 'll_project_functionality_tests.py')
    try:
        cmd = f"{llenv_python_cmd} {func_test_path} http://localhost:8008/"
        output = utils.run_command(cmd)
    except subprocess.CalledProcessError as e:
        print("---- STDOUT ----")
        print(e.stdout)
        print("---- STDERR ----")
        print(e.stderr)
        # Copy e.stdout to output, for following assertions to run.
        output = e.stdout
    finally:
        # Stop the development server.
        print("\n***** Stopping server...")

        import signal
        # os.kill()?
        # os.kill(server_process.pid, signal.SIGTERM)
        # sleep(3)

        pgid = os.getpgid(server_process.pid)
        os.killpg(pgid, signal.SIGTERM)

        # server_process.terminate()
        server_process.wait()
        # print("***** Server terminated.")

        if server_process.poll() is None:
            print("\n***** Server is still running. PID:", server_process.pid)
        else:
            print("\n***** Server process terminated.")

    # These are individual assertions, so when it fails I can easily see which one failed.
    assert 'Testing functionality of deployed app...' in output
    assert '  Checking anonymous home page...' in output
    assert '  Checking that anonymous topics page redirects to login...' in output
    assert '  Checking that anonymous register page is available...' in output
    assert '  Checking that anonymous login page is available...' in output
    assert '  Checking that a user account can be made...' in output
    assert '  Checking that a new topic can be created...' in output
    assert '    Checking topics page as logged-in user...' in output
    assert '    Checking blank new_topic page as logged-in user...' in output
    assert '    Submitting post request for a new topic...' in output
    assert '    Checking topic page for topic that was just created...' in output
    assert '    Checking that a new entry can be made...' in output
    assert '      Checking blank new entry page...' in output
    assert '      Submitting post request for new entry...' in output
    assert '  All tested functionality works.' in output