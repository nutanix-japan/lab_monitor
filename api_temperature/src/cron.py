import subprocess
response = subprocess.check_output('date').decode()
print(response)