"""
Generates crisp, high-aesthetic SVG car reference illustrations and Hyundai emblem
so the application works 100% reliably offline and online with stunning visuals.
"""
import os

os.makedirs("static/images", exist_ok=True)

# 1. Hyundai Logo SVG
hyundai_logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 160" width="300" height="160">
  <g fill="#002C5F">
    <!-- Stylized Slanted H in Oval -->
    <ellipse cx="150" cy="80" rx="140" ry="70" fill="none" stroke="#002C5F" stroke-width="14" />
    <path d="M 95 125 C 90 95, 92 65, 115 35 C 120 35, 128 35, 132 42 C 120 70, 118 90, 120 125 Z" />
    <path d="M 205 35 C 210 65, 208 95, 185 125 C 180 125, 172 125, 168 118 C 180 90, 182 70, 180 35 Z" />
    <path d="M 105 82 C 130 68, 170 92, 195 78 C 195 86, 190 94, 182 96 C 160 86, 130 106, 105 82 Z" />
  </g>
</svg>'''

with open("static/images/hyundai_logo.svg", "w", encoding="utf-8") as f:
    f.write(hyundai_logo_svg)

# 2. Reusable Car SVGs with tailored styling for each model
def create_car_svg(model_name, make, body_type, primary_color, accent_color):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad_{model_name}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc" />
      <stop offset="100%" stop-color="#e2e8f0" />
    </linearGradient>
    <linearGradient id="carBody_{model_name}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{primary_color}" />
      <stop offset="50%" stop-color="{accent_color}" />
      <stop offset="100%" stop-color="{primary_color}" />
    </linearGradient>
    <linearGradient id="windowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#334155" stop-opacity="0.7" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#002c5f" flood-opacity="0.18" />
    </filter>
  </defs>

  <!-- Background Canvas -->
  <rect width="640" height="360" rx="16" fill="url(#bgGrad_{model_name})" />
  
  <!-- Subtle Studio Grid Floor -->
  <path d="M 40 280 L 600 280 M 80 300 L 560 300 M 120 320 L 520 320" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4 4" />
  
  <!-- Shadow Under Car -->
  <ellipse cx="320" cy="275" rx="230" ry="18" fill="#001a33" opacity="0.25" filter="blur(6px)" />

  <!-- Car Group with Drop Shadow -->
  <g filter="url(#shadow)">
    <!-- Main Body Silhouette -->
    <!-- Front Bumper, Hood, Windshield, Roof, Rear Slope, Trunk -->
    <path d="M 100 235 
             C 100 220, 115 210, 140 205 
             C 170 200, 200 195, 230 165 
             C 260 135, 300 120, 390 120 
             C 450 120, 485 135, 515 175 
             C 535 200, 545 220, 540 238 
             C 538 245, 520 250, 490 250 
             L 450 250 
             C 445 220, 405 220, 400 250 
             L 240 250 
             C 235 220, 195 220, 190 250 
             L 120 250 
             C 105 250, 100 245, 100 235 Z" 
          fill="url(#carBody_{model_name})" stroke="#002c5f" stroke-width="2" />

    <!-- Sleek Aerodynamic Character Lines -->
    <path d="M 145 208 C 220 205, 340 195, 525 185" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.65" />
    <path d="M 180 230 C 260 228, 360 220, 430 225" stroke="#001937" stroke-width="2" opacity="0.3" />

    <!-- Windows Greenhouse -->
    <path d="M 238 168 
             C 265 142, 300 130, 385 130 
             C 440 130, 470 142, 498 175 
             C 460 176, 320 178, 238 168 Z" 
          fill="url(#windowGrad)" stroke="#1e293b" stroke-width="2" />

    <!-- Window Pillar Dividers (B-Pillar & C-Pillar) -->
    <line x1="355" y1="130" x2="352" y2="173" stroke="#0f172a" stroke-width="6" />
    <line x1="435" y1="133" x2="445" y2="173" stroke="#0f172a" stroke-width="5" />

    <!-- Headlight & Tail Light -->
    <!-- Hyundai LED Signature Light Strip -->
    <path d="M 105 225 C 115 215, 140 215, 155 218 L 140 225 Z" fill="#e0f2fe" stroke="#38bdf8" stroke-width="2" />
    <path d="M 525 210 C 538 215, 538 225, 528 230 Z" fill="#ef4444" stroke="#b91c1c" stroke-width="1.5" />

    <!-- Front Wheel -->
    <g transform="translate(215, 250)">
      <circle cx="0" cy="0" r="38" fill="#1e293b" stroke="#0f172a" stroke-width="3" />
      <circle cx="0" cy="0" r="28" fill="#475569" />
      <!-- Alloy Spokes -->
      <circle cx="0" cy="0" r="18" fill="#94a3b8" />
      <circle cx="0" cy="0" r="8" fill="#002c5f" />
      <line x1="-24" y1="0" x2="24" y2="0" stroke="#f8fafc" stroke-width="4" />
      <line x1="0" y1="-24" x2="0" y2="24" stroke="#f8fafc" stroke-width="4" />
      <line x1="-17" y1="-17" x2="17" y2="17" stroke="#f8fafc" stroke-width="4" />
      <line x1="-17" y1="17" x2="17" y2="-17" stroke="#f8fafc" stroke-width="4" />
    </g>

    <!-- Rear Wheel -->
    <g transform="translate(425, 250)">
      <circle cx="0" cy="0" r="38" fill="#1e293b" stroke="#0f172a" stroke-width="3" />
      <circle cx="0" cy="0" r="28" fill="#475569" />
      <!-- Alloy Spokes -->
      <circle cx="0" cy="0" r="18" fill="#94a3b8" />
      <circle cx="0" cy="0" r="8" fill="#002c5f" />
      <line x1="-24" y1="0" x2="24" y2="0" stroke="#f8fafc" stroke-width="4" />
      <line x1="0" y1="-24" x2="0" y2="24" stroke="#f8fafc" stroke-width="4" />
      <line x1="-17" y1="-17" x2="17" y2="17" stroke="#f8fafc" stroke-width="4" />
      <line x1="-17" y1="17" x2="17" y2="-17" stroke="#f8fafc" stroke-width="4" />
    </g>
  </g>

  <!-- Model & Spec Watermark / Badge -->
  <rect x="28" y="24" width="130" height="26" rx="6" fill="#002c5f" />
  <text x="93" y="41" fill="#ffffff" font-family="'Plus Jakarta Sans', 'Inter', sans-serif" font-size="11" font-weight="700" letter-spacing="1.5" text-anchor="middle">{make.upper()}</text>
  
  <text x="28" y="78" fill="#0f172a" font-family="'Plus Jakarta Sans', 'Inter', sans-serif" font-size="22" font-weight="800">{model_name}</text>
  <text x="28" y="98" fill="#64748b" font-family="'Plus Jakarta Sans', 'Inter', sans-serif" font-size="12" font-weight="600" letter-spacing="0.5">{body_type} · Official Workshop Spec</text>
</svg>'''

cars = [
    ("Creta", "Hyundai", "Premium SUV", "#002c5f", "#007fa8"),
    ("Verna", "Hyundai", "Sedan", "#1e3a8a", "#2563eb"),
    ("Tucson", "Hyundai", "Luxury AWD SUV", "#0f172a", "#0284c7"),
    ("City", "Honda", "Sedan", "#991b1b", "#dc2626"),
    ("Fortuner", "Toyota", "Full-Size SUV", "#334155", "#64748b"),
    ("Swift", "Maruti", "Hatchback", "#b91c1c", "#ef4444"),
    ("Nexon", "Tata", "Compact SUV", "#047857", "#10b981"),
    ("Default", "Vehicle", "Service Unit", "#002c5f", "#007fa8")
]

for model, make, body, c1, c2 in cars:
    fname = f"static/images/{model.lower()}.svg"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(create_car_svg(model, make, body, c1, c2))
    print(f"Generated {fname}")

print("All car reference SVG assets created successfully.")
