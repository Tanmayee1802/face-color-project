import { useState } from "react"
import Upload from "./Upload"
import Results from "./Results"
import Skeleton from "./Skeleton"

export default function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <>
      {loading && <Skeleton />}
      {!loading && !result && (
        <Upload
          onResult={(data) => {
            setResult(data)
            setLoading(false)
          }}
          onLoading={() => {
            setLoading(true)
            setResult(null)
          }}
        />
      )}
      {!loading && result && (
        <Results data={result} onReset={() => setResult(null)} />
      )}
    </>
  )
}