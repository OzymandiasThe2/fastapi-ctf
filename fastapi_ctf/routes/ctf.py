import base64
import codecs
import hashlib
import json
import os
import subprocess
import tempfile
import magic

from fastapi import APIRouter, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import b64decode

router = APIRouter()

@router.post("/BASE64-decrypt")
def decrypt(ciphertext: str):
    decrypted_data = {}

    # BASE64 decryption
    try:
        decrypted_data['BASE64'] = base64.b64decode(ciphertext.encode()).decode()
    except:
        decrypted_data['BASE64'] = 'Decoding failed for BASE64.'

    # TODO Add more decryption techniques here...

    return decrypted_data

@router.post("/file_analysis")
async def file_analysis(file: UploadFile = File(...)):
    # Read the contents of the uploaded file
    contents = await file.read()

    # Compute the MD5 hash of the file
    md5 = hashlib.md5(contents).hexdigest()

    # Determine the file type using the magic library
    file_type = magic.from_buffer(contents)

    # Determine the file size in bytes
    file_size = len(contents)

    # Return the file analysis results
    return {"md5": md5, "file_type": file_type, "file_size": file_size}


# @router.post("/stegsnow")
# async def analyze(file: UploadFile = File(...)):
#         # Save the uploaded file to a temporary location
#     with tempfile.NamedTemporaryFile(prefix="temp_fastapifile_", delete=False) as temp_file:
#         temp_file.write(await file.read())
#         temp_file.flush()
#         results = {}
#         try:
#             process = subprocess.run(['stegsnow', '-C', '-p', temp_file.name], capture_output=True)
#             results['stegsnow'] = process.stdout.decode()
#         except FileNotFoundError:
#             results['stegsnow'] = "Error: stegsnow not found."
#         # Remove the temporary file
#         temp_file.close()
#         subprocess.run(['rm', temp_file.name])
#         return results

@router.post("/strings")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        output = subprocess.check_output(["strings", file.filename])
    except subprocess.CalledProcessError as e:
        if not e.output.strip():
            return {"filename": file.filename, "strings_output": "no strings in file"}
        else:
            raise
    output_lines = output.decode().splitlines()
    return {"filename": file.filename, "strings_output": output_lines}

@router.post("/exiftool/")
async def create_upload_file(file: UploadFile = File(...)):
    output = subprocess.check_output(["exiftool", "-j", file.filename])
    exif_data = json.loads(output.decode())
    return JSONResponse(content={"filename": file.filename, "exiftool_output": exif_data})

@router.post("/zsteg/")
async def create_upload_file(file: UploadFile = File(...)):
    output = subprocess.check_output(["zsteg", file.filename])
    output_lines = output.decode().splitlines()
    return {"filename": file.filename, "zsteg_output": output_lines}

@router.post("/nmap/")
async def run_nmap(target: str = Query(...)):
    try:
        output = subprocess.check_output(["nmap", target], stderr=subprocess.STDOUT)
        result = {"result": output.decode('utf-8')}
    except subprocess.CalledProcessError as e:
        result = {"error": e.output.decode('utf-8')}
    return {"message": "Scan complete", "scan_results": json.loads(json.dumps(result, indent=4))}

@router.post("/unshadow/")
async def unshadow(passwd_file: UploadFile = File(...), shadow_file: UploadFile = File(...)):
    # Get file extension (if there is any)
    ext1 = os.path.splitext(passwd_file.filename)[1]
    ext2 = os.path.splitext(shadow_file.filename)[1]

    # Save files with appropriate names
    with open(f"passwd{ext1}", "wb") as f1, open(f"shadow{ext2}", "wb") as f2:
        contents1 = await passwd_file.read()
        contents2 = await shadow_file.read()
        f1.write(contents1)
        f2.write(contents2)

    # Run unshadow command and capture output
    command = f"unshadow passwd{ext1} shadow{ext2} > unshadowed.txt"
    output = subprocess.run(command, shell=True)

    # Read the contents of the file and return it as a response
    with open('unshadowed.txt', 'r') as f:
        content = f.read().splitlines()

    return {'unshadowed': content}


