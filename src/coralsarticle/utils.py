import subprocess


def execute(cmd, conda_env=None):
    """
    Source: https://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
    """

    if conda_env is not None:
        cmd = f"source activate {conda_env}; {cmd}"

    popen = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True, 
        shell=True,
        executable='/bin/bash')
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line, end="") 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
