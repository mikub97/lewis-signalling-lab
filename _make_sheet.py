"""Creates lewis_signalling_game.xlsx for the human experiment."""

from openpyxl import Workbook
from openpyxl.styles import (
    Alignment, Border, Font, PatternFill, Side
)
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.datavalidation import DataValidation

STATES = [
    3,1,4,2,3,4,1,2,4,3,
    2,1,3,4,1,2,4,3,1,4,
    2,3,1,4,3,2,4,1,2,3,
    4,1,3,2,1,4,2,3,4,1,
]

wb = Workbook()
ws = wb.active
ws.title = "Game"

# ── Styles ────────────────────────────────────────────────────────────────────
thin = Side(style="thin", color="BBBBBB")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

hdr_fill   = PatternFill("solid", fgColor="2F4F7F")   # dark blue header
sender_fill = PatternFill("solid", fgColor="FFF3CD")  # pale yellow — sender only
input_fill  = PatternFill("solid", fgColor="F0F8FF")  # pale blue — input cells
match_fill  = PatternFill("solid", fgColor="F5F5F5")  # light grey — formula

green_fill = PatternFill("solid", fgColor="C6EFCE")
red_fill   = PatternFill("solid", fgColor="FFC7CE")

hdr_font  = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
data_font = Font(name="Calibri", size=11)
note_font = Font(name="Calibri", size=9, italic=True, color="888888")

center = Alignment(horizontal="center", vertical="center")

# ── Column widths ─────────────────────────────────────────────────────────────
ws.column_dimensions["A"].width = 9
ws.column_dimensions["B"].width = 16
ws.column_dimensions["C"].width = 22
ws.column_dimensions["D"].width = 22
ws.column_dimensions["E"].width = 10
ws.column_dimensions["F"].width = 10

# ── Sub-header row (row 1) ─────────────────────────────────────────────────────
ws.row_dimensions[1].height = 14
note = ws.cell(1, 2, "⚠ Receiver: hide this column →")
note.font = Font(name="Calibri", size=9, italic=True, color="B85C00", bold=True)
note.alignment = Alignment(horizontal="left")

# ── Header row (row 2) ────────────────────────────────────────────────────────
ws.row_dimensions[2].height = 24
headers = ["Round", "State\n(Sender only)", "Signal\n(Sender: A/B/C/D)", "Action\n(Receiver: 1/2/3/4)", "Match?", "Reward"]
for col, text in enumerate(headers, 1):
    cell = ws.cell(2, col, text)
    cell.font = hdr_font
    cell.fill = hdr_fill
    cell.border = border
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# ── Data rows (rows 3–42) ──────────────────────────────────────────────────────
for i, state in enumerate(STATES):
    row = i + 3

    # Round
    c = ws.cell(row, 1, i + 1)
    c.font = data_font; c.fill = input_fill; c.border = border; c.alignment = center

    # State
    c = ws.cell(row, 2, state)
    c.font = Font(name="Calibri", size=11, bold=True)
    c.fill = sender_fill; c.border = border; c.alignment = center

    # Signal (empty — sender fills in)
    c = ws.cell(row, 3, "")
    c.fill = input_fill; c.border = border; c.alignment = center

    # Action (empty — receiver fills in)
    c = ws.cell(row, 4, "")
    c.fill = input_fill; c.border = border; c.alignment = center

    # Match formula
    c = ws.cell(row, 5)
    c.value = f'=IF(AND(C{row}<>"",D{row}<>""),IF(B{row}=D{row},"✓","✗"),"")'
    c.fill = match_fill; c.border = border; c.alignment = center
    c.font = Font(name="Calibri", size=12, bold=True)

    # Reward formula (for analysis)
    c = ws.cell(row, 6)
    c.value = f'=IF(AND(C{row}<>"",D{row}<>""),IF(B{row}=D{row},1,0),"")'
    c.fill = match_fill; c.border = border; c.alignment = center
    c.font = data_font

# ── Conditional formatting on Match column ────────────────────────────────────
match_range = "E3:E42"
ws.conditional_formatting.add(
    match_range,
    CellIsRule(operator="equal", formula=['"✓"'], fill=green_fill)
)
ws.conditional_formatting.add(
    match_range,
    CellIsRule(operator="equal", formula=['"✗"'], fill=red_fill)
)

# ── Data validation — Signal column (A/B/C/D) ─────────────────────────────────
dv_signal = DataValidation(type="list", formula1='"A,B,C,D"', allow_blank=True)
dv_signal.error = "Enter A, B, C, or D"
dv_signal.errorTitle = "Invalid signal"
dv_signal.prompt = "Type A, B, C, or D"
dv_signal.promptTitle = "Sender: choose a signal"
ws.add_data_validation(dv_signal)
dv_signal.sqref = "C3:C42"

# ── Data validation — Action column (1/2/3/4) ────────────────────────────────
dv_action = DataValidation(type="list", formula1='"1,2,3,4"', allow_blank=True)
dv_action.error = "Enter 1, 2, 3, or 4"
dv_action.errorTitle = "Invalid action"
dv_action.prompt = "Type 1, 2, 3, or 4"
dv_action.promptTitle = "Receiver: choose an action"
ws.add_data_validation(dv_action)
dv_action.sqref = "D3:D42"

# ── Freeze top two rows ────────────────────────────────────────────────────────
ws.freeze_panes = "A3"

# ── Analysis sheet ────────────────────────────────────────────────────────────
wa = wb.create_sheet("Analysis")
wa.column_dimensions["A"].width = 18
wa.column_dimensions["B"].width = 14

wa["A1"] = "Analysis"
wa["A1"].font = Font(bold=True, size=14, name="Calibri")

wa["A3"] = "Total rounds played"
wa["B3"] = '=COUNTA(Game!F3:F42)'
wa["A4"] = "Total reward"
wa["B4"] = '=SUM(Game!F3:F42)'
wa["A5"] = "Accuracy"
wa["B5"] = '=IF(B3>0,B4/B3,"")'
wa["B5"].number_format = "0.0%"

wa["A7"] = "Rolling avg (window=5)"
wa["A7"].font = Font(bold=True, name="Calibri")
wa["A8"] = "Round"
wa["B8"] = "5-round avg"
for i in range(5, 41):
    wa.cell(i - 5 + 9, 1, i)
    wa.cell(i - 5 + 9, 2).value = (
        f"=IF(COUNTA(Game!F{i-1}:F{i+3})=5,"
        f"AVERAGE(Game!F{i-1}:F{i+3}),\"\")"
    )

for cell in [wa["A3"], wa["A4"], wa["A5"]]:
    cell.font = Font(name="Calibri", size=11)
for cell in [wa["B3"], wa["B4"], wa["B5"]]:
    cell.font = Font(name="Calibri", size=11, bold=True)
    cell.alignment = Alignment(horizontal="center")

out = "/Users/m11/Documents/Nauczanie/cpm2/signalling/lewis_signalling_game.xlsx"
wb.save(out)
print(f"Saved: {out}")
