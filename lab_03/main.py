from tkinter import *
import algs
from math import ceil

DEFAULT_ROWS_COUNT = 25
CELL_WIDTH = 5
FONT = ("Arial", 15)


class YScrollableTable:
    def __init__(self, window, columns, rows):
        self.__cellState = "normal"
        self.__visibleRowsCnt = 15
        self.__visibleColumnsCnt = len(columns)

        self.__frameCanvas = LabelFrame(window)
        self.__frameCanvas.grid(column=0, row=0, sticky="nw")
        self.__canvas = Canvas(
            self.__frameCanvas, borderwidth=0, highlightthickness=0
        )
        self.__canvas.grid(
            row=0, column=0, sticky="news", padx=(5, 0), pady=(5, 5)
        )

        self.__scrollbar = Scrollbar(
            self.__frameCanvas, orient="vertical", command=self.__canvas.yview
        )
        self.__scrollbar.grid(row=0, column=1, sticky="ns", padx=0, pady=5)
        self.__canvas.configure(yscrollcommand=self.__scrollbar.set)

        self.__frame = Frame(self.__canvas)
        self.__canvas.create_window((0, 0), window=self.__frame, anchor="nw")

        self.__table = []
        self.__columns = []
        self.__rows = []
        cell = self.__createLabelCell(row=0, column=0)
        for i, rowName in enumerate(rows):
            row = []
            cell = self.__createLabelCell(row=i + 1, column=0, value=rowName)
            self.__rows.append(cell)
            for j, columnName in enumerate(columns):
                cell = self.__createLabelCell(
                    row=0, column=j + 1, value=columnName
                )
                if i == 0:
                    self.__columns.append(cell)

                cell = self.__createTableCell(row=i + 1, column=j + 1, value=0)
                row.append(cell)
            self.__table.append(row)
        self.__frame.update_idletasks()

        self.__width = (
            self.__table[0][0].winfo_width() * self.__visibleColumnsCnt
            + self.__rows[0].winfo_width()
        )
        self.__height = (
            self.__table[0][0].winfo_height() * self.__visibleRowsCnt
            + self.__columns[0].winfo_height()
        )
        self.__canvas.config(width=self.__width, height=self.__height)
        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))

    def __createTableCell(self, row, column, value=0):
        cell = Entry(
            self.__frame,
            width=CELL_WIDTH,
            font=FONT,
            fg="blue",
            highlightthickness=1,
            relief=FLAT,
        )
        cell.insert(END, str(value))
        cell.grid(column=column, row=row, sticky=NSEW)
        cell.config(state=self.__cellState, readonlybackground="red")
        return cell

    def __createLabelCell(self, row, column, value=""):
        cell = Entry(
            self.__frame,
            width=CELL_WIDTH,
            font=FONT,
            highlightthickness=1,
            relief=FLAT,
        )
        cell.grid(column=column, row=row, sticky=NSEW)
        cell.insert(END, str(value))
        cell.config(readonlybackground="red")
        return cell

    def grid(self, row, column, padx=0, pady=0, columnspan=1):
        self.__frameCanvas.grid(
            column=column,
            row=row,
            padx=padx,
            pady=pady,
            columnspan=columnspan,
            sticky="nw",
        )

    def setTitle(self, text):
        self.__frameCanvas.configure(text=text)

    def setVisibleRowsCount(self, cnt):
        self.__visibleRowsCnt = cnt
        self.__height = (
            sum(
                [
                    self.__table[i][0].winfo_height()
                    for i in range(self.__visibleRowsCnt)
                ]
            )
            + self.__columns[0].winfo_height()
        )
        self.__canvas.config(height=self.__height)
        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))

    def rowsCount(self):
        return len(self.__rows)

    def columnsCount(self):
        return len(self.__columns)

    def width(self):
        return self.__width

    def height(self):
        return self.__height

    def visibleRowsCount(self):
        return self.__visibleRowsCnt

    def visibleColumnsCount(self):
        return self.__visibleColumnsCnt

    def table(self):
        return [[cell.get() for cell in row] for row in self.__table]

    def setCellState(self, state):
        self.__cellState = state
        for row in self.__table:
            for cell in row:
                cell.config(state=self.__cellState)

    def setCellValue(self, value, row, column):
        self.__table[row - 1][column - 1].config(state="normal")
        self.__table[row - 1][column - 1].delete(0, END)
        self.__table[row - 1][column - 1].insert(END, value)
        self.__table[row - 1][column - 1].config(state=self.__cellState)

    def setRowName(self, row, name):
        self.__rows[row - 1].config(state="normal")
        self.__rows[row - 1].delete(0, END)
        self.__rows[row - 1].insert(END, name)
        # self.__rows[row - 1].config(state="readonly")

    def addRow(self, name, values=[]):
        i = len(self.__rows)
        cell = self.__createLabelCell(row=i + 1, column=0, value=name)
        self.__rows.append(cell)

        row = []
        for j in range(len(self.__columns)):
            cell = self.__createTableCell(row=i + 1, column=j + 1, value=0)
            cell.config(state="normal")
            cell.delete(0, END)
            if len(values) != 0:
                cell.insert(END, values[j])
            else:
                cell.insert(END, 0)
            cell.config(state=self.__cellState)
            row.append(cell)
        self.__table.append(row)

        self.__canvas.update_idletasks()
        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))
        self.__canvas.yview_moveto("1.0")

    def removeRow(self, index=None):
        if not index:
            index = len(self.__rows)

        self.__rows[index - 1].destroy()
        del self.__rows[index - 1]
        for cell in self.__table[index - 1]:
            cell.destroy()
        del self.__table[index - 1]

        self.__canvas.update_idletasks()
        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))
        self.__canvas.yview_moveto("1.0")


def __generateMethod(method, count, step, table, txtRes):
    if count < 0 or step < 0:
        return

    seq1digit = method(count, 0, 10)
    seq2digit = method(count, 10, 100)
    seq3digit = method(count, 100, 1000)

    seq = []
    seq.append(seq1digit)
    seq.append(seq2digit)
    seq.append(seq3digit)

    columnsCount = table.columnsCount()
    iSeq = 0
    iRow = 0
    while iSeq < count:
        if iRow >= table.rowsCount():
            table.addRow(
                name=str(iSeq + 1),
                values=[seq[j][iSeq] for j in range(columnsCount)],
            )
        else:
            table.setRowName(row=iRow + 1, name=str(iSeq + 1))
            for j in range(columnsCount):
                table.setCellValue(seq[j][iSeq], iRow + 1, j + 1)
        iRow += 1
        iSeq += step

    while table.rowsCount() > ceil(count / step):
        table.removeRow()

    for i, s in enumerate(seq):
        factor = algs.approve_sequence(s)
        txtRes[i].config(state="normal")
        txtRes[i].delete(0, END)
        txtRes[i].insert(END, "{:.2f}".format(factor))
        # txtRes[i].config(state="readonly")


def calculateManual():
    seq = list(map(lambda n: int(n[0]), tableManual.table()))
    print(seq)
    factor = algs.approve_sequence(seq)
    txtResManual.config(state="normal")
    txtResManual.delete(0, END)
    txtResManual.insert(END, "{:.2f}".format(factor))
    # txtResManual.config(state="readonly")


def generateAlgorithmic():
    global tableAlgorithmic, txtResAlgorithmic
    count = int(txtCountAlgorithmic.get())
    step = int(txtStepAlgorithmic.get())
    __generateMethod(
        algs.generate_linear_congruent,
        count,
        step,
        tableAlgorithmic,
        txtResAlgorithmic,
    )


def generateTabular():
    global tableTabular, txtResTabular
    count = int(txtCountTabular.get())
    step = int(txtStepTabular.get())
    __generateMethod(
        algs.generate_tabular, count, step, tableTabular, txtResTabular
    )


window = Tk()

window.title("Lab3: Random number generators")
window.geometry("720x700")
window.resizable(False, False)

tableManual = YScrollableTable(
    window, columns=["any"], rows=[i + 1 for i in range(DEFAULT_ROWS_COUNT)]
)
tableManual.setTitle("Manual input: ")
tableManual.grid(row=1, column=0, padx=20, pady=10, columnspan=2)

btnAddManual = Button(
    window,
    text="+",
    width=3,
    command=lambda: tableManual.addRow(len(tableManual.table()) + 1),
)
btnAddManual.grid(row=2, column=0, padx=(20, 0), pady=5, sticky="we")

btnRemoveManual = Button(
    window, text="-", width=3, command=lambda: tableManual.removeRow()
)
btnRemoveManual.grid(row=2, column=1, padx=(0, 20), pady=5, sticky="we")

btnCalcManual = Button(window, text="Calculate", command=calculateManual)
btnCalcManual.grid(row=3, column=0, padx=20, columnspan=2, sticky="we")

tableTabular = YScrollableTable(
    window,
    columns=["1-digit", "2-digit", "3-digit"],
    rows=[i + 1 for i in range(DEFAULT_ROWS_COUNT)],
)
tableTabular.setTitle("Tabular method: ")
tableTabular.grid(row=1, column=2, padx=20, pady=10, columnspan=4)
# tableTabular.setCellState("readonly")

lblCountTabular = Label(window, text="Count:")
lblCountTabular.grid(row=2, column=2, padx=(20, 0), pady=5, sticky="we")

txtCountTabular = Entry(window, font=FONT, width=3)
txtCountTabular.grid(row=2, column=3, padx=(0, 0), pady=5, sticky="we")
txtCountTabular.insert(END, 100)

lblStepTabular = Label(window, text="Step:")
lblStepTabular.grid(row=2, column=4, padx=(0, 0), pady=5, sticky="we")

txtStepTabular = Entry(window, font=FONT, width=3)
txtStepTabular.grid(row=2, column=5, padx=(0, 20), pady=5, sticky="we")
txtStepTabular.insert(END, 1)

btnCalcTabular = Button(window, text="Calculate", command=generateTabular)
btnCalcTabular.grid(row=3, column=2, padx=20, columnspan=4, sticky="we")

tableAlgorithmic = YScrollableTable(
    window,
    columns=["1-digit", "2-digit", "3-digit"],
    rows=[i + 1 for i in range(DEFAULT_ROWS_COUNT)],
)
tableAlgorithmic.setTitle("Algorithmic method: ")
tableAlgorithmic.grid(row=1, column=6, padx=20, pady=10, columnspan=4)
# tableAlgorithmic.setCellState(state="readonly")

lblCountAlgorithmic = Label(window, text="Count:")
lblCountAlgorithmic.grid(row=2, column=6, padx=(20, 0), pady=5, sticky="we")

txtCountAlgorithmic = Entry(window, font=FONT, width=3)
txtCountAlgorithmic.grid(row=2, column=7, padx=(0, 0), pady=5, sticky="we")
txtCountAlgorithmic.insert(END, 100)

lblStepAlgorithmic = Label(window, text="Step:")
lblStepAlgorithmic.grid(row=2, column=8, padx=(0, 0), pady=5, sticky="we")

txtStepAlgorithmic = Entry(window, font=FONT, width=3)
txtStepAlgorithmic.grid(row=2, column=9, padx=(0, 20), pady=5, sticky="we")
txtStepAlgorithmic.insert(END, 1)

btnCalcAlgorithmic = Button(
    window, text="Calculate", command=generateAlgorithmic
)
btnCalcAlgorithmic.grid(row=3, column=6, padx=20, columnspan=4, sticky="we")

frameResManual = LabelFrame(window, text="Randomness rate:")
frameResManual.grid(row=5, column=0, padx=20, pady=20, columnspan=2)

lblResManual = Label(frameResManual, text="factor: ", width=CELL_WIDTH)
lblResManual.grid(row=0, column=0, pady=10, padx=(10, 0), sticky=NSEW)

txtResManual = Entry(
    frameResManual,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResManual.grid(row=0, column=1, pady=10, padx=(0, 10), sticky=NSEW)
# txtResManual.config(state="readonly")


frameResTabular = LabelFrame(window, text="Randomness rate:")
frameResTabular.grid(row=5, column=2, padx=20, pady=20, columnspan=4)

lblResTabular = Label(frameResTabular, text="factor: ", width=CELL_WIDTH)
lblResTabular.grid(row=0, column=0, pady=10, padx=(10, 0), sticky=NSEW)

txtResTabular = []

txtResTabular1 = Entry(
    frameResTabular,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResTabular1.grid(row=0, column=1, pady=10, sticky=NSEW)
# txtResTabular1.config(state="readonly")
txtResTabular.append(txtResTabular1)

txtResTabular2 = Entry(
    frameResTabular,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResTabular2.grid(row=0, column=2, pady=10, sticky=NSEW)
# txtResTabular2.config(state="readonly")
txtResTabular.append(txtResTabular2)

txtResTabular3 = Entry(
    frameResTabular,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResTabular3.grid(row=0, column=3, pady=10, padx=(0, 10), sticky=NSEW)
# txtResTabular3.config(state="readonly")
txtResTabular.append(txtResTabular3)

frameResAlgorithmic = LabelFrame(window, text="Randomness rate:")
frameResAlgorithmic.grid(row=5, column=6, padx=20, pady=20, columnspan=6)

lblResAlgorithmic = Label(
    frameResAlgorithmic, text="factor: ", width=CELL_WIDTH
)
lblResAlgorithmic.grid(row=0, column=0, pady=10, padx=(10, 0), sticky=NSEW)

txtResAlgorithmic = []

txtResAlgorithmic1 = Entry(
    frameResAlgorithmic,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResAlgorithmic1.grid(row=0, column=1, padx=(0, 0), pady=10)
# txtResAlgorithmic1.config(state="readonly")
txtResAlgorithmic.append(txtResAlgorithmic1)

txtResAlgorithmic2 = Entry(
    frameResAlgorithmic,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResAlgorithmic2.grid(row=0, column=2, padx=(0, 0), pady=10)
# txtResTabular2.config(state="readonly")
txtResAlgorithmic.append(txtResAlgorithmic2)

txtResAlgorithmic3 = Entry(
    frameResAlgorithmic,
    width=CELL_WIDTH,
    font=FONT,
    highlightthickness=1,
    relief=FLAT,
    readonlybackground="green",
)
txtResAlgorithmic3.grid(row=0, column=3, padx=(0, 10), pady=10)
# txtResAlgorithmic3.config(state="readonly")
txtResAlgorithmic.append(txtResAlgorithmic3)

window.mainloop()
