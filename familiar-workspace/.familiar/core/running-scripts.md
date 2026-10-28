# Running familiar's scripts when something is missing

Read when no Python 3.10 or newer is found, or a script stops with "familiar needs Python" or a
missing package (`routes.md` → Running familiar's scripts). A script that cannot run is never
worked around silently.

1. Run `.familiar/scripts/doctor.py` with any Python that exists, and tell the user in plain words
   what will not work.
2. Offer to install what is missing with the command doctor prints. With no Python at all, use
   `winget install 9NQ7512CXL7T -e` on Windows, the python.org installer on macOS, or the system
   package manager on Linux. Install only on the user's yes (`CORE-HUMAN-APPROVAL`). A command
   starting with `sudo` asks for the user's password: give it to them to run in their own terminal.
   A new terminal or session may be needed before the new command is found.
3. If the user declines or the install fails, do the step by hand where the skill allows it, and say
   in the reply that it was done by hand.
