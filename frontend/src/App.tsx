import ReactMarkdown from 'react-markdown'
import { useEffect, useRef, useState } from 'react'
import './App.css'

type Product = {
  id: number
  name: string
  description?: string | null
  price?: number | null
  currency?: string
  in_stock: boolean
  skin_type?: string | null
  spf?: number | null
  ingredients?: string[] | null
  volume_ml?: number | null
  key_features?: string[] | null
  brand?: { name: string } | null
  category?: { name: string } | null
}

type Message = {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [productError, setProductError] = useState('')
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('ALL')

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am ROSE, your AI beauty assistant. Tell me what you are looking for.',
    },
  ])
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [chatOpen, setChatOpen] = useState(false)
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem('rose_session_id') || '',
  )
  const chatInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    async function loadProducts() {
      try {
        const response = await fetch('/api/products/?skip=0&limit=100')
        if (!response.ok) throw new Error(`Server returned ${response.status}`)
        const data: Product[] = await response.json()
        setProducts(data)
      } catch {
        setProductError('Could not connect to the product database. Please check that the backend is running.')
      } finally {
        setLoadingProducts(false)
      }
    }

    loadProducts()
  }, [])

  useEffect(() => {
    if (chatOpen) chatInput.current?.focus()
  }, [chatOpen])

  async function sendMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const text = message.trim()
    if (!text || sending) return

    setMessages((previous) => [...previous, { role: 'user', content: text }])
    setMessage('')
    setSending(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId || null,
        }),
      })

      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || `Server returned ${response.status}`)
      }

      const data: { response: string; session_id: string } = await response.json()
      setSessionId(data.session_id)
      localStorage.setItem('rose_session_id', data.session_id)
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: data.response },
      ])
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          role: 'assistant',
          content: 'I could not reach the AI service. Please check that the backend and Ollama are running, then try again.',
        },
      ])
    } finally {
      setSending(false)
    }
  }

  const categories = [
    'ALL',
    ...Array.from(
      new Set(products.map((product) => product.category?.name).filter(Boolean) as string[]),
    ),
  ]

  const filteredProducts = products.filter((product) => {
    const term = search.toLowerCase()
    const matchesSearch =
      product.name.toLowerCase().includes(term) ||
      product.brand?.name.toLowerCase().includes(term) ||
      product.category?.name.toLowerCase().includes(term)

    const matchesCategory =
      category === 'ALL' || product.category?.name === category

    return matchesSearch && matchesCategory
  })

  return (
    <main>
      <header className="navbar">
        <a className="brand-mark" href="#home">ROSE</a>
        <nav>
          <a href="#home">HOME</a>
          <a href="#shop">SHOP</a>
          <a href="#categories">CATEGORIES</a>
          <a href="#assistant">AI ASSISTANT</a>
        </nav>
        <button className="nav-chat" onClick={() => setChatOpen(true)}>
          CHAT WITH AI <span className="online-dot" />
        </button>
      </header>

      <section className="hero" id="home">
        <div className="hero-content">
          <span className="eyebrow">YOUR PERSONAL BEAUTY SPACE</span>
          <h1>Beauty, made<br /><em>personal.</em></h1>
          <p>
            Discover products that fit your needs. Get thoughtful recommendations
            with the help of your personal AI beauty assistant.
          </p>
          <a className="primary-button" href="#shop">EXPLORE PRODUCTS <span>↗</span></a>
        </div>
        <div className="hero-rose" aria-hidden="true">
          <svg viewBox="0 0 260 300">
            <path d="M130 280 C126 230 137 190 130 150" fill="none" stroke="currentColor" strokeWidth="5" />
            <path d="M130 220 C88 185 65 210 82 235 C98 252 119 237 130 220Z" fill="currentColor" />
            <path d="M132 190 C170 155 194 180 177 205 C162 221 143 205 132 190Z" fill="currentColor" />
            <path d="M130 150 C78 143 52 112 75 75 C91 48 121 57 130 79 C144 45 185 51 194 83 C208 125 169 148 130 150Z" fill="currentColor" />
            <path d="M130 133 C103 120 105 88 130 83 C153 76 169 103 151 119 C143 126 133 119 137 110 C140 102 151 106 149 113" fill="none" stroke="#38383c" strokeWidth="7" strokeLinecap="round" />
          </svg>
        </div>
      </section>

      <section className="shop-section" id="shop">
        <div className="section-heading">
          <div>
            <span className="eyebrow">THE ROSE COLLECTION</span>
            <h2>Find your essentials.</h2>
          </div>
          <span className="product-count">{products.length} PRODUCTS</span>
        </div>

        <div className="filters" id="categories">
          <input
            className="search-input"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search products or brands..."
          />
          <div className="category-list">
            {categories.map((item) => (
              <button
                key={item}
                className={category === item ? 'category-chip active' : 'category-chip'}
                onClick={() => setCategory(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>

        {loadingProducts ? (
          <p className="status-message">Loading products from database...</p>
        ) : productError ? (
          <p className="status-message error-message">{productError}</p>
        ) : filteredProducts.length === 0 ? (
          <p className="status-message">No products found. Try another search.</p>
        ) : (
          <div className="product-grid">
            {filteredProducts.map((product) => (
              <article className="product-card" key={product.id}>
                <div className="product-visual">
                  <span className="product-category">{product.category?.name || 'BEAUTY'}</span>
                  <span className="product-symbol">✿</span>
                  {product.spf ? <span className="spf-label">SPF {product.spf}</span> : null}
                </div>
                <div className="product-info">
                  <span className="product-brand">{product.brand?.name || 'ROSE SELECTION'}</span>
                  <h3>{product.name}</h3>
                  <p>{product.description || 'Discover more about this product with ROSE AI.'}</p>
                  <div className="product-bottom">
                    <span className="product-price">
                      {product.price != null
                        ? `${product.price} ${product.currency || 'USD'}`
                        : 'PRICE UNAVAILABLE'}
                    </span>
                    <span className={product.in_stock ? 'stock available' : 'stock'}>
                      {product.in_stock ? 'IN STOCK' : 'OUT OF STOCK'}
                    </span>
                  </div>
                  <button
                    className="ask-product"
                    onClick={() => {
                      setChatOpen(true)
                      setMessage(`Tell me about ${product.name}. Is it suitable for my skin?`)
                    }}
                  >
                    ASK AI ABOUT THIS <span>↗</span>
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="assistant-section" id="assistant">
        <span className="eyebrow">A LITTLE HELP, A LOT MORE PERSONAL</span>
        <h2>Meet your beauty assistant.</h2>
        <p>
          Not sure what suits your skin? Ask ROSE about ingredients, routines,
          product comparisons and recommendations.
        </p>
        <button className="primary-button" onClick={() => setChatOpen(true)}>
          START A CONVERSATION <span>↗</span>
        </button>
      </section>

      <footer>
        <a className="brand-mark" href="#home">ROSE</a>
        <span>BEAUTY DISCOVERY, REIMAGINED.</span>
        <span>© 2026 ROSE</span>
      </footer>

      <button
        className="floating-chat"
        onClick={() => setChatOpen((open) => !open)}
        aria-label="Open AI chat"
      >
        <span className="online-dot" /> CHAT WITH AI <span className="chat-arrow">↗</span>
      </button>

      {chatOpen && (
        <aside className="chat-panel" aria-label="ROSE AI chat">
          <div className="chat-header">
            <div>
              <span className="chat-title">ROSE AI</span>
              <span className="chat-subtitle"><span className="online-dot" /> ONLINE ASSISTANT</span>
            </div>
            <button className="close-chat" onClick={() => setChatOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="chat-messages">
            {messages.map((item, index) => (
              <div className={`chat-message ${item.role}`} key={index}>
                {item.role === 'assistant' ? (
                  <ReactMarkdown>{item.content}</ReactMarkdown>
                ) : (
                  item.content
                )}
              </div>
            ))}
            {sending && <div className="chat-message assistant">Thinking...</div>}
          </div>
          <form className="chat-form" onSubmit={sendMessage}>
            <input
              ref={chatInput}
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask me anything..."
              disabled={sending}
            />
            <button type="submit" disabled={sending || !message.trim()}>↑</button>
          </form>
        </aside>
      )}
    </main>
  )
}

export default App
