"""
Project Tracker Agent - Cosmic Query Agent
===========================================

Agent de suivi des modifications pour le projet ActInSpace.
Intègre le tracking des tâches, métriques et changelog.

Usage:
    from project_tracker import ProjectTracker
    tracker = ProjectTracker()
    tracker.start_task("FEAT-001")
    # ... travail ...
    tracker.complete_task("FEAT-001", "Amélioration affichage LLM terminée")
"""

import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
import subprocess
import sys


# ============================================================
# CONFIGURATION
# ============================================================

TRACKER_FILE = Path(__file__).parent.parent / "docs" / "project_tracker.yaml"
SESSION_LOG = Path(__file__).parent / "data" / "session_log.json"


@dataclass
class TaskStatus:
    """Statut d'une tâche."""
    pending: str = "pending"
    in_progress: str = "in_progress"
    completed: str = "completed"
    blocked: str = "blocked"


@dataclass
class SessionEntry:
    """Entrée de log de session."""
    timestamp: str
    task_id: str
    action: str  # started | completed | note | error
    message: str
    duration_minutes: Optional[int] = None


@dataclass
class ProjectMetrics:
    """Métriques du projet."""
    total_loc: int = 0
    modules: int = 0
    functions: int = 0
    test_coverage: float = 0.0
    print_statements: int = 0
    last_updated: str = ""


# ============================================================
# PROJECT TRACKER AGENT
# ============================================================

class ProjectTracker:
    """
    Agent de suivi des modifications du projet.

    Fonctionnalités:
    - Tracking des tâches (start, complete, block)
    - Logging de session
    - Mise à jour des métriques
    - Génération de changelog
    - Intégration TTS (optionnel via AgentVibes)
    """

    def __init__(self, tracker_file: Path = TRACKER_FILE):
        self.tracker_file = tracker_file
        self.config = self._load_config()
        self.session_start = datetime.now()
        self.session_log: List[SessionEntry] = []
        self._active_task: Optional[str] = None
        self._task_start_time: Optional[datetime] = None

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration du tracker."""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _save_config(self) -> None:
        """Sauvegarde la configuration."""
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

    def _log_session(self, entry: SessionEntry) -> None:
        """Ajoute une entrée au log de session."""
        self.session_log.append(entry)

        # Persist to file
        SESSION_LOG.parent.mkdir(parents=True, exist_ok=True)

        logs = []
        if SESSION_LOG.exists():
            with open(SESSION_LOG, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(asdict(entry))

        with open(SESSION_LOG, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def _announce(self, message: str, level: str = "info") -> None:
        """
        Annonce vocale via AgentVibes TTS (si disponible).

        Args:
            message: Message à annoncer
            level: info | success | warning | error
        """
        verbosity = self.config.get('tracker_config', {}).get('verbosity', 'medium')
        voice_enabled = self.config.get('tracker_config', {}).get('voice_enabled', False)

        if not voice_enabled:
            print(f"[{level.upper()}] {message}")
            return

        # Filtrage par verbosité
        if verbosity == 'low' and level == 'info':
            return
        if verbosity == 'medium' and level == 'info':
            # Only announce important info
            pass

        print(f"[{level.upper()}] {message}")
        # Note: TTS integration would go here via MCP call

    # ============================================================
    # TASK MANAGEMENT
    # ============================================================

    def list_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """Liste toutes les tâches, optionnellement filtrées par statut."""
        tasks = []
        priority_tasks = self.config.get('priority_tasks', {})

        for priority, task_list in priority_tasks.items():
            if isinstance(task_list, list):
                for task in task_list:
                    if status is None or task.get('status') == status:
                        task['priority_level'] = priority
                        tasks.append(task)

        return tasks

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Récupère une tâche par son ID."""
        for task in self.list_tasks():
            if task.get('id') == task_id:
                return task
        return None

    def start_task(self, task_id: str) -> bool:
        """
        Démarre une tâche.

        Args:
            task_id: ID de la tâche (ex: FEAT-001)

        Returns:
            True si succès, False sinon
        """
        task = self.get_task(task_id)
        if not task:
            self._announce(f"Tâche {task_id} non trouvée", "error")
            return False

        if task.get('status') == 'completed':
            self._announce(f"Tâche {task_id} déjà terminée", "warning")
            return False

        # Update status
        self._update_task_status(task_id, 'in_progress')
        self._active_task = task_id
        self._task_start_time = datetime.now()

        # Log
        entry = SessionEntry(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            action="started",
            message=f"Début: {task.get('title', task_id)}"
        )
        self._log_session(entry)

        self._announce(f"Démarrage de {task.get('title', task_id)}", "info")
        return True

    def complete_task(self, task_id: str, notes: str = "") -> bool:
        """
        Marque une tâche comme terminée.

        Args:
            task_id: ID de la tâche
            notes: Notes de complétion

        Returns:
            True si succès
        """
        task = self.get_task(task_id)
        if not task:
            self._announce(f"Tâche {task_id} non trouvée", "error")
            return False

        # Calculate duration
        duration = None
        if self._active_task == task_id and self._task_start_time:
            duration = int((datetime.now() - self._task_start_time).total_seconds() / 60)

        # Update status
        self._update_task_status(task_id, 'completed')
        self._active_task = None
        self._task_start_time = None

        # Log
        entry = SessionEntry(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            action="completed",
            message=notes or f"Terminé: {task.get('title', task_id)}",
            duration_minutes=duration
        )
        self._log_session(entry)

        # Update current session in config
        session = self.config.setdefault('current_session', {})
        completed = session.setdefault('completed_tasks', [])
        completed.append({
            'task_id': task_id,
            'completed_at': datetime.now().isoformat(),
            'notes': notes
        })
        self._save_config()

        self._announce(f"Tâche {task_id} terminée!", "success")
        return True

    def add_note(self, note: str, task_id: Optional[str] = None) -> None:
        """Ajoute une note à la session ou à une tâche."""
        entry = SessionEntry(
            timestamp=datetime.now().isoformat(),
            task_id=task_id or self._active_task or "general",
            action="note",
            message=note
        )
        self._log_session(entry)

        session = self.config.setdefault('current_session', {})
        notes = session.setdefault('notes', [])
        notes.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'note': note
        })
        self._save_config()

    def _update_task_status(self, task_id: str, status: str) -> None:
        """Met à jour le statut d'une tâche dans le fichier."""
        priority_tasks = self.config.get('priority_tasks', {})

        for priority, task_list in priority_tasks.items():
            if isinstance(task_list, list):
                for task in task_list:
                    if task.get('id') == task_id:
                        task['status'] = status
                        if status == 'completed':
                            task['completed_at'] = datetime.now().isoformat()
                        self._save_config()
                        return

    # ============================================================
    # METRICS
    # ============================================================

    def update_metrics(self) -> ProjectMetrics:
        """
        Met à jour les métriques du projet en analysant le code.

        Returns:
            ProjectMetrics avec les valeurs actuelles
        """
        src_path = Path(__file__).parent

        metrics = ProjectMetrics(
            last_updated=datetime.now().isoformat()
        )

        # Count LOC and modules
        py_files = list(src_path.glob("*.py"))
        metrics.modules = len([f for f in py_files if not f.name.startswith('test_')])

        total_loc = 0
        total_functions = 0
        print_count = 0

        for py_file in py_files:
            if py_file.name == 'project_tracker.py':
                continue  # Skip self

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                total_loc += len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                total_functions += content.count('def ')
                print_count += content.count('print(')
            except Exception:
                pass

        metrics.total_loc = total_loc
        metrics.functions = total_functions
        metrics.print_statements = print_count

        # Update config
        self.config.setdefault('baseline_metrics', {}).update({
            'total_loc': metrics.total_loc,
            'modules': metrics.modules,
            'functions': metrics.functions,
            'print_statements': metrics.print_statements,
            'timestamp': metrics.last_updated
        })
        self._save_config()

        return metrics

    # ============================================================
    # CHANGELOG
    # ============================================================

    def add_changelog_entry(
        self,
        version: str,
        changes: List[str],
        date: Optional[str] = None
    ) -> None:
        """
        Ajoute une entrée au changelog.

        Args:
            version: Numéro de version (ex: 2.2.0)
            changes: Liste des changements
            date: Date (défaut: aujourd'hui)
        """
        changelog = self.config.setdefault('changelog', [])

        entry = {
            'version': version,
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'changes': changes
        }

        # Insert at beginning
        changelog.insert(0, entry)

        # Update project version
        self.config.setdefault('project', {})['version'] = version

        self._save_config()
        self._announce(f"Changelog mis à jour: v{version}", "success")

    # ============================================================
    # REPORTS
    # ============================================================

    def status_report(self) -> str:
        """Génère un rapport de statut."""
        tasks = self.list_tasks()

        pending = len([t for t in tasks if t.get('status') == 'pending'])
        in_progress = len([t for t in tasks if t.get('status') == 'in_progress'])
        completed = len([t for t in tasks if t.get('status') == 'completed'])

        metrics = self.config.get('baseline_metrics', {})

        report = f"""
# Rapport de Statut - Cosmic Query Agent
## {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Tâches
- En attente: {pending}
- En cours: {in_progress}
- Terminées: {completed}

## Métriques
- LOC: {metrics.get('total_loc', 'N/A')}
- Modules: {metrics.get('modules', 'N/A')}
- Fonctions: {metrics.get('functions', 'N/A')}
- Score dette: {metrics.get('score', 'N/A')}/10

## Tâche Active
- {self._active_task or 'Aucune'}

## Session
- Durée: {int((datetime.now() - self.session_start).total_seconds() / 60)} min
- Actions: {len(self.session_log)}
"""
        return report.strip()

    def session_summary(self) -> str:
        """Résumé de la session de travail."""
        if not self.session_log:
            return "Aucune activité enregistrée dans cette session."

        completed = [e for e in self.session_log if e.action == 'completed']
        notes = [e for e in self.session_log if e.action == 'note']

        summary = f"""
## Résumé de Session
- Début: {self.session_start.strftime('%H:%M')}
- Durée: {int((datetime.now() - self.session_start).total_seconds() / 60)} minutes
- Tâches complétées: {len(completed)}
- Notes ajoutées: {len(notes)}

### Tâches Complétées
"""
        for entry in completed:
            summary += f"- [{entry.task_id}] {entry.message}"
            if entry.duration_minutes:
                summary += f" ({entry.duration_minutes} min)"
            summary += "\n"

        return summary.strip()


# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    """Interface CLI pour le tracker."""
    import argparse

    parser = argparse.ArgumentParser(description="Project Tracker CLI")
    parser.add_argument('command', choices=[
        'status', 'tasks', 'start', 'complete', 'note', 'metrics', 'report'
    ])
    parser.add_argument('--task', '-t', help="Task ID")
    parser.add_argument('--message', '-m', help="Message or note")
    parser.add_argument('--status', '-s', help="Filter by status")

    args = parser.parse_args()
    tracker = ProjectTracker()

    if args.command == 'status':
        print(tracker.status_report())

    elif args.command == 'tasks':
        tasks = tracker.list_tasks(args.status)
        for task in tasks:
            status_icon = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'blocked': '🚫'
            }.get(task.get('status', 'pending'), '❓')
            print(f"{status_icon} [{task['id']}] {task.get('title', 'No title')}")

    elif args.command == 'start':
        if not args.task:
            print("Error: --task required")
            sys.exit(1)
        tracker.start_task(args.task)

    elif args.command == 'complete':
        if not args.task:
            print("Error: --task required")
            sys.exit(1)
        tracker.complete_task(args.task, args.message or "")

    elif args.command == 'note':
        if not args.message:
            print("Error: --message required")
            sys.exit(1)
        tracker.add_note(args.message, args.task)

    elif args.command == 'metrics':
        metrics = tracker.update_metrics()
        print(f"LOC: {metrics.total_loc}")
        print(f"Modules: {metrics.modules}")
        print(f"Functions: {metrics.functions}")
        print(f"Print statements: {metrics.print_statements}")

    elif args.command == 'report':
        print(tracker.session_summary())


if __name__ == "__main__":
    main()
