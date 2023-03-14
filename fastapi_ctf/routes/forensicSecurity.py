import subprocess
import hashlib
from fastapi import APIRouter, UploadFile, File, Query


router = APIRouter()

@router.post("/fsstat")
async def create_upload_file(file: UploadFile = File(...)):
    fsstat_command = f"fsstat {UploadFile}"
    output = subprocess.check_output(fsstat_command, shell=True)
    output_lines = output.decode().splitlines()
    return {"message": output_lines}


@router.post("/calculate_sha256")
async def create_upload_file(file: UploadFile = File(...)):
    with open(file, 'rb') as f:
        data = f.read()
    sha256_hash = hashlib.sha256(data).hexdigest()
    return {"sha256_hash": sha256_hash}