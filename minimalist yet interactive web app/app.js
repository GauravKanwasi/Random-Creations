// Theme Configuration
const themes = [
  { bg: "#f0f4f8", text: "#2d3748", accent: "#4FD1C5" }, // Teal
  { bg: "#1a202c", text: "#e2e8f0", accent: "#F687B3" }, // Dark Pink
  { bg: "#fefefe", text: "#333", accent: "#FFA500" },    // Orange
  { bg: "#0f172a", text: "#cbd5e1", accent: "#6EE7B7" }  // Blue-Green
];

let currentTheme = 0;

// Particle System
class Particle {
  constructor() {
    this.x = Math.random() * canvas.width;
    this.y = Math.random() * canvas.height;
    this.vx = (Math.random() - 0.5) * 0.5;
    this.vy = (Math.random() - 0.5) * 0.5;
    this.radius = Math.random() * 2 + 1;
    this.alpha = Math.random() * 0.5 + 0.3;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255,255,255,${this.alpha})`;
    ctx.fill();
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
  }
}

let particles = [];
let canvas = document.getElementById("backgroundCanvas");
let ctx = canvas.getContext("2d");

function resizeCanvas() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  particles = Array.from({ length: 100 }, () => new Particle());
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

// Mouse Interaction
let mouse = { x: null, y: null };
document.addEventListener("mousemove", (e) => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});

// Animation Loop
function animate() {
  requestAnimationFrame(animate);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  particles.forEach(particle => {
    particle.update();
    particle.draw();
    
    // Interaction with mouse
    if (mouse.x && mouse.y) {
      const dx = particle.x - mouse.x;
      const dy = particle.y - mouse.y;
      const distance = Math.sqrt(dx*dx + dy*dy);
      if (distance < 100) {
        particle.alpha = Math.min(1, particle.alpha + 0.02);
        particle.radius = Math.min(5, particle.radius + 0.05);
      } else {
        particle.alpha = Math.max(0.3, particle.alpha - 0.01);
        particle.radius = Math.max(1, particle.radius - 0.02);
      }
    }
  });
}
animate();

// Counter Logic
let count = 0;
const counterDisplay = document.getElementById("counterDisplay");

function updateCounter() {
  counterDisplay.textContent = count;
}

function animateCounter() {
  counterDisplay.classList.add("animate");
  setTimeout(() => counterDisplay.classList.remove("animate"), 300);
}

document.getElementById("incrementBtn").addEventListener("click", () => {
  count++;
  animateCounter();
  updateCounter();
});

document.getElementById("resetBtn").addEventListener("click", () => {
  count = 0;
  animateCounter();
  updateCounter();
});

// Theme Toggle
function applyTheme(index) {
  document.documentElement.style.setProperty("--bg-color", themes[index].bg);
  document.documentElement.style.setProperty("--text-color", themes[index].text);
  document.documentElement.style.setProperty("--accent-color", themes[index].accent);
  document.body.style.background = themes[index].bg;
}

document.getElementById("themeToggle").addEventListener("click", () => {
  currentTheme = (currentTheme + 1) % themes.length;
  applyTheme(currentTheme);
});

// Particle Toggle
let particlesEnabled = true;
document.getElementById("particleToggle").addEventListener("click", () => {
  particlesEnabled = !particlesEnabled;
  if (!particlesEnabled) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  } else {
    animate();
  }
});

// Keyboard Shortcuts
document.addEventListener("keydown", (e) => {
  if (e.code === "Space") document.getElementById("incrementBtn").click();
  if (e.code === "KeyR") document.getElementById("resetBtn").click();
  if (e.code === "KeyT") document.getElementById("themeToggle").click();
  if (e.code === "KeyP") document.getElementById("particleToggle").click();
});

// Initial Setup
updateCounter();
applyTheme(currentTheme);
