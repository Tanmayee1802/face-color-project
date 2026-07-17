import cv2
import mediapipe as mp
import numpy as np
import colorsys
import os
import json
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from sklearn.cluster import KMeans
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
_gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
print(f"DEBUG: GEMINI_API_KEY loaded = {bool(GEMINI_API_KEY)}, length = {len(GEMINI_API_KEY) if GEMINI_API_KEY else 0}")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

if not os.path.exists(MODEL_PATH):
    print("Downloading face landmarker model...")
    urllib.request.urlretrieve(
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
        MODEL_PATH
    )
    print("Model downloaded!")

# --- face outline polygon ---
FACE_OVAL = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
    361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
    176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
    162, 21, 54, 103, 67, 109
]

# --- regions to exclude from skin ---
LEFT_EYE = [
    33, 7, 163, 144, 145, 153, 154, 155,
    133, 173, 157, 158, 159, 160, 161, 246
]
RIGHT_EYE = [
    362, 382, 381, 380, 374, 373, 390, 249,
    263, 466, 388, 387, 386, 385, 384, 398
]
LEFT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
RIGHT_EYEBROW = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]
NOSE = [1, 2, 98, 327, 168, 195, 197, 4, 240, 97, 2]
LIPS_OUTER = [
    61, 146, 91, 181, 84, 17, 314,
    405, 321, 375, 291, 409, 270,
    269, 267, 0, 37, 39, 40, 185
]

# --- lip polygon ---
LIPS_ALL = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
    375, 321, 405, 314, 17, 84, 181, 91, 146,
    78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308
]


def get_polygon_mask(landmarks, indices, h, w):
    """create a filled polygon mask from landmark indices"""
    points = []
    for idx in indices:
        lm = landmarks[idx]
        px = int(lm.x * w)
        py = int(lm.y * h)
        points.append([px, py])
    points = np.array(points, dtype=np.int32)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask


def get_skin_mask(landmarks, h, w):
    """face polygon minus eyes, eyebrows, nose, lips"""
    # start with full face
    face_mask = get_polygon_mask(landmarks, FACE_OVAL, h, w)

    # subtract exclusion zones
    for region in [LEFT_EYE, RIGHT_EYE, LEFT_EYEBROW, RIGHT_EYEBROW, NOSE, LIPS_OUTER]:
        exclude = get_polygon_mask(landmarks, region, h, w)
        face_mask = cv2.subtract(face_mask, exclude)

    return face_mask


def get_lip_mask(landmarks, h, w):
    """filled lip polygon"""
    return get_polygon_mask(landmarks, LIPS_ALL, h, w)


def get_dominant_color(pixels, n_clusters):
    """K-means on pixel array, return dominant cluster color"""
    if len(pixels) < n_clusters:
        return pixels.mean(axis=0).astype(int)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    counts = np.bincount(kmeans.labels_)
    return colors[np.argmax(counts)]


def rgb_to_hsv_degrees(rgb):
    r, g, b = np.array(rgb) / 255.0
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s, v


def get_undertone(r, g, b):
    """
    improved undertone detection using channel ratios
    instead of simple HSV hue threshold
    """
    total = r + g + b + 1e-5

    warm_score = (r - b) / 255.0        # warm = red dominates over blue
    cool_score = (b - r) / 255.0        # cool = blue dominates over red
    neutral_score = 1 - abs(warm_score) # neutral = balanced

    if warm_score > 0.08:
        result = "WARM", warm_score
    elif cool_score > 0.08:
        result = "COOL", cool_score
    else:
        result = "NEUTRAL", neutral_score

    return result[0], result[1], {
        "warm_score": round(float(warm_score), 4),
        "cool_score": round(float(cool_score), 4),
        "neutral_score": round(float(neutral_score), 4),
    }


def correct_lighting(img_rgb):
    """
    simple white balance correction to normalize lighting
    makes results consistent across different lighting conditions
    """
    img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

    # normalize L channel to target brightness
    l, a, b = cv2.split(img_lab)
    target_l = 128.0
    current_l = l.mean()
    scale = target_l / (current_l + 1e-5)
    l = np.clip(l * scale, 0, 255)

    img_lab = cv2.merge([l, a, b]).astype(np.uint8)
    return cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB)


def classify_season(undertone, skin_val):
    if undertone == "WARM":
        return "Spring" if skin_val >= 0.65 else "Autumn"
    else:
        return "Summer" if skin_val >= 0.60 else "Winter"


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


def get_ai_insights(season, undertone, skin_color, lip_color, undertone_scores):
    """
    Calls Gemini to generate:
    1. A short color-theory explanation grounded in this person's actual measured values
       (not a generic template) - this is the explainability layer.
    2. Budget-friendly product suggestions from accessible Indian drugstore brands,
       instead of only luxury picks - this is the accessibility layer.
    Falls back to a static (non-AI) message if no API key is configured or the call fails,
    so the app never breaks in front of judges.
    """
    fallback = {
        "ai_reasoning": (
            f"Your skin reads as {undertone.lower()} because your red channel value "
            f"is measurably higher than blue in the pixels sampled from your cheeks and "
            f"forehead. Combined with a brightness (V) value that places you in the "
            f"{season} range, warm/cool color families in that season tend to harmonize "
            f"with your natural coloring rather than clash against it."
        ),
        "budget_picks": [
            {"item": "Check Lakmé, Sugar Cosmetics, or Insight Cosmetics", "note": "Affordable Indian brands with shades close to this palette"},
        ],
        "ai_generated": False,
    }

    if not _gemini_client:
        return fallback

    prompt = f"""You are a color-theory assistant for a free student-built app. A user's photo was analyzed with computer vision, producing these MEASURED values (not guesses):

- Detected season: {season}
- Detected undertone: {undertone}
- Undertone confidence scores: warm={undertone_scores['warm_score']}, cool={undertone_scores['cool_score']}, neutral={undertone_scores['neutral_score']}
- Measured skin RGB: {list(skin_color)}
- Measured natural lip RGB: {list(lip_color)}

Return ONLY valid JSON (no markdown fences, no preamble) matching exactly this shape:
{{
  "ai_reasoning": "2-3 sentences explaining WHY this season/undertone follows from these specific measured values, using real color theory (complementary/analogous relationships, warm-cool contrast). Reference the actual numbers given. Do not use generic filler.",
  "budget_picks": [
    {{"item": "a specific type of product (e.g. 'terracotta lipstick')", "note": "1 or 2 affordable Indian drugstore brands (Lakmé, Sugar Cosmetics, Insight, Maybelline, Faces Canada, Colorbar) known for having a shade in this color family, with an approx price range in INR"}},
    {{"item": "...", "note": "..."}},
    {{"item": "...", "note": "..."}}
  ]
}}"""

    try:
        response = _gemini_client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
        )
        raw = response.text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)
        parsed["ai_generated"] = True
        return parsed
    except Exception as e:
        print(f"Gemini call failed, using fallback: {e}")
        return fallback


def analyze_image(img_bytes: bytes) -> dict:
    # --- decode image ---
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # --- lighting correction ---
    img_rgb = correct_lighting(img_rgb)

    h, w = img_rgb.shape[:2]

    # --- mediapipe ---
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        results = landmarker.detect(mp_image)

        if not results.face_landmarks:
            return {"error": "No face detected. Please upload a clear front-facing photo."}

        landmarks = results.face_landmarks[0]

        # --- skin: all pixels inside face polygon minus exclusion zones ---
        skin_mask = get_skin_mask(landmarks, h, w)
        skin_pixels = img_rgb[skin_mask == 255]
        print(f"Skin pixels extracted: {len(skin_pixels)}")  # will be 40k+ now

        if len(skin_pixels) < 10:
            return {"error": "Could not extract enough skin pixels. Try a clearer photo."}

        skin_color = get_dominant_color(skin_pixels, n_clusters=4)
        skin_hue, skin_sat, skin_val = rgb_to_hsv_degrees(skin_color)

        # --- improved undertone detection ---
        undertone, confidence, undertone_scores = get_undertone(*skin_color)

        # --- lip: all pixels inside lip polygon ---
        lip_mask = get_lip_mask(landmarks, h, w)
        lip_pixels = img_rgb[lip_mask == 255]
        print(f"Lip pixels extracted: {len(lip_pixels)}")

        lip_color = get_dominant_color(lip_pixels, n_clusters=2) if len(lip_pixels) >= 2 else skin_color

        # --- season + palette ---
        season = classify_season(undertone, skin_val)
        palette = get_palette(season)

        # --- AI reasoning + budget-friendly picks (Gemini) ---
        ai_insights = get_ai_insights(season, undertone, skin_color, lip_color, undertone_scores)

        return {
            "season": season,
            "undertone": undertone,
            "description": palette["description"],
            "skin_color": skin_color.tolist(),
            "lip_color": lip_color.tolist(),
            "skin_pixels_used": len(skin_pixels),
            "clothing": [{"name": n, "rgb": c} for n, c in palette["clothing"]],
            "lipstick": [{"name": n, "rgb": c} for n, c in palette["lipstick"]],
            "avoid": palette["avoid"],
            # --- explainability panel data ---
            "explainability": {
                "skin_hue": round(skin_hue, 1),
                "skin_saturation": round(skin_sat, 3),
                "skin_brightness": round(skin_val, 3),
                "undertone_scores": undertone_scores,
            },
            # --- AI reasoning + accessible product picks ---
            "ai_reasoning": ai_insights["ai_reasoning"],
            "budget_picks": ai_insights["budget_picks"],
            "ai_generated": ai_insights["ai_generated"],
        }