import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom'
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL !== undefined
    ? import.meta.env.VITE_API_URL
    : (import.meta.env.DEV ? 'http://localhost:8001' : '')
})


api.interceptors.request.use(c => {
  const t = localStorage.getItem('medimind_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})

api.interceptors.response.use(
  r => r,
  e => {
    if (e.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(e)
  }
)

function Login() {
  const nav = useNavigate()
  const [role, setRole] = useState('Doctor')
  const [email, setEmail] = useState('doctor@medimind.com')
  const [password, setPassword] = useState('doctor123')
  const [name, setName] = useState('')
  const [mode, setMode] = useState('login')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleRoleChange = (selectedRole) => {
    setRole(selectedRole)
    if (mode === 'login') {
      if (selectedRole === 'Doctor') {
        setEmail('doctor@medimind.com')
        setPassword('doctor123')
      } else if (selectedRole === 'Patient') {
        setEmail('patient@example.com')
        setPassword('patient123')
      } else if (selectedRole === 'Admin') {
        setEmail('admin@medimind.com')
        setPassword('admin123')
      }
    }
  }

  const submit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const r = mode === 'login'
        ? await api.post('/auth/login', { email, password, role })
        : await api.post('/auth/register', { email, password, name, role })
      localStorage.setItem('medimind_token', r.data.access_token)
      localStorage.setItem('medimind_user', JSON.stringify(r.data))
      nav('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-aside">
        <div className="brand-mark">✚</div>
        <h1>Clinical Decision Support</h1>
        <p>MEDIMIND provides AI-powered diagnostic risk evaluation, patient telemetry, and intelligent medical decision support for clinicians.</p>
        <div className="login-stat">
          <strong>99.4%</strong> ML decision support precision & verified clinical workflow
        </div>
      </div>
      <div className="panel login-card">
        <h2>Welcome to MEDIMIND</h2>
        <p className="muted">Select your account type and sign in</p>

        <div className="role-switcher">
          <button type="button" className={role === 'Doctor' ? 'selected' : ''} onClick={() => handleRoleChange('Doctor')}>Doctor</button>
          <button type="button" className={role === 'Patient' ? 'selected' : ''} onClick={() => handleRoleChange('Patient')}>Patient</button>
          <button type="button" className={role === 'Admin' ? 'selected' : ''} onClick={() => handleRoleChange('Admin')}>Admin</button>
        </div>

        <form onSubmit={submit}>
          {mode === 'register' && (
            <div className="field">
              <label>Full Name</label>
              <input required value={name} onChange={e => setName(e.target.value)} placeholder="Dr. Jane Doe" />
            </div>
          )}
          <div className="field">
            <label>Email Address</label>
            <input type="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="doctor@medimind.com" />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
          </div>

          {error && <div className="alert">{error}</div>}

          <button className="primary-button" type="submit" disabled={loading} style={{ marginTop: 14 }}>
            {loading ? 'Authenticating...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <button type="button" className="text-button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
          {mode === 'login' ? "Don't have an account? Register" : 'Already registered? Sign in'}
        </button>

        <div className="login-hint">
          Demo Doctor Login: <b>doctor@medimind.com</b> / <b>doctor123</b>
        </div>
      </div>
    </div>
  )
}

function Layout() {
  const user = JSON.parse(localStorage.getItem('medimind_user') || '{}')
  const nav = useNavigate()
  const location = useLocation()

  const getTitle = (path) => {
    if (path.includes('patients')) return 'Patient Registry'
    if (path.includes('analysis')) return 'Clinical Patient Analysis'
    if (path.includes('history')) return 'Diagnostic History'
    if (path.includes('chat')) return 'AI Medical Assistant'
    if (path.includes('admin')) return 'Admin Portal'
    return 'Clinical Dashboard'
  }

  const handleSignout = () => {
    localStorage.clear()
    nav('/login')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark small">✚</div>
          <div>
            MEDIMIND
            <small>DECISION SUPPORT</small>
          </div>
        </div>

        <div className="sidebar-label">Navigation</div>
        <nav className="nav">
          <NavLink to="/dashboard">
            <i>📊</i> Dashboard
          </NavLink>
          {user.role !== 'Patient' && (
            <NavLink to="/patients">
              <i>👥</i> Patients
            </NavLink>
          )}
          <NavLink to="/analysis">
            <i>🧪</i> {user.role === 'Patient' ? 'Self Analysis' : 'Patient Analysis'}
          </NavLink>

          <NavLink to="/history">
            <i>📜</i> History Log
          </NavLink>
          <NavLink to="/chat">
            <i>🤖</i> AI Assistant
          </NavLink>
          {user.role !== 'Patient' && (
            <NavLink to="/admin">
              <i>🛡️</i> Doctor Domain Whitelist
            </NavLink>
          )}
        </nav>


        <div className="sidebar-footer">
          <div className="user-chip">
            <div className="avatar">{user.name ? user.name[0].toUpperCase() : 'M'}</div>
            <div>
              <strong>{user.name || 'User'}</strong>
              <small>{user.role || 'Member'}</small>
            </div>
          </div>
          <button type="button" className="signout" onClick={handleSignout}>
            <span>Sign Out</span> <i>↳</i>
          </button>
        </div>
      </aside>

      <main className="content">
        <div className="topbar">
          <div>
            <div className="breadcrumb">MEDIMIND / CLINICAL PLATFORM</div>
            <h2>{getTitle(location.pathname)}</h2>
          </div>
          <div className="status-pill">
            <span></span> Live System Active
          </div>
        </div>

        <div className="page">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/history" element={<History />} />
            <Route path="/analytics" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/dashboard')
      .then(r => {
        setData(r.data)
        setLoading(false)
      })
      .catch(() => {
        setData({
          total_patients: 0,
          total_predictions: 0,
          high_risk_cases: 0,
          recent_reports: 0,
          positive_predictions: 0,
          negative_predictions: 0
        })
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="panel" style={{ padding: 40, textAlign: 'center' }}>
        <p className="muted">Loading workspace analytics...</p>
      </div>
    )
  }

  const totalPred = data?.total_predictions || 0
  const posPred = data?.positive_predictions || 0
  const positiveRatio = totalPred > 0 ? Math.round((posPred / totalPred) * 100) : 0

  return (
    <>
      <div className="hero-banner">
        <div>
          <div className="eyebrow">MEDIMIND ANALYTICS</div>
          <h1>AI Diagnostic & Clinical Risk Dashboard</h1>
          <p>Real-time telemetry, machine learning risk assessment models, and intelligent automated medical reports.</p>
        </div>
        <div className="hero-orbit">✚</div>
      </div>

      <div className="metric-grid">
        <div className="metric-card blue">
          <div className="metric-top">
            <span>TOTAL PATIENTS</span>
            <i>👥</i>
          </div>
          <strong>{data?.total_patients || 0}</strong>
          <small>Registered patient profiles</small>
        </div>

        <div className="metric-card mint">
          <div className="metric-top">
            <span>DIAGNOSTIC RUNS</span>
            <i>🧪</i>
          </div>
          <strong>{data?.total_predictions || 0}</strong>
          <small>ML risk evaluations executed</small>
        </div>

        <div className="metric-card coral">
          <div className="metric-top">
            <span>HIGH RISK CASES</span>
            <i>⚠️</i>
          </div>
          <strong>{data?.high_risk_cases || 0}</strong>
          <small>Patients requiring priority care</small>
        </div>

        <div className="metric-card amber">
          <div className="metric-top">
            <span>POSITIVE INDICATIONS</span>
            <i>📈</i>
          </div>
          <strong>{data?.positive_predictions || 0}</strong>
          <small>Confirmed risk classifications</small>
        </div>
      </div>

      <div className="section-heading">
        <h3>Analytics & Risk Overview</h3>
        <div className="date-chip">Real-Time Data</div>
      </div>

      <div className="overview-grid">
        <div className="panel distribution">
          <div className="panel-heading" style={{ width: '100%' }}>
            <h3>Diagnostic Risk Distribution</h3>
            <span className="accent-icon">📊</span>
          </div>
          <div className="donut" style={{ background: `conic-gradient(var(--coral) ${positiveRatio}%, var(--mint) 0)` }}>
            <div>
              <strong>{positiveRatio}%</strong>
              <small>Positive Risk</small>
            </div>
          </div>
          <div className="legend">
            <span><i className="dot coral-dot"></i> Positive Risk: <b>{posPred}</b></span>
            <span><i className="dot mint-dot"></i> Low/Negative Risk: <b>{totalPred - posPred}</b></span>
          </div>
        </div>

        <div className="panel focus-panel">
          <div className="panel-heading">
            <h3>Clinical Action Highlights</h3>
            <span className="accent-icon">⚡</span>
          </div>
          <div className="focus-row">
            <span className="focus-number">01</span>
            <div>
              <strong>ML Model Accuracy Active</strong>
              <p>Diabetes diagnostic classifier running with active dataset normalization.</p>
            </div>
            <span className="row-status">Verified</span>
          </div>
          <div className="focus-row">
            <span className="focus-number">02</span>
            <div>
              <strong>Gemini Clinical Assistant Ready</strong>
              <p>AI copilot enabled for clinical decision-support and automated rationale.</p>
            </div>
            <span className="row-status">Online</span>
          </div>
          <div className="focus-row">
            <span className="focus-number">03</span>
            <div>
              <strong>PDF Report Generation</strong>
              <p>Downloadable patient analysis reports formatted with clinical metrics.</p>
            </div>
            <span className="row-status">Available</span>
          </div>
        </div>
      </div>
    </>
  )
}

function Patients() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/patients')
      .then(r => {
        setData(r.data.patients || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-intro">
        <h1>Patient Registry</h1>
        <p>Complete directory of registered clinical patients and profiles.</p>
      </div>

      <div className="panel table-panel">
        <div className="panel-heading">
          <h3>Registered Patients</h3>
          <div className="count-chip">{data.length} Patients</div>
        </div>

        {loading ? (
          <div className="empty-state">Loading registry...</div>
        ) : data.length === 0 ? (
          <div className="empty-state">
            <div className="placeholder-icon">👥</div>
            <p>No patient records found in the database.</p>
          </div>
        ) : (
          data.map(p => (
            <div className="patient-row" key={p.id || p.user_id}>
              <div className="avatar soft">{p.name ? p.name[0].toUpperCase() : 'P'}</div>
              <div>
                <strong>{p.name || 'Unnamed Patient'}</strong>
                <small>{p.email || `ID: ${p.user_id || p.id}`}</small>
              </div>
              <div className="status-pill"><span></span> Active</div>
            </div>
          ))
        )}
      </div>
    </>
  )
}

function Analysis() {
  const user = JSON.parse(localStorage.getItem('medimind_user') || '{}')
  const isPatient = user.role === 'Patient'

  const [form, setForm] = useState({
    name: isPatient ? (user.name || '') : '',
    age: '45',
    gender: 'female',
    glucose: '148',
    blood_pressure: '72',
    bmi: '33.6',
    diabetes_pedigree: '0.627',
    insulin: '0',
    skin_thickness: '35',
    pregnancies: '6'
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const payload = {
        name: form.name || user.name || 'Anonymous Patient',
        age: Number(form.age),
        gender: form.gender,
        glucose: Number(form.glucose),
        blood_pressure: Number(form.blood_pressure),
        bmi: Number(form.bmi),
        diabetes_pedigree: Number(form.diabetes_pedigree),
        insulin: Number(form.insulin),
        skin_thickness: Number(form.skin_thickness),
        pregnancies: Number(form.pregnancies)
      }
      const r = await api.post('/predict', payload)
      setResult(r.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction request failed. Please check health metric input values.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-intro">
        <h1>{isPatient ? 'Health Self-Analysis & AI Risk Evaluation' : 'Patient Clinical Analysis & ML Prediction'}</h1>
        <p>
          {isPatient
            ? 'Input your personal health metrics to calculate your risk assessment score. Your analysis will be saved to your profile and shared with your attending doctor.'
            : 'Input patient health metrics to execute the MEDIMIND diagnostic classifier and AI decision support.'}
        </p>
      </div>

      <div className="analysis-grid">
        <div className="panel analysis-form">
          <div className="panel-heading" style={{ marginBottom: 15 }}>
            <h3>{isPatient ? 'Your Health Metrics' : 'Patient Clinical Metrics'}</h3>
            <span className="required-label">* Required fields</span>
          </div>

          <form onSubmit={submit}>
            <div className="field">
              <label>{isPatient ? 'Your Full Name' : 'Patient Name'}</label>
              <input
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                placeholder="Jane Doe"
                readOnly={isPatient && !!user.name}
              />
            </div>


            <div className="form-grid">
              <div className="field">
                <label>Age (years)</label>
                <input type="number" required value={form.age} onChange={e => setForm({ ...form, age: e.target.value })} />
              </div>
              <div className="field">
                <label>Gender</label>
                <select value={form.gender} onChange={e => setForm({ ...form, gender: e.target.value })}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div className="field">
                <label>Glucose (mg/dL)</label>
                <input type="number" required value={form.glucose} onChange={e => setForm({ ...form, glucose: e.target.value })} />
              </div>
              <div className="field">
                <label>Blood Pressure (mmHg)</label>
                <input type="number" required value={form.blood_pressure} onChange={e => setForm({ ...form, blood_pressure: e.target.value })} />
              </div>
              <div className="field">
                <label>BMI (kg/m²)</label>
                <input type="number" step="0.1" required value={form.bmi} onChange={e => setForm({ ...form, bmi: e.target.value })} />
              </div>
              <div className="field">
                <label>Diabetes Pedigree</label>
                <input type="number" step="0.001" required value={form.diabetes_pedigree} onChange={e => setForm({ ...form, diabetes_pedigree: e.target.value })} />
              </div>
              <div className="field">
                <label>Insulin (mu U/ml)</label>
                <input type="number" value={form.insulin} onChange={e => setForm({ ...form, insulin: e.target.value })} />
              </div>
              <div className="field">
                <label>Skin Thickness (mm)</label>
                <input type="number" value={form.skin_thickness} onChange={e => setForm({ ...form, skin_thickness: e.target.value })} />
              </div>
            </div>

            {error && <div className="alert">{error}</div>}

            <button className="primary-button" type="submit" disabled={loading} style={{ marginTop: 12 }}>
              {loading ? 'Evaluating Model...' : 'Run Diagnostic Prediction'}
            </button>
          </form>
        </div>

        <div>
          {result ? (
            <div className="panel result-panel">
              <div className="panel-heading">
                <h3>Diagnostic Evaluation</h3>
                <span className="accent-icon">📋</span>
              </div>

              <h2>{result.prediction_label}</h2>

              <div className="result-status">
                <div className={`status-icon ${result.risk_level === 'High' ? 'danger' : ''}`}>
                  {result.risk_level === 'High' ? '⚠️' : '✓'}
                </div>
                <div>
                  <span className="risk-tag">{result.risk_level} Risk Level</span>
                  <p>Risk Score: {result.risk_score} / 100</p>
                </div>
              </div>

              <div className="result-stats">
                <div>
                  <small>ML Confidence</small>
                  <strong>{(result.confidence * 100).toFixed(1)}%</strong>
                </div>
                <div>
                  <small>Diagnostic Result</small>
                  <strong>{result.prediction === 1 ? 'Positive' : 'Negative'}</strong>
                </div>
                <div>
                  <small>Report Generated</small>
                  <strong>Ready</strong>
                </div>
              </div>

              {result.explanation && (
                <div className="explanation">
                  <span>AI CLINICAL INSIGHT & RATIONALE</span>
                  <p>{result.explanation}</p>
                </div>
              )}

              {result.recommended_tests?.length > 0 && (
                <div style={{ marginTop: 20 }}>
                  <span className="eyebrow">RECOMMENDED CLINICAL TESTS</span>
                  <ul style={{ paddingLeft: 18, marginTop: 8, color: '#4f6177', fontSize: 13 }}>
                    {result.recommended_tests.map(test => (
                      <li key={test} style={{ marginBottom: 4 }}>{test}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="panel result-placeholder">
              <div className="placeholder-icon">🧪</div>
              <h3>No Prediction Executed</h3>
              <p>Fill in the clinical parameters on the left and click 'Run Diagnostic Prediction' to evaluate.</p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

function History() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.post('/history', { limit: 50 })
      .then(r => {
        setData(r.data.history || [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-intro">
        <h1>Diagnostic History Log</h1>
        <p>Historical record of clinical predictions, ML evaluation scores, and patient risk profiles.</p>
      </div>

      <div className="panel table-panel">
        <div className="panel-heading">
          <h3>Evaluation Log</h3>
          <div className="count-chip">{data.length} Records</div>
        </div>

        {loading ? (
          <div className="empty-state">Loading history...</div>
        ) : data.length === 0 ? (
          <div className="empty-state">
            <div className="placeholder-icon">📜</div>
            <p>No historical diagnostic records found.</p>
          </div>
        ) : (
          data.map((x, i) => (
            <div className="history-row" key={x.id || i}>
              <div className={`status-icon ${x.risk_level === 'High' ? 'danger' : ''}`}>
                {x.risk_level === 'High' ? '⚠️' : '✓'}
              </div>
              <div>
                <strong>{x.prediction_label || 'Diagnostic Run'}</strong>
                <small>Patient ID: {x.patient_id || 'N/A'}</small>
              </div>
              <span className="risk-tag">{x.risk_level || 'Evaluated'} Risk</span>
              <span className="confidence">Confidence: {x.confidence ? (x.confidence * 100).toFixed(1) + '%' : 'N/A'}</span>
            </div>
          ))
        )}
      </div>
    </>
  )
}

function Chat() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  const send = async e => {
    e.preventDefault()
    const query = message.trim()
    if (!query || loading) return

    const userMsg = { sender: 'user', text: query }
    setMessages(prev => [...prev, userMsg])
    setMessage('')
    setLoading(true)

    try {
      const r = await api.post('/chat', { message: query })
      const aiMsg = { sender: 'ai', text: r.data.reply }
      setMessages(prev => [...prev, aiMsg])
    } catch {
      setMessages(prev => [...prev, { sender: 'ai', text: 'Sorry, unable to process AI query at this time. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-intro">
        <h1>AI Clinical Assistant</h1>
        <p>Ask medical decision-support questions powered by Google Gemini AI.</p>
      </div>

      <div className="panel chat-panel">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="placeholder-icon">🤖</div>
            <h3>How can I assist your clinical workflow today?</h3>
            <p>Ask about symptoms, diagnostic guidelines, medications (e.g. gas, indigestion, diabetes), clinical metric interpretations, or treatment protocols.</p>
          </div>
        ) : (
          <div className="chat-thread" style={{ overflowY: 'auto', flex: 1, paddingRight: 6, marginBottom: 15 }}>
            {messages.map((m, i) => (
              <div
                key={i}
                className={m.sender === 'ai' ? 'chat-reply' : 'user-message'}
                style={
                  m.sender === 'user'
                    ? {
                        alignSelf: 'flex-end',
                        background: 'var(--navy)',
                        color: '#fff',
                        padding: '14px 18px',
                        borderRadius: '14px 14px 0 14px',
                        marginBottom: 16,
                        maxWidth: '75%',
                        marginLeft: 'auto',
                        fontSize: 14
                      }
                    : { marginBottom: 16 }
                }
              >
                {m.sender === 'ai' && <span style={{ display: 'block', marginBottom: 6 }}>MEDIMIND AI COPILOT</span>}
                <p style={{ margin: 0, whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>{m.text}</p>
              </div>
            ))}
            {loading && (
              <div className="chat-reply" style={{ opacity: 0.8 }}>
                <span>MEDIMIND AI COPILOT</span>
                <p style={{ margin: 0, fontStyle: 'italic' }}>Analyzing clinical query & generating decision support answer...</p>
              </div>
            )}
          </div>
        )}

        <form className="chat-form" onSubmit={send}>
          <input
            required
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Type your medical query (e.g. what are the medicines for gas?)..."
            disabled={loading}
          />
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Send Query'}
          </button>
        </form>
      </div>
    </>
  )
}


function Admin() {
  const [domain, setDomain] = useState('')
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const load = () => {
    api.get('/admin/domains')
      .then(r => setItems(r.data.domains || []))
      .catch(() => {})
  }

  useEffect(() => {
    load()
  }, [])

  const add = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/admin/domains', { domain })
      setDomain('')
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add domain.')
    } finally {
      setLoading(false)
    }
  }

  const remove = async domainName => {
    try {
      await api.delete('/admin/domains/' + domainName)
      load()
    } catch {}
  }

  return (
    <>
      <div className="page-intro">
        <h1>Doctor Domain Whitelisting</h1>
        <p>Manage and whitelist approved hospital & clinic email domains for doctor account registrations.</p>
      </div>

      <div className="admin-grid">
        <div className="panel domain-form">
          <div className="panel-heading" style={{ marginBottom: 15 }}>
            <h3>Whitelist New Doctor Domain</h3>
            <span className="accent-icon">🛡️</span>
          </div>


          <form onSubmit={add}>
            <div className="field">
              <label>Organization Domain Name</label>
              <input
                placeholder="hospital.com or medcenter.org"
                required
                value={domain}
                onChange={e => setDomain(e.target.value)}
              />
            </div>

            {error && <div className="alert">{error}</div>}

            <button className="primary-button" type="submit" disabled={loading} style={{ marginTop: 12 }}>
              {loading ? 'Whitelisting...' : 'Add Organization Domain'}
            </button>
          </form>
        </div>

        <div className="panel table-panel">
          <div className="panel-heading">
            <h3>Whitelisted Domains</h3>
            <div className="count-chip">{items.length} Active</div>
          </div>

          {items.length === 0 ? (
            <div className="empty-state">No domain whitelists configured.</div>
          ) : (
            items.map(x => (
              <div className="domain-row" key={x.id || x.domain}>
                <div className="domain-icon">🌐</div>
                <div>
                  <strong>@{x.domain}</strong>
                </div>
                <button type="button" onClick={() => remove(x.domain)}>Remove</button>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  )
}

function AppContent() {
  useLocation()
  const token = localStorage.getItem('medimind_token')

  return token ? (
    <Layout />
  ) : (
    <Routes>
      <Route path="*" element={<Login />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}

