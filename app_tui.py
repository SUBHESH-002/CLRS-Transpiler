from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, TextArea, Button, Static
from textual.binding import Binding
import transpiler  # Your back-end engine

class CLRSTranspilerTUI(App):
    """A Cyberpunk TUI for the CLRS to Python Transpiler."""
    
    # CSS styling for the Matrix/Cyberpunk aesthetic
    # Final corrected CSS for the Cyberpunk TUI
    CSS = """
    Screen {
        background: #000000;
        color: #00FF41;
    }

    #header {
        background: #001100;
        color: #00FF41;
        text-align: center;
        text-style: bold;
        border-bottom: double #00FF41;
    }

    .pane-container {
        width: 100%;
        height: 100%;
    }

    TextArea {
        background: #000000;
        color: #00FF41;
        border: tall #00FF41;
        height: 1fr; /* Changed from 100% to 1fr to show the button */
    }

    TextArea:focus {
        border: tall #00FF41; 
    }

    #transpile-btn {
        background: #000000;
        color: #00FF41;
        border: wide #00FF41;
        margin: 1 2;
        width: 100%;
        height: 3; /* Fixed height for the button */
    }

    #transpile-btn:hover {
        background: #00FF41;
        color: #000000;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("ctrl+enter", "transpile", "Run Transpiler"),
        Binding("q", "quit", "Quit System")
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="header", show_clock=True)
        with Horizontal(classes="pane-container"):
            with Vertical():
                yield Static(" [ CLRS PSEUDOCODE INPUT ] ", expand=True)
                self.input_area = TextArea(placeholder="procedure INSERTION-SORT(A)...", show_line_numbers=True)
                yield self.input_area
                yield Button("[ RUN_TRANSPILER ]", id="transpile-btn")
            
            with Vertical():
                yield Static(" [ EXECUTABLE PYTHON OUTPUT ] ", expand=True)
                self.output_area = TextArea(read_only=True, show_line_numbers=True)
                yield self.output_area
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "transpile-btn":
            self.action_transpile()

    def action_transpile(self) -> None:
        """The 'Brain' of the TUI: Connects to the transpiler logic."""
        source_code = self.input_area.text
        if not source_code:
            return

        try:
            # Execute the transformation logic (indexing shift, etc.)
            result = transpiler.translate(source_code)
            self.output_area.text = result
            self.notify("TRANSPILATION COMPLETE", severity="information")
        except Exception as e:
            # Stylized error output
            self.output_area.text = f"!!! SYSTEM ERROR !!!\n\n{str(e)}"
            self.notify("CRITICAL ERROR DETECTED", severity="error")

if __name__ == "__main__":
    app = CLRSTranspilerTUI()
    app.run()