import { useRef } from "react"
import html2canvas from "html2canvas"

export default function Results({ data, onReset }) {
  const resultRef = useRef(null)
  const skinRgb = `rgb(${data.skin_color.join(",")})`
  const lipRgb = `rgb(${data.lip_color.join(",")})`

  const seasonEmoji = {
    Spring: "🌸", Summer: "☁️", Autumn: "🍂", Winter: "❄️"
  }

  async function handleShare() {
    const canvas = await html2canvas(resultRef.current, {
      backgroundColor: "#fdf6f0",
      scale: 2,
    })
    const link = document.createElement("a")
    link.download = "my-color-analysis.png"
    link.href = canvas.toDataURL("image/png")
    link.click()
  }

  return (
    <div style={styles.page}>
      <div style={styles.container} ref={resultRef}>

        {/* header */}
        <div style={styles.header}>
          <h1 style={styles.title}>Your Color Analysis</h1>
          <div style={styles.seasonBadge}>
            {seasonEmoji[data.season]} {data.season} — {data.undertone}
          </div>
          <p style={styles.description}>{data.description}</p>
        </div>

        {/* skin + lip colors */}
        <div style={styles.card}>
          <p style={styles.cardLabel}>Your Colors</p>
          <div style={styles.colorRow}>
            <div style={styles.colorItem}>
              <div style={{ ...styles.skinSwatch, background: skinRgb }} />
              <p style={styles.colorName}>Skin tone</p>
              <p style={styles.colorRgb}>rgb({data.skin_color.join(", ")})</p>
            </div>
            <div style={styles.colorItem}>
              <div style={{
                ...styles.skinSwatch,
                background: lipRgb,
                borderRadius: "50%"
              }} />
              <p style={styles.colorName}>Natural lip</p>
              <p style={styles.colorRgb}>rgb({data.lip_color.join(", ")})</p>
            </div>
          </div>
        </div>

        {/* clothing */}
        <div style={styles.card}>
          <p style={styles.cardLabel}>Clothing Colors For You</p>
          <div style={styles.swatchGrid}>
            {data.clothing.map((item) => (
              <div key={item.name} style={styles.swatchItem}>
                <div style={{
                  ...styles.clothingSwatch,
                  background: `rgb(${item.rgb.join(",")})`
                }} />
                <p style={styles.swatchName}>{item.name}</p>
              </div>
            ))}
          </div>
        </div>

        {/* lipstick */}
        <div style={styles.card}>
          <p style={styles.cardLabel}>Lipstick Shades For You</p>
          <div style={styles.swatchGrid}>
            {data.lipstick.map((item) => (
              <div key={item.name} style={styles.swatchItem}>
                <div style={{
                  ...styles.lipSwatch,
                  background: `rgb(${item.rgb.join(",")})`
                }} />
                <p style={styles.swatchName}>{item.name}</p>
              </div>
            ))}
          </div>
        </div>

        {/* avoid */}
        <div style={styles.card}>
          <p style={styles.cardLabel}>Colors To Avoid</p>
          <div style={styles.avoidRow}>
            {data.avoid.map((color) => (
              <div key={color} style={styles.avoidTag}>✗ {color}</div>
            ))}
          </div>
        </div>

        {/* buttons */}
        <button style={styles.shareBtn} onClick={handleShare}>
          📸 Save as Image
        </button>

        <button style={styles.resetBtn} onClick={onReset}>
          Analyse Another Photo
        </button>

      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "24px",
    display: "flex",
    justifyContent: "center",
  },
  container: {
    width: "100%",
    maxWidth: "520px",
  },
  header: {
    textAlign: "center",
    padding: "32px 0 20px",
  },
  title: {
    fontSize: "26px",
    fontWeight: "700",
    marginBottom: "12px",
    color: "#1a1a1a",
  },
  seasonBadge: {
    display: "inline-block",
    padding: "6px 18px",
    background: "linear-gradient(135deg, #e8956d, #c06030)",
    color: "#fff",
    borderRadius: "20px",
    fontSize: "14px",
    fontWeight: "600",
    marginBottom: "12px",
  },
  description: {
    fontSize: "14px",
    color: "#888",
    lineHeight: "1.6",
  },
  card: {
    background: "#fff",
    borderRadius: "16px",
    padding: "20px",
    marginBottom: "16px",
    boxShadow: "0 2px 16px rgba(0,0,0,0.06)",
  },
  cardLabel: {
    fontSize: "11px",
    fontWeight: "600",
    color: "#c06030",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    marginBottom: "14px",
  },
  colorRow: {
    display: "flex",
    gap: "20px",
  },
  colorItem: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "6px",
  },
  skinSwatch: {
    width: "72px",
    height: "72px",
    borderRadius: "12px",
    border: "0.5px solid rgba(0,0,0,0.08)",
  },
  colorName: {
    fontSize: "13px",
    fontWeight: "500",
    color: "#333",
  },
  colorRgb: {
    fontSize: "11px",
    color: "#aaa",
    fontFamily: "monospace",
  },
  swatchGrid: {
    display: "flex",
    flexWrap: "wrap",
    gap: "12px",
  },
  swatchItem: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "5px",
  },
  clothingSwatch: {
    width: "52px",
    height: "52px",
    borderRadius: "10px",
    border: "0.5px solid rgba(0,0,0,0.08)",
  },
  lipSwatch: {
    width: "52px",
    height: "52px",
    borderRadius: "50%",
    border: "0.5px solid rgba(0,0,0,0.08)",
  },
  swatchName: {
    fontSize: "10px",
    color: "#888",
    textAlign: "center",
    maxWidth: "56px",
  },
  avoidRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
  avoidTag: {
    padding: "5px 12px",
    background: "#fdf0f0",
    color: "#c0392b",
    borderRadius: "20px",
    fontSize: "12px",
    border: "0.5px solid #f5c6c6",
  },
  shareBtn: {
    width: "100%",
    padding: "14px",
    background: "linear-gradient(135deg, #e8956d, #c06030)",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "12px",
  },
  resetBtn: {
    width: "100%",
    padding: "14px",
    background: "transparent",
    border: "2px solid #e8956d",
    color: "#c06030",
    borderRadius: "12px",
    fontSize: "15px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "40px",
  },
}