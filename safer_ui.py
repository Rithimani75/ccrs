import os
import glob
import re

emoji_map = {
    '🔒': '<i class="fas fa-lock"></i>',
    '👋': '<i class="fas fa-hand-paper"></i>',
    '📋': '<i class="fas fa-clipboard-list"></i>',
    '⏳': '<i class="fas fa-hourglass-half"></i>',
    '⚙️': '<i class="fas fa-cog"></i>',
    '⚙': '<i class="fas fa-cog"></i>',
    '✅': '<i class="fas fa-check-circle"></i>',
    '🔍': '<i class="fas fa-search"></i>',
    '📊': '<i class="fas fa-chart-bar"></i>',
    '📝': '<i class="fas fa-edit"></i>',
    '👤': '<i class="fas fa-user"></i>',
    '👨‍💼': '<i class="fas fa-user-tie"></i>',
    '👩‍💼': '<i class="fas fa-user-tie"></i>',
    '🏢': '<i class="fas fa-building"></i>',
    '📈': '<i class="fas fa-chart-line"></i>',
    '🛡️': '<i class="fas fa-shield-alt"></i>',
    '🛡': '<i class="fas fa-shield-alt"></i>',
    '🔑': '<i class="fas fa-key"></i>',
    '🚪': '<i class="fas fa-sign-out-alt"></i>',
    '📧': '<i class="fas fa-envelope"></i>',
    '📅': '<i class="fas fa-calendar-alt"></i>',
    '🎓': '<i class="fas fa-graduation-cap"></i>',
    '⚠️': '<i class="fas fa-exclamation-triangle"></i>',
    '⚠': '<i class="fas fa-exclamation-triangle"></i>',
    '💬': '<i class="fas fa-comment"></i>',
    '✨': '<i class="fas fa-sparkles"></i>',
    '🔎': '<i class="fas fa-search"></i>',
    '🗑️': '<i class="fas fa-trash-alt"></i>',
    '🗑': '<i class="fas fa-trash-alt"></i>',
    '❌': '<i class="fas fa-times-circle"></i>',
    '🟢': '<i class="fas fa-circle" style="color: #10b981;"></i>',
    '🟠': '<i class="fas fa-circle" style="color: #f59e0b;"></i>',
    '🔴': '<i class="fas fa-circle" style="color: #ef4444;"></i>'
}

head_injection = """
    <!-- Professional Fonts and Icons -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
"""

polish_css = """
        <style>
            /* Global Polish */
            body { font-family: 'Inter', sans-serif !important; }
            input, button, select, textarea { font-family: 'Inter', sans-serif !important; }
            .btn, button, .button { transition: all 0.2s ease-in-out !important; cursor: pointer; }
            .btn:hover, button:hover, .button:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            input:focus, textarea:focus, select:focus { outline: none !important; border-color: #3b82f6 !important; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3) !important; }
        </style>
    </head>
"""

templates = glob.glob('templates/*.html')

for template in templates:
    with open(template, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject head
    if '<link rel="preconnect" href="https://fonts.googleapis.com">' not in content:
        content = content.replace('</head>', head_injection + '</head>')
    
    # Replace emojis
    for emoji, fa_tag in emoji_map.items():
        content = content.replace(emoji, fa_tag)
        
    # Remove all other non-ascii emoji characters to prevent mojibake
    content = re.sub(r'[\U00010000-\U0010ffff]', '', content)

    # Safe font-family replacement (only characters within the same line)
    content = re.sub(r"font-family:[^\n;}]*([;}])", r"font-family: 'Inter', sans-serif\1", content)

    # Add polish css
    if "/* Global Polish */" not in content:
        content = content.replace('</head>', polish_css)

    with open(template, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Updated all templates successfully.")
