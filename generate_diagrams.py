from PIL import Image, ImageDraw, ImageFont
import sys

def create_architecture_diagram():
    # Create image
    img = Image.new('RGB', (1200, 1400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Title
    draw.text((600, 60), "PropBot Architecture", fill='#333333', font=title_font, anchor='mm')
    
    # Layers data
    layers = [
        (120, "User Interface Layer", ["Chat Interface", "API Endpoints"]),
        (280, "AI/ML Layer", ["RAG Pipeline", "Embedding Model", "LLM"]),
        (440, "Data Layer", ["PostgreSQL", "ChromaDB", "Redis"]),
        (600, "Data Pipeline Layer", ["Apache Airflow", "Data Validation", "ETL Pipeline"]),
        (760, "External Data Sources", ["Boston Open Data", "Crime Statistics", "Property Listings"])
    ]
    
    for y, title, components in layers:
        # Layer background
        draw.rectangle([50, y, 1150, y+120], fill='#f8f9fa')
        # Left border
        draw.rectangle([50, y, 55, y+120], fill='#667eea')
        # Title
        draw.text((70, y+30), title, fill='#667eea', font=header_font)
        # Components
        for i, comp in enumerate(components):
            draw.text((150 + i*350, y+70), comp, fill='#333333', font=normal_font)
        
        # Arrow (except last layer)
        if y < 760:
            draw.text((600, y+145), "⬇", fill='#667eea', font=title_font, anchor='mm')
    
    img.save('docs/architecture_diagram.png')
    print("✅ Architecture diagram saved!")

def create_gantt_chart():
    img = Image.new('RGB', (1400, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except:
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Title
    draw.text((700, 50), "PropBot Project Timeline", fill='#333333', font=title_font, anchor='mm')
    draw.text((700, 80), "IE 7374 MLOps - Fall 2025", fill='#666666', font=normal_font, anchor='mm')
    
    # Tasks
    tasks = [
        ("Project Setup & Requirements", 1, 1, '#667eea', 'Completed'),
        ("Database Design (PostgreSQL, ChromaDB, Redis)", 2, 1, '#667eea', 'Completed'),
        ("RAG Pipeline Implementation", 3, 2, '#667eea', 'In Progress'),
        ("Apache Airflow Setup", 5, 1, '#f5576c', 'In Progress'),
        ("Data Validation (Great Expectations)", 6, 1, '#f5576c', 'Planned'),
        ("ETL Pipeline Development", 7, 1, '#f5576c', 'Planned'),
        ("Docker Containerization", 8, 1, '#4facfe', 'Planned'),
        ("CI/CD Pipeline (GitHub Actions)", 9, 1, '#4facfe', 'In Progress'),
        ("Testing & Quality Assurance", 10, 1, '#4facfe', 'Planned'),
        ("Model Monitoring & Logging", 11, 1, '#43e97b', 'Planned'),
        ("Production Deployment", 12, 1, '#43e97b', 'Planned'),
        ("Documentation & Presentation", 13, 1, '#43e97b', 'Planned'),
    ]
    
    y = 150
    week_width = 70
    start_x = 600
    
    # Week headers
    for i in range(1, 14):
        draw.text((start_x + (i-1)*week_width + week_width//2, 130), f"Week {i}", 
                 fill='#666666', font=small_font, anchor='mm')
    
    for name, week, width, color, status in tasks:
        # Task name
        draw.text((start_x - 20, y + 15), name, fill='#333333', font=normal_font, anchor='rm')
        
        # Task bar
        bar_x = start_x + (week - 1) * week_width
        bar_width = width * week_width - 5
        draw.rectangle([bar_x, y, bar_x + bar_width, y + 25], fill=color)
        
        # Week label
        draw.text((bar_x + bar_width//2, y + 13), f"W{week}", fill='white', font=small_font, anchor='mm')
        
        # Status
        status_color = '#155724' if status == 'Completed' else '#856404' if status == 'In Progress' else '#666666'
        draw.text((start_x + 13*week_width + 10, y + 15), status, fill=status_color, font=small_font)
        
        y += 40
    
    img.save('docs/gantt_chart.png')
    print("✅ Gantt chart saved!")

if __name__ == "__main__":
    create_architecture_diagram()
    create_gantt_chart()
    print("\n✅ Both diagrams created successfully in docs/ folder!")
