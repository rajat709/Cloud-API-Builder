import streamlit as st
import subprocess
import multiprocessing
import tempfile
import shutil
import psutil
import os
import re


def validate_token(token):
    with open("tokens.txt", "r") as tokens_file:
        valid_tokens = [line.strip() for line in tokens_file.readlines()]
        return token in valid_tokens

def mark_token_as_used(token, port):
    with open("used-tokens.txt", "a") as used_tokens_file:
        used_tokens_file.write(f"{token} --{port}\n")

def remove_token_from_tokens_file(token):
    with open("tokens.txt", "r") as tokens_file:
        lines = tokens_file.readlines()
    with open("tokens.txt", "w") as tokens_file:
        for line in lines:
            if line.strip() != token:
                tokens_file.write(line)

def process_requirements_file(requirements_file_path):
    with open(requirements_file_path, "r") as requirements_file:
        lines = requirements_file.readlines()

    with open(requirements_file_path, "w") as requirements_file:
        for line in lines:
            # Remove version specifications from the line
            line = re.sub(r"[<>=].*", "", line).strip()
            requirements_file.write(f"{line}\n")

def create_fastapi_api(token, app_file, pickle_file=None, requirements_file=None):
    if not validate_token(token):
        print("Wrong token. Please buy a valid plan here: https://hypy.quantumopenai.com")
        return

    # Process requirements file to remove version specifications
    if requirements_file:
        process_requirements_file(requirements_file)

    # Generate a unique port using the hash of a temporary directory
    temp_dir = tempfile.mkdtemp()
    generated_port = hash(temp_dir) % 65536  # Ensure the port is within valid range

    # Create a temporary directory and copy the app file
    shutil.copy(app_file, temp_dir)

    # Copy optional files if provided
    if pickle_file:
        shutil.copy(pickle_file, temp_dir)
    if requirements_file:
        shutil.copy(requirements_file, temp_dir)
        subprocess.run(["pip", "install", "-r", os.path.join(temp_dir, "requirements.txt")])
        
    # Download and extract bore binary
    bore_url = "https://github.com/ekzhang/bore/releases/download/v0.5.0/bore-v0.5.0-x86_64-unknown-linux-musl.tar.gz"
    bore_tar = os.path.join(temp_dir, "bore.tar.gz")
    
    subprocess.run(["wget", bore_url, "-O", bore_tar])
    subprocess.run(["tar", "-xzf", bore_tar, "-C", temp_dir])
    bore_path = os.path.join(temp_dir, "bore")
    os.chmod(bore_path, 0o755)  # Add execute permissions

    # Run FastAPI app and bore in the background
    cmd = f"uvicorn {os.path.basename(app_file)[:-3]}:app --host 0.0.0.0 --port {generated_port} & {bore_path} local {generated_port} --to bore.pub --port {generated_port}"
    subprocess.Popen(cmd, shell=True, cwd=temp_dir)

    # Mark token as used and write to used-tokens.txt
    mark_token_as_used(token, generated_port)

    # Remove token from tokens.txt
    remove_token_from_tokens_file(token)

    # Return the API link
    api_link = f"http://api.quantumopenai.com:{generated_port}"
    return api_link


def validate_used_token(token, port):
    with open("used-tokens.txt", "r") as used_tokens_file:
        used_tokens = [line.strip() for line in used_tokens_file.readlines()]
        for used_token_port in used_tokens:
            used_token, used_port = used_token_port.split(" --")
            if token == used_token and int(port) == int(used_port):
                return True
        return False

def stop_fastapi_instance(port):
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == int(port):
                process = psutil.Process(conn.pid)
                process.terminate()
                print(f"Terminated process on port {port}")
                return
        print(f"No process found on port {port}")
    except Exception as e:
        print("Error:", e)

def deregister_api(token, port):
    if validate_used_token(token, port):
        stop_fastapi_instance(port)
        print("API Deregistered Successfully.")
    else:
        print("Invalid token or port. Please try again after some time.")


# Define your existing functions here

def main():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    username = "..."
    pass_key = "..."

    # Create a sidebar with a username, pass-key input fields, and a Login button
    st.sidebar.title("HyPy Cloud, Region-East")
    user_username = st.sidebar.text_input("Username")
    user_pass_key = st.sidebar.text_input("Pass-key", type="password")
    login_button = st.sidebar.button("Login")

    if (user_username == username and user_pass_key == pass_key) or login_button:
        
        # Create a sidebar with navigation links
        st.sidebar.markdown("---")  # Adding a horizontal line for spacing
        st.sidebar.title("Navigation")
        page = st.sidebar.selectbox("Go to:", ["Deploy API", "Deregister API"])

        if page == "Deploy API":
            deploy_page()

        elif page == "Deregister API":
            deregister_page()

        # Add spacing
        st.sidebar.markdown("---")  # Adding a horizontal line for spacing
        st.sidebar.markdown("---")  # Adding a horizontal line for spacing
        
        # Style the "Build Model" link (styled to look like a button)
        link_style = "display: block; width: 100%; padding: 10px 0; text-align: center; background: linear-gradient(135deg, #3154FF, #7D4DFF); color: white; border-radius: 6px; text-decoration: none; box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.15); font-weight: bold;"
        st.sidebar.markdown(f'<a href="http://api.quantumopenai.com:37442" style="{link_style}" target="_blank">Build Model</a>', unsafe_allow_html=True)
        st.sidebar.markdown("---")  # Adding a horizontal line for spacing
        
    
    elif user_username or user_pass_key:
        st.sidebar.error("Incorrect username or pass-key. Please try again.")

# ...

def deploy_page():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.title("FastAPI API Deployment")
        
    # Get user inputs
    token = st.text_input("Enter your token:")
    app_file = st.file_uploader("Upload your app.py file:", type=["py"])
    pickle_file = st.file_uploader("Upload your pickle file (optional):", type=["pkl"])
    requirements_file = st.file_uploader("Upload your requirements.txt file (optional):", type=["txt"])

    if st.button("Deploy API"):
        with st.spinner("Deploying your API..."):
            # Create temporary directories to hold the uploaded files
            temp_dir = tempfile.mkdtemp()
            
            # Save uploaded files to the temporary directory
            if app_file:
                app_file_path = os.path.join(temp_dir, "app.py")
                with open(app_file_path, "wb") as f:
                    f.write(app_file.read())
            else:
                st.warning("Please upload an app.py file.")

            if pickle_file:
                pickle_file_path = os.path.join(temp_dir, "pickle_file.pkl")
                with open(pickle_file_path, "wb") as f:
                    f.write(pickle_file.read())
            else:
                pickle_file_path = None

            if requirements_file:
                requirements_file_path = os.path.join(temp_dir, "requirements.txt")
                with open(requirements_file_path, "wb") as f:
                    f.write(requirements_file.read())
                process_requirements_file(requirements_file_path)
            else:
                requirements_file_path = None

            api_link = create_fastapi_api(token, app_file_path, pickle_file_path, requirements_file_path)
            st.success(f"API deployed successfully! You can access it at: {api_link}")
            
            # Add a button to copy the API link
            if api_link:
                st.write("API Link:")
                st.code(api_link)

            # Display additional message
            st.info("Please keep the API link safe or take a screenshot.")

def deregister_page():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.title("Deregister FastAPI API")

    # Get user inputs for deregistering
    token = st.text_input("Enter the token:")
    port = st.text_input("Enter the port:")

    if st.button("Deregister API"):
        with st.spinner("Deregistering API..."):
            deregister_api(token, port)
            st.success("API Deregistered Successfully.")

if __name__ == "__main__":
    main()
