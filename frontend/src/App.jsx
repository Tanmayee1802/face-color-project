import { useState } from "react"
import Upload from "./Upload"
import Results from "./Results"

export default function App() {
  const [result, setResult] = useState(null)

  return result ? (
    <Results data={result} onReset={() => setResult(null)} />
  ) : (
    <Upload onResult={setResult} />
  )
}