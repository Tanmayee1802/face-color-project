# 🎨 Face Color Analysis

An AI-powered web app that analyzes your facial features to recommend personalized lipstick shades and clothing colors based on seasonal color theory.

## 🌸 What it does

Upload a photo or use your webcam — the app will:

1. Detect your face using MediaPipe (478 facial landmarks)
2. Extract your skin tone from cheek and forehead pixels
3. Extract your natural lip color
4. Classify you into a seasonal color type — Spring, Summer, Autumn, or Winter
5. Recommend lipstick shades and clothing colors that suit you
6. Show colors to avoid
7. Let you download your results as a shareable image

## 🖥️ Live Demo

- **App:** https://face-color-project.vercel.app

## 🧠 How it works

```
Photo uploaded
      ↓
MediaPipe detects 478 face landmarks
      ↓
Cheek + forehead pixels extracted → K-means clustering → dominant skin color
      ↓
RGB → HSV conversion → undertone detection (Warm/Cool/Neutral)
      ↓
Lip landmarks extracted → natural lip color
      ↓
Season classification (Spring/Summer/Autumn/Winter)
      ↓
Palette recommendations returned as JSON → React renders results
```

### Seasonal Color Theory

| Season | Undertone | Key Colors |
|--------|-----------|------------|
| 🌸 Spring | Warm | Peach, coral, golden yellow |
| ☁️ Summer | Cool | Dusty rose, lavender, powder blue |
| 🍂 Autumn | Warm | Rust, olive, burnt orange |
| ❄️ Winter | Cool | True red, navy, emerald |

## 🚀 Run Locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:
```
VITE_API_URL=http://127.0.0.1:8000
```

## ✨ Features

- 📁 Photo upload with drag and drop
- 📷 Live webcam capture
- 🎨 Skin tone and lip color detection
- 🌸 Seasonal color classification
- 👗 Clothing palette recommendations
- 💄 Lipstick shade suggestions
- 📸 Download results as image

## 🔮 Future Ideas

- Virtual lipstick try-on overlay
- Multiple face analysis
- Share directly to social media

## 🛠️ Tech

Python · FastAPI · MediaPipe · OpenCV · scikit-learn · React · Vite
