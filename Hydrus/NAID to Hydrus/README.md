## Python File Instructions

### Prerequisites
1. **Python Installation**: Ensure you have Python installed on your system. You can download and install Python from the [official Python website](https://www.python.org/downloads/). Version must be 3.9+

2. **Library Installation**:
   - Install the `hydrus-api` library:
     ```bash
     pip install hydrus-api
     ```
   - Install the `pyexiftool` library:
     ```bash
     pip install pyexiftool
     ```

3. **Hydrus API Keys**:
   - Obtain a **File Domain Service Key** from your Hydrus Client.
   - Obtain an **Access Key** from your Hydrus Client.

### Configuration
When running the Python file, you need to configure the following parameters:
- **Import Path**: Specify the path to the import file.
- **Service Key**: Use the File Domain Service Key obtained from Hydrus.
- **Access Key**: Use the Access Key obtained from Hydrus.

### Running the Python File
1. Open a terminal or command prompt.

2. Navigate to the directory containing the Python file.

3. Run the Python file using the following command:
   ```bash
   python your_file_name.py
   ```

4. Follow the prompts to interact with the program.
   
### Changing Configuration
If you need to change the configuration (import path, service key, access key), you can do so by editing the appropriate variables in the Python file directly.

### Additional Notes
- Ensure you have proper permissions to access the files and directories specified in the import path.
- Make sure to keep your Hydrus API keys secure and do not share them with unauthorized users.
- Replace `your_file_name.py` with the actual name of your Python file.