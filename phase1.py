from PIL import Image
import numpy as np
import colorsys

img = Image.open("tan.jpg")
img = img.convert("RGB")
pixels = np.array(img)

# --- crop just the face region ---
face = pixels[200:850, 350:900]
print("Face crop shape:", face.shape)

# --- average color of JUST the face ---
avg_face = face.mean(axis=(0,1))
print(f"\nFace average color: R={avg_face[0]:.0f} G={avg_face[1]:.0f} B={avg_face[2]:.0f}")

# --- convert to HSV ---
r, g, b = avg_face / 255.0
h, s, v = colorsys.rgb_to_hsv(r, g, b)
hue_degrees = h * 360
print(f"Hue: {hue_degrees:.0f}°  Saturation: {s*100:.0f}%  Value: {v*100:.0f}%")

# --- undertone guess ---
if 10 <= hue_degrees <= 45 and s > 0.2:
    print("\nUndertone: WARM")
elif 180 <= hue_degrees <= 280:
    print("\nUndertone: COOL")
else:
    print("\nUndertone: NEUTRAL or unclear")

# --- save the crop so you can SEE what we analysed ---
face_img = Image.fromarray(face)
face_img.save("face_crop.jpg")
print("\nSaved face_crop.jpg — open it to see exactly what pixels we averaged!")