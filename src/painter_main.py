from render.painter_renderer import PainterRenderer

if __name__ == "__main__":
    # Create renderer with screen dimensions
    renderer = PainterRenderer(1024, 768)
    # Run the main loop
    renderer.run() 