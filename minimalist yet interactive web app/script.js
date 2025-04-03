// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
});

// Random Content Generator
const content = [
    "Did you know? Honey never spoils! 🍯",
    "Challenge: Do 10 jumping jacks! 💪",
    "Random cat fact: Cats can jump up to 6 times their height! 🐈",
    "Mini-game: Find the hidden number -> " + Math.floor(Math.random() * 100),
    "Quote: 'The only way to do great work is to love what you do.' – Steve Jobs"
];

function spinWheel() {
    const wheel = document.getElementById('wheel');
    const contentCard = document.getElementById('contentText');
    
    // Spin animation
    wheel.style.animation = 'spin 2s ease-out';
    
    // Randomize content after spin
    setTimeout(() => {
        const randomIndex = Math.floor(Math.random() * content.length);
        contentCard.textContent = content[randomIndex];
        wheel.style.animation = '';
    }, 2000);
}

// Bonus: Add hover effect to wheel
document.getElementById('wheel').addEventListener('mouseover', () => {
    document.getElementById('wheel').style.transform = 'scale(1.1)';
});

document.getElementById('wheel').addEventListener('mouseout', () => {
    document.getElementById('wheel').style.transform = 'scale(1)';
});
