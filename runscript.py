import subprocess

def create_exe(url, app_name, platform):
    try:
        command = ["nativefier", "--name", app_name, url, "--platform", platform]
        subprocess.run(command, check=True)
        print(f"Created the app {app_name} for {platform}!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create the app. Error: {e}")

url = "https://marylandzoo.streamlit.app/"
app_name = "bobcats"
platform = "mac"

create_exe(url, app_name, platform)