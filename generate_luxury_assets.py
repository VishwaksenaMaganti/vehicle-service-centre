"""
Generate luxury car model visuals and emblems for BMW and Porsche models.
"""
import os

os.makedirs("static/images", exist_ok=True)

# 1. BMW Roundel Logo SVG
bmw_logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <circle cx="50" cy="50" r="48" fill="#ffffff" stroke="#000000" stroke-width="4"/>
  <circle cx="50" cy="50" r="40" fill="#000000"/>
  <!-- Silver Text Ring -->
  <text x="50" y="24" fill="#ffffff" font-family="'Inter', sans-serif" font-weight="900" font-size="14" text-anchor="middle" letter-spacing="4">BMW</text>
  <!-- Inner Quarters -->
  <g transform="translate(50,50)">
    <circle cx="0" cy="0" r="26" fill="#ffffff" stroke="#ffffff" stroke-width="1"/>
    <!-- Top-Left quadrant (Blue) -->
    <path d="M 0 0 L 0 -26 A 26 26 0 0 0 -26 0 Z" fill="#0066B1"/>
    <!-- Bottom-Right quadrant (Blue) -->
    <path d="M 0 0 L 0 26 A 26 26 0 0 0 26 0 Z" fill="#0066B1"/>
  </g>
</svg>'''

with open("static/images/bmw_logo.svg", "w", encoding="utf-8") as f:
    f.write(bmw_logo_svg)

# 2. Porsche Crest / Lettermark SVG
porsche_logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 50" width="240" height="50">
  <text x="120" y="32" fill="#111111" font-family="'Inter', sans-serif" font-weight="800" font-size="24" letter-spacing="10" text-anchor="middle">PORSCHE</text>
</svg>'''

with open("static/images/porsche_logo.svg", "w", encoding="utf-8") as f:
    f.write(porsche_logo_svg)

# 3. Model silhouettes for the luxury cars
def make_luxury_car_svg(brand, model_name, subtitle, bg_color, car_color, accent_color):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 340" width="100%" height="100%">
  <defs>
    <linearGradient id="grad_{model_name.replace(' ', '_')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f1f3f5"/>
    </linearGradient>
    <filter id="carShadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000000" flood-opacity="0.25"/>
    </filter>
  </defs>

  <rect width="600" height="340" rx="12" fill="url(#grad_{model_name.replace(' ', '_')})" stroke="#e9ecef" stroke-width="1"/>
  
  <!-- Subtle floor line -->
  <line x1="40" y1="260" x2="560" y2="260" stroke="#dee2e6" stroke-width="1.5" stroke-dasharray="6 4"/>
  <ellipse cx="300" cy="256" rx="210" ry="14" fill="#000000" opacity="0.2" filter="blur(5px)"/>

  <!-- Brand watermark -->
  <text x="40" y="50" fill="#111111" font-family="'Inter', sans-serif" font-size="11" font-weight="800" letter-spacing="3">{brand.upper()}</text>
  <text x="40" y="78" fill="#111111" font-family="'Inter', sans-serif" font-size="22" font-weight="800">{model_name}</text>
  <text x="40" y="98" fill="#6c757d" font-family="'Inter', sans-serif" font-size="12" font-weight="500">{subtitle}</text>

  <!-- Luxury Silhouette -->
  <g filter="url(#carShadow)">
    <path d="M 90 220 
             C 95 205, 115 195, 150 190 
             C 185 185, 210 180, 245 150 
             C 280 120, 330 110, 420 112 
             C 475 114, 505 130, 525 165 
             C 535 185, 540 210, 535 224 
             C 530 230, 500 232, 470 232 
             L 440 232 
             C 435 205, 395 205, 390 232 
             L 220 232 
             C 215 205, 175 205, 170 232 
             L 105 232 
             C 95 232, 90 228, 90 220 Z" 
          fill="{car_color}" stroke="#111111" stroke-width="2"/>
    
    <!-- Aerodynamic Roof and Windows -->
    <path d="M 245 152 
             C 275 125, 320 118, 415 118 
             C 460 118, 485 130, 508 165 
             C 460 166, 320 168, 245 152 Z" 
          fill="#111111" stroke="#212529" stroke-width="1.5"/>

    <line x1="355" y1="118" x2="352" y2="162" stroke="#000000" stroke-width="5"/>

    <!-- Light bar -->
    <path d="M 95 210 C 110 205, 130 205, 145 208 Z" fill="#ffffff" stroke="{accent_color}" stroke-width="2"/>
    <path d="M 525 195 C 535 200, 535 210, 528 214 Z" fill="#ff0000" stroke="#cc0000" stroke-width="1"/>

    <!-- Front Wheel -->
    <g transform="translate(195, 232)">
      <circle cx="0" cy="0" r="34" fill="#111111"/>
      <circle cx="0" cy="0" r="24" fill="#343a40"/>
      <circle cx="0" cy="0" r="14" fill="#adb5bd"/>
      <line x1="-20" y1="0" x2="20" y2="0" stroke="#ffffff" stroke-width="3"/>
      <line x1="0" y1="-20" x2="0" y2="20" stroke="#ffffff" stroke-width="3"/>
      <line x1="-14" y1="-14" x2="14" y2="14" stroke="#ffffff" stroke-width="3"/>
      <line x1="-14" y1="14" x2="14" y2="-14" stroke="#ffffff" stroke-width="3"/>
    </g>

    <!-- Rear Wheel -->
    <g transform="translate(415, 232)">
      <circle cx="0" cy="0" r="34" fill="#111111"/>
      <circle cx="0" cy="0" r="24" fill="#343a40"/>
      <circle cx="0" cy="0" r="14" fill="#adb5bd"/>
      <line x1="-20" y1="0" x2="20" y2="0" stroke="#ffffff" stroke-width="3"/>
      <line x1="0" y1="-20" x2="0" y2="20" stroke="#ffffff" stroke-width="3"/>
      <line x1="-14" y1="-14" x2="14" y2="14" stroke="#ffffff" stroke-width="3"/>
      <line x1="-14" y1="14" x2="14" y2="-14" stroke="#ffffff" stroke-width="3"/>
    </g>
  </g>
</svg>'''

models = [
    ("bmw_7_series", "BMW", "7 Series Sedan", "Flagship Executive Sedan", "#ffffff", "#1e293b", "#0066B1"),
    ("bmw_i7", "BMW", "i7 xDrive60", "All-Electric Luxury Sedan", "#ffffff", "#0f172a", "#38bdf8"),
    ("porsche_911", "Porsche", "911 Carrera", "Iconic Rear-Engine Sports Car", "#ffffff", "#7f1d1d", "#dc2626"),
    ("porsche_taycan", "Porsche", "Taycan Turbo", "High-Voltage Electric GT", "#ffffff", "#1e3a8a", "#60a5fa"),
    ("porsche_718", "Porsche", "718 Boxster", "Mid-Engine Precision Roadster", "#ffffff", "#14532d", "#22c55e")
]

for fname, brand, mname, sub, bg, car_col, acc in models:
    path = f"static/images/{fname}.svg"
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_luxury_car_svg(brand, mname, sub, bg, car_col, acc))
    print("Generated", path)
