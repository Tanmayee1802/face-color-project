import { useState, useRef } from "react"

export default function Upload({ onResult, onLoading })  {
  const [mode, setMode] = useState("upload")
  const [preview, setPreview] = useState(null)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [cameraActive, setCameraActive] = useState(false)
  const inputRef = useRef()
  const videoRef = useRef()
  const streamRef = useRef()

  function handleFile(selected) {
    setFile(selected)
    setPreview(URL.createObjectURL(selected))
    setError(null)
  }

  function handleDrop(e) {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFile(dropped)
  }

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      streamRef.current = stream
      videoRef.current.srcObject = stream
      setCameraActive(true)
      setError(null)
    } catch (err) {
      setError("Could not access camera. Please allow camera permission.")
    }
  }

  function stopCamera() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
    }
    setCameraActive(false)
  }

  function capturePhoto() {
    const canvas = document.createElement("canvas")
    canvas.width = videoRef.current.videoWidth
    canvas.height = videoRef.current.videoHeight
    canvas.getContext("2d").drawImage(videoRef.current, 0, 0)
    canvas.toBlob((blob) => {
      const captured = new File([blob], "webcam.jpg", { type: "image/jpeg" })
      setFile(captured)
      setPreview(canvas.toDataURL("image/jpeg"))
      stopCamera()
    }, "image/jpeg")
  }

  function switchMode(newMode) {
    setMode(newMode)
    setPreview(null)
    setFile(null)
    setError(null)
    if (newMode === "upload") stopCamera()
    if (newMode === "webcam") startCamera()
  }

  async function handleAnalyze() {
    if (!file) return
    setLoading(true)
    setError(null)
    onLoading() 

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/analyze`, {
        method: "POST",
        body: formData,
      })
      const data = await response.json()
      if (data.error) {
        setError(data.error)
      } else {
        onResult(data)
      }
    } catch (err) {
      setError("Could not connect to server. Make sure the backend is running.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>

        {/* header */}
        <div style={styles.header}>
          <div style={styles.emoji}>🎨</div>
          <h1 style={styles.title}>Color Analysis</h1>
          <p style={styles.subtitle}>
            Discover your season, ideal lipstick shades, and clothing palette
          </p>
        </div>

        {/* mode toggle */}
        <div style={styles.toggle}>
          <button
            style={{
              ...styles.toggleBtn,
              background: mode === "upload" ? "#c06030" : "transparent",
              color: mode === "upload" ? "#fff" : "#888",
            }}
            onClick={() => switchMode("upload")}
          >
            📁 Upload Photo
          </button>
          <button
            style={{
              ...styles.toggleBtn,
              background: mode === "webcam" ? "#c06030" : "transparent",
              color: mode === "webcam" ? "#fff" : "#888",
            }}
            onClick={() => switchMode("webcam")}
          >
            📷 Use Camera
          </button>
        </div>

        {/* instructions */}
        <div style={styles.tips}>
          <p style={styles.tipsTitle}>For best results:</p>
          <p style={styles.tip}>✓ Natural lighting, no makeup</p>
          <p style={styles.tip}>✓ Face the camera directly</p>
          <p style={styles.tip}>✓ Hair pulled back if possible</p>
        </div>

        {/* upload mode */}
        {mode === "upload" && (
          <div
            style={styles.dropzone}
            onClick={() => !preview && inputRef.current.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            {preview ? (
              <div style={{ width: "100%", position: "relative" }}>
                <img src={preview} alt="preview" style={styles.preview} />
                <button
                  style={styles.changeBtn}
                  onClick={(e) => {
                    e.stopPropagation()
                    inputRef.current.click()
                  }}
                >
                  Change Photo
                </button>
              </div>
            ) : (
              <div style={styles.dropContent}>
                <div style={styles.uploadIcon}>📷</div>
                <p style={styles.dropText}>Click or drag a photo here</p>
                <p style={styles.dropSub}>JPG or PNG, clear front-facing photo</p>
              </div>
            )}
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          style={{ display: "none" }}
          onChange={(e) => handleFile(e.target.files[0])}
        />

        {/* webcam mode */}
        {mode === "webcam" && (
          <div style={styles.webcamBox}>
            {!preview ? (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  style={styles.video}
                />
                {cameraActive && (
                  <button style={styles.captureBtn} onClick={capturePhoto}>
                    ⚪ Capture
                  </button>
                )}
              </>
            ) : (
              <>
                <img src={preview} alt="captured" style={styles.preview} />
                <button
                  style={styles.retakeBtn}
                  onClick={() => {
                    setPreview(null)
                    setFile(null)
                    startCamera()
                  }}
                >
                  Retake
                </button>
              </>
            )}
          </div>
        )}

        {/* error */}
        {error && <p style={styles.error}>{error}</p>}

        {/* analyze button */}
        <button
          style={{
            ...styles.button,
            opacity: !file || loading ? 0.6 : 1,
            cursor: !file || loading ? "not-allowed" : "pointer",
          }}
          onClick={handleAnalyze}
          disabled={!file || loading}
        >
          {loading ? "Analysing..." : "Analyse My Colors"}
        </button>

      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
  },
  card: {
    background: "#fff",
    borderRadius: "20px",
    padding: "36px",
    width: "100%",
    maxWidth: "480px",
    boxShadow: "0 4px 32px rgba(0,0,0,0.08)",
  },
  header: {
    textAlign: "center",
    marginBottom: "20px",
  },
  emoji: { fontSize: "40px", marginBottom: "8px" },
  title: {
    fontSize: "28px",
    fontWeight: "700",
    color: "#1a1a1a",
    marginBottom: "8px",
  },
  subtitle: {
    fontSize: "14px",
    color: "#888",
    lineHeight: "1.5",
  },
  toggle: {
    display: "flex",
    background: "#f5f5f5",
    borderRadius: "12px",
    padding: "4px",
    marginBottom: "16px",
    gap: "4px",
  },
  toggleBtn: {
    flex: 1,
    padding: "10px",
    border: "none",
    borderRadius: "10px",
    fontSize: "14px",
    fontWeight: "500",
    cursor: "pointer",
    transition: "all 0.2s",
  },
  tips: {
    background: "#fdf6f0",
    borderRadius: "12px",
    padding: "14px 18px",
    marginBottom: "16px",
  },
  tipsTitle: {
    fontSize: "12px",
    fontWeight: "600",
    color: "#c06030",
    marginBottom: "6px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  tip: {
    fontSize: "13px",
    color: "#666",
    lineHeight: "2",
  },
  dropzone: {
    border: "2px dashed #e8c9a0",
    borderRadius: "14px",
    padding: "20px",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "16px",
    minHeight: "180px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#fffaf5",
  },
  dropContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "8px",
  },
  uploadIcon: { fontSize: "36px" },
  dropText: {
    fontSize: "15px",
    color: "#555",
    fontWeight: "500",
  },
  dropSub: { fontSize: "12px", color: "#aaa" },
  preview: {
    width: "100%",
    maxHeight: "280px",
    objectFit: "cover",
    borderRadius: "10px",
  },
  changeBtn: {
    position: "absolute",
    bottom: "10px",
    right: "10px",
    padding: "6px 14px",
    background: "rgba(0,0,0,0.6)",
    color: "#fff",
    border: "none",
    borderRadius: "20px",
    fontSize: "12px",
    cursor: "pointer",
    fontWeight: "500",
  },
  webcamBox: {
    marginBottom: "16px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "12px",
  },
  video: {
    width: "100%",
    borderRadius: "14px",
    background: "#000",
  },
  captureBtn: {
    padding: "12px 32px",
    background: "#1a1a1a",
    color: "#fff",
    border: "none",
    borderRadius: "30px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
  },
  retakeBtn: {
    padding: "8px 24px",
    background: "transparent",
    color: "#888",
    border: "1px solid #ddd",
    borderRadius: "20px",
    fontSize: "13px",
    cursor: "pointer",
  },
  error: {
    color: "#e53e3e",
    fontSize: "13px",
    marginBottom: "12px",
    textAlign: "center",
  },
  button: {
    width: "100%",
    padding: "14px",
    background: "linear-gradient(135deg, #e8956d, #c06030)",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "opacity 0.2s",
  },
}