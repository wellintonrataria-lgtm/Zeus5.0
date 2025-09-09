import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3, 
  Target, 
  Shield, 
  Zap,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Settings
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './App.css'

function App() {
  const [signals, setSignals] = useState([])
  const [marketData, setMarketData] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [lastUpdate, setLastUpdate] = useState(new Date())
  const [selectedPair, setSelectedPair] = useState('EURUSD=X')
  const [ws, setWs] = useState(null)

  const forexPairs = [
    { symbol: 'EURUSD=X', name: 'EUR/USD', flag: '🇪🇺🇺🇸' },
    { symbol: 'GBPUSD=X', name: 'GBP/USD', flag: '🇬🇧🇺🇸' },
    { symbol: 'USDJPY=X', name: 'USD/JPY', flag: '🇺🇸🇯🇵' },
    { symbol: 'USDCHF=X', name: 'USD/CHF', flag: '🇺🇸🇨🇭' },
    { symbol: 'AUDUSD=X', name: 'AUD/USD', flag: '🇦🇺🇺🇸' },
    { symbol: 'USDCAD=X', name: 'USD/CAD', flag: '🇺🇸🇨🇦' }
  ]

  // Conectar WebSocket para sinais em tempo real
  useEffect(() => {
    const connectWebSocket = () => {
      const websocket = new WebSocket('ws://localhost:8000/ws')
      
      websocket.onopen = () => {
        console.log('WebSocket conectado')
        setWs(websocket)
      }
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'signals') {
          setSignals(data.data)
          setLastUpdate(new Date())
        }
      }
      
      websocket.onclose = () => {
        console.log('WebSocket desconectado')
        // Reconectar após 5 segundos
        setTimeout(connectWebSocket, 5000)
      }
      
      websocket.onerror = (error) => {
        console.error('Erro WebSocket:', error)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  // Buscar sinais manualmente
  const fetchSignals = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/signals/all')
      const data = await response.json()
      setSignals(data.signals || [])
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Erro ao buscar sinais:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Buscar dados de mercado para um par específico
  const fetchMarketData = async (symbol) => {
    try {
      const response = await fetch(`http://localhost:8000/market-data/${symbol}?timeframe=15m&period=1d`)
      const data = await response.json()
      
      if (data.data) {
        // Processar dados para o gráfico
        const chartData = data.data.slice(-50).map((item, index) => ({
          time: index,
          price: item.close,
          volume: item.volume || 0
        }))
        
        setMarketData(prev => ({
          ...prev,
          [symbol]: {
            ...data,
            chartData
          }
        }))
      }
    } catch (error) {
      console.error('Erro ao buscar dados de mercado:', error)
    }
  }

  // Buscar dados iniciais
  useEffect(() => {
    fetchSignals()
    forexPairs.forEach(pair => {
      fetchMarketData(pair.symbol)
    })
  }, [])

  const getSignalColor = (signalType) => {
    switch (signalType) {
      case 'BUY': return 'text-green-600 bg-green-50 border-green-200'
      case 'SELL': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatTime = (date) => {
    return new Intl.DateTimeFormat('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date)
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      minimumFractionDigits: 4,
      maximumFractionDigits: 5
    }).format(price)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Zeus 5.0</h1>
                <p className="text-sm text-slate-400">Robô de Trading Profissional</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-slate-400">Última atualização</p>
                <p className="text-sm font-medium text-white">{formatTime(lastUpdate)}</p>
              </div>
              
              <Button 
                onClick={fetchSignals} 
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Atualizar
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800 border-slate-700">
            <TabsTrigger value="dashboard" className="data-[state=active]:bg-blue-600">
              <BarChart3 className="w-4 h-4 mr-2" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="signals" className="data-[state=active]:bg-blue-600">
              <Target className="w-4 h-4 mr-2" />
              Sinais
            </TabsTrigger>
            <TabsTrigger value="analysis" className="data-[state=active]:bg-blue-600">
              <Activity className="w-4 h-4 mr-2" />
              Análise
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-blue-600">
              <Settings className="w-4 h-4 mr-2" />
              Configurações
            </TabsTrigger>
          </TabsList>

          {/* Dashboard */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Estatísticas Gerais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-slate-200">Sinais Ativos</CardTitle>
                  <Target className="h-4 w-4 text-blue-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{signals.length}</div>
                  <p className="text-xs text-slate-400">
                    {signals.filter(s => s.confidence >= 70).length} alta confiança
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-slate-200">Pares Monitorados</CardTitle>
                  <Eye className="h-4 w-4 text-green-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">{forexPairs.length}</div>
                  <p className="text-xs text-slate-400">Forex principais</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-slate-200">Confiança Média</CardTitle>
                  <Shield className="h-4 w-4 text-yellow-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white">
                    {signals.length > 0 
                      ? Math.round(signals.reduce((acc, s) => acc + s.confidence, 0) / signals.length)
                      : 0}%
                  </div>
                  <p className="text-xs text-slate-400">Baseado no Método Gorila 4.0</p>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-slate-200">Status Sistema</CardTitle>
                  <CheckCircle className="h-4 w-4 text-green-400" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-400">Online</div>
                  <p className="text-xs text-slate-400">Todos os sistemas operacionais</p>
                </CardContent>
              </Card>
            </div>

            {/* Gráfico de Mercado */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-white">Análise de Mercado</CardTitle>
                    <CardDescription className="text-slate-400">
                      Dados em tempo real dos principais pares de Forex
                    </CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    {forexPairs.slice(0, 3).map(pair => (
                      <Button
                        key={pair.symbol}
                        variant={selectedPair === pair.symbol ? "default" : "outline"}
                        size="sm"
                        onClick={() => setSelectedPair(pair.symbol)}
                        className="text-xs"
                      >
                        {pair.flag} {pair.name}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {marketData[selectedPair]?.chartData ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={marketData[selectedPair].chartData}>
                      <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="time" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#1F2937', 
                          border: '1px solid #374151',
                          borderRadius: '8px',
                          color: '#F9FAFB'
                        }} 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#3B82F6" 
                        fillOpacity={1} 
                        fill="url(#colorPrice)" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    <div className="text-center">
                      <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>Carregando dados de mercado...</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sinais de Trading */}
          <TabsContent value="signals" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">Sinais de Trading</h2>
                <p className="text-slate-400">Baseado no Método Gorila 4.0 com análise multi-timeframe</p>
              </div>
              
              <Alert className="w-auto bg-blue-900/50 border-blue-700">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription className="text-blue-200">
                  Filosofia: "Ganhar muito, perder pouco" - Gestão de risco rigorosa
                </AlertDescription>
              </Alert>
            </div>

            <div className="grid gap-6">
              {signals.length > 0 ? (
                signals.map((signal, index) => (
                  <Card key={index} className="bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getSignalColor(signal.signal_type)}`}>
                            {signal.signal_type === 'BUY' ? (
                              <><TrendingUp className="w-4 h-4 inline mr-1" />COMPRA</>
                            ) : (
                              <><TrendingDown className="w-4 h-4 inline mr-1" />VENDA</>
                            )}
                          </div>
                          <div>
                            <CardTitle className="text-white">{signal.symbol.replace('=X', '')}</CardTitle>
                            <CardDescription className="text-slate-400">
                              {forexPairs.find(p => p.symbol === signal.symbol)?.name || signal.symbol}
                            </CardDescription>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className={`text-lg font-bold ${getConfidenceColor(signal.confidence)}`}>
                            {signal.confidence.toFixed(1)}%
                          </div>
                          <p className="text-xs text-slate-400">Confiança</p>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Preço de Entrada</p>
                          <p className="font-medium text-white">{formatPrice(signal.entry_price)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Stop Loss</p>
                          <p className="font-medium text-red-400">{formatPrice(signal.stop_loss)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 mb-1">Take Profit 1</p>
                          <p className="font-medium text-green-400">{formatPrice(signal.take_profit[0])}</p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-400 mb-1">R/R Ratio</p>
                          <p className="font-medium text-blue-400">1:{signal.risk_reward_ratio}</p>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400">Nível de Confiança</span>
                          <span className={getConfidenceColor(signal.confidence)}>
                            {signal.confidence.toFixed(1)}%
                          </span>
                        </div>
                        <Progress 
                          value={signal.confidence} 
                          className="h-2 bg-slate-700"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between text-xs text-slate-400">
                        <div className="flex items-center space-x-4">
                          <span>Tendência: {signal.analysis?.trend || 'N/A'}</span>
                          <span>Timeframe: {signal.timeframe}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{new Date(signal.timestamp).toLocaleTimeString('pt-BR')}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="py-12">
                    <div className="text-center text-slate-400">
                      <Target className="w-16 h-16 mx-auto mb-4 opacity-50" />
                      <h3 className="text-lg font-medium mb-2">Nenhum sinal ativo</h3>
                      <p>O Zeus 5.0 está analisando o mercado. Novos sinais aparecerão quando as condições forem favoráveis.</p>
                      <Button 
                        onClick={fetchSignals} 
                        className="mt-4 bg-blue-600 hover:bg-blue-700"
                        disabled={isLoading}
                      >
                        <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Verificar Novamente
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Análise Técnica */}
          <TabsContent value="analysis" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Análise Técnica Avançada</h2>
              <p className="text-slate-400">Baseada no Método Gorila 4.0 - Análise multi-timeframe com confluências</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {forexPairs.map(pair => (
                <Card key={pair.symbol} className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-white">
                      <span>{pair.flag}</span>
                      <span>{pair.name}</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-slate-400 mb-1">Tendência Principal</p>
                          <Badge variant="outline" className="text-blue-400 border-blue-400">
                            Analisando...
                          </Badge>
                        </div>
                        <div>
                          <p className="text-slate-400 mb-1">Força do Sinal</p>
                          <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                            Moderada
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <p className="text-xs text-slate-400">Confluências Detectadas</p>
                        <div className="flex flex-wrap gap-1">
                          <Badge variant="secondary" className="text-xs bg-slate-700 text-slate-300">
                            Médias Alinhadas
                          </Badge>
                          <Badge variant="secondary" className="text-xs bg-slate-700 text-slate-300">
                            Fibonacci 61.8%
                          </Badge>
                          <Badge variant="secondary" className="text-xs bg-slate-700 text-slate-300">
                            Suporte/Resistência
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Configurações */}
          <TabsContent value="settings" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">Configurações do Sistema</h2>
              <p className="text-slate-400">Personalize o comportamento do Zeus 5.0</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Gestão de Risco</CardTitle>
                  <CardDescription className="text-slate-400">
                    Configurações baseadas no Método Gorila 4.0
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">
                      Confiança Mínima para Sinais (%)
                    </label>
                    <input 
                      type="range" 
                      min="50" 
                      max="90" 
                      defaultValue="60"
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>50%</span>
                      <span>90%</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm text-slate-300 mb-2 block">
                      Relação Risco/Retorno Mínima
                    </label>
                    <input 
                      type="range" 
                      min="1" 
                      max="5" 
                      step="0.5"
                      defaultValue="2"
                      className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="flex justify-between text-xs text-slate-400 mt-1">
                      <span>1:1</span>
                      <span>1:5</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white">Notificações</CardTitle>
                  <CardDescription className="text-slate-400">
                    Configure alertas e notificações
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-300">Sinais de Alta Confiança</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-300">Alertas de Risco</span>
                    <input type="checkbox" defaultChecked className="rounded" />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-300">Relatórios Diários</span>
                    <input type="checkbox" className="rounded" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

