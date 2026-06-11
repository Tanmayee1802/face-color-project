import cv2
import mediapipe as mp
import numpy as np
import colorsys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from sklearn.cluster import KMeans
import os

import urllib.request

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    print("Downloading face landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        MODEL_PATH
    )
    print("Model downloaded!")

SKIN_INDICES = [
    10, 67, 69, 104, 108, 151, 337, 299, 333, 298,
    50, 101, 118, 117, 116, 123, 147, 187, 207,
    280, 330, 347, 346, 345, 352, 376, 411, 427,
]

LIP_INDICES = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
    375, 321, 405, 314, 17, 84, 181, 91, 146, 61,
    78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308,
]

def get_dominant_color(pixels, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(kmeans.labels_)
    return colors[np.argmax(counts)]

def rgb_to_hsv_degrees(rgb):
    r, g, b = rgb / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v

def classify_season(hue, sat, val, undertone):
    if undertone == "WARM":
        return "Spring" if val >= 0.70 and sat <= 0.45 else "Autumn"
    else:
        return "Summer" if val >= 0.65 and sat <= 0.45 else "Winter"

def get_palette(season):
    palettes = {
        "Spring": {
            "description": "Warm, light, fresh. You suit clear warm colours with a light airy feel.",
            "clothing": [
                ("Peach",         [255, 180, 140]),
                ("Warm coral",    [255, 127, 100]),
                ("Golden yellow", [255, 200,  80]),
                ("Warm green",    [120, 180,  80]),
                ("Camel",         [200, 160, 110]),
                ("Ivory",         [255, 248, 220]),
                ("Warm red",      [210,  60,  40]),
                ("Light orange",  [255, 160,  80]),
            ],
            "lipstick": [
                ("Peachy coral",  [220, 120,  90]),
                ("Warm pink",     [210, 100, 110]),
                ("Salmon",        [215, 130, 100]),
                ("Warm nude",     [200, 150, 120]),
                ("Light coral",   [230, 110,  90]),
            ],
            "avoid": ["Cool gray", "Icy blue", "Pure white", "Black", "Cool purple"]
        },
        "Autumn": {
            "description": "Warm, rich, earthy. You suit deep muted tones with golden warmth.",
            "clothing": [
                ("Rust",          [180,  70,  30]),
                ("Olive green",   [ 90, 130,  50]),
                ("Burnt orange",  [200,  90,  40]),
                ("Warm brown",    [140,  85,  50]),
                ("Mustard",       [200, 160,  40]),
                ("Terracotta",    [190, 100,  70]),
                ("Dark olive",    [ 70, 100,  40]),
                ("Caramel",       [190, 135,  75]),
            ],
            "lipstick": [
                ("Terracotta",    [196,  98,  58]),
                ("Warm red",      [180,  48,  35]),
                ("Peachy nude",   [201, 143, 110]),
                ("Burnt coral",   [210,  90,  60]),
                ("Warm brown",    [139,  69,  40]),
            ],
            "avoid": ["Cool pink", "Icy gray", "Navy blue", "Pure black", "Lavender"]
        },
        "Summer": {
            "description": "Cool, soft, muted. You suit dusty cool tones with a gentle feel.",
            "clothing": [
                ("Dusty rose",    [200, 150, 160]),
                ("Soft blue",     [130, 170, 200]),
                ("Lavender",      [180, 160, 210]),
                ("Soft gray",     [180, 180, 190]),
                ("Cool pink",     [220, 160, 180]),
                ("Powder blue",   [170, 200, 220]),
                ("Mauve",         [180, 140, 160]),
                ("Soft white",    [240, 238, 245]),
            ],
            "lipstick": [
                ("Mauve",         [180, 100, 130]),
                ("Dusty rose",    [185, 110, 120]),
                ("Cool pink",     [210,  80, 120]),
                ("Soft berry",    [160,  80, 110]),
                ("Rose",          [195,  90, 110]),
            ],
            "avoid": ["Orange", "Warm brown", "Gold", "Olive", "Rust"]
        },
        "Winter": {
            "description": "Cool, deep, high contrast. You suit bold clear colours and sharp contrasts.",
            "clothing": [
                ("True red",      [200,  20,  20]),
                ("Royal blue",    [ 30,  60, 180]),
                ("Pure black",    [ 20,  20,  20]),
                ("Pure white",    [245, 245, 245]),
                ("Deep purple",   [ 80,  20, 120]),
                ("Emerald",       [ 20, 130,  80]),
                ("Hot pink",      [220,  40, 120]),
                ("Navy",          [ 20,  30,  80]),
            ],
            "lipstick": [
                ("Berry",         [150,  40,  80]),
                ("True red",      [190,  20,  40]),
                ("Plum",          [120,  40,  80]),
                ("Deep rose",     [170,  50,  90]),
                ("Cool fuchsia",  [200,  40, 130]),
            ],
            "avoid": ["Orange", "Warm beige", "Mustard", "Olive", "Camel"]
        }
    }
    return palettes[season]

def analyze_image(img_bytes: bytes) -> dict:
    """
    main function — receives image as bytes, returns full analysis as dict
    this is what FastAPI will call
    """

    # --- decode bytes into image ---
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    # --- mediapipe ---
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        results = landmarker.detect(mp_image)

        if not results.face_landmarks:
            return {"error": "No face detected. Please upload a clear front-facing photo."}

        landmarks = results.face_landmarks[0]

        # --- skin ---
        skin_pixels = []
        for idx in SKIN_INDICES:
            lm = landmarks[idx]
            px, py = int(lm.x * w), int(lm.y * h)
            skin_pixels.append(img_rgb[py, px])
        skin_pixels = np.array(skin_pixels)
        skin_color = get_dominant_color(skin_pixels, 3)
        skin_hue, skin_sat, skin_val = rgb_to_hsv_degrees(skin_color)

        # --- lips ---
        lip_pixels = []
        for idx in LIP_INDICES:
            lm = landmarks[idx]
            px, py = int(lm.x * w), int(lm.y * h)
            lip_pixels.append(img_rgb[py, px])
        lip_pixels = np.array(lip_pixels)
        lip_color = get_dominant_color(lip_pixels, 2)

        # --- undertone ---
        if 10 <= skin_hue <= 45 and skin_sat > 0.2:
            undertone = "WARM"
        elif 180 <= skin_hue <= 280:
            undertone = "COOL"
        else:
            undertone = "NEUTRAL"

        # --- season + palette ---
        season = classify_season(skin_hue, skin_sat, skin_val, undertone)
        palette = get_palette(season)

        # --- return as dict (FastAPI converts to JSON) ---
        return {
            "season": season,
            "undertone": undertone,
            "description": palette["description"],
            "skin_color": skin_color.tolist(),
            "lip_color": lip_color.tolist(),
            "clothing": [{"name": n, "rgb": c} for n, c in palette["clothing"]],
            "lipstick": [{"name": n, "rgb": c} for n, c in palette["lipstick"]],
            "avoid": palette["avoid"]
        }