import os, random, requests
OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY","")
def get_weather(lat,lon):
    if not OPENWEATHER_API_KEY: return {"rainfall_mm":800,"tmin":12,"tmax":35}
    try:
        r=requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric",timeout=10).json()
        return {"rainfall_mm": r.get("rain",{}).get("1h",0)*24*30 if r.get("rain") else 60, "tmin": r.get("main",{}).get("temp_min",18), "tmax": r.get("main",{}).get("temp_max",32)}
    except Exception: return {"rainfall_mm":800,"tmin":12,"tmax":35}
def get_soil(lat,lon): return {"pH":6.6,"organic_carbon_pct":0.9,"texture":"loam"}
def get_ndvi(lat,lon): return round(random.uniform(0.05,0.6),2)
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError
AWS_S3_BUCKET=os.getenv("AWS_S3_BUCKET"); AWS_S3_REGION=os.getenv("AWS_S3_REGION","ap-south-1")
def s3_client():
    if not AWS_S3_BUCKET: return None
    try: return boto3.client("s3", region_name=AWS_S3_REGION)
    except Exception: return None
def s3_upload_bytes(key,data,content_type="application/octet-stream"):
    c=s3_client()
    if not c: return None
    try:
        c.put_object(Bucket=AWS_S3_BUCKET, Key=key, Body=data, ContentType=content_type, ACL="public-read")
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{key}"
    except (BotoCoreError, NoCredentialsError, ClientError): return None
