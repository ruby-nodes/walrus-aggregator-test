#!/usr/bin/env python3
import random
import string
import time
import threading
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Configuration variables
PUBLISHER_URL = "https://walrus-publisher.rubynodes.io"     # Replace with the actual publisher endpoint
AGGREGATOR_URL = "https://walrus-aggregator.rubynodes.io"    # Replace with the actual aggregator endpoint 

# Blobs config
BLOB_MAX_SIZE = 1000   # in kilobytes
BLOB_MIN_SIZE = 900   # in kilobytes
BLOBS_NUM = 5        # number of blobs to generate and upload

# Settings
MAX_THREADS = 8       # number of threads to run uploads in parallel
EXPORT_RESULTS = True  # set to True to export summary results to JSON

# Lock for thread-safe printing
print_lock = threading.Lock()

def colored_print(message, color=Fore.WHITE):
    """Thread-safe colored print to terminal."""
    with print_lock:
        print(color + message + Style.RESET_ALL)

def generate_random_blob():
    """
    Generates a random blob. The blob size (in bytes) is chosen randomly between 1 and BLOB_MAX_SIZE * 1024.
    The content may be random binary data or a random string.
    """
    # Determine blob size in bytes
    max_bytes = BLOB_MAX_SIZE * 1024
    min_bytes = BLOB_MIN_SIZE * 1024
    size = random.randint(min_bytes, max_bytes)
    
    # Randomly decide to generate binary or text content (50/50 chance)
    if random.choice([True, False]):
        # Generate random binary data
        blob = bytearray(random.getrandbits(8) for _ in range(size))
    else:
        # Generate random string content: using letters, digits, and punctuation
        choices = string.ascii_letters + string.digits + string.punctuation + " " * 5
        blob = ''.join(random.choice(choices) for _ in range(size))
        # Convert string to bytes (UTF-8)
        blob = blob.encode('utf-8')
    
    return blob

def upload_blob(blob_data, blob_number):
    """
    Uploads blob_data to the publisher endpoint.
    Measures the upload response time.
    Returns a tuple (blob_id, upload_time, blob_size_kb).
    """
    headers = {
        "Content-Type": "application/octet-stream"
    }
    start_time = time.time()
    size_kb = len(blob_data) / 1024.0 # in kb
    try:
        response = requests.put(PUBLISHER_URL + "/v1/blobs", data=blob_data)
        response_time = time.time() - start_time
    except Exception as e:
        colored_print(f"[UPLOAD #{blob_number}] Error during upload: {e}", Fore.RED)
        return None, None

    try:
        response_json = response.json()
    except Exception as e:
        colored_print(f"[UPLOAD #{blob_number}] Failed to parse JSON response: {e}", Fore.RED)
        return None, response_time

    blob_id = None
    if "newlyCreated" in response_json:
        blob_id = response_json["newlyCreated"]["blobObject"]["blobId"]
        colored_print(f"[UPLOAD #{blob_number}] Uploaded successfully. Blob created with id: {blob_id}", Fore.GREEN)
    elif "alreadyCertified" in response_json:
        blob_id = response_json["alreadyCertified"]["blobId"]
        colored_print(f"[UPLOAD #{blob_number}] Blob already exists with id: {blob_id}", Fore.YELLOW)
    else:
        colored_print(f"[UPLOAD #{blob_number}] Unexpected response format: {response_json}", Fore.RED)
    
    colored_print(f"[UPLOAD #{blob_number}] Response time: {response_time:.3f} seconds", Fore.CYAN)
    colored_print(f"[UPLOAD #{blob_number}] Blob size: {size_kb:.2f} kB", Fore.CYAN)
    colored_print("", Fore.WHITE)
    return blob_id, response_time, size_kb

def download_blob(blob_id, download_number, attempt):
    """
    Downloads a blob from the aggregator endpoint by appending blob_id to the URL.
    Measures the download response time.
    Returns the response time in seconds.
    """
    url = AGGREGATOR_URL + "/v1/blobs/" + blob_id
    start_time = time.time()
    try:
        response = requests.get(url)
        download_time = time.time() - start_time
        colored_print(f"[DOWNLOAD {download_number} Attempt {attempt}] Blob ID - {blob_id} - Response time: {download_time:.3f} seconds", 
                      Fore.MAGENTA if attempt == 1 else Fore.GREEN)
    except Exception as e:
        colored_print(f"[DOWNLOAD {download_number} Attempt {attempt}] Error during download: {e}", Fore.RED)
        download_time = None
    return download_time

def main():
    colored_print("Starting stress test...", Fore.WHITE)
    
    # Data structure to store results
    results = []
    
    # Use ThreadPoolExecutor for concurrent uploads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_blob = {}
        for i in range(1, BLOBS_NUM + 1):
            blob_data = generate_random_blob()
            future = executor.submit(upload_blob, blob_data, i)
            future_to_blob[future] = i

        # Gather upload results
        for future in as_completed(future_to_blob):
            blob_number = future_to_blob[future]
            blob_id, upload_time, blob_size_kb = future.result()
            if blob_id is None:
                colored_print(f"[RESULT #{blob_number}] Skipping downloads due to upload error.", Fore.RED)
                continue

            # Perform two downloads for each blob id
            download_time_1 = download_blob(blob_id, blob_number, attempt=1)
            download_time_2 = download_blob(blob_id, blob_number, attempt=2)
            colored_print("", Fore.WHITE)
            results.append({
                 "blob_number": blob_number,
                 "blob_id": blob_id,
                 "upload_time": upload_time,
                 "blob_size_kb": blob_size_kb,
                 "download_time_first": download_time_1,
                 "download_time_cached": download_time_2
             })
            

     # Summary results printing
    colored_print("\n=== Stress Test Summary ===", Fore.WHITE)
    all_download_times = []
    for res in sorted(results, key=lambda x: x["blob_number"]):
        all_download_times.append(res['download_time_cached'])
        colored_print(f"Blob #{res['blob_number']} - ID: {res['blob_id']}", Fore.WHITE)
        colored_print(f"   Upload time:         {res['upload_time']:.3f} seconds", Fore.CYAN)
        colored_print(f"   Blob size:           {res['blob_size_kb']:.2f} kB", Fore.YELLOW)
        colored_print(f"   Download (first):    {res['download_time_first']:.3f} seconds", Fore.MAGENTA)
        colored_print(f"   Download (cached):   {res['download_time_cached']:.3f} seconds", Fore.GREEN)
    
    if all_download_times:
        shortest = min(all_download_times)
        longest = max(all_download_times)
        colored_print("\nOverall Download Times From Cache:", Fore.WHITE)
        colored_print(f"   Shortest: {shortest:.3f} seconds", Fore.GREEN)
        colored_print(f"   Longest:  {longest:.3f} seconds", Fore.RED)
    if EXPORT_RESULTS:
        try:
            with open("results.json", "w") as f:
                json.dump(results, f, indent=4)
            colored_print("\nSummary results exported to results.json", Fore.WHITE)
        except Exception as e:
            colored_print(f"\nFailed to export summary results: {e}", Fore.RED)

if __name__ == '__main__':
    main()
