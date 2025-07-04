 Your task, should you choose to accept it, is to navigate the Overseer's terminal. This interface holds the key to the vault's secrets, the grim realities of Project Chimera, and the ultimate directives of ASCENSION. Be warned: the path to enlightenment is fraught with digital defenses and hidden truths. Only those with the sharpest minds and the most tenacious will uncover the final protocol.

### Are you ready to see what Vault-Tec truly built?

---

## Challenge Overview: Navigating the Vault's Defenses

This Capture The Flag (CTF) challenges you to exploit common web vulnerabilities to progressively gain deeper access into Vault 73's systems and uncover the full scope of Project Chimera. The challenges are designed to be tackled in a sequential flow, with each successful breach potentially revealing clues or access points for the next.

**Your mission objectives, in order of discovery:**

1.  **Initial Access: The Overseer's Oversight**
    * **Challenge Type:** Credential Exploitation / Weak Authentication
    * **Objective:** Gain unauthorized access to the Overseer's primary dashboard. The initial entry point is the login portal.

2.  **Subject Dossiers: Unveiling the Anomaly**
    * **Challenge Type:** Insecure Direct Object Reference (IDOR)
    * **Objective:** Once on the dashboard, uncover hidden or restricted subject dossiers that are not directly linked but exist within the system. There are disturbing truths about certain "subjects" that only an advanced Overseer should witness.

3.  **Psycho-Aptitude Scan: Echoes of Corruption**
    * **Challenge Type:** Cross-Site Scripting (XSS)
    * **Objective:** The psycho-aptitude scanner provides volatile feedback. Manipulate its output to demonstrate control over the terminal's display. What data can you inject, and what does it reveal about the system's integrity?

4.  **Research Protocols: Data Interception**
    * **Challenge Type:** SQL Injection (SQLi)
    * **Objective:** The research query interface is designed to filter information. Bypass its controls to extract highly classified Project Chimera protocols, including internal notes and objectives not meant for general viewing.

5.  **Surveillance Archives: The Vault's Hidden Logs**
    * **Challenge Type:** Local File Inclusion (LFI)
    * **Objective:** Access archived surveillance logs and other internal files not directly served by the web application. The vault keeps meticulous records, even of its most unsettling incidents.

6.  **Remote Data Synchronization: The Internal Core**
    * **Challenge Type:** Server-Side Request Forgery (SSRF)
    * **Objective:** The "Remote Data Synchronization Module" is meant for external data exchange. However, its true power lies in its ability to access highly isolated internal network nodes. Discover and interact with these hidden services to uncover ASCENSION's ultimate directive.

---

**Good luck, Overseer. Project Chimera awaits your command.**

