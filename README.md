# Stress Test Script

This Python script performs a stress test on a system by uploading randomly generated blobs of data to a publisher endpoint and then downloading the blobs from an aggregator endpoint. It measures the response times for both upload and download operations, and prints a summary of the results including details such as upload time, blob size, and download times. The script also optionally exports the summary results to a JSON file.

## Features

- **Random Blob Generation:**  
  Generates random blobs with sizes in a specified range (in kilobytes). Blobs can be either binary data or UTF-8 encoded strings.

- **Parallel Uploads:**  
  Uses a thread pool (configurable via `MAX_THREADS`) to perform uploads concurrently to the publisher endpoint.

- **Dual Download Testing:**  
  Each blob is downloaded twice from the aggregator endpoint:
  - **First Download:** Simulates an uncached request.
  - **Second Download:** Simulates a cached request to compare performance.

- **Response Time Measurement:**  
  Measures and displays the response times for both upload and download operations.

- **Colorful Terminal Output:**  
  Uses the `colorama` library for color-coded terminal messages, making it easier to identify statuses and errors.

- **Summary Export:**  
  Optionally exports the summary results to a JSON file if `EXPORT_RESULTS` is set to `True`.

## Prerequisites

- Python 3.x
- Required Python packages:
  - `requests`
  - `colorama`

You can install the required packages using pip:

```bash
pip install requests colorama
```

Configuration Variables
-----------------------

At the top of the script, you can configure the following variables:

*   **PUBLISHER\_URL**The URL of the publisher endpoint. Replace with your actual endpoint.
    
*   **AGGREGATOR\_URL**The URL of the aggregator endpoint. Ensure that it includes a trailing slash.
    
*   **BLOB\_MAX\_SIZE**The maximum size of a blob in kilobytes.
    
*   **BLOB\_MIN\_SIZE**The minimum size of a blob in kilobytes.
    
*   **BLOBS\_NUM**The number of blobs to generate and upload.
    
*   **MAX\_THREADS**The number of threads to use for parallel uploads.
    
*   **EXPORT\_RESULTS**Set to True to export the summary results to a JSON file named stress\_test\_summary.json.
    

Usage
-----

1. Clone the repository
```
git clone https://github.com/ruby-nodes/walrus-aggregator-test.git
cd walrus-aggregator-test
```
2. Configure the script:

Open the script file and update the configuration variables (PUBLISHER_URL, AGGREGATOR_URL, etc.) as needed.

3. Run the script:
```bash
python3 stress_test.py
```
The script will output the progress and results in the terminal, including detailed response times for each upload and download. If enabled, the summary will be saved to `results.json`.

Output
------

* **Terminal Output:** The script prints messages with color coding for different types of events:
    
    *   **Green:** Successful uploads and short download times.
        
    *   **Yellow:** Existing blobs and blob size details.
        
    *   **Magenta & Green:** First and cached download response times.
        
    *   **Red:** Errors encountered during uploads/downloads.
        
* **JSON Summary (Optional):** If EXPORT\_RESULTS is set to True, a JSON file named stress\_test\_summary.json will be created, containing an array of objects with the following keys:
    
    *   blob\_number
        
    *   blob\_id
        
    *   upload\_time
        
    *   blob\_size\_kb
        
    *   download\_time\_first
        
    *   download\_time\_cached

Contributing
------------

Contributions are welcome! Please fork the repository and create a pull request with your improvements or bug fixes.
