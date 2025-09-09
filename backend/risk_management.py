"""
Gestão de Risco Avançada - Método Gorila 4.0
Implementação da filosofia "Ganhar muito, perder pouco"
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """Gerenciador de Risco baseado no Método Gorila 4.0"""
    
    def __init__(self):
        self.max_daily_risk = 0.02  # 2% máximo por dia
        self.max_position_risk = 0.01  # 1% máximo por posição
        self.min_risk_reward = 2.0  # Mínimo 1:2 R/R
        self.golden_week_multiplier = 0.5  # Redução na semana de ouro
        
    def calculate_position_size(self, 
                              account_balance: float,
                              entry_price: float,
                              stop_loss: float,
                              risk_percentage: float = 1.0,
                              is_golden_week: bool = None) -> Dict:
        """
        Calcula tamanho da posição com base na gestão de risco
        
        Args:
            account_balance: Saldo da conta
            entry_price: Preço de entrada
            stop_loss: Preço do stop loss
            risk_percentage: Percentual de risco (padrão 1%)
            is_golden_week: Se é semana de ouro (primeira semana do mês)
        """
        
        if is_golden_week is None:
            is_golden_week = self._is_golden_week()
        
        # Ajustar risco para semana de ouro
        if is_golden_week:
            risk_percentage *= self.golden_week_multiplier
            
        # Validar limites de risco
        risk_percentage = min(risk_percentage, self.max_position_risk * 100)
        
        # Calcular risco em valor monetário
        risk_amount = account_balance * (risk_percentage / 100)
        
        # Calcular risco por unidade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            return {
                "error": "Stop loss deve ser diferente do preço de entrada",
                "position_size": 0,
                "risk_amount": 0
            }
        
        # Calcular tamanho da posição
        position_size = risk_amount / price_risk
        
        # Informações adicionais
        result = {
            "position_size": round(position_size, 2),
            "risk_amount": round(risk_amount, 2),
            "risk_percentage": risk_percentage,
            "price_risk": round(price_risk, 5),
            "is_golden_week": is_golden_week,
            "max_loss": round(risk_amount, 2),
            "account_balance": account_balance,
            "entry_price": entry_price,
            "stop_loss": stop_loss
        }
        
        return result
    
    def calculate_take_profit_levels(self,
                                   entry_price: float,
                                   stop_loss: float,
                                   signal_type: str,
                                   min_rr_ratio: float = 2.0) -> Dict:
        """
        Calcula níveis de take profit escalonados
        
        Estratégia:
        - TP1: 1:1.5 (realização parcial 30%)
        - TP2: 1:2.5 (realização parcial 40%) 
        - TP3: 1:4.0 (posição restante 30%)
        """
        
        risk = abs(entry_price - stop_loss)
        
        if signal_type.upper() == "BUY":
            tp1 = entry_price + (risk * 1.5)
            tp2 = entry_price + (risk * 2.5)
            tp3 = entry_price + (risk * 4.0)
        else:  # SELL
            tp1 = entry_price - (risk * 1.5)
            tp2 = entry_price - (risk * 2.5)
            tp3 = entry_price - (risk * 4.0)
        
        return {
            "tp1": {
                "price": round(tp1, 5),
                "ratio": 1.5,
                "percentage": 30,
                "description": "Realização parcial conservadora"
            },
            "tp2": {
                "price": round(tp2, 5),
                "ratio": 2.5,
                "percentage": 40,
                "description": "Realização principal"
            },
            "tp3": {
                "price": round(tp3, 5),
                "ratio": 4.0,
                "percentage": 30,
                "description": "Posição de tendência"
            },
            "risk": round(risk, 5),
            "signal_type": signal_type
        }
    
    def validate_trade_setup(self,
                           entry_price: float,
                           stop_loss: float,
                           take_profit: float,
                           confidence: float,
                           min_confidence: float = 60.0) -> Dict:
        """
        Valida se o setup de trade atende aos critérios de risco
        """
        
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "risk_reward_ratio": 0,
            "confidence_check": False
        }
        
        # Calcular R/R ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk > 0:
            rr_ratio = reward / risk
            validation["risk_reward_ratio"] = round(rr_ratio, 2)
            
            # Verificar R/R mínimo
            if rr_ratio < self.min_risk_reward:
                validation["errors"].append(
                    f"R/R ratio {rr_ratio:.2f} abaixo do mínimo {self.min_risk_reward}"
                )
                validation["valid"] = False
        else:
            validation["errors"].append("Risco inválido (stop loss = entrada)")
            validation["valid"] = False
        
        # Verificar confiança
        if confidence >= min_confidence:
            validation["confidence_check"] = True
        else:
            validation["warnings"].append(
                f"Confiança {confidence}% abaixo do recomendado {min_confidence}%"
            )
        
        # Verificar se é fim de semana (Forex fechado)
        if self._is_weekend():
            validation["warnings"].append("Mercado Forex fechado (fim de semana)")
        
        return validation
    
    def calculate_portfolio_risk(self, open_positions: List[Dict]) -> Dict:
        """
        Calcula risco total do portfólio
        """
        
        total_risk = 0
        position_count = len(open_positions)
        correlations = []
        
        for position in open_positions:
            position_risk = position.get("risk_amount", 0)
            total_risk += position_risk
        
        # Verificar correlação entre pares (simplificado)
        if position_count > 1:
            correlation_risk = self._calculate_correlation_risk(open_positions)
        else:
            correlation_risk = 0
        
        return {
            "total_risk": round(total_risk, 2),
            "position_count": position_count,
            "correlation_risk": round(correlation_risk, 2),
            "adjusted_risk": round(total_risk + correlation_risk, 2),
            "risk_distribution": self._analyze_risk_distribution(open_positions)
        }
    
    def generate_risk_report(self, 
                           account_balance: float,
                           daily_pnl: float,
                           open_positions: List[Dict],
                           closed_trades_today: List[Dict]) -> Dict:
        """
        Gera relatório completo de risco
        """
        
        # Calcular métricas do dia
        daily_risk_used = sum(pos.get("risk_amount", 0) for pos in open_positions)
        daily_risk_pct = (daily_risk_used / account_balance) * 100
        
        # Calcular P&L do dia
        realized_pnl = sum(trade.get("pnl", 0) for trade in closed_trades_today)
        unrealized_pnl = sum(pos.get("unrealized_pnl", 0) for pos in open_positions)
        total_daily_pnl = realized_pnl + unrealized_pnl
        
        # Calcular win rate do dia
        winning_trades = len([t for t in closed_trades_today if t.get("pnl", 0) > 0])
        total_trades = len(closed_trades_today)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Status da semana de ouro
        is_golden_week = self._is_golden_week()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "account_summary": {
                "balance": account_balance,
                "daily_pnl": round(total_daily_pnl, 2),
                "daily_pnl_pct": round((total_daily_pnl / account_balance) * 100, 2),
                "realized_pnl": round(realized_pnl, 2),
                "unrealized_pnl": round(unrealized_pnl, 2)
            },
            "risk_metrics": {
                "daily_risk_used": round(daily_risk_used, 2),
                "daily_risk_pct": round(daily_risk_pct, 2),
                "max_daily_risk": self.max_daily_risk * 100,
                "risk_remaining": round((self.max_daily_risk * account_balance) - daily_risk_used, 2),
                "is_golden_week": is_golden_week
            },
            "trading_performance": {
                "trades_today": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": total_trades - winning_trades,
                "win_rate": round(win_rate, 1),
                "open_positions": len(open_positions)
            },
            "recommendations": self._generate_recommendations(
                daily_risk_pct, win_rate, is_golden_week, total_trades
            )
        }
        
        return report
    
    def _is_golden_week(self) -> bool:
        """Verifica se é a primeira semana do mês (semana de ouro)"""
        today = datetime.now()
        return today.day <= 7
    
    def _is_weekend(self) -> bool:
        """Verifica se é fim de semana"""
        today = datetime.now()
        return today.weekday() >= 5  # Sábado (5) ou Domingo (6)
    
    def _calculate_correlation_risk(self, positions: List[Dict]) -> float:
        """
        Calcula risco adicional por correlação entre posições
        (Implementação simplificada)
        """
        
        # Pares correlacionados no Forex
        correlations = {
            ("EURUSD", "GBPUSD"): 0.7,
            ("EURUSD", "AUDUSD"): 0.6,
            ("GBPUSD", "AUDUSD"): 0.5,
            ("USDCHF", "EURUSD"): -0.8,
            ("USDJPY", "USDCHF"): 0.4
        }
        
        additional_risk = 0
        symbols = [pos.get("symbol", "").replace("=X", "") for pos in positions]
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                correlation = correlations.get((symbol1, symbol2), 0)
                correlation = abs(correlation)  # Usar valor absoluto
                
                if correlation > 0.5:  # Correlação significativa
                    risk1 = positions[i].get("risk_amount", 0)
                    risk2 = positions[j].get("risk_amount", 0)
                    additional_risk += (risk1 + risk2) * correlation * 0.1
        
        return additional_risk
    
    def _analyze_risk_distribution(self, positions: List[Dict]) -> Dict:
        """Analisa distribuição de risco por ativo"""
        
        distribution = {}
        total_risk = sum(pos.get("risk_amount", 0) for pos in positions)
        
        for position in positions:
            symbol = position.get("symbol", "Unknown")
            risk = position.get("risk_amount", 0)
            
            if symbol in distribution:
                distribution[symbol]["risk"] += risk
                distribution[symbol]["positions"] += 1
            else:
                distribution[symbol] = {
                    "risk": risk,
                    "positions": 1,
                    "percentage": 0
                }
        
        # Calcular percentuais
        for symbol in distribution:
            if total_risk > 0:
                distribution[symbol]["percentage"] = round(
                    (distribution[symbol]["risk"] / total_risk) * 100, 1
                )
        
        return distribution
    
    def _generate_recommendations(self, 
                                daily_risk_pct: float,
                                win_rate: float,
                                is_golden_week: bool,
                                trades_today: int) -> List[str]:
        """Gera recomendações baseadas nas métricas de risco"""
        
        recommendations = []
        
        # Recomendações de risco
        if daily_risk_pct > 1.5:
            recommendations.append("⚠️ Risco diário elevado - considere reduzir exposição")
        elif daily_risk_pct < 0.5:
            recommendations.append("💡 Risco baixo - pode aumentar exposição com setups de alta confiança")
        
        # Recomendações de performance
        if win_rate < 40 and trades_today >= 3:
            recommendations.append("📉 Win rate baixo - revisar estratégia e aguardar setups melhores")
        elif win_rate > 70 and trades_today >= 2:
            recommendations.append("📈 Excelente performance - manter disciplina")
        
        # Recomendações da semana de ouro
        if is_golden_week:
            recommendations.append("🥇 Semana de Ouro ativa - foco em acumular capital com risco reduzido")
        
        # Recomendações de overtrading
        if trades_today > 5:
            recommendations.append("⏸️ Muitas operações hoje - considere pausar e analisar")
        elif trades_today == 0:
            recommendations.append("👀 Nenhuma operação hoje - aguardar setups de qualidade")
        
        # Recomendação padrão
        if not recommendations:
            recommendations.append("✅ Gestão de risco dentro dos parâmetros - continuar operando com disciplina")
        
        return recommendations
    
    def calculate_drawdown_metrics(self, equity_curve: List[float]) -> Dict:
        """
        Calcula métricas de drawdown
        """
        
        if len(equity_curve) < 2:
            return {"max_drawdown": 0, "current_drawdown": 0, "drawdown_duration": 0}
        
        # Converter para numpy array
        equity = np.array(equity_curve)
        
        # Calcular running maximum
        running_max = np.maximum.accumulate(equity)
        
        # Calcular drawdown
        drawdown = (equity - running_max) / running_max * 100
        
        # Drawdown máximo
        max_drawdown = np.min(drawdown)
        
        # Drawdown atual
        current_drawdown = drawdown[-1]
        
        # Duração do drawdown atual
        drawdown_duration = 0
        for i in range(len(drawdown) - 1, -1, -1):
            if drawdown[i] < 0:
                drawdown_duration += 1
            else:
                break
        
        return {
            "max_drawdown": round(max_drawdown, 2),
            "current_drawdown": round(current_drawdown, 2),
            "drawdown_duration": drawdown_duration,
            "recovery_factor": round(equity[-1] / abs(max_drawdown) if max_drawdown != 0 else 0, 2)
        }
    
    def optimize_position_sizing(self,
                               account_balance: float,
                               win_rate: float,
                               avg_win: float,
                               avg_loss: float,
                               confidence: float) -> Dict:
        """
        Otimiza tamanho da posição usando Kelly Criterion adaptado
        """
        
        # Kelly Criterion: f = (bp - q) / b
        # onde: b = odds, p = probabilidade de ganho, q = probabilidade de perda
        
        if avg_loss <= 0:
            return {"error": "Perda média deve ser positiva"}
        
        p = win_rate / 100  # Probabilidade de ganho
        q = 1 - p  # Probabilidade de perda
        b = avg_win / avg_loss  # Odds
        
        # Kelly fraction
        kelly_fraction = (b * p - q) / b
        
        # Ajustar por confiança
        confidence_multiplier = confidence / 100
        adjusted_kelly = kelly_fraction * confidence_multiplier
        
        # Limitar a 25% do Kelly (conservador)
        safe_kelly = min(adjusted_kelly * 0.25, 0.02)  # Máximo 2%
        
        # Calcular tamanho recomendado
        recommended_risk_pct = max(safe_kelly * 100, 0.5)  # Mínimo 0.5%
        recommended_risk_amount = account_balance * (recommended_risk_pct / 100)
        
        return {
            "kelly_fraction": round(kelly_fraction, 4),
            "adjusted_kelly": round(adjusted_kelly, 4),
            "safe_kelly": round(safe_kelly, 4),
            "recommended_risk_pct": round(recommended_risk_pct, 2),
            "recommended_risk_amount": round(recommended_risk_amount, 2),
            "win_rate": win_rate,
            "avg_win_loss_ratio": round(b, 2),
            "confidence_factor": confidence
        }

