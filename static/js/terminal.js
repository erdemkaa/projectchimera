
// project_chimera/static/js/terminal.js

document.addEventListener('DOMContentLoaded', () => {
    // Activate the correct navigation link based on the current page
    activateNav();

    // Run the boot-up sequence if we are on the login page
    if (document.getElementById('login-boot-sequence')) {
        runBootSequence();
    }
});

/**
 * Adds an 'active' class to the navigation link corresponding to the current page.
 */
function activateNav() {
    const navLinks = document.querySelectorAll('.overseer-nav-link');
    if (!navLinks.length) return;

    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        // Check if the link's href is a substring of the current path.
        // This handles both the base dashboard and other pages.
        if (currentPath.startsWith(linkPath)) {
            link.classList.add('active');
        }
    });
}

/**
 * Simulates a terminal boot-up sequence by typing out text.
 */
function runBootSequence() {
    const sequenceContainer = document.getElementById('login-boot-sequence');
    const lines = [
        ">> Initializing Vault-Tec Mainframe Interface v7.3.4.A...",
        ">> Checking system integrity...",
        ">> All systems nominal.",
        ">> ASCENSION protocol active.",
        ">> Awaiting user authentication."
    ];
    const form = document.querySelector('.login-form');
    const container = document.querySelector('.terminal-card');

    // Hide form initially
    form.style.display = 'none';
    sequenceContainer.innerHTML = ''; // Clear static content

    let lineIndex = 0;

    function typeLine() {
        if (lineIndex < lines.length) {
            const lineElement = document.createElement('p');
            lineElement.className = 'terminal-text';
            sequenceContainer.appendChild(lineElement);
            
            let charIndex = 0;
            const line = lines[lineIndex];
            
            const typingInterval = setInterval(() => {
                if (charIndex < line.length) {
                    lineElement.textContent += line.charAt(charIndex);
                    charIndex++;
                } else {
                    clearInterval(typingInterval);
                    lineIndex++;
                    // Add a small delay before typing the next line
                    setTimeout(typeLine, 200);
                }
            }, 25); // Typing speed
        } else {
            // After all lines are typed, show the form
            form.style.display = 'block';
            // Add a blinking cursor to the last line
            addBlinkingCursor(sequenceContainer.lastChild);
        }
    }

    typeLine();
}

/**
 * Adds a blinking cursor to the end of a given element.
 * @param {HTMLElement} element The element to append the cursor to.
 */
function addBlinkingCursor(element) {
    if (!element) return;
    const cursor = document.createElement('span');
    cursor.className = 'blinking-cursor';
    cursor.textContent = '█';
    element.appendChild(cursor);
}
