from nicegui import ui
import transpiler
import traceback

# --- Noir Style CSS (Strict Monochrome) ---
DARK_BG = 'background-color: #000000 !important;'
WHITE_TEXT = 'color: #FFFFFF !important;'
WHITE_BORDER = 'border: 1px solid #FFFFFF !important;'
MONO_FONT = "font-family: 'Courier New', monospace;"

# Force global body styling to override default web backgrounds
ui.query('body').style(f'{DARK_BG} {WHITE_TEXT} {MONO_FONT}')

def handle_transpile():
    try:
        source = input_area.value
        if not source: 
            return
        # Passes both the code and the selected target language to the engine
        result = transpiler.translate(source, lang_selector.value)
        output_area.set_value(result)
    except Exception:
        # Displays the full traceback in the output area for debugging
        output_area.set_value(f"SYSTEM ERROR:\n{traceback.format_exc()}")

# --- Layout Configuration ---
with ui.column().classes('w-full h-screen p-6 no-wrap items-center'):
    
    # Header & Language Selector Row
    with ui.row().classes('w-full justify-between items-center mb-8'):
        ui.label('CLRS TRANSPILER').classes('text-3xl font-light')
        lang_selector = ui.select(['Python', 'C++'], value='Python') \
            .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} width: 150px;')

    # 50/50 Split Container (Forced Side-by-Side)
    with ui.row().classes('w-full h-full no-wrap gap-0 items-stretch'):
        
        # Left Pane: Pseudocode Input
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ PSEUDOCODE ]').classes('text-xs tracking-widest')
            input_area = ui.textarea(placeholder='Line-by-line code with "end"...') \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} resize: none; box-shadow: none;')
            
            ui.button('RUN TRANSPILER', on_click=handle_transpile) \
                .props('flat').classes('w-full py-2') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} border-radius: 0px;')

        # Right Pane: Editable Output
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ EDITABLE OUTPUT ]').classes('text-xs tracking-widest')
            # CHANGE: Removed .props('readonly') to enable manual editing
            output_area = ui.textarea() \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} resize: none; box-shadow: none;')
            
            ui.button('COPY CODE', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{output_area.value}`)')) \
                .props('flat').classes('w-full py-2') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} border-radius: 0px;')

ui.run(title='Transpiler', dark=True, port=8080)