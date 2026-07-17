export default function Skeleton() {
  return (
    <div style={styles.page}>
      <div style={styles.container}>

        {/* header skeleton */}
        <div style={styles.header}>
          <div style={{ ...styles.bone, width: "200px", height: "32px", margin: "0 auto 12px" }} />
          <div style={{ ...styles.bone, width: "140px", height: "28px", borderRadius: "20px", margin: "0 auto 12px" }} />
          <div style={{ ...styles.bone, width: "280px", height: "16px", margin: "0 auto" }} />
        </div>

        {/* your colors skeleton */}
        <div style={styles.card}>
          <div style={{ ...styles.bone, width: "100px", height: "12px", marginBottom: "16px" }} />
          <div style={styles.colorRow}>
            <div style={styles.colorItem}>
              <div style={{ ...styles.bone, width: "72px", height: "72px", borderRadius: "12px" }} />
              <div style={{ ...styles.bone, width: "60px", height: "12px", marginTop: "8px" }} />
            </div>
            <div style={styles.colorItem}>
              <div style={{ ...styles.bone, width: "72px", height: "72px", borderRadius: "50%" }} />
              <div style={{ ...styles.bone, width: "60px", height: "12px", marginTop: "8px" }} />
            </div>
          </div>
        </div>

        {/* clothing skeleton */}
        <div style={styles.card}>
          <div style={{ ...styles.bone, width: "160px", height: "12px", marginBottom: "16px" }} />
          <div style={styles.swatchRow}>
            {[...Array(8)].map((_, i) => (
              <div key={i} style={styles.swatchItem}>
                <div style={{ ...styles.bone, width: "52px", height: "52px", borderRadius: "10px" }} />
                <div style={{ ...styles.bone, width: "44px", height: "10px", marginTop: "6px" }} />
              </div>
            ))}
          </div>
        </div>

        {/* lipstick skeleton */}
        <div style={styles.card}>
          <div style={{ ...styles.bone, width: "180px", height: "12px", marginBottom: "16px" }} />
          <div style={styles.swatchRow}>
            {[...Array(5)].map((_, i) => (
              <div key={i} style={styles.swatchItem}>
                <div style={{ ...styles.bone, width: "52px", height: "52px", borderRadius: "50%" }} />
                <div style={{ ...styles.bone, width: "44px", height: "10px", marginTop: "6px" }} />
              </div>
            ))}
          </div>
        </div>

        {/* avoid skeleton */}
        <div style={styles.card}>
          <div style={{ ...styles.bone, width: "130px", height: "12px", marginBottom: "16px" }} />
          <div style={styles.avoidRow}>
            {[...Array(5)].map((_, i) => (
              <div key={i} style={{ ...styles.bone, width: "80px", height: "28px", borderRadius: "20px" }} />
            ))}
          </div>
        </div>

      </div>

      <style>{`
        @keyframes shimmer {
          0% { background-position: -400px 0; }
          100% { background-position: 400px 0; }
        }
      `}</style>
    </div>
  )
}

const shimmerBg = {
  background: "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
  backgroundSize: "400px 100%",
  animation: "shimmer 1.4s ease infinite",
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "24px",
    display: "flex",
    justifyContent: "center",
    background: "#fdf6f0",
  },
  container: {
    width: "100%",
    maxWidth: "520px",
  },
  header: {
    textAlign: "center",
    padding: "32px 0 20px",
  },
  card: {
    background: "#fff",
    borderRadius: "16px",
    padding: "20px",
    marginBottom: "16px",
    boxShadow: "0 2px 16px rgba(0,0,0,0.06)",
  },
  bone: {
    ...shimmerBg,
    borderRadius: "6px",
  },
  colorRow: {
    display: "flex",
    gap: "20px",
  },
  colorItem: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  swatchRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "12px",
  },
  swatchItem: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  avoidRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
  },
}