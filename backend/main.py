from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from analyzer import analyze_image

app = FastAPI()

# CORS lets the React frontend talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "Face Color Analysis API is running"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    img_bytes = await file.read()   # read uploaded photo as bytes
    result = analyze_image(img_bytes)  # run your analysis
    return result                   # FastAPI auto-converts dict to JSON