"""
Système de collecte de métriques pour monitorer les performances.
Implémente le pattern Observer pour notifier les changements de métriques.
"""
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import asyncio
import threading
from .interfaces import MetricData


@dataclass
class PerformanceMetrics:
    """Métriques de performance pour les différentes étapes du pipeline."""
    ttfb: Optional[float] = None  # Time To First Byte
    ttft: Optional[float] = None  # Time To First Token
    total_latency: Optional[float] = None  # Latence totale
    stt_latency: Optional[float] = None
    llm_latency: Optional[float] = None
    tts_latency: Optional[float] = None
    audio_duration: Optional[float] = None
    response_length: Optional[int] = None


class MetricsCollector:
    """Collecteur de métriques avec pattern Observer."""
    
    def __init__(self, max_history: int = 1000):
        self._metrics_history: deque = deque(maxlen=max_history)
        self._observers: List[Callable[[MetricData], None]] = []
        self._session_metrics: Dict[str, PerformanceMetrics] = {}
        self._lock = threading.Lock()
        # Fichier partagé pour permettre au serveur de lire les métriques
        self._shared_file = os.path.join(os.path.dirname(__file__), '..', 'shared_metrics.json')
    
    def record_metric(self, metric: MetricData) -> None:
        """Enregistre une métrique et notifie les observateurs."""
        with self._lock:
            self._metrics_history.append(metric)
            
            # Notifier les observateurs
            for observer in self._observers:
                try:
                    observer(metric)
                except Exception as e:
                    print(f"Erreur dans l'observateur de métrique: {e}")
            
            # Sauvegarder dans le fichier partagé pour le serveur
            try:
                self._update_shared_file()
            except Exception as e:
                print(f"Erreur sauvegarde métrique: {e}")
    
    def get_metrics(self, name: Optional[str] = None, 
                   session_id: Optional[str] = None,
                   time_range: Optional[timedelta] = None) -> List[MetricData]:
        """Récupère les métriques selon les critères."""
        with self._lock:
            metrics = list(self._metrics_history)
        
        if name:
            metrics = [m for m in metrics if m.name == name]
        
        if time_range:
            cutoff = datetime.now() - time_range
            metrics = [m for m in metrics if m.timestamp > cutoff]
        
        if session_id:
            metrics = [m for m in metrics if session_id in str(m.metadata or {})]
        
        return metrics
    
    def add_observer(self, observer: Callable[[MetricData], None]) -> None:
        """Ajoute un observateur de métriques."""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Callable[[MetricData], None]) -> None:
        """Supprime un observateur de métriques."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def start_session_tracking(self, session_id: str) -> None:
        """Démarre le tracking des métriques pour une session."""
        self._session_metrics[session_id] = PerformanceMetrics()
    
    def record_session_metric(self, session_id: str, metric_name: str, 
                            value: float, unit: str = "ms") -> None:
        """Enregistre une métrique spécifique à une session."""
        if session_id not in self._session_metrics:
            self.start_session_tracking(session_id)
        
        metric = MetricData(
            name=metric_name,
            value=value,
            timestamp=datetime.now(),
            unit=unit,
            metadata={"session_id": session_id}
        )
        self.record_metric(metric)
        
        # Mettre à jour les métriques de session
        session_metrics = self._session_metrics[session_id]
        if metric_name == "stt_latency":
            session_metrics.stt_latency = value
        elif metric_name == "llm_latency":
            session_metrics.llm_latency = value
        elif metric_name == "tts_latency":
            session_metrics.tts_latency = value
        elif metric_name == "total_latency":
            session_metrics.total_latency = value
    
    def get_session_metrics(self, session_id: str) -> Optional[PerformanceMetrics]:
        """Récupère les métriques d'une session."""
        return self._session_metrics.get(session_id)
    
    def get_average_metrics(self, time_range: Optional[timedelta] = None) -> Dict[str, float]:
        """Calcule les métriques moyennes."""
        metrics = self.get_metrics(time_range=time_range)
        if not metrics:
            return {}
        
        grouped_metrics = defaultdict(list)
        for metric in metrics:
            grouped_metrics[metric.name].append(metric.value)
        
        averages = {}
        for name, values in grouped_metrics.items():
            averages[name] = sum(values) / len(values)
        
        return averages
    
    def get_active_sessions(self) -> Dict[str, PerformanceMetrics]:
        """Récupère toutes les sessions actives et leurs métriques."""
        with self._lock:
            return dict(self._session_metrics)
    
    def _update_shared_file(self) -> None:
        """Met à jour le fichier partagé avec les métriques actuelles."""
        try:
            # Préparer les données pour la sérialisation JSON
            recent_metrics = []
            for metric in list(self._metrics_history)[-50:]:  # Les 50 dernières
                recent_metrics.append({
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat(),
                    "metadata": metric.metadata
                })
            
            # Convertir les sessions en format JSON-sérialisable
            active_sessions = {}
            for session_id, session_metrics in self._session_metrics.items():
                active_sessions[session_id] = {
                    "ttfb": session_metrics.ttfb,
                    "ttft": session_metrics.ttft,
                    "total_latency": session_metrics.total_latency,
                    "stt_latency": session_metrics.stt_latency,
                    "llm_latency": session_metrics.llm_latency,
                    "tts_latency": session_metrics.tts_latency,
                    "audio_duration": session_metrics.audio_duration,
                    "response_length": session_metrics.response_length
                }
            
            # Calculer le résumé
            summary = {
                "total_metrics_count": len(self._metrics_history),
                "connection_success": len([m for m in self._metrics_history if m.name == "connection_success"]),
                "connection_errors": len([m for m in self._metrics_history if m.name == "connection_error"]),
                "active_sessions_count": len(self._session_metrics)
            }
            
            # Écrire le fichier partagé
            shared_data = {
                "last_updated": datetime.now().isoformat(),
                "recent_metrics": recent_metrics,
                "active_sessions": active_sessions,
                "summary": summary
            }
            
            with open(self._shared_file, 'w', encoding='utf-8') as f:
                json.dump(shared_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour du fichier partagé: {e}")


class MetricsTimer:
    """Contexte manager pour mesurer le temps d'exécution."""
    
    def __init__(self, collector: MetricsCollector, metric_name: str, 
                 session_id: str = None):
        self.collector = collector
        self.metric_name = metric_name
        self.session_id = session_id
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000  # en ms
            if self.session_id:
                self.collector.record_session_metric(
                    self.session_id, self.metric_name, duration
                )
            else:
                metric = MetricData(
                    name=self.metric_name,
                    value=duration,
                    timestamp=datetime.now(),
                    unit="ms"
                )
                self.collector.record_metric(metric)


# Instance globale du collecteur de métriques
metrics_collector = MetricsCollector()
