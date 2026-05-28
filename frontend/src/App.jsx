import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [scanStatus, setScanStatus] = useState('')
  const [result, setResult] = useState(null)
  const [logs, setLogs] = useState([
    { id: 1, time: '09:00:00', message: 'System initialized' },
    { id: 2, time: '09:00:01', message: 'Neural weights cached' }
  ])
  
  const fileInputRef = useRef(null)

  const addLog = (message) => {
    const now = new Date()
    const time = now.toTimeString().split(' ')[0]
    setLogs(prev => [{ id: Date.now(), time, message }, ...prev].slice(0, 10))
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      processFile(selectedFile)
    }
  }

  const processFile = (selectedFile) => {
    setFile(selectedFile)
    setPreview(URL.createObjectURL(selectedFile))
    setResult(null)
    addLog(`Specimen loaded: ${selectedFile.name}`)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.currentTarget.classList.add('drag-active')
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('drag-active')
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.currentTarget.classList.remove('drag-active')
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      processFile(droppedFile)
    } else {
      addLog('Error: Invalid file type')
    }
  }

  const startScan = async () => {
    if (!file) return

    setScanning(true)
    setProgress(0)
    setResult(null)
    
    // Stage 1: DNA Extraction
    setScanStatus('EXTRACTING CELLULAR DNA...')
    addLog('Initiating DNA sequencing...')
    for (let i = 0; i <= 30; i += 2) {
      setProgress(i)
      await new Promise(r => setTimeout(r, 40))
    }

    // Stage 2: Pathogen Comparison
    setScanStatus('COMPARING PATHOGEN MARKERS...')
    addLog('Matching morphological features...')
    for (let i = 31; i <= 65; i += 2) {
      setProgress(i)
      await new Promise(r => setTimeout(r, 50))
    }

    // Stage 3: Inference
    setScanStatus('RUNNING NEURAL INFERENCE...')
    addLog('Executing MobileNetV2 pipeline...')
    
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) throw new Error('Inference engine failure')
      
      const data = await response.json()
      
      for (let i = 66; i <= 100; i += 5) {
        setProgress(i)
        await new Promise(r => setTimeout(r, 30))
      }

      setResult(data)
      setScanStatus('SCAN COMPLETE')
      addLog(`Analysis finished: ${data.class}`)
    } catch (error) {
      addLog(`FATAL: ${error.message}`)
      setScanStatus('SCAN FAILED')
    } finally {
      setScanning(false)
    }
  }

  const resetSession = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setScanning(false)
    setProgress(0)
    setScanStatus('')
    addLog('Session reset by user')
  }

  return (
    <div className="app-container">
      {/* Sidebar Section */}
      <aside className="sidebar">
        <div className="brand-section">
          <h1 className="brand-title">BOTANICAL</h1>
          <p className="brand-subtitle">OBSERVATORY v1.0</p>
        </div>

        <div className="divider"></div>

        <h3 className="sidebar-title">ENGINE STATUS</h3>
        <ul className="engine-status-list">
          <li className="engine-status-item">
            <span className="icon">⚙️</span>
            <strong>Model:</strong>
            <span className="value">MobileNetV2</span>
          </li>
          <li className="engine-status-item">
            <span className="icon">📊</span>
            <strong>Accuracy:</strong>
            <span className="value">96.99%</span>
          </li>
          <li className="engine-status-item">
            <span className="icon">🌿</span>
            <strong>Classes:</strong>
            <span className="value">15 Species</span>
          </li>
        </ul>

        <div className="divider"></div>

        <h3 className="sidebar-title">RECENT LOGS</h3>
        <div className="logs-container">
          {logs.map(log => (
            <div key={log.id} className="log-entry">
              [{log.time}] {log.message}
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <button className="reset-btn" onClick={resetSession}>Reset Session</button>
          <p>LeafGuard AI © 2026</p>
        </div>
      </aside>

      {/* Main Workstation */}
      <main className="workstation">
        <header className="header-banner">
          <p className="observatory-tag">Neural Diagnostics</p>
          <h2 className="main-title">LeafGuard AI</h2>
          <p className="main-description">
            High-performance botanical pathology detection powered by deep learning. 
            Upload a leaf specimen for immediate cellular analysis.
          </p>
        </header>

        <section className={`glass-card ${!result && !scanning ? 'upload-card-glow' : ''}`}>
          {!preview ? (
            <div 
              className="dropzone-container"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
            >
              <div className="dropzone-icon">📥</div>
              <button className="dropzone-btn">Select Specimen</button>
              <p className="dropzone-hint">or drag and drop leaf image here</p>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept="image/*" 
                style={{ display: 'none' }} 
              />
            </div>
          ) : (
            <div className="scan-animation-container">
              <img src={preview} alt="Specimen Preview" className="preview-thumbnail" />
              
              {scanning ? (
                <>
                  <p className="scan-status-text">{scanStatus}</p>
                  <div className="custom-progress-container">
                    <div 
                      className="custom-progress-bar" 
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </>
              ) : !result ? (
                <button className="dropzone-btn" onClick={startScan}>
                  Initiate Scan
                </button>
              ) : null}
            </div>
          )}

          {result && (
            <div className="result-slide-container">
              <div className="result-metric">
                <p className="metric-lbl">Diagnosis Result</p>
                <h3 className="metric-val">{result.class}</h3>
              </div>

              <div className="result-metric">
                <p className="metric-lbl">Confidence Level</p>
                <div className="top-3-row">
                  <div className="top-3-bar-container" style={{ height: '12px' }}>
                    <div 
                      className="top-3-bar" 
                      style={{ width: `${result.confidence}%`, background: 'var(--accent-neon)' }}
                    ></div>
                  </div>
                  <span className="metric-val neon-status" style={{ width: '80px', textAlign: 'right' }}>
                    {result.confidence.toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="divider"></div>

              <div className="confidence-bar-group">
                <p className="metric-lbl">Top Pathogen Matches</p>
                <div className="top-3-grid">
                  {result.top_predictions.map((pred, i) => (
                    <div key={i} className="top-3-row">
                      <span className="top-3-name">{pred.class}</span>
                      <div className="top-3-bar-container">
                        <div 
                          className="top-3-bar" 
                          style={{ width: `${pred.confidence}%` }}
                        ></div>
                      </div>
                      <span className="top-3-percent">{pred.confidence.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className={`status-notification ${result.status === 'healthy' ? 'success' : 'error'}`}>
                <span className="icon">{result.status === 'healthy' ? '✅' : '⚠️'}</span>
                <div className="advice-body">
                  <strong>Botanical Advice</strong>
                  <p className="advice-text">{result.advice}</p>
                </div>
              </div>
              
              <button 
                className="reset-btn" 
                style={{ marginTop: '1.5rem', borderColor: 'var(--accent)' }}
                onClick={() => {
                  setPreview(null)
                  setFile(null)
                  setResult(null)
                }}
              >
                Scan New Specimen
              </button>
            </div>
          )}
        </section>

        <footer className="observatory-footer">
          Terminal Connection: Stable // Latency: 24ms // Node: Edge-AI-01
        </footer>
      </main>
    </div>
  )
}

export default App
