# Zeus 5.0 - Robô de Trading Profissional

![Zeus 5.0 Logo](https://img.shields.io/badge/Zeus%205.0-Trading%20Bot-blue?style=for-the-badge&logo=trending-up)

## 🚀 Visão Geral

O **Zeus 5.0** é um robô de trading profissional baseado no **Método Gorila 4.0**, desenvolvido para operar no mercado Forex com análise multi-timeframe e gestão de risco rigorosa. Segue a filosofia "**Ganhar muito, perder pouco**" através de estratégias comprovadas e automação inteligente.

### ✨ Características Principais

- 🎯 **Setups Específicos**: 9.1, 9.2, Ponto Contínuo, Agulhada
- 📊 **Análise Multi-Timeframe**: Hierarquia dos tempos gráficos (15m, 1h, 1d, 1wk)
- 🛡️ **Gestão de Risco Avançada**: Semana de Ouro, R/R mínimo 1:2
- 📈 **Indicadores Técnicos**: Médias móveis, VWAP, Fibonacci, ATR
- 🕯️ **Padrões de Candlestick**: Martelo, Estrela Cadente, Engolfo, Doji
- 🌐 **Interface Moderna**: Dashboard em tempo real com React
- 🔄 **WebSocket**: Sinais em tempo real
- 📱 **Responsivo**: Funciona em desktop e mobile

## 🏗️ Arquitetura

### Backend (FastAPI)
- **API RESTful** com documentação automática
- **WebSocket** para dados em tempo real
- **Módulos especializados**:
  - `gorila_strategies.py`: Implementação dos setups
  - `risk_management.py`: Gestão de risco avançada
  - `main.py`: API principal

### Frontend (React)
- **Interface moderna** com Tailwind CSS
- **Componentes UI** com shadcn/ui
- **Gráficos interativos** com Recharts
- **Dashboard em tempo real**

## 🚀 Deploy Rápido

### Opção 1: Vercel (Recomendado)

1. **Fork/Clone** este repositório
2. **Conecte ao Vercel**:
   ```bash
   npm i -g vercel
   vercel --prod
   ```
3. **Configure as variáveis** (se necessário)
4. **Acesse seu link permanente**

### Opção 2: Render

1. **Conecte seu repositório** ao Render
2. **Use o arquivo** `render.yaml` (já configurado)
3. **Deploy automático** será iniciado
4. **Acesse seu link permanente**

### Opção 3: Docker (Local/VPS)

```bash
# Clone o repositório
git clone <seu-repo>
cd zeus-5.0

# Inicie com Docker Compose
docker-compose up -d

# Acesse:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 🛠️ Desenvolvimento Local

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pnpm (recomendado)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
pnpm install
pnpm run dev
```

## 📊 Método Gorila 4.0 - Implementação

### Setups Automatizados

#### 🎯 Setup 9.1
- **Compra**: MME9 vira para cima → Entrada no rompimento da máxima
- **Venda**: MME9 vira para baixo → Entrada no rompimento da mínima
- **Stop**: Extremo oposto do candle de virada
- **Condução**: Pela MME9

#### 🎯 Setup 9.2
- **Gatilho**: Deslocamento (candle fecha abaixo da mínima anterior)
- **Entrada**: Rompimento da máxima do candle de deslocamento
- **Flexibilidade**: Deslocamento de gatilho automático

#### 🎯 Ponto Contínuo (PC)
- **Contexto**: Preços acima da MM21 ascendente
- **Entrada**: Recuo até a MM21 + rompimento
- **Força**: Proximidade das médias

#### 🎯 Agulhada
- **Alinhamento**: MME9 > MMA21 > MMA50 (ou inverso)
- **Confluência**: Médias passam pelo candle
- **Força**: Volume e inclinação das médias

### Análise Multi-Timeframe

| Timeframe | Peso | Função |
|-----------|------|--------|
| **Semanal** | 40% | Tendência principal |
| **Diário** | 30% | Contexto macro |
| **1 Hora** | 20% | Entrada e saída |
| **15 Min** | 10% | Timing preciso |

### Gestão de Risco

- **Risco máximo por operação**: 1-2% do capital
- **Relação R/R mínima**: 1:2
- **Semana de Ouro**: Primeira semana do mês (risco reduzido)
- **Take Profit escalonado**: 30% em 1:1.5, 40% em 1:2.5, 30% em 1:4

## 📈 Funcionalidades da Interface

### Dashboard Principal
- **Estatísticas em tempo real**
- **Sinais ativos** com níveis de confiança
- **Gráficos interativos** dos principais pares
- **Status do sistema**

### Sinais de Trading
- **Lista completa** de sinais ativos
- **Detalhes técnicos**: Setup usado, confluências, R/R
- **Filtros por confiança** e timeframe
- **Atualizações automáticas**

### Análise Técnica
- **Confluências detectadas**
- **Força da tendência** por timeframe
- **Suporte e resistência** dinâmicos
- **Padrões de candlestick** identificados

### Configurações
- **Gestão de risco** personalizável
- **Níveis de confiança** ajustáveis
- **Notificações** configuráveis

## 🔧 API Endpoints

### Principais Rotas

```
GET  /                     # Status da API
GET  /health              # Health check
GET  /forex-pairs         # Pares disponíveis
GET  /market-data/{symbol} # Dados de mercado
GET  /signal/{symbol}     # Sinal específico
GET  /signals/all         # Todos os sinais
GET  /analysis/{symbol}   # Análise detalhada
WS   /ws                  # WebSocket (tempo real)
```

### Exemplo de Resposta - Sinal

```json
{
  "symbol": "EURUSD=X",
  "timeframe": "15m",
  "signal_type": "BUY",
  "confidence": 85.2,
  "entry_price": 1.0850,
  "stop_loss": 1.0820,
  "take_profit": [1.0895, 1.0925, 1.0970],
  "risk_reward_ratio": 2.5,
  "analysis": {
    "setup_used": "Setup 9.1 Compra",
    "mtf_analysis": {...},
    "confluences": [
      "Tendência de Alta Multi-Timeframe",
      "Médias Alinhadas Multi-Timeframe"
    ]
  }
}
```

## 🎨 Personalização

### Modificar Parâmetros de Risco
```python
# backend/risk_management.py
class RiskManager:
    def __init__(self):
        self.max_daily_risk = 0.02      # 2% máximo por dia
        self.max_position_risk = 0.01   # 1% máximo por posição
        self.min_risk_reward = 2.0      # Mínimo 1:2 R/R
```

### Adicionar Novos Pares
```python
# backend/main.py
self.forex_pairs = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X",
    "SEUS_NOVOS_PARES=X"  # Adicione aqui
]
```

### Customizar Interface
```jsx
// frontend/src/App.jsx
// Modifique cores, layout e componentes
```

## 📊 Métricas e Monitoramento

### Indicadores de Performance
- **Win Rate**: Taxa de acerto
- **Profit Factor**: Fator de lucro
- **Drawdown**: Rebaixamento máximo
- **Sharpe Ratio**: Relação risco/retorno

### Logs e Debugging
```bash
# Logs do backend
tail -f backend/logs/zeus.log

# Logs do frontend
# Disponíveis no console do navegador
```

## 🔒 Segurança

- **Validação rigorosa** de todos os inputs
- **Rate limiting** nas APIs
- **CORS configurado** adequadamente
- **Logs de auditoria** para todas as operações

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie uma branch** (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra um Pull Request**

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Documentação**: Este README
- **Issues**: Use o sistema de issues do GitHub
- **Discussões**: Aba Discussions do repositório

## 🎯 Roadmap

- [ ] **Backtesting** automatizado
- [ ] **Alertas por email/SMS**
- [ ] **Integração com brokers**
- [ ] **Machine Learning** para otimização
- [ ] **App mobile** nativo
- [ ] **Análise de sentimento** do mercado

---

**⚠️ Aviso Legal**: Este software é apenas para fins educacionais e de pesquisa. Trading envolve riscos significativos. Sempre consulte um profissional qualificado antes de tomar decisões de investimento.

**💡 Filosofia Zeus 5.0**: "Ganhar muito, perder pouco" - Disciplina, paciência e gestão de risco são as chaves do sucesso no trading.

---

Desenvolvido com ❤️ baseado no **Método Gorila 4.0**

