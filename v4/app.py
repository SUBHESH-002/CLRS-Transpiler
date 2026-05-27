from nicegui import ui
import transpiler
import traceback
import os

# --- Noir Style CSS ---
DARK_BG = 'background-color: #000000 !important;'
WHITE_TEXT = 'color: #FFFFFF !important;'
WHITE_BORDER = 'border: 1px solid #FFFFFF !important;'
MONO_FONT = "font-family: 'Courier New', monospace;"

ui.query('body').style(f'{DARK_BG} {WHITE_TEXT} {MONO_FONT}')

def handle_transpile():
    try:
        source = input_area.value
        if not source: return
        result = transpiler.translate(source, lang_selector.value)
        output_area.set_value(result)
    except Exception:
        output_area.set_value(f"SYSTEM ERROR:\n{traceback.format_exc()}")

# --- UI Layout ---
with ui.column().classes('w-full h-screen p-6 no-wrap items-center'):
    
    # Header & Lang Selector
    with ui.row().classes('w-full justify-between items-center mb-8'):
        ui.label('CLRS TRANSPILER v4').classes('text-3xl font-light')
        test_dir = os.path.join(os.path.dirname(__file__), 'test_cases')
        test_files = [f for f in os.listdir(test_dir) if f.endswith('.clrs')] if os.path.exists(test_dir) else []
        
        def load_test_case(e):
            if e.value and e.value != 'Load Test Case...':
                with open(os.path.join(test_dir, e.value), 'r', encoding='utf-8') as f:
                    input_area.set_value(f.read())
                    
        ui.select(['Load Test Case...'] + test_files, value='Load Test Case...', on_change=load_test_case) \
            .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} width: 250px;')
            
        lang_selector = ui.select(['Python', 'C++'], value='Python') \
            .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} width: 150px;')

    # 50/50 Split
    with ui.row().classes('w-full h-full no-wrap gap-0 items-stretch'):
        
        # Left Pane
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ PSEUDOCODE ]').classes('text-xs tracking-widest')
            input_area = ui.textarea(placeholder='Line-by-line with "end"...') \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} resize: none;')
            ui.button('RUN TRANSPILER', on_click=handle_transpile) \
                .props('flat').classes('w-full py-2').style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER}')

        # Right Pane (Editable)
        with ui.column().classes('w-1/2 h-full gap-4 p-2'):
            ui.label('[ OUTPUT ]').classes('text-xs tracking-widest')
            output_area = ui.textarea() \
                .classes('w-full h-full text-lg p-4') \
                .style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER} resize: none;')
            ui.button('COPY CODE', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText(`{output_area.value}`)')) \
                .props('flat').classes('w-full py-2').style(f'{DARK_BG} {WHITE_TEXT} {WHITE_BORDER}')

ui.run(title='Transpiler v4', dark=True, port=8080)