from nicegui import ui
import transpiler  # Your back-end engine
import traceback

# --- Strict Monochrome Configuration ---
DARK_BG = 'background-color: #000000 !important;'
WHITE_TEXT = 'color: #FFFFFF !important;'
WHITE_BORDER = 'border: 1px solid #FFFFFF !important;'
MONO_FONT = "font-family: 'Courier New', Courier, monospace;"

# Force global body styling for pure black background
ui.query('body').style(f'{DARK_BG} {WHITE_TEXT} {MONO_FONT}')

def handle_transpile():
    """Triggers the indexing shift and logic conversion."""
    try:
        source = input_area.value
        if not source:
            return
            
        # Execute the transformation logic
        result = transpiler.translate(source)
        output_area.set_value(result)
    except Exception:
        error_msg = f"SYSTEM ERROR:\n{traceback.format_exc()}"
        output_area.set_value(error_msg)

# --- Cleaned UI Layout ---
with ui.column().classes('w-full h-screen p-6 no-wrap items-center'):
    
    # 1. Header (Emoji and v1.0 removed)
    ui.label('CLRS-TO-PYTHON TRANSPILER').classes('text-3xl font-light mb-8')
    
    # 2. Side-by-Side Split (Separator/Gap removed)
    with ui.row().classes('w-full h-full no-wrap gap-0 items-stretch'):
        
        # Left Pane: Pseudocode
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ PSEUDOCODE ]').classes('text-xs tracking-widest')
            input_area = ui.textarea(placeholder='Enter pseudocode...') \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} {MONO_FONT} resize: none;')
            
            # Button (Blue removed, set to pure black/white)
            ui.button('RUN TRANSPILER', on_click=handle_transpile) \
                .props('flat') \
                .classes('w-full py-2') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} border-radius: 0px; text-transform: uppercase;')

        # Right Pane: Python Output
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ PYTHON CODE ]').classes('text-xs tracking-widest')
            output_area = ui.textarea().props('readonly') \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} {MONO_FONT} resize: none;')
            
            # Button (Blue removed, set to pure black/white)
            ui.button('COPY CODE', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{output_area.value}`)')) \
                .props('flat') \
                .classes('w-full py-2') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} border-radius: 0px; text-transform: uppercase;')

ui.run(title='Transpiler', dark=True, port=8080)