import cv2
import mediapipe as mp
import numpy as np
from sklearn.cluster import KMeans
import os

# --- load model ---
model_path = "face_landmarker.task"

# --- load image ---
img = cv2.imread("tan.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]

# --- mediapipe setup ---
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

with vision.FaceLandmarker.create_from_options(options) as landmarker:
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    results = landmarker.detect(mp_image)

    if results.face_landmarks:
        landmarks = results.face_landmarks[0]

        # --- cheek and forehead landmark indices ---
        SKIN_INDICES = [
            # forehead
            10, 67, 69, 104, 108, 151, 337, 299, 333, 298,
            # left cheek
            50, 101, 118, 117, 116, 123, 147, 187, 207,
            # right cheek
            280, 330, 347, 346, 345, 352, 376, 411, 427,
        ]

        # --- extract pixel colors at those landmarks ---
        skin_pixels = []
        img_copy = img_rgb.copy()

        for idx in SKIN_INDICES:
            lm = landmarks[idx]
            px = int(lm.x * w)
            py = int(lm.y * h)

            # draw dot so we can see which points we used
            cv2.circle(img_copy, (px, py), radius=6, color=(255, 100, 0), thickness=-1)

            # grab the color at this pixel
            color = img_rgb[py, px]
            skin_pixels.append(color)

        skin_pixels = np.array(skin_pixels)
        print(f"Collected {len(skin_pixels)} skin pixels")
        print("Sample colors (RGB):", skin_pixels[:3])

        # --- K-means: find 3 dominant colors ---
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(skin_pixels)

        # cluster centers are the dominant colors
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_

        # find which cluster has the most pixels
        counts = np.bincount(labels)
        dominant_idx = np.argmax(counts)
        dominant_color = colors[dominant_idx]

        print(f"\nDominant skin color (RGB): {dominant_color}")
        print(f"R={dominant_color[0]}  G={dominant_color[1]}  B={dominant_color[2]}")

        # --- convert to HSV ---
        import colorsys
        r, g, b = dominant_color / 255.0
        hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
        hue_deg = hue * 360
        print(f"\nHue: {hue_deg:.0f}°  Saturation: {sat*100:.0f}%  Value: {val*100:.0f}%")

        # --- undertone ---
        if 10 <= hue_deg <= 45 and sat > 0.2:
            undertone = "WARM"
        elif 180 <= hue_deg <= 280:
            undertone = "COOL"
        else:
            undertone = "NEUTRAL"
        print(f"Undertone: {undertone}")

        # save image with skin points marked
        cv2.imwrite("skin_points.jpg", cv2.cvtColor(img_copy, cv2.COLOR_RGB2BGR))
        print("\nSaved skin_points.jpg — orange dots show which pixels we analysed!")
# ============================================================
    # PHASE 2B — Lip Color Extraction
    # ============================================================

    # --- Step 9: Define lip landmark indices ---
    # these trace the outer edge of both lips
    LIP_INDICES = [
        # outer upper lip
        61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
        # outer lower lip
        375, 321, 405, 314, 17, 84, 181, 91, 146, 61,
        # inner lip line
        78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308,
    ]

    # --- Step 10: Extract lip pixel colors ---
    lip_pixels = []
    for idx in LIP_INDICES:
        lm = landmarks[idx]
        px = int(lm.x * w)
        py = int(lm.y * h)
        color = img_rgb[py, px]
        lip_pixels.append(color)

    lip_pixels = np.array(lip_pixels)
    print(f"\nCollected {len(lip_pixels)} lip pixels")
    print("Sample lip colors (RGB):", lip_pixels[:3])

    # --- Step 11: K-means on lip pixels ---
    kmeans_lip = KMeans(n_clusters=2, random_state=42, n_init=10)
    kmeans_lip.fit(lip_pixels)

    lip_colors = kmeans_lip.cluster_centers_.astype(int)
    lip_counts = np.bincount(kmeans_lip.labels_)
    dominant_lip_idx = np.argmax(lip_counts)
    dominant_lip = lip_colors[dominant_lip_idx]

    print(f"Natural lip color: R={dominant_lip[0]} G={dominant_lip[1]} B={dominant_lip[2]}")

    # --- Step 12: Convert lip color to HSV ---
    r, g, b = dominant_lip / 255.0
    lip_hue, lip_sat, lip_val = colorsys.rgb_to_hsv(r, g, b)
    lip_hue_deg = lip_hue * 360
    print(f"Lip Hue: {lip_hue_deg:.0f}°  Saturation: {lip_sat*100:.0f}%  Value: {lip_val*100:.0f}%")

    # --- Step 13: Lipstick recommendations based on natural lip color ---
    # we shift hue slightly and vary saturation to suggest complementary shades
    print("\nLipstick shades that suit you:")

    if undertone == "WARM":
        print("  Terracotta   → RGB approx (196, 98, 58)")
        print("  Warm red     → RGB approx (180, 48, 35)")
        print("  Peachy nude  → RGB approx (201, 143, 110)")
        print("  Burnt coral  → RGB approx (210, 90, 60)")
        print("  Warm brown   → RGB approx (139, 69, 40)")
    elif undertone == "COOL":
        print("  Berry        → RGB approx (150, 40, 80)")
        print("  Mauve        → RGB approx (180, 100, 130)")
        print("  Cool pink    → RGB approx (210, 80, 120)")
        print("  Plum         → RGB approx (120, 40, 80)")
        print("  Rose         → RGB approx (195, 90, 110)")
    else:
        print("  Dusty rose   → RGB approx (185, 110, 110)")
        print("  Soft berry   → RGB approx (160, 70, 90)")
        print("  Nude pink    → RGB approx (195, 135, 120)")
        print("  Muted coral  → RGB approx (200, 110, 90)")
        print("  Soft brown   → RGB approx (155, 95, 80)")

    # --- Step 14: Save image with lip points marked ---
    img_lips = img_rgb.copy()
    for idx in LIP_INDICES:
        lm = landmarks[idx]
        px = int(lm.x * w)
        py = int(lm.y * h)
        cv2.circle(img_lips, (px, py), radius=5, color=(220, 50, 50), thickness=-1)

    cv2.imwrite("lip_points.jpg", cv2.cvtColor(img_lips, cv2.COLOR_RGB2BGR))
    print("\nSaved lip_points.jpg — red dots show which pixels we analysed!")