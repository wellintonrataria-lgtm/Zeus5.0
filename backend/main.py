"""
Zeus 5.0 - Robô de Trading Profissional
Backend FastAPI com integração do Método Gorila 4.0

Desenvolvido com base nas estratégias do "Método do Gorila 4.0"
Focado em Forex com análise multi-timeframe e gestão de risco rigorosa
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from pydantic import BaseModel
import uvicorn
import os

# Importar módulos do Método Gorila 4.0
from gorila_strategies import GorilaStrategies
from risk_management import RiskManager

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos Pydantic
class TradingSignal(BaseModel):
    symbol: str
    timeframe: str
    signal_type: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0-100%
    entry_price: float
    stop_loss: float
    take_profit: List[float]
    risk_reward_ratio: float
    analysis: Dict
    timestamp: datetime

class MarketData(BaseModel):
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime

# Inicialização do FastAPI
app = FastAPI(
    title="Zeus 5.0 - Robô de Trading",
    description="Sistema de Trading Automatizado baseado no Método Gorila 4.0",
    version="5.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Classe principal do Zeus 5.0
class Zeus50TradingBot:
    def __init__(self):
        self.forex_pairs = [
            "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", 
            "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "EURJPY=X"
        ]
        self.timeframes = ["15m", "1h", "1d", "1wk"]
        self.active_signals = {}
        self.market_data_cache = {}
        
        # Inicializar módulos do Método Gorila 4.0
        self.gorila_strategies = GorilaStrategies()
        self.risk_manager = RiskManager()
        
    def get_market_data(self, symbol: str, period: str = "1mo", interval: str = "15m") -> pd.DataFrame:
        """Obtém dados de mercado usando Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"Dados vazios para {symbol}")
                return pd.DataFrame()
                
            # Renomear colunas para padrão
            data.columns = [col.lower() for col in data.columns]
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados para {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_moving_averages(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula médias móveis conforme Método Gorila 4.0"""
        if data.empty:
            return data
            
        # Médias Móveis Exponenciais
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mme400'] = data['close'].ewm(span=400).mean()
        
        # Médias Móveis Aritméticas
        data['mma3'] = data['close'].rolling(window=3).mean()
        data['mma21'] = data['close'].rolling(window=21).mean()
        data['mma50'] = data['close'].rolling(window=50).mean()
        data['mma200'] = data['close'].rolling(window=200).mean()
        
        # VWAP (Volume Weighted Average Price)
        if 'volume' in data.columns:
            data['vwap'] = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
        else:
            data['vwap'] = data['close']  # Fallback se não houver volume
            
        return data
    
    def identify_candlestick_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Identifica padrões de candlestick do Método Gorila 4.0"""
        if len(data) < 2:
            return data
            
        # Corpo do candle
        data['body'] = abs(data['close'] - data['open'])
        data['upper_shadow'] = data['high'] - data[['close', 'open']].max(axis=1)
        data['lower_shadow'] = data[['close', 'open']].min(axis=1) - data['low']
        
        # Padrões de Reversão
        data['martelo'] = self._detect_hammer(data)
        data['estrela_cadente'] = self._detect_shooting_star(data)
        data['enforcado'] = self._detect_hanging_man(data)
        data['doji'] = self._detect_doji(data)
        data['engolfo_alta'] = self._detect_bullish_engulfing(data)
        data['engolfo_baixa'] = self._detect_bearish_engulfing(data)
        data['marubozu_alta'] = self._detect_bullish_marubozu(data)
        data['marubozu_baixa'] = self._detect_bearish_marubozu(data)
        
        return data
    
    def _detect_hammer(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Martelo"""
        condition = (
            (data['lower_shadow'] >= 2.5 * data['body']) &
            (data['upper_shadow'] <= 0.1 * data['body']) &
            (data['body'] > 0)
        )
        return condition.astype(int)
    
    def _detect_shooting_star(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Estrela Cadente"""
        condition = (
            (data['upper_shadow'] >= 2.5 * data['body']) &
            (data['lower_shadow'] <= 0.1 * data['body']) &
            (data['body'] > 0)
        )
        return condition.astype(int)
    
    def _detect_hanging_man(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Enforcado"""
        condition = (
            (data['lower_shadow'] >= 2.5 * data['body']) &
            (data['upper_shadow'] <= 0.1 * data['body']) &
            (data['close'] < data['open'])  # Candle de baixa
        )
        return condition.astype(int)
    
    def _detect_doji(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Doji"""
        avg_body = data['body'].rolling(window=20).mean()
        condition = data['body'] <= (avg_body * 0.1)
        return condition.astype(int)
    
    def _detect_bullish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Engolfo de Alta"""
        if len(data) < 2:
            return pd.Series([0] * len(data), index=data.index)
            
        condition = pd.Series([0] * len(data), index=data.index)
        
        for i in range(1, len(data)):
            prev_candle_bearish = data.iloc[i-1]['close'] < data.iloc[i-1]['open']
            curr_candle_bullish = data.iloc[i]['close'] > data.iloc[i]['open']
            curr_engulfs_prev = (
                data.iloc[i]['open'] < data.iloc[i-1]['close'] and
                data.iloc[i]['close'] > data.iloc[i-1]['open']
            )
            
            if prev_candle_bearish and curr_candle_bullish and curr_engulfs_prev:
                condition.iloc[i] = 1
                
        return condition
    
    def _detect_bearish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Engolfo de Baixa"""
        if len(data) < 2:
            return pd.Series([0] * len(data), index=data.index)
            
        condition = pd.Series([0] * len(data), index=data.index)
        
        for i in range(1, len(data)):
            prev_candle_bullish = data.iloc[i-1]['close'] > data.iloc[i-1]['open']
            curr_candle_bearish = data.iloc[i]['close'] < data.iloc[i]['open']
            curr_engulfs_prev = (
                data.iloc[i]['open'] > data.iloc[i-1]['close'] and
                data.iloc[i]['close'] < data.iloc[i-1]['open']
            )
            
            if prev_candle_bullish and curr_candle_bearish and curr_engulfs_prev:
                condition.iloc[i] = 1
                
        return condition
    
    def _detect_bullish_marubozu(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Marubozu de Alta"""
        avg_body = data['body'].rolling(window=20).mean()
        condition = (
            (data['close'] > data['open']) &
            (data['body'] >= avg_body * 1.5) &
            (data['upper_shadow'] <= data['body'] * 0.1) &
            (data['lower_shadow'] <= data['body'] * 0.1)
        )
        return condition.astype(int)
    
    def _detect_bearish_marubozu(self, data: pd.DataFrame) -> pd.Series:
        """Detecta padrão Marubozu de Baixa"""
        avg_body = data['body'].rolling(window=20).mean()
        condition = (
            (data['close'] < data['open']) &
            (data['body'] >= avg_body * 1.5) &
            (data['upper_shadow'] <= data['body'] * 0.1) &
            (data['lower_shadow'] <= data['body'] * 0.1)
        )
        return condition.astype(int)
    
    def calculate_fibonacci_levels(self, data: pd.DataFrame, lookback: int = 50) -> Dict:
        """Calcula níveis de Fibonacci"""
        if len(data) < lookback:
            return {}
            
        recent_data = data.tail(lookback)
        high = recent_data['high'].max()
        low = recent_data['low'].min()
        
        diff = high - low
        
        levels = {
            'high': high,
            'low': low,
            '23.6%': high - (diff * 0.236),
            '38.2%': high - (diff * 0.382),
            '50%': high - (diff * 0.5),
            '61.8%': high - (diff * 0.618),
            '78.6%': high - (diff * 0.786)
        }
        
        return levels
    
    def identify_trend(self, data: pd.DataFrame) -> str:
        """Identifica tendência baseada em topos e fundos"""
        if len(data) < 20:
            return "INDEFINIDA"
            
        # Últimos 20 períodos
        recent = data.tail(20)
        
        # Identificar topos e fundos locais
        highs = []
        lows = []
        
        for i in range(2, len(recent) - 2):
            # Topo local
            if (recent.iloc[i]['high'] > recent.iloc[i-1]['high'] and 
                recent.iloc[i]['high'] > recent.iloc[i-2]['high'] and
                recent.iloc[i]['high'] > recent.iloc[i+1]['high'] and 
                recent.iloc[i]['high'] > recent.iloc[i+2]['high']):
                highs.append((i, recent.iloc[i]['high']))
            
            # Fundo local
            if (recent.iloc[i]['low'] < recent.iloc[i-1]['low'] and 
                recent.iloc[i]['low'] < recent.iloc[i-2]['low'] and
                recent.iloc[i]['low'] < recent.iloc[i+1]['low'] and 
                recent.iloc[i]['low'] < recent.iloc[i+2]['low']):
                lows.append((i, recent.iloc[i]['low']))
        
        # Analisar tendência
        if len(highs) >= 2 and len(lows) >= 2:
            # Topos e fundos ascendentes = Alta
            if (highs[-1][1] > highs[-2][1] and lows[-1][1] > lows[-2][1]):
                return "ALTA"
            # Topos e fundos descendentes = Baixa
            elif (highs[-1][1] < highs[-2][1] and lows[-1][1] < lows[-2][1]):
                return "BAIXA"
        
        return "INDEFINIDA"
    
    def calculate_signal_confidence(self, data: pd.DataFrame, signal_type: str) -> float:
        """Calcula confiança do sinal baseado em confluências"""
        if data.empty:
            return 0.0
            
        confidence = 0.0
        latest = data.iloc[-1]
        
        # Confluência de médias móveis (30 pontos)
        if signal_type == "BUY":
            if latest['close'] > latest['mme9'] > latest['mma21'] > latest['mma50']:
                confidence += 30
        elif signal_type == "SELL":
            if latest['close'] < latest['mme9'] < latest['mma21'] < latest['mma50']:
                confidence += 30
        
        # Padrões de candlestick (25 pontos)
        if signal_type == "BUY":
            if (latest['martelo'] or latest['engolfo_alta'] or latest['marubozu_alta']):
                confidence += 25
        elif signal_type == "SELL":
            if (latest['estrela_cadente'] or latest['engolfo_baixa'] or latest['marubozu_baixa']):
                confidence += 25
        
        # Tendência (20 pontos)
        trend = self.identify_trend(data)
        if (signal_type == "BUY" and trend == "ALTA") or (signal_type == "SELL" and trend == "BAIXA"):
            confidence += 20
        
        # Proximidade das médias (15 pontos)
        ma_distance = abs(latest['mme9'] - latest['mma21']) / latest['close']
        if ma_distance < 0.002:  # Médias próximas (menos de 0.2%)
            confidence += 15
        
        # Volume (10 pontos) - Se disponível
        if 'volume' in data.columns and len(data) > 20:
            avg_volume = data['volume'].tail(20).mean()
            if latest['volume'] > avg_volume * 1.2:
                confidence += 10
        
        return min(confidence, 100.0)
    
    def calculate_risk_management(self, entry_price: float, signal_type: str, data: pd.DataFrame) -> Dict:
        """Calcula stop loss e take profit baseado no ATR e Fibonacci"""
        if len(data) < 14:
            return {}
        
        # Calcular ATR (Average True Range)
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1]
        
        # Níveis de Fibonacci
        fib_levels = self.calculate_fibonacci_levels(data)
        
        if signal_type == "BUY":
            # Stop Loss: 2 ATRs abaixo do preço de entrada
            stop_loss = entry_price - (2 * atr)
            
            # Take Profits escalonados
            tp1 = entry_price + (1.5 * atr)  # 1:1.5 R/R
            tp2 = entry_price + (3 * atr)    # 1:3 R/R
            tp3 = entry_price + (4.5 * atr)  # 1:4.5 R/R
            
        else:  # SELL
            # Stop Loss: 2 ATRs acima do preço de entrada
            stop_loss = entry_price + (2 * atr)
            
            # Take Profits escalonados
            tp1 = entry_price - (1.5 * atr)  # 1:1.5 R/R
            tp2 = entry_price - (3 * atr)    # 1:3 R/R
            tp3 = entry_price - (4.5 * atr)  # 1:4.5 R/R
        
        risk = abs(entry_price - stop_loss)
        reward = abs(tp2 - entry_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            'stop_loss': round(stop_loss, 5),
            'take_profit': [round(tp1, 5), round(tp2, 5), round(tp3, 5)],
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'atr': round(atr, 5)
        }
    
    def generate_trading_signal(self, symbol: str, timeframe: str = "15m") -> Optional[TradingSignal]:
        """Gera sinal de trading baseado no Método Gorila 4.0 com setups avançados"""
        try:
            # Obter dados de mercado
            data = self.get_market_data(symbol, period="3mo", interval=timeframe)
            
            if data.empty or len(data) < 50:
                return None
            
            # Calcular indicadores básicos
            data = self.calculate_moving_averages(data)
            data = self.identify_candlestick_patterns(data)
            
            latest = data.iloc[-1]
            entry_price = latest['close']
            
            # Análise Multi-Timeframe (Hierarquia dos Tempos Gráficos)
            mtf_analysis = self.gorila_strategies.analyze_multi_timeframe(symbol, self.get_market_data)
            overall_bias = mtf_analysis.get("overall_bias", "NEUTRO")
            mtf_confidence = mtf_analysis.get("confidence", 0)
            
            # Testar setups específicos do Método Gorila 4.0
            setups_results = []
            
            # Setup 9.1 Compra
            setup_91_compra = self.gorila_strategies.setup_91_compra(data.copy())
            if setup_91_compra["signal"]:
                setups_results.append(setup_91_compra)
            
            # Setup 9.1 Venda
            setup_91_venda = self.gorila_strategies.setup_91_venda(data.copy())
            if setup_91_venda["signal"]:
                setups_results.append(setup_91_venda)
            
            # Setup 9.2
            setup_92 = self.gorila_strategies.setup_92(data.copy())
            if setup_92["signal"]:
                setups_results.append(setup_92)
            
            # Setup Ponto Contínuo
            setup_pc = self.gorila_strategies.setup_ponto_continuo(data.copy())
            if setup_pc["signal"]:
                setups_results.append(setup_pc)
            
            # Setup Agulhada
            setup_agulhada = self.gorila_strategies.setup_agulhada(data.copy(), timeframe)
            if setup_agulhada["signal"]:
                setups_results.append(setup_agulhada)
            
            # Se nenhum setup específico foi encontrado, usar lógica geral
            if not setups_results:
                return self._generate_general_signal(data, symbol, timeframe, mtf_analysis)
            
            # Escolher o setup com maior confiança
            best_setup = max(setups_results, key=lambda x: x.get("confidence", 0))
            setup_details = best_setup["details"]
            
            # Determinar tipo de sinal
            signal_type = "BUY" if "COMPRA" in setup_details["type"] else "SELL"
            
            # Usar preços do setup
            entry_price = setup_details["entry_price"]
            stop_loss = setup_details["stop_loss"]
            
            # Calcular take profits usando gestão de risco avançada
            tp_levels = self.risk_manager.calculate_take_profit_levels(
                entry_price, stop_loss, signal_type
            )
            
            take_profit = [
                tp_levels["tp1"]["price"],
                tp_levels["tp2"]["price"],
                tp_levels["tp3"]["price"]
            ]
            
            # Calcular confiança combinada
            setup_confidence = best_setup.get("confidence", 0)
            combined_confidence = (setup_confidence * 0.7) + (mtf_confidence * 0.3)
            
            # Validar setup com gestão de risco
            validation = self.risk_manager.validate_trade_setup(
                entry_price, stop_loss, take_profit[1], combined_confidence
            )
            
            if not validation["valid"]:
                logger.warning(f"Setup inválido para {symbol}: {validation['errors']}")
                return None
            
            # Calcular relação risco/retorno
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit[1] - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Análise detalhada
            analysis = {
                'setup_used': best_setup["setup"],
                'setup_details': setup_details,
                'mtf_analysis': mtf_analysis,
                'trend': self.identify_trend(data),
                'ma_alignment': {
                    'mme9': latest['mme9'],
                    'mma21': latest['mma21'],
                    'mma50': latest['mma50'],
                    'mma200': latest['mma200']
                },
                'candlestick_patterns': {
                    'martelo': bool(latest['martelo']),
                    'estrela_cadente': bool(latest['estrela_cadente']),
                    'engolfo_alta': bool(latest['engolfo_alta']),
                    'engolfo_baixa': bool(latest['engolfo_baixa']),
                    'doji': bool(latest['doji'])
                },
                'fibonacci_levels': self.calculate_fibonacci_levels(data),
                'risk_validation': validation,
                'confluences': mtf_analysis.get("confluences", [])
            }
            
            return TradingSignal(
                symbol=symbol,
                timeframe=timeframe,
                signal_type=signal_type,
                confidence=combined_confidence,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_reward_ratio=risk_reward_ratio,
                analysis=analysis,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinal para {symbol}: {e}")
            return None
    
    def _generate_general_signal(self, data: pd.DataFrame, symbol: str, timeframe: str, mtf_analysis: Dict) -> Optional[TradingSignal]:
        """Gera sinal usando lógica geral quando nenhum setup específico é encontrado"""
        
        latest = data.iloc[-1]
        entry_price = latest['close']
        
        # Lógica de sinal baseada no Método Gorila 4.0
        signal_type = "HOLD"
        
        # Sinal de COMPRA
        buy_conditions = [
            latest['close'] > latest['mme9'],  # Preço acima da MME9
            latest['mme9'] > latest['mma21'],  # MME9 acima da MMA21
            latest['mma21'] > latest['mma50'], # MMA21 acima da MMA50
            (latest['martelo'] or latest['engolfo_alta'] or latest['marubozu_alta']),  # Padrão de alta
            mtf_analysis.get("overall_bias") in ["ALTA", "NEUTRO"]  # Viés MTF favorável
        ]
        
        # Sinal de VENDA
        sell_conditions = [
            latest['close'] < latest['mme9'],  # Preço abaixo da MME9
            latest['mme9'] < latest['mma21'],  # MME9 abaixo da MMA21
            latest['mma21'] < latest['mma50'], # MMA21 abaixo da MMA50
            (latest['estrela_cadente'] or latest['engolfo_baixa'] or latest['marubozu_baixa']),  # Padrão de baixa
            mtf_analysis.get("overall_bias") in ["BAIXA", "NEUTRO"]  # Viés MTF favorável
        ]
        
        # Determinar sinal
        if sum(buy_conditions) >= 3:
            signal_type = "BUY"
        elif sum(sell_conditions) >= 3:
            signal_type = "SELL"
        
        if signal_type == "HOLD":
            return None
        
        # Calcular confiança
        confidence = self.calculate_signal_confidence(data, signal_type)
        mtf_confidence = mtf_analysis.get("confidence", 0)
        combined_confidence = (confidence * 0.6) + (mtf_confidence * 0.4)
        
        # Filtro de confiança mínima (60%)
        if combined_confidence < 60:
            return None
        
        # Calcular gestão de risco
        risk_mgmt = self.calculate_risk_management(entry_price, signal_type, data)
        
        if not risk_mgmt:
            return None
        
        # Análise detalhada
        analysis = {
            'setup_used': 'Análise Geral',
            'mtf_analysis': mtf_analysis,
            'trend': self.identify_trend(data),
            'ma_alignment': {
                'mme9': latest['mme9'],
                'mma21': latest['mma21'],
                'mma50': latest['mma50'],
                'mma200': latest['mma200']
            },
            'candlestick_patterns': {
                'martelo': bool(latest['martelo']),
                'estrela_cadente': bool(latest['estrela_cadente']),
                'engolfo_alta': bool(latest['engolfo_alta']),
                'engolfo_baixa': bool(latest['engolfo_baixa']),
                'doji': bool(latest['doji'])
            },
            'fibonacci_levels': self.calculate_fibonacci_levels(data),
            'atr': risk_mgmt.get('atr', 0),
            'confluences': mtf_analysis.get("confluences", [])
        }
        
        return TradingSignal(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=signal_type,
            confidence=combined_confidence,
            entry_price=entry_price,
            stop_loss=risk_mgmt['stop_loss'],
            take_profit=risk_mgmt['take_profit'],
            risk_reward_ratio=risk_mgmt['risk_reward_ratio'],
            analysis=analysis,
            timestamp=datetime.now()
        )

# Instância global do bot
zeus_bot = Zeus50TradingBot()

# Rotas da API
@app.get("/")
async def root():
    """Página inicial"""
    return {"message": "Zeus 5.0 - Robô de Trading Profissional", "status": "online", "version": "5.0.0"}

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/forex-pairs")
async def get_forex_pairs():
    """Lista os pares de Forex disponíveis"""
    return {"pairs": zeus_bot.forex_pairs}

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "15m", period: str = "1mo"):
    """Obtém dados de mercado para um símbolo"""
    try:
        data = zeus_bot.get_market_data(symbol, period, timeframe)
        
        if data.empty:
            raise HTTPException(status_code=404, detail="Dados não encontrados")
        
        # Converter para formato JSON
        data_dict = data.reset_index().to_dict('records')
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "data": data_dict[-100:]  # Últimos 100 registros
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signal/{symbol}")
async def get_trading_signal(symbol: str, timeframe: str = "15m"):
    """Gera sinal de trading para um símbolo"""
    try:
        signal = zeus_bot.generate_trading_signal(symbol, timeframe)
        
        if not signal:
            return {"message": "Nenhum sinal gerado no momento", "symbol": symbol}
        
        return signal.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/signals/all")
async def get_all_signals():
    """Gera sinais para todos os pares de Forex"""
    signals = []
    
    for pair in zeus_bot.forex_pairs:
        try:
            signal = zeus_bot.generate_trading_signal(pair, "15m")
            if signal:
                signals.append(signal.dict())
        except Exception as e:
            logger.error(f"Erro ao gerar sinal para {pair}: {e}")
    
    return {"signals": signals, "count": len(signals)}

@app.get("/analysis/{symbol}")
async def get_detailed_analysis(symbol: str, timeframe: str = "15m"):
    """Análise técnica detalhada de um símbolo"""
    try:
        data = zeus_bot.get_market_data(symbol, period="3mo", interval=timeframe)
        
        if data.empty:
            raise HTTPException(status_code=404, detail="Dados não encontrados")
        
        # Calcular indicadores
        data = zeus_bot.calculate_moving_averages(data)
        data = zeus_bot.identify_candlestick_patterns(data)
        
        latest = data.iloc[-1]
        
        analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": latest['close'],
            "trend": zeus_bot.identify_trend(data),
            "moving_averages": {
                "mme9": latest['mme9'],
                "mma21": latest['mma21'],
                "mma50": latest['mma50'],
                "mma200": latest['mma200'],
                "vwap": latest['vwap']
            },
            "candlestick_patterns": {
                "martelo": bool(latest['martelo']),
                "estrela_cadente": bool(latest['estrela_cadente']),
                "enforcado": bool(latest['enforcado']),
                "doji": bool(latest['doji']),
                "engolfo_alta": bool(latest['engolfo_alta']),
                "engolfo_baixa": bool(latest['engolfo_baixa']),
                "marubozu_alta": bool(latest['marubozu_alta']),
                "marubozu_baixa": bool(latest['marubozu_baixa'])
            },
            "fibonacci_levels": zeus_bot.calculate_fibonacci_levels(data),
            "support_resistance": {
                "support": data['low'].tail(50).min(),
                "resistance": data['high'].tail(50).max()
            },
            "timestamp": datetime.now()
        }
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para sinais em tempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # Enviar sinais a cada 30 segundos
            await asyncio.sleep(30)
            
            signals = []
            for pair in zeus_bot.forex_pairs[:4]:  # Primeiros 4 pares para não sobrecarregar
                try:
                    signal = zeus_bot.generate_trading_signal(pair, "15m")
                    if signal:
                        signals.append(signal.dict())
                except:
                    pass
            
            if signals:
                await manager.send_personal_message(
                    json.dumps({"type": "signals", "data": signals}), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Servir arquivos estáticos do frontend
if os.path.exists("../frontend/build"):
    app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve o frontend React"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse("../frontend/build/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

