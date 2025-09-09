"""
Estratégias Avançadas do Método Gorila 4.0
Implementação completa dos setups e análises multi-timeframe
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GorilaStrategies:
    """Implementação das estratégias do Método Gorila 4.0"""
    
    def __init__(self):
        self.timeframes = {
            "15m": {"period": "1mo", "interval": "15m"},
            "1h": {"period": "3mo", "interval": "1h"},
            "1d": {"period": "1y", "interval": "1d"},
            "1wk": {"period": "2y", "interval": "1wk"}
        }
    
    def setup_91_compra(self, data: pd.DataFrame) -> Dict:
        """
        Setup 9.1 de Compra - Método Gorila 4.0
        
        Regras:
        1. MME9 caindo, esperar virar para cima
        2. Marcar máxima do candle que fez a virada
        3. Entrada: rompimento da máxima (1 tick acima)
        4. Stop: mínima do candle de virada
        5. Condução: pela MME9
        """
        if len(data) < 10:
            return {"signal": False, "details": "Dados insuficientes"}
        
        # Calcular MME9
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mme9_slope'] = data['mme9'].diff()
        
        signals = []
        
        for i in range(2, len(data)):
            # Verificar se MME9 estava caindo e agora está subindo
            prev_slope = data['mme9_slope'].iloc[i-1]
            curr_slope = data['mme9_slope'].iloc[i]
            
            if prev_slope < 0 and curr_slope > 0:
                # Virada detectada
                virada_candle = data.iloc[i]
                entry_price = virada_candle['high'] + 0.0001  # 1 pip acima
                stop_loss = virada_candle['low']
                
                # Validar se o risco é aceitável (máximo 2% do preço)
                risk_pct = abs(entry_price - stop_loss) / entry_price
                if risk_pct <= 0.02:
                    signals.append({
                        "type": "SETUP_91_COMPRA",
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "virada_index": i,
                        "risk_pct": risk_pct,
                        "timestamp": virada_candle.name
                    })
        
        if signals:
            latest_signal = signals[-1]
            return {
                "signal": True,
                "setup": "9.1 Compra",
                "details": latest_signal,
                "confidence": 75  # Base para setup 9.1
            }
        
        return {"signal": False, "details": "Condições não atendidas"}
    
    def setup_91_venda(self, data: pd.DataFrame) -> Dict:
        """
        Setup 9.1 de Venda - Método Gorila 4.0
        
        Regras:
        1. MME9 subindo, esperar virar para baixo
        2. Marcar mínima do candle que fez a virada
        3. Entrada: rompimento da mínima (1 tick abaixo)
        4. Stop: máxima do candle de virada
        5. Condução: pela MME9
        """
        if len(data) < 10:
            return {"signal": False, "details": "Dados insuficientes"}
        
        # Calcular MME9
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mme9_slope'] = data['mme9'].diff()
        
        signals = []
        
        for i in range(2, len(data)):
            # Verificar se MME9 estava subindo e agora está caindo
            prev_slope = data['mme9_slope'].iloc[i-1]
            curr_slope = data['mme9_slope'].iloc[i]
            
            if prev_slope > 0 and curr_slope < 0:
                # Virada detectada
                virada_candle = data.iloc[i]
                entry_price = virada_candle['low'] - 0.0001  # 1 pip abaixo
                stop_loss = virada_candle['high']
                
                # Validar se o risco é aceitável
                risk_pct = abs(entry_price - stop_loss) / entry_price
                if risk_pct <= 0.02:
                    signals.append({
                        "type": "SETUP_91_VENDA",
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "virada_index": i,
                        "risk_pct": risk_pct,
                        "timestamp": virada_candle.name
                    })
        
        if signals:
            latest_signal = signals[-1]
            return {
                "signal": True,
                "setup": "9.1 Venda",
                "details": latest_signal,
                "confidence": 75
            }
        
        return {"signal": False, "details": "Condições não atendidas"}
    
    def setup_92(self, data: pd.DataFrame) -> Dict:
        """
        Setup 9.2 - Método Gorila 4.0
        
        Regras:
        1. MME9 subindo
        2. Candle fecha abaixo da mínima do anterior (deslocamento de gatilho)
        3. Marcar máxima desse candle
        4. Entrada: rompimento da máxima
        5. Deslocamento de gatilho: abaixar entrada se não romper
        """
        if len(data) < 10:
            return {"signal": False, "details": "Dados insuficientes"}
        
        # Calcular MME9
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mme9_slope'] = data['mme9'].diff()
        
        signals = []
        
        for i in range(2, len(data)):
            # Verificar se MME9 está subindo
            if data['mme9_slope'].iloc[i] > 0:
                # Verificar deslocamento de gatilho
                curr_candle = data.iloc[i]
                prev_candle = data.iloc[i-1]
                
                if curr_candle['close'] < prev_candle['low']:
                    # Deslocamento detectado
                    entry_price = curr_candle['high'] + 0.0001
                    stop_loss = curr_candle['low']
                    
                    risk_pct = abs(entry_price - stop_loss) / entry_price
                    if risk_pct <= 0.02:
                        signals.append({
                            "type": "SETUP_92",
                            "entry_price": entry_price,
                            "stop_loss": stop_loss,
                            "gatilho_index": i,
                            "risk_pct": risk_pct,
                            "timestamp": curr_candle.name
                        })
        
        if signals:
            latest_signal = signals[-1]
            return {
                "signal": True,
                "setup": "9.2",
                "details": latest_signal,
                "confidence": 70
            }
        
        return {"signal": False, "details": "Condições não atendidas"}
    
    def setup_ponto_continuo(self, data: pd.DataFrame) -> Dict:
        """
        Setup Ponto Contínuo (PC) - Método Gorila 4.0
        
        Regras:
        1. Preços trabalhando acima da MM21
        2. Recuo (correção) para a média
        3. Candle encosta na MM21
        4. Marcar máxima e aguardar rompimento
        5. MM21 deve estar ascendente
        """
        if len(data) < 25:
            return {"signal": False, "details": "Dados insuficientes"}
        
        # Calcular médias
        data['mma21'] = data['close'].rolling(window=21).mean()
        data['mma21_slope'] = data['mma21'].diff()
        
        signals = []
        
        for i in range(21, len(data)):
            # Verificar se MM21 está ascendente
            if data['mma21_slope'].iloc[i] > 0:
                curr_candle = data.iloc[i]
                
                # Verificar se preço está próximo da MM21 (tolerância de 0.1%)
                distance_to_ma21 = abs(curr_candle['low'] - curr_candle['mma21']) / curr_candle['close']
                
                if distance_to_ma21 <= 0.001:  # Muito próximo da MM21
                    # Verificar se estava acima da MM21 nos últimos candles
                    recent_above_ma21 = all(
                        data['close'].iloc[j] > data['mma21'].iloc[j] 
                        for j in range(max(0, i-5), i)
                    )
                    
                    if recent_above_ma21:
                        entry_price = curr_candle['high'] + 0.0001
                        stop_loss = curr_candle['mma21'] - 0.0002  # Abaixo da MM21
                        
                        risk_pct = abs(entry_price - stop_loss) / entry_price
                        if risk_pct <= 0.02:
                            signals.append({
                                "type": "PONTO_CONTINUO",
                                "entry_price": entry_price,
                                "stop_loss": stop_loss,
                                "pc_index": i,
                                "risk_pct": risk_pct,
                                "timestamp": curr_candle.name
                            })
        
        if signals:
            latest_signal = signals[-1]
            return {
                "signal": True,
                "setup": "Ponto Contínuo",
                "details": latest_signal,
                "confidence": 80
            }
        
        return {"signal": False, "details": "Condições não atendidas"}
    
    def setup_agulhada(self, data: pd.DataFrame, timeframe: str = "15m") -> Dict:
        """
        Setup Agulhada - Método Gorila 4.0
        
        Regras para Intraday (15m, 5m):
        1. MME9 > MMA21 > MMA50 (alinhamento)
        2. As 3 médias passam por dentro do candle (agulha)
        3. Médias viradas ou virando para cima
        4. Rompimento de suporte/resistência importante
        """
        if len(data) < 55:
            return {"signal": False, "details": "Dados insuficientes"}
        
        # Calcular médias
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mma21'] = data['close'].rolling(window=21).mean()
        data['mma50'] = data['close'].rolling(window=50).mean()
        
        # Calcular inclinações
        data['mme9_slope'] = data['mme9'].diff()
        data['mma21_slope'] = data['mma21'].diff()
        data['mma50_slope'] = data['mma50'].diff()
        
        signals = []
        
        for i in range(50, len(data)):
            curr_candle = data.iloc[i]
            
            # Verificar alinhamento das médias (compra)
            ma_alignment_bull = (
                curr_candle['mme9'] > curr_candle['mma21'] > curr_candle['mma50']
            )
            
            # Verificar alinhamento das médias (venda)
            ma_alignment_bear = (
                curr_candle['mme9'] < curr_candle['mma21'] < curr_candle['mma50']
            )
            
            if ma_alignment_bull or ma_alignment_bear:
                # Verificar se as médias passam pelo candle (agulha)
                candle_high = curr_candle['high']
                candle_low = curr_candle['low']
                
                mme9_in_candle = candle_low <= curr_candle['mme9'] <= candle_high
                mma21_in_candle = candle_low <= curr_candle['mma21'] <= candle_high
                mma50_in_candle = candle_low <= curr_candle['mma50'] <= candle_high
                
                if mme9_in_candle and mma21_in_candle and mma50_in_candle:
                    # Verificar inclinação das médias
                    if ma_alignment_bull:
                        # Agulhada de compra
                        medias_inclinadas = (
                            curr_candle['mme9_slope'] > 0 and
                            curr_candle['mma21_slope'] > 0 and
                            curr_candle['mma50_slope'] >= 0
                        )
                        
                        if medias_inclinadas:
                            entry_price = curr_candle['high'] + 0.0001
                            stop_loss = min(curr_candle['mme9'], curr_candle['mma21']) - 0.0002
                            signal_type = "AGULHADA_COMPRA"
                    
                    elif ma_alignment_bear:
                        # Agulhada de venda
                        medias_inclinadas = (
                            curr_candle['mme9_slope'] < 0 and
                            curr_candle['mma21_slope'] < 0 and
                            curr_candle['mma50_slope'] <= 0
                        )
                        
                        if medias_inclinadas:
                            entry_price = curr_candle['low'] - 0.0001
                            stop_loss = max(curr_candle['mme9'], curr_candle['mma21']) + 0.0002
                            signal_type = "AGULHADA_VENDA"
                    
                    if 'signal_type' in locals():
                        risk_pct = abs(entry_price - stop_loss) / entry_price
                        if risk_pct <= 0.025:  # Agulhada permite risco um pouco maior
                            signals.append({
                                "type": signal_type,
                                "entry_price": entry_price,
                                "stop_loss": stop_loss,
                                "agulhada_index": i,
                                "risk_pct": risk_pct,
                                "timestamp": curr_candle.name
                            })
        
        if signals:
            latest_signal = signals[-1]
            confidence = 85 if "COMPRA" in latest_signal["type"] else 80
            return {
                "signal": True,
                "setup": "Agulhada",
                "details": latest_signal,
                "confidence": confidence
            }
        
        return {"signal": False, "details": "Condições não atendidas"}
    
    def analyze_multi_timeframe(self, symbol: str, get_data_func) -> Dict:
        """
        Análise Multi-Timeframe - Hierarquia dos Tempos Gráficos
        
        Ordem de importância:
        1. Semanal (1wk) - Tendência principal
        2. Diário (1d) - Contexto macro
        3. 1 Hora (1h) - Entrada e saída
        4. 15 Minutos (15m) - Timing preciso
        """
        analysis = {
            "symbol": symbol,
            "timeframes": {},
            "overall_bias": "NEUTRO",
            "confidence": 0,
            "confluences": []
        }
        
        # Analisar cada timeframe
        for tf, params in self.timeframes.items():
            try:
                data = get_data_func(symbol, params["period"], params["interval"])
                
                if data.empty:
                    continue
                
                # Calcular indicadores
                data = self._calculate_all_indicators(data)
                
                # Identificar tendência
                trend = self._identify_trend_advanced(data)
                
                # Calcular força da tendência
                trend_strength = self._calculate_trend_strength(data)
                
                # Identificar suporte/resistência
                support_resistance = self._find_support_resistance(data)
                
                analysis["timeframes"][tf] = {
                    "trend": trend,
                    "trend_strength": trend_strength,
                    "support_resistance": support_resistance,
                    "ma_alignment": self._check_ma_alignment(data),
                    "price_position": self._analyze_price_position(data)
                }
                
            except Exception as e:
                logger.error(f"Erro na análise {tf}: {e}")
                continue
        
        # Determinar viés geral baseado na hierarquia
        analysis["overall_bias"] = self._determine_overall_bias(analysis["timeframes"])
        analysis["confidence"] = self._calculate_mtf_confidence(analysis["timeframes"])
        analysis["confluences"] = self._find_confluences(analysis["timeframes"])
        
        return analysis
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos os indicadores necessários"""
        # Médias móveis
        data['mme9'] = data['close'].ewm(span=9).mean()
        data['mma3'] = data['close'].rolling(window=3).mean()
        data['mma21'] = data['close'].rolling(window=21).mean()
        data['mma50'] = data['close'].rolling(window=50).mean()
        data['mma200'] = data['close'].rolling(window=200).mean()
        data['mme400'] = data['close'].ewm(span=400).mean()
        
        # VWAP
        if 'volume' in data.columns:
            data['vwap'] = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
        else:
            data['vwap'] = data['close']
        
        # ATR para volatilidade
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data['atr'] = true_range.rolling(window=14).mean()
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        return data
    
    def _identify_trend_advanced(self, data: pd.DataFrame) -> str:
        """Identifica tendência usando múltiplos critérios"""
        if len(data) < 50:
            return "INDEFINIDA"
        
        recent = data.tail(20)
        
        # Critério 1: Médias móveis
        latest = recent.iloc[-1]
        ma_trend = "NEUTRO"
        
        if (latest['mme9'] > latest['mma21'] > latest['mma50'] > latest['mma200']):
            ma_trend = "ALTA"
        elif (latest['mme9'] < latest['mma21'] < latest['mma50'] < latest['mma200']):
            ma_trend = "BAIXA"
        
        # Critério 2: Topos e fundos
        highs = []
        lows = []
        
        for i in range(2, len(recent) - 2):
            if (recent.iloc[i]['high'] > recent.iloc[i-1]['high'] and 
                recent.iloc[i]['high'] > recent.iloc[i+1]['high']):
                highs.append(recent.iloc[i]['high'])
            
            if (recent.iloc[i]['low'] < recent.iloc[i-1]['low'] and 
                recent.iloc[i]['low'] < recent.iloc[i+1]['low']):
                lows.append(recent.iloc[i]['low'])
        
        structure_trend = "NEUTRO"
        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                structure_trend = "ALTA"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                structure_trend = "BAIXA"
        
        # Critério 3: Inclinação das médias
        slope_trend = "NEUTRO"
        ma21_slope = (latest['mma21'] - recent.iloc[-5]['mma21']) / 5
        
        if ma21_slope > 0:
            slope_trend = "ALTA"
        elif ma21_slope < 0:
            slope_trend = "BAIXA"
        
        # Combinar critérios
        trends = [ma_trend, structure_trend, slope_trend]
        alta_count = trends.count("ALTA")
        baixa_count = trends.count("BAIXA")
        
        if alta_count >= 2:
            return "ALTA"
        elif baixa_count >= 2:
            return "BAIXA"
        else:
            return "INDEFINIDA"
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calcula força da tendência (0-100)"""
        if len(data) < 20:
            return 0
        
        latest = data.iloc[-1]
        strength = 0
        
        # Proximidade das médias (25 pontos)
        ma_distances = [
            abs(latest['mme9'] - latest['mma21']) / latest['close'],
            abs(latest['mma21'] - latest['mma50']) / latest['close']
        ]
        avg_distance = sum(ma_distances) / len(ma_distances)
        
        if avg_distance < 0.001:  # Muito próximas
            strength += 25
        elif avg_distance < 0.005:  # Próximas
            strength += 15
        elif avg_distance < 0.01:  # Moderadamente próximas
            strength += 10
        
        # Alinhamento das médias (25 pontos)
        if (latest['mme9'] > latest['mma21'] > latest['mma50']) or \
           (latest['mme9'] < latest['mma21'] < latest['mma50']):
            strength += 25
        
        # Inclinação consistente (25 pontos)
        slopes = [
            data['mme9'].diff().tail(5).mean(),
            data['mma21'].diff().tail(5).mean(),
            data['mma50'].diff().tail(5).mean()
        ]
        
        if all(s > 0 for s in slopes) or all(s < 0 for s in slopes):
            strength += 25
        
        # Volume (se disponível) (25 pontos)
        if 'volume' in data.columns and len(data) > 20:
            recent_volume = data['volume'].tail(5).mean()
            avg_volume = data['volume'].tail(20).mean()
            
            if recent_volume > avg_volume * 1.2:
                strength += 25
            elif recent_volume > avg_volume:
                strength += 15
        else:
            strength += 10  # Bonus se não há dados de volume
        
        return min(strength, 100)
    
    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Encontra níveis de suporte e resistência"""
        if len(data) < 50:
            return {"support": [], "resistance": []}
        
        # Usar últimos 50 períodos
        recent = data.tail(50)
        
        # Encontrar topos e fundos locais
        highs = []
        lows = []
        
        for i in range(2, len(recent) - 2):
            # Topo local
            if (recent.iloc[i]['high'] > recent.iloc[i-1]['high'] and 
                recent.iloc[i]['high'] > recent.iloc[i-2]['high'] and
                recent.iloc[i]['high'] > recent.iloc[i+1]['high'] and 
                recent.iloc[i]['high'] > recent.iloc[i+2]['high']):
                highs.append(recent.iloc[i]['high'])
            
            # Fundo local
            if (recent.iloc[i]['low'] < recent.iloc[i-1]['low'] and 
                recent.iloc[i]['low'] < recent.iloc[i-2]['low'] and
                recent.iloc[i]['low'] < recent.iloc[i+1]['low'] and 
                recent.iloc[i]['low'] < recent.iloc[i+2]['low']):
                lows.append(recent.iloc[i]['low'])
        
        # Agrupar níveis próximos
        resistance_levels = self._cluster_levels(highs, recent['close'].iloc[-1])
        support_levels = self._cluster_levels(lows, recent['close'].iloc[-1])
        
        return {
            "support": support_levels,
            "resistance": resistance_levels
        }
    
    def _cluster_levels(self, levels: List[float], current_price: float, tolerance: float = 0.002) -> List[float]:
        """Agrupa níveis próximos"""
        if not levels:
            return []
        
        clustered = []
        sorted_levels = sorted(levels)
        
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_price <= tolerance:
                current_cluster.append(level)
            else:
                # Finalizar cluster atual
                clustered.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]
        
        # Adicionar último cluster
        if current_cluster:
            clustered.append(sum(current_cluster) / len(current_cluster))
        
        return clustered
    
    def _check_ma_alignment(self, data: pd.DataFrame) -> Dict:
        """Verifica alinhamento das médias móveis"""
        if data.empty:
            return {"aligned": False, "direction": "NEUTRO"}
        
        latest = data.iloc[-1]
        
        # Alinhamento de alta
        bull_alignment = (
            latest['mme9'] > latest['mma21'] > latest['mma50'] > latest['mma200']
        )
        
        # Alinhamento de baixa
        bear_alignment = (
            latest['mme9'] < latest['mma21'] < latest['mma50'] < latest['mma200']
        )
        
        if bull_alignment:
            return {"aligned": True, "direction": "ALTA"}
        elif bear_alignment:
            return {"aligned": True, "direction": "BAIXA"}
        else:
            return {"aligned": False, "direction": "NEUTRO"}
    
    def _analyze_price_position(self, data: pd.DataFrame) -> Dict:
        """Analisa posição do preço em relação às médias"""
        if data.empty:
            return {}
        
        latest = data.iloc[-1]
        price = latest['close']
        
        return {
            "above_mme9": price > latest['mme9'],
            "above_mma21": price > latest['mma21'],
            "above_mma50": price > latest['mma50'],
            "above_mma200": price > latest['mma200'],
            "distance_to_mme9": (price - latest['mme9']) / price,
            "distance_to_mma21": (price - latest['mma21']) / price,
            "distance_to_vwap": (price - latest['vwap']) / price if 'vwap' in latest else 0
        }
    
    def _determine_overall_bias(self, timeframes: Dict) -> str:
        """Determina viés geral baseado na hierarquia dos timeframes"""
        if not timeframes:
            return "NEUTRO"
        
        # Pesos por timeframe (hierarquia)
        weights = {
            "1wk": 40,   # Semanal - maior peso
            "1d": 30,    # Diário
            "1h": 20,    # 1 Hora
            "15m": 10    # 15 Minutos
        }
        
        alta_score = 0
        baixa_score = 0
        total_weight = 0
        
        for tf, analysis in timeframes.items():
            if tf in weights:
                weight = weights[tf]
                trend = analysis.get("trend", "INDEFINIDA")
                strength = analysis.get("trend_strength", 0)
                
                # Ajustar peso pela força da tendência
                adjusted_weight = weight * (strength / 100)
                
                if trend == "ALTA":
                    alta_score += adjusted_weight
                elif trend == "BAIXA":
                    baixa_score += adjusted_weight
                
                total_weight += weight
        
        if total_weight == 0:
            return "NEUTRO"
        
        # Determinar viés
        alta_pct = alta_score / total_weight
        baixa_pct = baixa_score / total_weight
        
        if alta_pct > 0.6:
            return "ALTA"
        elif baixa_pct > 0.6:
            return "BAIXA"
        else:
            return "NEUTRO"
    
    def _calculate_mtf_confidence(self, timeframes: Dict) -> float:
        """Calcula confiança da análise multi-timeframe"""
        if not timeframes:
            return 0
        
        total_confidence = 0
        count = 0
        
        for tf, analysis in timeframes.items():
            trend_strength = analysis.get("trend_strength", 0)
            ma_alignment = analysis.get("ma_alignment", {})
            
            tf_confidence = trend_strength
            
            # Bonus por alinhamento das médias
            if ma_alignment.get("aligned", False):
                tf_confidence += 10
            
            total_confidence += tf_confidence
            count += 1
        
        return min(total_confidence / count if count > 0 else 0, 100)
    
    def _find_confluences(self, timeframes: Dict) -> List[str]:
        """Encontra confluências entre timeframes"""
        confluences = []
        
        if not timeframes:
            return confluences
        
        # Verificar alinhamento de tendências
        trends = [analysis.get("trend", "INDEFINIDA") for analysis in timeframes.values()]
        
        if trends.count("ALTA") >= 3:
            confluences.append("Tendência de Alta Multi-Timeframe")
        elif trends.count("BAIXA") >= 3:
            confluences.append("Tendência de Baixa Multi-Timeframe")
        
        # Verificar alinhamento de médias em múltiplos timeframes
        aligned_count = sum(
            1 for analysis in timeframes.values() 
            if analysis.get("ma_alignment", {}).get("aligned", False)
        )
        
        if aligned_count >= 2:
            confluences.append("Médias Alinhadas Multi-Timeframe")
        
        # Verificar força consistente
        strong_trends = sum(
            1 for analysis in timeframes.values() 
            if analysis.get("trend_strength", 0) > 70
        )
        
        if strong_trends >= 2:
            confluences.append("Força Consistente Multi-Timeframe")
        
        return confluences
    
    def calculate_position_size(self, account_balance: float, risk_pct: float, entry_price: float, stop_loss: float) -> Dict:
        """
        Calcula tamanho da posição baseado na gestão de risco do Método Gorila 4.0
        
        Regras:
        - Risco máximo por operação: 1-2% do capital
        - Relação risco/retorno mínima: 1:2
        - Semana de Ouro: primeira semana do mês com risco reduzido
        """
        risk_amount = account_balance * (risk_pct / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return {"error": "Risco de preço inválido"}
        
        # Calcular tamanho da posição
        position_size = risk_amount / price_risk
        
        # Verificar se é semana de ouro (primeira semana do mês)
        current_date = datetime.now()
        is_golden_week = current_date.day <= 7
        
        if is_golden_week:
            # Reduzir risco na semana de ouro
            position_size *= 0.5
            risk_amount *= 0.5
        
        return {
            "position_size": round(position_size, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_percentage": risk_pct,
            "price_risk": round(price_risk, 5),
            "is_golden_week": is_golden_week,
            "max_loss": round(risk_amount, 2)
        }

