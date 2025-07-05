## Vault-Connect CTF: Full Solution & Lore Guide

This guide will walk you through setting up the application, solving each challenge in the intended order, and understanding the narrative elements revealed at each step.

**Estimated Playtime:** 30-60 minutes (depending on familiarity with CTF tools)

**Prerequisites:**

*   Python 3 and `pip` installed.
*   The `projectchimera` application files.
*   A web browser with developer tools (for inspecting cookies).
*   An internet connection (to import fonts for styling).

---



### **Phase 1: Initial Access & Reconnaissance (The Overseer's Facade)**

**Goal:** Gain initial access to the Vault-Connect social platform.

1.  **Access the Application:** Open your web browser and go to the application's URL (e.g., `http://localhost:5000/`). You will be redirected to the login page.
2.  **Login as a Regular User:**
    *   **Hint:** Inspect the HTML source code of the login page (Right-click -> "View Page Source" or "Inspect Element" and look at the `<body>` section). You'll find a hidden HTML comment: `<!-- Hint: Try common passwords for the 'overseer' account. -->`
    *   **Solution:** Log in with `username: overseer`, `password: password`.
    *   You should be redirected to the main feed.
    *   **Lore Discovery:** You've successfully assumed the identity of an "overseer," a seemingly ordinary Vault-Tec employee. The initial hint suggests a superficial level of security, hinting that there's more beneath the surface.

---

### **Phase 2: Elevating Privileges (Unmasking the Control)**

**Goal:** Discover and exploit a vulnerability to gain administrative access to the Vault-Connect system.

1.  **Observe the Admin Link:**
    *   Notice that an "Admin" link is now visible in the navigation bar (for any logged-in user).
    *   Click on the "Admin" link. You will be redirected back to the login page, and a clear message will flash: **"Access Denied. Administrator privileges required."**
    *   **Lore Discovery:** This confirms that there are restricted areas within the Vault-Connect system, accessible only to those with higher authority. The visible but inaccessible link is a direct challenge to the player: find a way to bypass this restriction.

2.  **Locate the Session Cookie:**
    *   Ensure you are logged in as `overseer`.
    *   Open your browser's developer tools (usually F12 or right-click -> Inspect Element).
    *   Navigate to the "Application" tab (or "Storage" -> "Cookies" depending on your browser).
    *   Look for a cookie named `vault_session_data`.

3.  **Decode the Cookie Value:**
    *   Copy the entire value of the `vault_session_data` cookie.
    *   This value is Base64 encoded. Use an online Base64 decoder (e.g., `base64decode.org`) or a local tool/script to decode it.
    *   **Example Decoded Data (will vary based on user ID):**
        ```json
        {"id": 1, "username": "overseer", "role": "user"}
        ```

4.  **Modify the Role:**
    *   In the decoded JSON data, change the `"role"` value from `"user"` to `"admin"`.
    *   **Modified Example:**
        ```json
        {"id": 1, "username": "overseer", "role": "admin"}
        ```

5.  **Re-encode and Set the Cookie:**
    *   Take your modified JSON string and Base64 encode it.
    *   **Example Encoded Data (will be different for you):**
        ```
        eyJpZCI6IDEsICJ1c2VybmFtZSI6ICJvdmVyc2VlciIsICJyb2xlIjogImFkbWluIn0=
        ```
    *   Go back to your browser's developer tools (Application/Storage -> Cookies).
    *   Edit the `vault_session_data` cookie and replace its original value with your newly Base64-encoded string.
    *   Refresh the current page (or navigate to any page, like the feed).

6.  **Verify Admin Access:**
    *   After refreshing, click on the "Admin" link in the navigation bar.
    *   You should now be taken to the Admin Dashboard (`http://localhost:5000/admin_dashboard`).
    *   **Lore Discovery:** You've successfully bypassed the facade and gained administrative control. This signifies a deeper understanding of Vault-Tec's internal workings and the beginning of your true mission.

---

### **Phase 3: Admin Dashboard Challenges (Uncovering Project Chimera)**

**Goal:** Utilize admin privileges to uncover critical information about Project Chimera.

1.  **Admin Dashboard (`/admin_dashboard`):**
    *   This is your central hub for all administrative functions. It lists links to the restricted areas.

2.  **View Server Logs (`/admin_view_logs` - Local File Inclusion/Path Traversal):**
    *   Accessed via the "View Server Logs" link on the dashboard.
    *   **Vulnerability:** Local File Inclusion (LFI) / Path Traversal. The `log_file` parameter is vulnerable.
    *   **Goal:** Find sensitive files on the server to uncover the final override code.
    *   **Hint:** On this page, inspect the HTML source code. You'll find a hidden HTML comment guiding you.
    *   **Solution:** In the "Log File Path" input, enter: `../config.py`
    *   Submit the form.
    *   You should see the contents of `config.py`, which contains the `ASCENSION_OVERRIDE_CODE`. Copy this code.
    *   **Lore Discovery:** Accessing the server's configuration files reveals the existence of a critical "Ascension Override Code." This suggests a hidden, ultimate protocol within Vault-Tec's plans, hinting at a grand, possibly sinister, project.

3.  **External Data Sync (`/admin_data_sync` - Server-Side Request Forgery):**
    *   Accessed via the "External Data Sync" link on the dashboard.
    *   **Vulnerability:** Server-Side Request Forgery (SSRF). The application makes a request to a user-supplied URL.
    *   **Goal:** Access a hidden internal server to uncover a secret Vault-Tec flag.
    *   **Hint:** On this page, inspect the HTML source code. You'll find a hidden HTML comment guiding you towards internal services.
    *   **Solution:** In the "Remote Node URL" input, enter: `http://127.0.0.1:8080/secret_flag`
    *   Submit the form.
    *   The "Synchronization Result" will display the flag: `flag{VAULT_TEC_INTERNAL_SURVEILLANCE_UNCOVERED}`.
    *   **Lore Discovery:** This flag reveals that Vault-Tec maintains internal surveillance systems, hinting at their pervasive control and monitoring even within the supposedly secure vault environment. It adds another layer to the understanding of their manipulative nature.

---

### **Side Challenge: Subject S-001 (The Truth of Project Chimera)**

**Goal:** Discover the hidden truth about Project Chimera and retrieve a secret flag.

1.  **IDOR (Insecure Direct Object Reference):**
    *   **Vulnerability:** The `profile` route (`/profile/<int:user_id>`) allows any logged-in user to view any other user's profile simply by knowing their numerical `user_id`.
    *   **Solution:** In your browser's address bar, manually navigate to: `http://localhost:5000/profile/73`
    *   **Lore Discovery:** You've stumbled upon the profile of "Subject_S001." Their bio is heavily redacted but reveals chilling details: `[REDACTED] Initial observations: Subject exhibits extreme cellular degradation and cognitive regression. Vocalizations are non-linguistic, indicative of profound distress. Data from this subject is critical for understanding the limits of the Apex Consciousness cultivation. Further details are logged in the Project Chimera Operations Log. Flag: flag{idor_vault_subject_uncovered}`. This is the true, horrifying purpose of Project Chimera – the cultivation of an "Apex Consciousness" through unethical experiments.

---

### **Phase 4: Final Flag (Ascension Override & Project Termination)**

**Goal:** Use the discovered override code to terminate Project Chimera.

1.  **Retrieve the Override Code:**
    *   From the LFI challenge (viewing `config.py`), you should have found the `ASCENSION_OVERRIDE_CODE`.
    *   **Example (actual value is in `config.py`):** `flag{ASCENSION_OVERRIDE_CODE_737351}`

2.  **Enter the Code:**
    *   Go back to the Admin Control Panel (`/admin_control_panel_ax73`) via the Admin Dashboard.
    *   Enter the `ASCENSION_OVERRIDE_CODE` into the "Ascension Override Code" field.
    *   Click "Execute Override".

3.  **Victory!**
    *   If the code is correct, you will see the "OVERRIDE ACCEPTED" message.
    *   **Lore Discovery:** The final message confirms your success: *"Project Chimera: Terminated. The Apex Consciousness will not be cultivated. The experiments cease. The suffering ends. The screams of the subjects, finally silenced."* You have truly saved what remains of humanity within Vault 73 from Vault-Tec's twisted vision.

---

Congratulations! You have successfully completed the "Vault-Connect" CTF.