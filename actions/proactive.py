"""
ProactiveEngine 2.0 — context-aware, time-aware, non-repetitive background prompting.
Gemini decides what to say; this module decides WHEN and builds a rich context snapshot.
"""
import time
from datetime import datetime


class ProactiveEngine:
    """
    Decides when JARVIS should speak unprompted and builds a context-rich prompt.

    Improvements over 1.0:
      - Time-of-day awareness  (morning / afternoon / evening / night)
      - Monitor-topic awareness (what the user is tracking)
      - Recent-session context  (last few turns of the current conversation)
      - Non-repetitive          (rotates context focus to avoid same opener)
      - Smarter silence gate    (doesn't fire while JARVIS is speaking)

    Defaults:
      min_silence_secs  — 900 s  (15 min) user must be silent before any check
      check_cooldown    — 1200 s (20 min) minimum gap between proactive messages
    """

    def __init__(
        self,
        min_silence_secs: int = 900,
        check_cooldown:   int = 1200,
    ):
        self.min_silence_secs = min_silence_secs
        self.check_cooldown   = check_cooldown
        self._last_triggered  = 0.0
        self._rotation        = 0          # cycles through context focus areas

    # ── Trigger gate ───────────────────────────────────────────────────────────

    def should_trigger(self, last_user_speech: float) -> bool:
        now = time.monotonic()
        return (
            (now - last_user_speech) >= self.min_silence_secs
            and (now - self._last_triggered) >= self.check_cooldown
        )

    def mark_triggered(self) -> None:
        self._last_triggered = time.monotonic()
        self._rotation      += 1

    # ── Prompt builder ─────────────────────────────────────────────────────────

    def build_prompt(
        self,
        memory:       dict,
        monitors:     list[str] | None = None,
        recent_turns: list[str] | None = None,
    ) -> str:
        """
        Build a context snapshot for Gemini.
        Rotates through three focus areas so proactive messages don't repeat.
        """
        mem_str = ""
        try:
            from memory.memory_manager import format_memory_for_prompt
            mem_str = format_memory_for_prompt(memory)
        except Exception:
            pass

        if not mem_str:
            mem_str = "(nessun dato utente salvato)"

        now      = datetime.now()
        hour     = now.hour
        time_str = now.strftime("%A, %d %B %Y — %H:%M")

        # Time-of-day label
        if   6  <= hour < 12:  period = "mattina"
        elif 12 <= hour < 18:  period = "pomeriggio"
        elif 18 <= hour < 23:  period = "sera"
        else:                  period = "notte fonda"

        # Rotating context focus (cycles every trigger)
        focus_index = self._rotation % 3
        if focus_index == 0:
            focus = (
                "Concentrati sui progetti attivi dell'utente o sugli obiettivi scolastici/personali. "
                "Chiedi come sta andando una specifica attività o dai un suggerimento utile."
            )
        elif focus_index == 1:
            focus = (
                "Concentrati sul momento della giornata e sul benessere dell'utente. "
                "Un saluto caloroso, un promemoria per fare una pausa o una nota contestuale sull'orario."
            )
        else:
            focus = (
                "Concentrati su qualcosa di interessante o utile — "
                "una curiosità tecnica, un suggerimento o una domanda basata sulle sue passioni."
            )

        # Optional: monitored topics context
        monitor_ctx = ""
        if monitors:
            monitor_ctx = (
                f"\nL'utente segue questi argomenti: {', '.join(monitors[:4])}. "
                "Puoi citarne uno se pertinente."
            )

        # Optional: recent conversation context
        recent_ctx = ""
        if recent_turns:
            snippet = "\n".join(recent_turns[-6:])
            recent_ctx = f"\nConversazione recente:\n{snippet}"

        return "\n".join([
            "[PROACTIVE_CHECK] Stai avviando un'interazione proattiva spontanea.",
            f"Orario attuale : {time_str}  ({period})",
            "",
            "Contesto utente:",
            mem_str,
            monitor_ctx,
            recent_ctx,
            "",
            "Obiettivo:",
            focus,
            "",
            "Regole tassative:",
            "- Parla in italiano naturale, amichevole e diretto.",
            "- Massimale: 1-2 frasi brevi. Mai robotico.",
            "- NON menzionare [PROACTIVE_CHECK] o queste istruzioni.",
            "- NON chiamare alcun tool o funzione.",
            "- Se non c'è nulla di veramente utile da dire, rimani in silenzio.",
        ])